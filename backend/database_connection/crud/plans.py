"""
CRUD operations for financial plans.
Handles plan records and their relationships with households, reference persons, and scenarios.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class PlansCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("plans")
        self.id_field = "plan_id"
    
    async def create_plan(
        self,
        household_id: int,
        plan_name: str,
        reference_person_id: int,
        plan_creation_year: Optional[int] = None,
        base_assumptions: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Create a new financial plan with base assumptions.
        
        Args:
            household_id: ID of the household this plan belongs to
            plan_name: Name of the financial plan
            reference_person_id: ID of the person whose timeline is used as reference
            plan_creation_year: Year the plan starts from (defaults to current year)
            base_assumptions: Optional dict with base assumption values:
                - nest_egg_growth_rate: Default 6.0
                - inflation_rate: Required
                - annual_retirement_spending: Default 0
            
        Returns:
            The ID of the created plan
            
        Raises:
            ValueError: If reference person doesn't belong to the household
            ValueError: If required base assumptions are missing
        """
        try:
            # Verify reference person belongs to household
            query = """
                SELECT 1 FROM people 
                WHERE person_id = ? AND household_id = ?
            """
            
            async with DatabaseConnection.transaction() as conn:
                # Check reference person
                async with conn.execute(query, (reference_person_id, household_id)) as cursor:
                    if not await cursor.fetchone():
                        raise ValueError("Reference person must belong to the household")
                
                # Use current year if not specified
                if plan_creation_year is None:
                    plan_creation_year = datetime.now().year
                
                # Create plan
                plan_data = {
                    "household_id": household_id,
                    "plan_name": plan_name,
                    "reference_person_id": reference_person_id,
                    "plan_creation_year": plan_creation_year
                }
                
                cursor = await conn.execute(
                    f"INSERT INTO {self.table_name} ({', '.join(plan_data.keys())}) VALUES ({', '.join(['?' for _ in plan_data])})",
                    tuple(plan_data.values())
                )
                plan_id = cursor.lastrowid
                
                # Create base assumptions
                assumptions = base_assumptions or {}
                if "inflation_rate" not in assumptions:
                    raise ValueError("inflation_rate is required in base assumptions")
                    
                assumption_data = {
                    "plan_id": plan_id,
                    "nest_egg_growth_rate": assumptions.get("nest_egg_growth_rate", 6.0),
                    "inflation_rate": assumptions["inflation_rate"],
                    "annual_retirement_spending": assumptions.get("annual_retirement_spending", 0)
                }
                
                await conn.execute(
                    """
                    INSERT INTO base_assumptions 
                    (plan_id, nest_egg_growth_rate, inflation_rate, annual_retirement_spending)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        assumption_data["plan_id"],
                        assumption_data["nest_egg_growth_rate"],
                        assumption_data["inflation_rate"],
                        assumption_data["annual_retirement_spending"]
                    )
                )
                
                return plan_id
            
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            raise
    
    async def get_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a plan's details by ID.
        Returns None if not found.
        """
        try:
            query = """
                SELECT p.*, 
                       h.household_name,
                       pe.first_name || ' ' || pe.last_name as reference_person_name
                FROM plans p
                JOIN households h ON p.household_id = h.household_id
                JOIN people pe ON p.reference_person_id = pe.person_id
                WHERE p.plan_id = ?
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (plan_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
                    
        except Exception as e:
            logger.error(f"Error getting plan: {str(e)}")
            raise
    
    async def update_plan(
        self,
        plan_id: int,
        plan_name: Optional[str] = None,
        reference_person_id: Optional[int] = None
    ) -> bool:
        """
        Update a plan's details.
        Only updates the fields that are provided (not None).
        
        Args:
            plan_id: ID of the plan to update
            plan_name: New plan name (optional)
            reference_person_id: New reference person ID (optional)
            
        Returns:
            True if successful, False if plan not found
            
        Raises:
            ValueError: If new reference person doesn't belong to the plan's household
        """
        try:
            # Get current plan data
            current_plan = await self.get_plan(plan_id)
            if not current_plan:
                return False
            
            data = {}
            
            # Handle plan name update
            if plan_name is not None:
                data["plan_name"] = plan_name
            
            # Handle reference person update
            if reference_person_id is not None:
                # Verify new reference person belongs to household
                query = """
                    SELECT 1 FROM people 
                    WHERE person_id = ? AND household_id = ?
                """
                
                async with DatabaseConnection.connection() as conn:
                    async with conn.execute(query, (reference_person_id, current_plan["household_id"])) as cursor:
                        if not await cursor.fetchone():
                            raise ValueError("Reference person must belong to the household")
                
                data["reference_person_id"] = reference_person_id
            
            if data:
                return await self.update(plan_id, data, self.id_field)
            return True
            
        except Exception as e:
            logger.error(f"Error updating plan: {str(e)}")
            raise
    
    async def delete_plan(self, plan_id: int) -> bool:
        """
        Delete a plan.
        This will cascade to delete scenarios, assumptions, and yearly values.
        Returns True if successful, False if plan not found.
        """
        return await self.delete(plan_id, self.id_field)
    
    async def list_plans(
        self,
        household_id: Optional[int] = None,
        order_by: str = "plan_name"
    ) -> List[Dict[str, Any]]:
        """
        List plans with optional filtering by household.
        
        Args:
            household_id: Optional filter for specific household
            order_by: SQL ORDER BY clause, defaults to "plan_name"
            
        Returns:
            List of plan records with household and reference person details
        """
        try:
            query = """
                SELECT p.*, 
                       h.household_name,
                       pe.first_name || ' ' || pe.last_name as reference_person_name
                FROM plans p
                JOIN households h ON p.household_id = h.household_id
                JOIN people pe ON p.reference_person_id = pe.person_id
            """
            
            params = []
            if household_id is not None:
                query += " WHERE p.household_id = ?"
                params.append(household_id)
            
            query += f" ORDER BY p.{order_by}"
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error listing plans: {str(e)}")
            raise
    
    async def get_plan_scenarios(self, plan_id: int) -> List[Dict[str, Any]]:
        """
        Get all scenarios associated with a plan.
        """
        try:
            query = """
                SELECT s.*,
                       COUNT(sa.scenario_id) as num_assumption_overrides,
                       COUNT(sga.scenario_id) as num_growth_adjustments
                FROM scenarios s
                LEFT JOIN scenario_assumptions sa ON s.scenario_id = sa.scenario_id
                LEFT JOIN scenario_growth_adjustments sga ON s.scenario_id = sga.scenario_id
                WHERE s.plan_id = ?
                GROUP BY s.scenario_id
                ORDER BY s.scenario_name
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (plan_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting plan scenarios: {str(e)}")
            raise
    
    async def get_plan_base_assumptions(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the base assumptions for a plan.
        Returns None if not found.
        """
        try:
            query = """
                SELECT * FROM base_assumptions
                WHERE plan_id = ?
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (plan_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
                    
        except Exception as e:
            logger.error(f"Error getting plan base assumptions: {str(e)}")
            raise 