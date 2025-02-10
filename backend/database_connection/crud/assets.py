# crud/assets.py
"""
CRUD operations for assets and related tables (categories, owners, growth adjustments).
Handles asset creation, ownership management, and growth rate adjustments.
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class AssetsCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("assets")
        self.id_field = "asset_id"

    async def create_asset_category(self, household_id: int, category_name: str) -> int:
        """
        Create a new asset category for a household.
        
        Args:
            household_id: ID of the household this category belongs to
            category_name: Name of the category (e.g., "Real Estate", "Retirement Accounts")
            
        Returns:
            The ID of the created category
        """
        try:
            data = {
                "household_id": household_id,
                "category_name": category_name
            }
            async with DatabaseConnection.transaction() as conn:
                cursor = await conn.execute(
                    "INSERT INTO asset_categories (household_id, category_name) VALUES (?, ?)",
                    (household_id, category_name)
                )
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating asset category: {str(e)}")
            raise

    async def create_asset(
        self,
        plan_id: int,
        asset_category_id: int,
        asset_name: str,
        value: float,
        owner_ids: List[int],
        include_in_nest_egg: bool = True,
        independent_growth_rate: Optional[float] = None
    ) -> int:
        """
        Create a new asset with owners.
        
        Args:
            plan_id: ID of the financial plan this asset belongs to
            asset_category_id: ID of the asset's category
            asset_name: Name of the asset
            value: Current value of the asset
            owner_ids: List of person IDs who own this asset
            include_in_nest_egg: Whether to include in retirement calculations
            independent_growth_rate: Optional specific growth rate for this asset
            
        Returns:
            The ID of the created asset
            
        Raises:
            ValueError: If value is negative or growth rate is outside allowed range
            ValueError: If no owners are provided
            ValueError: If any owner doesn't belong to the household
        """
        if value < 0:
            raise ValueError("Asset value cannot be negative")
        if independent_growth_rate is not None and (independent_growth_rate < -200 or independent_growth_rate > 200):
            raise ValueError("Growth rate must be between -200 and 200")
        if not owner_ids:
            raise ValueError("At least one owner must be specified")

        try:
            # Verify owners belong to the household
            async with DatabaseConnection.transaction() as conn:
                # Get household_id from plan
                async with conn.execute(
                    "SELECT household_id FROM plans WHERE plan_id = ?",
                    (plan_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Invalid plan_id")
                    household_id = row[0]

                # Verify all owners belong to the household
                owner_placeholders = ','.join(['?' for _ in owner_ids])
                query = f"""
                    SELECT COUNT(*) 
                    FROM people 
                    WHERE person_id IN ({owner_placeholders})
                    AND household_id = ?
                """
                async with conn.execute(query, tuple(owner_ids) + (household_id,)) as cursor:
                    count = (await cursor.fetchone())[0]
                    if count != len(owner_ids):
                        raise ValueError("All owners must belong to the household")

                # Create asset
                data = {
                    "plan_id": plan_id,
                    "asset_category_id": asset_category_id,
                    "asset_name": asset_name,
                    "value": value,
                    "include_in_nest_egg": include_in_nest_egg,
                    "independent_growth_rate": independent_growth_rate
                }
                cursor = await conn.execute(
                    """
                    INSERT INTO assets (
                        plan_id, asset_category_id, asset_name, value,
                        include_in_nest_egg, independent_growth_rate
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["plan_id"],
                        data["asset_category_id"],
                        data["asset_name"],
                        data["value"],
                        data["include_in_nest_egg"],
                        data["independent_growth_rate"]
                    )
                )
                asset_id = cursor.lastrowid

                # Create ownership records
                for owner_id in owner_ids:
                    await conn.execute(
                        "INSERT INTO asset_owners (asset_id, person_id) VALUES (?, ?)",
                        (asset_id, owner_id)
                    )

                return asset_id

        except Exception as e:
            logger.error(f"Error creating asset: {str(e)}")
            raise

    async def add_growth_adjustment(
        self,
        asset_id: int,
        start_year: int,
        end_year: int,
        growth_rate: float
    ) -> int:
        """
        Add a temporary growth rate adjustment for an asset.
        
        Args:
            asset_id: ID of the asset to adjust
            start_year: First year the adjustment applies
            end_year: Last year the adjustment applies
            growth_rate: Growth rate during this period
            
        Returns:
            The ID of the created adjustment
            
        Raises:
            ValueError: If years are invalid or growth rate is out of range
            ValueError: If adjustment overlaps with existing ones
        """
        if start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")
        if growth_rate < -200 or growth_rate > 200:
            raise ValueError("Growth rate must be between -200 and 200")

        try:
            async with DatabaseConnection.transaction() as conn:
                # Check for overlapping adjustments
                async with conn.execute(
                    """
                    SELECT 1 FROM asset_growth_adjustments
                    WHERE asset_id = ?
                    AND (
                        (start_year <= ? AND end_year >= ?) OR
                        (start_year <= ? AND end_year >= ?) OR
                        (start_year >= ? AND end_year <= ?)
                    )
                    """,
                    (asset_id, start_year, start_year, end_year, end_year, start_year, end_year)
                ) as cursor:
                    if await cursor.fetchone():
                        raise ValueError("Growth adjustment overlaps with existing adjustment")

                # Create adjustment
                cursor = await conn.execute(
                    """
                    INSERT INTO asset_growth_adjustments (
                        asset_id, start_year, end_year, growth_rate
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (asset_id, start_year, end_year, growth_rate)
                )
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error adding growth adjustment: {str(e)}")
            raise

    async def get_asset(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an asset's details including category and ownership information.
        Returns None if not found.
        """
        try:
            query = """
                SELECT a.*,
                       ac.category_name,
                       GROUP_CONCAT(p.first_name || ' ' || p.last_name) as owner_names,
                       GROUP_CONCAT(p.person_id) as owner_ids
                FROM assets a
                JOIN asset_categories ac ON a.asset_category_id = ac.asset_category_id
                LEFT JOIN asset_owners ao ON a.asset_id = ao.asset_id
                LEFT JOIN people p ON ao.person_id = p.person_id
                WHERE a.asset_id = ?
                GROUP BY a.asset_id
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (asset_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        result = dict(row)
                        # Convert owner_ids from string to list
                        if result["owner_ids"]:
                            result["owner_ids"] = [int(id) for id in result["owner_ids"].split(',')]
                        return result
                    return None
        except Exception as e:
            logger.error(f"Error getting asset: {str(e)}")
            raise

    async def update_asset(
        self,
        asset_id: int,
        asset_name: Optional[str] = None,
        value: Optional[float] = None,
        include_in_nest_egg: Optional[bool] = None,
        independent_growth_rate: Optional[float] = None,
        owner_ids: Optional[List[int]] = None
    ) -> bool:
        """
        Update an asset's details and optionally its ownership.
        Only updates the fields that are provided (not None).
        
        Args:
            asset_id: ID of the asset to update
            asset_name: New name for the asset
            value: New value for the asset
            include_in_nest_egg: Whether to include in retirement calculations
            independent_growth_rate: New growth rate for the asset
            owner_ids: New list of owner IDs (if provided, replaces existing owners)
            
        Returns:
            True if successful, False if asset not found
            
        Raises:
            ValueError: If value is negative or growth rate is out of range
            ValueError: If new owners don't belong to the household
        """
        try:
            # Get current asset data
            current_asset = await self.get_asset(asset_id)
            if not current_asset:
                return False

            # Validate new values
            if value is not None and value < 0:
                raise ValueError("Asset value cannot be negative")
            if independent_growth_rate is not None and (independent_growth_rate < -200 or independent_growth_rate > 200):
                raise ValueError("Growth rate must be between -200 and 200")

            async with DatabaseConnection.transaction() as conn:
                # Update asset fields
                updates = []
                values = []
                if asset_name is not None:
                    updates.append("asset_name = ?")
                    values.append(asset_name)
                if value is not None:
                    updates.append("value = ?")
                    values.append(value)
                if include_in_nest_egg is not None:
                    updates.append("include_in_nest_egg = ?")
                    values.append(include_in_nest_egg)
                if independent_growth_rate is not None:
                    updates.append("independent_growth_rate = ?")
                    values.append(independent_growth_rate)

                if updates:
                    query = f"UPDATE assets SET {', '.join(updates)} WHERE asset_id = ?"
                    values.append(asset_id)
                    await conn.execute(query, tuple(values))

                # Update owners if provided
                if owner_ids is not None:
                    if not owner_ids:
                        raise ValueError("At least one owner must be specified")

                    # Get household_id
                    async with conn.execute(
                        """
                        SELECT p.household_id
                        FROM assets a
                        JOIN plans p ON a.plan_id = p.plan_id
                        WHERE a.asset_id = ?
                        """,
                        (asset_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        household_id = row[0]

                    # Verify new owners belong to household
                    owner_placeholders = ','.join(['?' for _ in owner_ids])
                    query = f"""
                        SELECT COUNT(*)
                        FROM people
                        WHERE person_id IN ({owner_placeholders})
                        AND household_id = ?
                    """
                    async with conn.execute(query, tuple(owner_ids) + (household_id,)) as cursor:
                        count = (await cursor.fetchone())[0]
                        if count != len(owner_ids):
                            raise ValueError("All owners must belong to the household")

                    # Replace owners
                    await conn.execute(
                        "DELETE FROM asset_owners WHERE asset_id = ?",
                        (asset_id,)
                    )
                    for owner_id in owner_ids:
                        await conn.execute(
                            "INSERT INTO asset_owners (asset_id, person_id) VALUES (?, ?)",
                            (asset_id, owner_id)
                        )

                return True

        except Exception as e:
            logger.error(f"Error updating asset: {str(e)}")
            raise

    async def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset and its related records (owners and growth adjustments).
        Returns True if successful, False if asset not found.
        """
        return await self.delete(asset_id, self.id_field)

    async def list_assets(
        self,
        plan_id: Optional[int] = None,
        category_id: Optional[int] = None,
        include_owners: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List assets with optional filtering.
        
        Args:
            plan_id: Optional filter for specific plan
            category_id: Optional filter for specific category
            include_owners: Whether to include ownership information
            
        Returns:
            List of asset records
        """
        try:
            query = """
                SELECT a.*,
                       ac.category_name
            """
            if include_owners:
                query += """,
                       GROUP_CONCAT(p.first_name || ' ' || p.last_name) as owner_names,
                       GROUP_CONCAT(p.person_id) as owner_ids
                """
            
            query += """
                FROM assets a
                JOIN asset_categories ac ON a.asset_category_id = ac.asset_category_id
            """
            
            if include_owners:
                query += """
                    LEFT JOIN asset_owners ao ON a.asset_id = ao.asset_id
                    LEFT JOIN people p ON ao.person_id = p.person_id
                """

            conditions = []
            params = []
            if plan_id is not None:
                conditions.append("a.plan_id = ?")
                params.append(plan_id)
            if category_id is not None:
                conditions.append("a.asset_category_id = ?")
                params.append(category_id)

            if conditions:
                query += f" WHERE {' AND '.join(conditions)}"

            if include_owners:
                query += " GROUP BY a.asset_id"

            query += " ORDER BY ac.category_name, a.asset_name"

            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    result = []
                    for row in rows:
                        asset_dict = dict(row)
                        if include_owners and asset_dict.get("owner_ids"):
                            asset_dict["owner_ids"] = [
                                int(id) for id in asset_dict["owner_ids"].split(',')
                            ]
                        result.append(asset_dict)
                    return result

        except Exception as e:
            logger.error(f"Error listing assets: {str(e)}")
            raise

   

    async def get_growth_adjustments(
        self,
        asset_id: int,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get growth rate adjustments for an asset.
        
        Args:
            asset_id: ID of the asset
            year: Optional specific year to check
            
        Returns:
            List of growth adjustment records that apply
        """
        try:
            query = """
                SELECT * FROM asset_growth_adjustments
                WHERE asset_id = ?
            """
            params = [asset_id]
            
            if year is not None:
                query += " AND start_year <= ? AND end_year >= ?"
                params.extend([year, year])
                
            query += " ORDER BY start_year"
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting growth adjustments: {str(e)}")
            raise

    async def get_asset_categories(self, household_id: int) -> List[Dict[str, Any]]:
        """
        Get all asset categories for a household.
        
        Args:
            household_id: ID of the household
            
        Returns:
            List of category records
        """
        try:
            query = """
                SELECT * FROM asset_categories
                WHERE household_id = ?
                ORDER BY category_name
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (household_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting asset categories: {str(e)}")
            raise

    async def delete_asset_category(self, category_id: int) -> bool:
        """
        Delete an asset category.
        Will fail if any assets are still using this category.
        
        Returns:
            True if successful, False if category not found or in use
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                cursor = await conn.execute(
                    "DELETE FROM asset_categories WHERE asset_category_id = ?",
                    (category_id,)
                )
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting asset category: {str(e)}")
            raise
