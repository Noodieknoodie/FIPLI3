# crud/liabilities.py

"""
CRUD operations for liabilities and liability categories.
Handles liability creation, updates, and category management.
"""
from typing import Dict, Any, List, Optional
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class LiabilitiesCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("liabilities")
        self.id_field = "liability_id"

    async def create_liability_category(self, household_id: int, category_name: str) -> int:
        """
        Create a new liability category for a household.
        
        Args:
            household_id: ID of the household this category belongs to
            category_name: Name of the category (e.g., "Mortgages", "Student Loans")
            
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
                    "INSERT INTO liability_categories (household_id, category_name) VALUES (?, ?)",
                    (household_id, category_name)
                )
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating liability category: {str(e)}")
            raise

    async def create_liability(
        self,
        plan_id: int,
        liability_category_id: int,
        liability_name: str,
        value: float,
        interest_rate: float,
        include_in_nest_egg: bool = True
    ) -> int:
        """
        Create a new liability.
        
        Args:
            plan_id: ID of the financial plan this liability belongs to
            liability_category_id: ID of the liability's category
            liability_name: Name of the liability
            value: Current balance of the liability
            interest_rate: Annual interest rate
            include_in_nest_egg: Whether to include in retirement calculations
            
        Returns:
            The ID of the created liability
            
        Raises:
            ValueError: If value is negative or interest rate is outside allowed range
        """
        if value < 0:
            raise ValueError("Liability value cannot be negative")
        if interest_rate < -200 or interest_rate > 200:
            raise ValueError("Interest rate must be between -200 and 200")

        try:
            data = {
                "plan_id": plan_id,
                "liability_category_id": liability_category_id,
                "liability_name": liability_name,
                "value": value,
                "interest_rate": interest_rate,
                "include_in_nest_egg": include_in_nest_egg
            }
            return await self.create(data)
        except Exception as e:
            logger.error(f"Error creating liability: {str(e)}")
            raise

    async def get_liability(self, liability_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a liability's details including category information.
        Returns None if not found.
        """
        try:
            query = """
                SELECT l.*, lc.category_name
                FROM liabilities l
                JOIN liability_categories lc ON l.liability_category_id = lc.liability_category_id
                WHERE l.liability_id = ?
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (liability_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting liability: {str(e)}")
            raise

    async def update_liability(
        self,
        liability_id: int,
        liability_name: Optional[str] = None,
        value: Optional[float] = None,
        interest_rate: Optional[float] = None,
        include_in_nest_egg: Optional[bool] = None
    ) -> bool:
        """
        Update a liability's details.
        Only updates the fields that are provided (not None).
        
        Args:
            liability_id: ID of the liability to update
            liability_name: New name for the liability
            value: New balance for the liability
            interest_rate: New interest rate
            include_in_nest_egg: Whether to include in retirement calculations
            
        Returns:
            True if successful, False if liability not found
            
        Raises:
            ValueError: If value is negative or interest rate is out of range
        """
        try:
            # Get current liability data
            current_liability = await self.get_liability(liability_id)
            if not current_liability:
                return False

            # Validate new values
            if value is not None and value < 0:
                raise ValueError("Liability value cannot be negative")
            if interest_rate is not None and (interest_rate < -200 or interest_rate > 200):
                raise ValueError("Interest rate must be between -200 and 200")

            # Build update data
            data = {}
            if liability_name is not None:
                data["liability_name"] = liability_name
            if value is not None:
                data["value"] = value
            if interest_rate is not None:
                data["interest_rate"] = interest_rate
            if include_in_nest_egg is not None:
                data["include_in_nest_egg"] = include_in_nest_egg

            if data:
                return await self.update(liability_id, data, self.id_field)
            return True

        except Exception as e:
            logger.error(f"Error updating liability: {str(e)}")
            raise

    async def delete_liability(self, liability_id: int) -> bool:
        """
        Delete a liability.
        Returns True if successful, False if liability not found.
        """
        return await self.delete(liability_id, self.id_field)

    async def list_liabilities(
        self,
        plan_id: Optional[int] = None,
        category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List liabilities with optional filtering.
        
        Args:
            plan_id: Optional filter for specific plan
            category_id: Optional filter for specific category
            
        Returns:
            List of liability records
        """
        try:
            query = """
                SELECT l.*, lc.category_name
                FROM liabilities l
                JOIN liability_categories lc ON l.liability_category_id = lc.liability_category_id
            """
            
            conditions = []
            params = []
            if plan_id is not None:
                conditions.append("l.plan_id = ?")
                params.append(plan_id)
            if category_id is not None:
                conditions.append("l.liability_category_id = ?")
                params.append(category_id)

            if conditions:
                query += f" WHERE {' AND '.join(conditions)}"

            query += " ORDER BY lc.category_name, l.liability_name"

            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing liabilities: {str(e)}")
            raise

    async def get_liability_categories(self, household_id: int) -> List[Dict[str, Any]]:
        """
        Get all liability categories for a household.
        
        Args:
            household_id: ID of the household
            
        Returns:
            List of category records
        """
        try:
            query = """
                SELECT * FROM liability_categories
                WHERE household_id = ?
                ORDER BY category_name
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (household_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting liability categories: {str(e)}")
            raise

    async def delete_liability_category(self, category_id: int) -> bool:
        """
        Delete a liability category.
        Will fail if any liabilities are still using this category.
        
        Returns:
            True if successful, False if category not found or in use
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                cursor = await conn.execute(
                    "DELETE FROM liability_categories WHERE liability_category_id = ?",
                    (category_id,)
                )
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error deleting liability category: {str(e)}")
            raise