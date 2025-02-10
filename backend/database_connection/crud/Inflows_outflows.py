
# crud/inflows_outflows.py


"""
CRUD operations for inflows and outflows.
Handles creation, updates, and management of cash flow entries.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class InflowsOutflowsCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("inflows_outflows")
        self.id_field = "inflow_outflow_id"

    async def create_inflow_outflow(
        self,
        plan_id: int,
        type: str,
        name: str,
        annual_amount: float,
        start_year: int,
        end_year: int,
        apply_inflation: bool = False
    ) -> int:
        """
        Create a new inflow or outflow entry.
        Args:
            plan_id: ID of the financial plan this entry belongs to
            type: Either 'INFLOW' or 'OUTFLOW'
            name: Description of the cash flow
            annual_amount: Annual amount (positive value)
            start_year: Year when this cash flow starts
            end_year: Year when this cash flow ends
            apply_inflation: Whether to adjust amount for inflation
        Returns:
            The ID of the created entry
        Raises:
            ValueError: If type is invalid or years are invalid
            ValueError: If plan_id doesn't exist
        """
        # Validate type
        type = type.upper()
        if type not in ('INFLOW', 'OUTFLOW'):
            raise ValueError("Type must be either 'INFLOW' or 'OUTFLOW'")

        # Validate years
        if start_year > end_year:
            raise ValueError("Start year must be before or equal to end year")

        try:
            async with DatabaseConnection.transaction() as conn:
                # Verify plan exists and get creation year
                async with conn.execute(
                    "SELECT plan_creation_year FROM plans WHERE plan_id = ?",
                    (plan_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Invalid plan_id")
                    plan_creation_year = row[0]

                # Validate years against plan creation year
                if start_year < plan_creation_year:
                    raise ValueError("Start year cannot be before plan creation year")

                data = {
                    "plan_id": plan_id,
                    "type": type,
                    "name": name,
                    "annual_amount": annual_amount,
                    "start_year": start_year,
                    "end_year": end_year,
                    "apply_inflation": apply_inflation
                }
                return await self.create(data)

        except Exception as e:
            logger.error(f"Error creating inflow/outflow: {str(e)}")
            raise

    async def get_inflow_outflow(self, inflow_outflow_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an inflow/outflow entry by ID.
        Returns None if not found.
        """
        try:
            query = """
                SELECT io.*, p.plan_name, p.plan_creation_year
                FROM inflows_outflows io
                JOIN plans p ON io.plan_id = p.plan_id
                WHERE io.inflow_outflow_id = ?
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (inflow_outflow_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting inflow/outflow: {str(e)}")
            raise

    async def update_inflow_outflow(
        self,
        inflow_outflow_id: int,
        type: Optional[str] = None,
        name: Optional[str] = None,
        annual_amount: Optional[float] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        apply_inflation: Optional[bool] = None
    ) -> bool:
        """
        Update an inflow/outflow entry.
        Only updates the fields that are provided (not None).
        Args:
            inflow_outflow_id: ID of the entry to update
            type: New type ('INFLOW' or 'OUTFLOW')
            name: New name/description
            annual_amount: New annual amount
            start_year: New start year
            end_year: New end year
            apply_inflation: Whether to adjust for inflation
        Returns:
            True if successful, False if entry not found
        Raises:
            ValueError: If type is invalid or years are invalid
        """
        try:
            # Get current data
            current_data = await self.get_inflow_outflow(inflow_outflow_id)
            if not current_data:
                return False

            # Validate type if provided
            if type is not None:
                type = type.upper()
                if type not in ('INFLOW', 'OUTFLOW'):
                    raise ValueError("Type must be either 'INFLOW' or 'OUTFLOW'")

            # Determine effective years
            effective_start = start_year if start_year is not None else current_data["start_year"]
            effective_end = end_year if end_year is not None else current_data["end_year"]

            # Validate years if either is being updated
            if start_year is not None or end_year is not None:
                if effective_start > effective_end:
                    raise ValueError("Start year must be before or equal to end year")
                if effective_start < current_data["plan_creation_year"]:
                    raise ValueError("Start year cannot be before plan creation year")

            # Build update data
            data = {}
            if type is not None:
                data["type"] = type
            if name is not None:
                data["name"] = name
            if annual_amount is not None:
                data["annual_amount"] = annual_amount
            if start_year is not None:
                data["start_year"] = start_year
            if end_year is not None:
                data["end_year"] = end_year
            if apply_inflation is not None:
                data["apply_inflation"] = apply_inflation

            if data:
                return await self.update(inflow_outflow_id, data, self.id_field)
            return True

        except Exception as e:
            logger.error(f"Error updating inflow/outflow: {str(e)}")
            raise

    async def delete_inflow_outflow(self, inflow_outflow_id: int) -> bool:
        """
        Delete an inflow/outflow entry.
        Returns True if successful, False if entry not found.
        """
        return await self.delete(inflow_outflow_id, self.id_field)

    async def list_inflows_outflows(
        self,
        plan_id: Optional[int] = None,
        type: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        order_by: str = "start_year, name"
    ) -> List[Dict[str, Any]]:
        """
        List inflow/outflow entries with optional filtering.
        Args:
            plan_id: Optional filter for specific plan
            type: Optional filter for INFLOW or OUTFLOW
            start_year: Optional filter for entries starting from this year
            end_year: Optional filter for entries ending by this year
            order_by: SQL ORDER BY clause
        Returns:
            List of inflow/outflow records
        """
        try:
            query = """
                SELECT io.*, p.plan_name, p.plan_creation_year
                FROM inflows_outflows io
                JOIN plans p ON io.plan_id = p.plan_id
            """
            conditions = []
            params = []

            if plan_id is not None:
                conditions.append("io.plan_id = ?")
                params.append(plan_id)

            if type is not None:
                type = type.upper()
                if type not in ('INFLOW', 'OUTFLOW'):
                    raise ValueError("Type must be either 'INFLOW' or 'OUTFLOW'")
                conditions.append("io.type = ?")
                params.append(type)

            if start_year is not None:
                conditions.append("io.end_year >= ?")
                params.append(start_year)

            if end_year is not None:
                conditions.append("io.start_year <= ?")
                params.append(end_year)

            if conditions:
                query += f" WHERE {' AND '.join(conditions)}"

            query += f" ORDER BY io.{order_by}"

            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing inflows/outflows: {str(e)}")
            raise

    async def get_plan_cash_flows(
        self,
        plan_id: int,
        year: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all cash flows for a plan, optionally filtered by year.
        Returns a dict with separate lists for inflows and outflows.
        Args:
            plan_id: ID of the plan
            year: Optional specific year to filter
        Returns:
            Dict with 'inflows' and 'outflows' lists
        """
        try:
            query = """
                SELECT io.*
                FROM inflows_outflows io
                WHERE io.plan_id = ?
            """
            params = [plan_id]

            if year is not None:
                query += " AND io.start_year <= ? AND io.end_year >= ?"
                params.extend([year, year])

            query += " ORDER BY io.start_year, io.name"

            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    result = {
                        "inflows": [],
                        "outflows": []
                    }
                    for row in rows:
                        entry = dict(row)
                        if entry["type"] == "INFLOW":
                            result["inflows"].append(entry)
                        else:
                            result["outflows"].append(entry)
                    return result

        except Exception as e:
            logger.error(f"Error getting plan cash flows: {str(e)}")
            raise

    async def validate_years(
        self,
        plan_id: int,
        start_year: int,
        end_year: int
    ) -> bool:
        """
        Validate year range against plan creation year.
        Args:
            plan_id: ID of the plan
            start_year: Start year to validate
            end_year: End year to validate
        Returns:
            True if valid, raises ValueError if invalid
        """
        try:
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(
                    "SELECT plan_creation_year FROM plans WHERE plan_id = ?",
                    (plan_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Invalid plan_id")
                    plan_creation_year = row[0]

                    if start_year > end_year:
                        raise ValueError("Start year must be before or equal to end year")
                    if start_year < plan_creation_year:
                        raise ValueError("Start year cannot be before plan creation year")
                    return True

        except Exception as e:
            logger.error(f"Error validating years: {str(e)}")
            raise