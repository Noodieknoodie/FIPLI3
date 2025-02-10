# crud/retirement_income.py


"""
CRUD operations for retirement income plans.
Handles retirement income creation, ownership management, and age-based validations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class RetirementIncomeCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("retirement_income_plans")
        self.id_field = "income_plan_id"

    async def create_retirement_income(
        self,
        plan_id: int,
        name: str,
        annual_income: float,
        start_age: int,
        end_age: Optional[int],
        owner_ids: List[int],
        apply_inflation: bool = False,
        include_in_nest_egg: bool = True
    ) -> int:
        """
        Create a new retirement income plan with owners.
        Args:
            plan_id: ID of the financial plan this income belongs to
            name: Description of the income source (e.g., "Social Security", "Pension")
            annual_income: Annual income amount
            start_age: Age when income starts
            end_age: Optional age when income ends (None for lifetime)
            owner_ids: List of person IDs who receive this income
            apply_inflation: Whether to adjust amount for inflation
            include_in_nest_egg: Whether to include in retirement calculations
        Returns:
            The ID of the created income plan
        Raises:
            ValueError: If ages are invalid or income is negative
            ValueError: If no owners provided or owners don't belong to household
        """
        if annual_income < 0:
            raise ValueError("Annual income cannot be negative")
        
        if start_age <= 0:
            raise ValueError("Start age must be positive")
            
        if end_age is not None and start_age > end_age:
            raise ValueError("Start age must be before or equal to end age")
            
        if not owner_ids:
            raise ValueError("At least one owner must be specified")

        try:
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
                    SELECT p.person_id, p.retirement_age, p.final_age 
                    FROM people p
                    WHERE p.person_id IN ({owner_placeholders})
                    AND p.household_id = ?
                """
                async with conn.execute(query, tuple(owner_ids) + (household_id,)) as cursor:
                    rows = await cursor.fetchall()
                    if len(rows) != len(owner_ids):
                        raise ValueError("All owners must belong to the household")
                    
                    # Validate ages against owners' retirement/final ages
                    for row in rows:
                        if start_age > row['final_age']:
                            raise ValueError(f"Start age cannot be after owner's final age")
                        if end_age is not None and end_age < row['retirement_age']:
                            raise ValueError(f"End age cannot be before owner's retirement age")

                # Create retirement income plan
                data = {
                    "plan_id": plan_id,
                    "name": name,
                    "annual_income": annual_income,
                    "start_age": start_age,
                    "end_age": end_age,
                    "apply_inflation": apply_inflation,
                    "include_in_nest_egg": include_in_nest_egg
                }
                cursor = await conn.execute(
                    """
                    INSERT INTO retirement_income_plans (
                        plan_id, name, annual_income, start_age, end_age,
                        apply_inflation, include_in_nest_egg
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["plan_id"],
                        data["name"],
                        data["annual_income"],
                        data["start_age"],
                        data["end_age"],
                        data["apply_inflation"],
                        data["include_in_nest_egg"]
                    )
                )
                income_plan_id = cursor.lastrowid

                # Create ownership records
                for owner_id in owner_ids:
                    await conn.execute(
                        """
                        INSERT INTO retirement_income_owners (
                            income_plan_id, person_id
                        ) VALUES (?, ?)
                        """,
                        (income_plan_id, owner_id)
                    )

                return income_plan_id

        except Exception as e:
            logger.error(f"Error creating retirement income: {str(e)}")
            raise

    async def get_retirement_income(self, income_plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a retirement income plan's details including ownership information.
        Returns None if not found.
        """
        try:
            query = """
                SELECT rip.*,
                       GROUP_CONCAT(p.first_name || ' ' || p.last_name) as owner_names,
                       GROUP_CONCAT(p.person_id) as owner_ids
                FROM retirement_income_plans rip
                LEFT JOIN retirement_income_owners rio ON rip.income_plan_id = rio.income_plan_id
                LEFT JOIN people p ON rio.person_id = p.person_id
                WHERE rip.income_plan_id = ?
                GROUP BY rip.income_plan_id
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (income_plan_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        result = dict(row)
                        if result["owner_ids"]:
                            result["owner_ids"] = [int(id) for id in result["owner_ids"].split(',')]
                        return result
                    return None

        except Exception as e:
            logger.error(f"Error getting retirement income: {str(e)}")
            raise

    async def update_retirement_income(
        self,
        income_plan_id: int,
        name: Optional[str] = None,
        annual_income: Optional[float] = None,
        start_age: Optional[int] = None,
        end_age: Optional[int] = None,
        owner_ids: Optional[List[int]] = None,
        apply_inflation: Optional[bool] = None,
        include_in_nest_egg: Optional[bool] = None
    ) -> bool:
        """
        Update a retirement income plan's details and optionally its ownership.
        Only updates the fields that are provided (not None).
        Args:
            income_plan_id: ID of the income plan to update
            name: New name for the income plan
            annual_income: New annual income amount
            start_age: New start age
            end_age: New end age
            owner_ids: New list of owner IDs (if provided, replaces existing owners)
            apply_inflation: Whether to adjust for inflation
            include_in_nest_egg: Whether to include in retirement calculations
        Returns:
            True if successful, False if income plan not found
        Raises:
            ValueError: If ages are invalid or income is negative
            ValueError: If new owners don't belong to household
        """
        try:
            # Get current income plan data
            current_plan = await self.get_retirement_income(income_plan_id)
            if not current_plan:
                return False

            # Validate values
            if annual_income is not None and annual_income < 0:
                raise ValueError("Annual income cannot be negative")

            effective_start = start_age if start_age is not None else current_plan["start_age"]
            effective_end = end_age if end_age is not None else current_plan["end_age"]

            if effective_end is not None and effective_start > effective_end:
                raise ValueError("Start age must be before or equal to end age")

            async with DatabaseConnection.transaction() as conn:
                # Update income plan fields
                updates = []
                values = []
                if name is not None:
                    updates.append("name = ?")
                    values.append(name)
                if annual_income is not None:
                    updates.append("annual_income = ?")
                    values.append(annual_income)
                if start_age is not None:
                    updates.append("start_age = ?")
                    values.append(start_age)
                if end_age is not None:
                    updates.append("end_age = ?")
                    values.append(end_age)
                if apply_inflation is not None:
                    updates.append("apply_inflation = ?")
                    values.append(apply_inflation)
                if include_in_nest_egg is not None:
                    updates.append("include_in_nest_egg = ?")
                    values.append(include_in_nest_egg)

                if updates:
                    query = f"""
                        UPDATE retirement_income_plans 
                        SET {', '.join(updates)}
                        WHERE income_plan_id = ?
                    """
                    values.append(income_plan_id)
                    await conn.execute(query, tuple(values))

                # Update owners if provided
                if owner_ids is not None:
                    if not owner_ids:
                        raise ValueError("At least one owner must be specified")

                    # Get household_id
                    async with conn.execute(
                        """
                        SELECT p.household_id
                        FROM retirement_income_plans rip
                        JOIN plans p ON rip.plan_id = p.plan_id
                        WHERE rip.income_plan_id = ?
                        """,
                        (income_plan_id,)
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
                        "DELETE FROM retirement_income_owners WHERE income_plan_id = ?",
                        (income_plan_id,)
                    )
                    for owner_id in owner_ids:
                        await conn.execute(
                            """
                            INSERT INTO retirement_income_owners (
                                income_plan_id, person_id
                            ) VALUES (?, ?)
                            """,
                            (income_plan_id, owner_id)
                        )

                return True

        except Exception as e:
            logger.error(f"Error updating retirement income: {str(e)}")
            raise

    async def delete_retirement_income(self, income_plan_id: int) -> bool:
        """
        Delete a retirement income plan and its ownership records.
        Returns True if successful, False if not found.
        """
        return await self.delete(income_plan_id, self.id_field)

    async def list_retirement_income(
        self,
        plan_id: Optional[int] = None,
        person_id: Optional[int] = None,
        include_owners: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List retirement income plans with optional filtering.
        Args:
            plan_id: Optional filter for specific plan
            person_id: Optional filter for specific beneficiary
            include_owners: Whether to include ownership information
        Returns:
            List of retirement income records
        """
        try:
            query = "SELECT rip.*"
            if include_owners:
                query += """,
                    GROUP_CONCAT(p.first_name || ' ' || p.last_name) as owner_names,
                    GROUP_CONCAT(p.person_id) as owner_ids
                """
            query += " FROM retirement_income_plans rip"
            
            if person_id is not None:
                query += """
                    JOIN retirement_income_owners rio 
                        ON rip.income_plan_id = rio.income_plan_id
                """
            if include_owners:
                query += """
                    LEFT JOIN retirement_income_owners rio2 
                        ON rip.income_plan_id = rio2.income_plan_id
                    LEFT JOIN people p ON rio2.person_id = p.person_id
                """

            conditions = []
            params = []
            if plan_id is not None:
                conditions.append("rip.plan_id = ?")
                params.append(plan_id)
            if person_id is not None:
                conditions.append("rio.person_id = ?")
                params.append(person_id)

            if conditions:
                query += f" WHERE {' AND '.join(conditions)}"

            if include_owners:
                query += " GROUP BY rip.income_plan_id"
            
            query += " ORDER BY rip.name"

            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    result = []
                    for row in rows:
                        income_dict = dict(row)
                        if include_owners and income_dict.get("owner_ids"):
                            income_dict["owner_ids"] = [
                                int(id) for id in income_dict["owner_ids"].split(',')
                            ]
                        result.append(income_dict)
                    return result

        except Exception as e:
            logger.error(f"Error listing retirement income: {str(e)}")
            raise

    async def validate_ages(
        self,
        person_id: int,
        start_age: int,
        end_age: Optional[int]
    ) -> bool:
        """
        Validate ages against a person's retirement and final ages.
        Returns True if valid, raises ValueError if invalid.
        """
        try:
            query = """
                SELECT retirement_age, final_age
                FROM people
                WHERE person_id = ?
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (person_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Invalid person_id")

                    if start_age > row["final_age"]:
                        raise ValueError("Start age cannot be after final age")
                    if end_age is not None:
                        if end_age < row["retirement_age"]:
                            raise ValueError("End age cannot be before retirement age")
                        if start_age > end_age:
                            raise ValueError("Start age must be before or equal to end age")

                    return True

        except Exception as e:
            logger.error(f"Error validating ages: {str(e)}")
            raise