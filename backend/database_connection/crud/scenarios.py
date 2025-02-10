# crud/scenarios.py

"""
CRUD operations for scenarios and scenario overrides.
Handles scenario creation, override management, and effective value calculation.
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class ScenariosCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("scenarios")
        self.id_field = "scenario_id"

    async def create_scenario(
        self,
        plan_id: int,
        scenario_name: str,
        assumption_overrides: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Create a new scenario with optional assumption overrides.
        
        Args:
            plan_id: ID of the financial plan this scenario belongs to
            scenario_name: Name of the scenario
            assumption_overrides: Optional dict with overridden assumptions:
                - nest_egg_growth_rate: Optional[float]
                - inflation_rate: Optional[float]
                - annual_retirement_spending: Optional[float]
        
        Returns:
            The ID of the created scenario

        Raises:
            ValueError: If growth or inflation rates are outside allowed range
            ValueError: If retirement spending is negative
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                # Verify plan exists
                async with conn.execute(
                    "SELECT 1 FROM plans WHERE plan_id = ?",
                    (plan_id,)
                ) as cursor:
                    if not await cursor.fetchone():
                        raise ValueError("Invalid plan_id")

                # Create scenario
                cursor = await conn.execute(
                    """
                    INSERT INTO scenarios (plan_id, scenario_name)
                    VALUES (?, ?)
                    """,
                    (plan_id, scenario_name)
                )
                scenario_id = cursor.lastrowid

                # Handle assumption overrides if provided
                if assumption_overrides:
                    # Validate override values
                    growth_rate = assumption_overrides.get('nest_egg_growth_rate')
                    inflation_rate = assumption_overrides.get('inflation_rate')
                    spending = assumption_overrides.get('annual_retirement_spending')

                    if growth_rate is not None:
                        if growth_rate < -200 or growth_rate > 200:
                            raise ValueError("Growth rate must be between -200 and 200")
                    
                    if inflation_rate is not None:
                        if inflation_rate < -200 or inflation_rate > 200:
                            raise ValueError("Inflation rate must be between -200 and 200")
                    
                    if spending is not None:
                        if spending < 0:
                            raise ValueError("Annual retirement spending cannot be negative")

                    # Create assumption overrides
                    await conn.execute(
                        """
                        INSERT INTO scenario_assumptions (
                            scenario_id,
                            overrides_nest_egg_growth_rate,
                            nest_egg_growth_rate,
                            overrides_inflation_rate,
                            inflation_rate,
                            overrides_annual_retirement_spending,
                            annual_retirement_spending
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            scenario_id,
                            1 if growth_rate is not None else 0,
                            growth_rate,
                            1 if inflation_rate is not None else 0,
                            inflation_rate,
                            1 if spending is not None else 0,
                            spending
                        )
                    )

                return scenario_id

        except Exception as e:
            logger.error(f"Error creating scenario: {str(e)}")
            raise

    async def get_scenario(self, scenario_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a scenario's details including its assumptions and override counts.
        Returns None if not found.
        """
        try:
            query = """
                SELECT s.*,
                       p.plan_name,
                       sa.nest_egg_growth_rate,
                       sa.inflation_rate,
                       sa.annual_retirement_spending,
                       COUNT(DISTINCT sga.adjustment_id) as num_growth_adjustments,
                       COUNT(DISTINCT spa.person_id) as num_person_overrides,
                       COUNT(DISTINCT sas.scenario_asset_id) as num_asset_overrides,
                       COUNT(DISTINCT sl.scenario_item_id) as num_liability_overrides,
                       COUNT(DISTINCT sio.scenario_item_id) as num_inflow_outflow_overrides,
                       COUNT(DISTINCT sri.scenario_item_id) as num_retirement_income_overrides
                FROM scenarios s
                JOIN plans p ON s.plan_id = p.plan_id
                LEFT JOIN scenario_assumptions sa ON s.scenario_id = sa.scenario_id
                LEFT JOIN scenario_growth_adjustments sga ON s.scenario_id = sga.scenario_id
                LEFT JOIN scenario_person_overrides spa ON s.scenario_id = spa.scenario_id
                LEFT JOIN scenario_assets sas ON s.scenario_id = sas.scenario_id
                LEFT JOIN scenario_liabilities sl ON s.scenario_id = sl.scenario_id
                LEFT JOIN scenario_inflows_outflows sio ON s.scenario_id = sio.scenario_id
                LEFT JOIN scenario_retirement_income sri ON s.scenario_id = sri.scenario_id
                WHERE s.scenario_id = ?
                GROUP BY s.scenario_id
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (scenario_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error getting scenario: {str(e)}")
            raise

    async def update_scenario(
        self,
        scenario_id: int,
        scenario_name: Optional[str] = None,
        assumption_overrides: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a scenario's details and assumptions.
        Only updates the fields that are provided (not None).

        Args:
            scenario_id: ID of the scenario to update
            scenario_name: New name for the scenario
            assumption_overrides: Optional dict with overridden assumptions:
                - nest_egg_growth_rate: Optional[float]
                - inflation_rate: Optional[float]
                - annual_retirement_spending: Optional[float]

        Returns:
            True if successful, False if scenario not found

        Raises:
            ValueError: If growth or inflation rates are outside allowed range
            ValueError: If retirement spending is negative
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                # Update scenario name if provided
                if scenario_name is not None:
                    cursor = await conn.execute(
                        "UPDATE scenarios SET scenario_name = ? WHERE scenario_id = ?",
                        (scenario_name, scenario_id)
                    )
                    if cursor.rowcount == 0:
                        return False

                # Handle assumption overrides if provided
                if assumption_overrides:
                    # Validate override values
                    growth_rate = assumption_overrides.get('nest_egg_growth_rate')
                    inflation_rate = assumption_overrides.get('inflation_rate')
                    spending = assumption_overrides.get('annual_retirement_spending')

                    if growth_rate is not None:
                        if growth_rate < -200 or growth_rate > 200:
                            raise ValueError("Growth rate must be between -200 and 200")
                    
                    if inflation_rate is not None:
                        if inflation_rate < -200 or inflation_rate > 200:
                            raise ValueError("Inflation rate must be between -200 and 200")
                    
                    if spending is not None:
                        if spending < 0:
                            raise ValueError("Annual retirement spending cannot be negative")

                    # Check if assumptions record exists
                    async with conn.execute(
                        "SELECT 1 FROM scenario_assumptions WHERE scenario_id = ?",
                        (scenario_id,)
                    ) as cursor:
                        exists = await cursor.fetchone()

                    if exists:
                        # Update existing assumptions
                        updates = []
                        values = []
                        if growth_rate is not None:
                            updates.extend([
                                "overrides_nest_egg_growth_rate = ?",
                                "nest_egg_growth_rate = ?"
                            ])
                            values.extend([1, growth_rate])
                        if inflation_rate is not None:
                            updates.extend([
                                "overrides_inflation_rate = ?",
                                "inflation_rate = ?"
                            ])
                            values.extend([1, inflation_rate])
                        if spending is not None:
                            updates.extend([
                                "overrides_annual_retirement_spending = ?",
                                "annual_retirement_spending = ?"
                            ])
                            values.extend([1, spending])

                        if updates:
                            query = f"""
                                UPDATE scenario_assumptions 
                                SET {', '.join(updates)}
                                WHERE scenario_id = ?
                            """
                            values.append(scenario_id)
                            await conn.execute(query, tuple(values))
                    else:
                        # Create new assumptions record
                        await conn.execute(
                            """
                            INSERT INTO scenario_assumptions (
                                scenario_id,
                                overrides_nest_egg_growth_rate,
                                nest_egg_growth_rate,
                                overrides_inflation_rate,
                                inflation_rate,
                                overrides_annual_retirement_spending,
                                annual_retirement_spending
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                scenario_id,
                                1 if growth_rate is not None else 0,
                                growth_rate,
                                1 if inflation_rate is not None else 0,
                                inflation_rate,
                                1 if spending is not None else 0,
                                spending
                            )
                        )

                return True

        except Exception as e:
            logger.error(f"Error updating scenario: {str(e)}")
            raise

async def delete_scenario(self, scenario_id: int) -> bool:
        """
        Delete a scenario and all its related records (cascading delete).
        Returns True if successful, False if scenario not found.
        """
        return await self.delete(scenario_id, self.id_field)

    async def list_scenarios(
        self,
        plan_id: Optional[int] = None,
        include_override_counts: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List scenarios with optional filtering and override counting.

        Args:
            plan_id: Optional filter for specific plan
            include_override_counts: Whether to include counts of various overrides

        Returns:
            List of scenario records with override counts if requested
        """
        try:
            if include_override_counts:
                query = """
                    SELECT s.*,
                           p.plan_name,
                           sa.nest_egg_growth_rate,
                           sa.inflation_rate,
                           sa.annual_retirement_spending,
                           COUNT(DISTINCT sga.adjustment_id) as num_growth_adjustments,
                           COUNT(DISTINCT spa.person_id) as num_person_overrides,
                           COUNT(DISTINCT sas.scenario_asset_id) as num_asset_overrides,
                           COUNT(DISTINCT sl.scenario_item_id) as num_liability_overrides,
                           COUNT(DISTINCT sio.scenario_item_id) as num_inflow_outflow_overrides,
                           COUNT(DISTINCT sri.scenario_item_id) as num_retirement_income_overrides
                    FROM scenarios s
                    JOIN plans p ON s.plan_id = p.plan_id
                    LEFT JOIN scenario_assumptions sa ON s.scenario_id = sa.scenario_id
                    LEFT JOIN scenario_growth_adjustments sga ON s.scenario_id = sga.scenario_id
                    LEFT JOIN scenario_person_overrides spa ON s.scenario_id = spa.scenario_id
                    LEFT JOIN scenario_assets sas ON s.scenario_id = sas.scenario_id
                    LEFT JOIN scenario_liabilities sl ON s.scenario_id = sl.scenario_id
                    LEFT JOIN scenario_inflows_outflows sio ON s.scenario_id = sio.scenario_id
                    LEFT JOIN scenario_retirement_income sri ON s.scenario_id = sri.scenario_id
                """
            else:
                query = """
                    SELECT s.*, p.plan_name
                    FROM scenarios s
                    JOIN plans p ON s.plan_id = p.plan_id
                """

            if plan_id is not None:
                query += " WHERE s.plan_id = ?"
                params = (plan_id,)
            else:
                params = ()

            query += " GROUP BY s.scenario_id ORDER BY s.created_at DESC"

            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing scenarios: {str(e)}")
            raise

    async def add_growth_adjustment(
        self,
        scenario_id: int,
        start_year: int,
        end_year: int,
        growth_rate: float
    ) -> int:
        """
        Add a temporary growth rate adjustment for a scenario.

        Args:
            scenario_id: ID of the scenario
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
                    SELECT 1 FROM scenario_growth_adjustments
                    WHERE scenario_id = ?
                    AND (
                        (start_year <= ? AND end_year >= ?) OR
                        (start_year <= ? AND end_year >= ?) OR
                        (start_year >= ? AND end_year <= ?)
                    )
                    """,
                    (scenario_id, start_year, start_year, end_year, end_year, start_year, end_year)
                ) as cursor:
                    if await cursor.fetchone():
                        raise ValueError("Growth adjustment overlaps with existing adjustment")

                # Create adjustment
                cursor = await conn.execute(
                    """
                    INSERT INTO scenario_growth_adjustments (
                        scenario_id, start_year, end_year, growth_rate
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (scenario_id, start_year, end_year, growth_rate)
                )
                return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error adding growth adjustment: {str(e)}")
            raise

    async def update_person_overrides(
        self,
        scenario_id: int,
        person_id: int,
        retirement_age: Optional[int] = None,
        final_age: Optional[int] = None
    ) -> bool:
        """
        Update retirement and final age overrides for a person in a scenario.

        Args:
            scenario_id: ID of the scenario
            person_id: ID of the person to override
            retirement_age: New retirement age override
            final_age: New final age override

        Returns:
            True if successful

        Raises:
            ValueError: If ages are invalid
            ValueError: If person doesn't belong to the scenario's household
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                # Verify person belongs to scenario's household
                query = """
                    SELECT p.retirement_age, p.final_age, p.household_id, pl.household_id as scenario_household_id
                    FROM people p
                    JOIN scenarios s ON s.scenario_id = ?
                    JOIN plans pl ON s.plan_id = pl.plan_id
                    WHERE p.person_id = ?
                """
                async with conn.execute(query, (scenario_id, person_id)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Person not found")
                    if row['household_id'] != row['scenario_household_id']:
                        raise ValueError("Person must belong to the scenario's household")

                    current_retirement_age = retirement_age if retirement_age is not None else row['retirement_age']
                    current_final_age = final_age if final_age is not None else row['final_age']

                    # Validate ages
                    if current_retirement_age <= 0:
                        raise ValueError("Retirement age must be positive")
                    if current_final_age <= current_retirement_age:
                        raise ValueError("Final age must be greater than retirement age")

                # Check if override record exists
                async with conn.execute(
                    "SELECT 1 FROM scenario_person_overrides WHERE scenario_id = ? AND person_id = ?",
                    (scenario_id, person_id)
                ) as cursor:
                    exists = await cursor.fetchone()

                if exists:
                    # Update existing override
                    updates = []
                    values = []
                    if retirement_age is not None:
                        updates.extend([
                            "overrides_retirement_age = 1",
                            "retirement_age = ?"
                        ])
                        values.append(retirement_age)
                    if final_age is not None:
                        updates.extend([
                            "overrides_final_age = 1",
                            "final_age = ?"
                        ])
                        values.append(final_age)

                    if updates:
                        query = f"""
                            UPDATE scenario_person_overrides 
                            SET {', '.join(updates)}
                            WHERE scenario_id = ? AND person_id = ?
                        """
                        values.extend([scenario_id, person_id])
                        await conn.execute(query, tuple(values))
                else:
                    # Create new override
                    await conn.execute(
                        """
                        INSERT INTO scenario_person_overrides (
                            scenario_id,
                            person_id,
                            overrides_retirement_age,
                            retirement_age,
                            overrides_final_age,
                            final_age
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            scenario_id,
                            person_id,
                            1 if retirement_age is not None else 0,
                            retirement_age,
                            1 if final_age is not None else 0,
                            final_age
                        )
                    )

                return True

        except Exception as e:
            logger.error(f"Error updating person overrides: {str(e)}")
            raise

async def override_asset(
        self,
        scenario_id: int,
        asset_id: int,
        value: Optional[float] = None,
        independent_growth_rate: Optional[float] = None,
        include_in_nest_egg: Optional[bool] = None,
        exclude_from_projection: bool = False
    ) -> int:
        """
        Create or update an asset override for a scenario.

        Args:
            scenario_id: ID of the scenario
            asset_id: ID of the asset to override
            value: New value override
            independent_growth_rate: New growth rate override
            include_in_nest_egg: Whether to include in retirement calculations
            exclude_from_projection: Whether to exclude this asset from the scenario

        Returns:
            The ID of the created/updated override

        Raises:
            ValueError: If value is negative
            ValueError: If growth rate is outside allowed range
            ValueError: If asset doesn't belong to scenario's plan
        """
        try:
            # Validate input values
            if value is not None and value < 0:
                raise ValueError("Asset value cannot be negative")
            if (independent_growth_rate is not None and 
                (independent_growth_rate < -200 or independent_growth_rate > 200)):
                raise ValueError("Growth rate must be between -200 and 200")

            async with DatabaseConnection.transaction() as conn:
                # Verify asset belongs to scenario's plan
                query = """
                    SELECT a.plan_id, s.plan_id as scenario_plan_id
                    FROM assets a
                    JOIN scenarios s ON s.scenario_id = ?
                    WHERE a.asset_id = ?
                """
                async with conn.execute(query, (scenario_id, asset_id)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Asset not found")
                    if row['plan_id'] != row['scenario_plan_id']:
                        raise ValueError("Asset must belong to the scenario's plan")

                # Check if override record exists
                async with conn.execute(
                    "SELECT scenario_asset_id FROM scenario_assets WHERE scenario_id = ? AND original_asset_id = ?",
                    (scenario_id, asset_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        # Update existing override
                        updates = []
                        values = []
                        if value is not None:
                            updates.extend([
                                "overrides_value = 1",
                                "value = ?"
                            ])
                            values.append(value)
                        if independent_growth_rate is not None:
                            updates.extend([
                                "overrides_independent_growth_rate = 1",
                                "independent_growth_rate = ?"
                            ])
                            values.append(independent_growth_rate)
                        if include_in_nest_egg is not None:
                            updates.append("include_in_nest_egg = ?")
                            values.append(include_in_nest_egg)
                        
                        updates.append("exclude_from_projection = ?")
                        values.append(exclude_from_projection)

                        if updates:
                            query = f"""
                                UPDATE scenario_assets 
                                SET {', '.join(updates)}
                                WHERE scenario_asset_id = ?
                            """
                            values.append(row['scenario_asset_id'])
                            await conn.execute(query, tuple(values))
                            return row['scenario_asset_id']
                    else:
                        # Create new override
                        cursor = await conn.execute(
                            """
                            INSERT INTO scenario_assets (
                                scenario_id,
                                original_asset_id,
                                overrides_value,
                                value,
                                overrides_independent_growth_rate,
                                independent_growth_rate,
                                include_in_nest_egg,
                                exclude_from_projection
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                scenario_id,
                                asset_id,
                                1 if value is not None else 0,
                                value,
                                1 if independent_growth_rate is not None else 0,
                                independent_growth_rate,
                                include_in_nest_egg if include_in_nest_egg is not None else 1,
                                exclude_from_projection
                            )
                        )
                        return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error overriding asset: {str(e)}")
            raise

    async def override_liability(
        self,
        scenario_id: int,
        liability_id: int,
        value: Optional[float] = None,
        interest_rate: Optional[float] = None,
        include_in_nest_egg: Optional[bool] = None,
        exclude_from_projection: bool = False
    ) -> int:
        """
        Create or update a liability override for a scenario.

        Args:
            scenario_id: ID of the scenario
            liability_id: ID of the liability to override
            value: New balance override
            interest_rate: New interest rate override
            include_in_nest_egg: Whether to include in retirement calculations
            exclude_from_projection: Whether to exclude this liability from the scenario

        Returns:
            The ID of the created/updated override

        Raises:
            ValueError: If value is negative
            ValueError: If interest rate is outside allowed range
            ValueError: If liability doesn't belong to scenario's plan
        """
        try:
            # Validate input values
            if value is not None and value < 0:
                raise ValueError("Liability value cannot be negative")
            if (interest_rate is not None and 
                (interest_rate < -200 or interest_rate > 200)):
                raise ValueError("Interest rate must be between -200 and 200")

            async with DatabaseConnection.transaction() as conn:
                # Verify liability belongs to scenario's plan
                query = """
                    SELECT l.plan_id, s.plan_id as scenario_plan_id
                    FROM liabilities l
                    JOIN scenarios s ON s.scenario_id = ?
                    WHERE l.liability_id = ?
                """
                async with conn.execute(query, (scenario_id, liability_id)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Liability not found")
                    if row['plan_id'] != row['scenario_plan_id']:
                        raise ValueError("Liability must belong to the scenario's plan")

                # Check if override record exists
                async with conn.execute(
                    """
                    SELECT scenario_item_id 
                    FROM scenario_liabilities 
                    WHERE scenario_id = ? AND original_liability_id = ?
                    """,
                    (scenario_id, liability_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        # Update existing override
                        updates = []
                        values = []
                        if value is not None:
                            updates.extend([
                                "overrides_value = 1",
                                "value = ?"
                            ])
                            values.append(value)
                        if interest_rate is not None:
                            updates.extend([
                                "overrides_interest_rate = 1",
                                "interest_rate = ?"
                            ])
                            values.append(interest_rate)
                        if include_in_nest_egg is not None:
                            updates.append("include_in_nest_egg = ?")
                            values.append(include_in_nest_egg)
                        
                        updates.append("exclude_from_projection = ?")
                        values.append(exclude_from_projection)

                        if updates:
                            query = f"""
                                UPDATE scenario_liabilities 
                                SET {', '.join(updates)}
                                WHERE scenario_item_id = ?
                            """
                            values.append(row['scenario_item_id'])
                            await conn.execute(query, tuple(values))
                            return row['scenario_item_id']
                    else:
                        # Create new override
                        cursor = await conn.execute(
                            """
                            INSERT INTO scenario_liabilities (
                                scenario_id,
                                original_liability_id,
                                overrides_value,
                                value,
                                overrides_interest_rate,
                                interest_rate,
                                include_in_nest_egg,
                                exclude_from_projection
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                scenario_id,
                                liability_id,
                                1 if value is not None else 0,
                                value,
                                1 if interest_rate is not None else 0,
                                interest_rate,
                                include_in_nest_egg if include_in_nest_egg is not None else 1,
                                exclude_from_projection
                            )
                        )
                        return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error overriding liability: {str(e)}")
            raise

async def override_inflow_outflow(
        self,
        scenario_id: int,
        inflow_outflow_id: int,
        annual_amount: Optional[float] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        apply_inflation: Optional[bool] = None,
        exclude_from_projection: bool = False
    ) -> int:
        """
        Create or update an inflow/outflow override for a scenario.

        Args:
            scenario_id: ID of the scenario
            inflow_outflow_id: ID of the inflow/outflow to override
            annual_amount: New amount override
            start_year: New start year override
            end_year: New end year override
            apply_inflation: Whether to adjust amount for inflation
            exclude_from_projection: Whether to exclude this item from the scenario

        Returns:
            The ID of the created/updated override

        Raises:
            ValueError: If years are invalid
            ValueError: If inflow/outflow doesn't belong to scenario's plan
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                # Verify inflow/outflow belongs to scenario's plan
                query = """
                    SELECT io.plan_id, s.plan_id as scenario_plan_id,
                           io.start_year as original_start_year,
                           io.end_year as original_end_year
                    FROM inflows_outflows io
                    JOIN scenarios s ON s.scenario_id = ?
                    WHERE io.inflow_outflow_id = ?
                """
                async with conn.execute(query, (scenario_id, inflow_outflow_id)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Inflow/outflow not found")
                    if row['plan_id'] != row['scenario_plan_id']:
                        raise ValueError("Inflow/outflow must belong to the scenario's plan")

                    # Validate years
                    effective_start = start_year if start_year is not None else row['original_start_year']
                    effective_end = end_year if end_year is not None else row['original_end_year']
                    if effective_start > effective_end:
                        raise ValueError("Start year must be before or equal to end year")

                # Check if override record exists
                async with conn.execute(
                    """
                    SELECT scenario_item_id 
                    FROM scenario_inflows_outflows 
                    WHERE scenario_id = ? AND original_inflow_outflow_id = ?
                    """,
                    (scenario_id, inflow_outflow_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        # Update existing override
                        updates = []
                        values = []
                        if annual_amount is not None:
                            updates.extend([
                                "overrides_annual_amount = 1",
                                "annual_amount = ?"
                            ])
                            values.append(annual_amount)
                        if start_year is not None:
                            updates.extend([
                                "overrides_start_year = 1",
                                "start_year = ?"
                            ])
                            values.append(start_year)
                        if end_year is not None:
                            updates.extend([
                                "overrides_end_year = 1",
                                "end_year = ?"
                            ])
                            values.append(end_year)
                        if apply_inflation is not None:
                            updates.append("apply_inflation = ?")
                            values.append(apply_inflation)
                        
                        updates.append("exclude_from_projection = ?")
                        values.append(exclude_from_projection)

                        if updates:
                            query = f"""
                                UPDATE scenario_inflows_outflows 
                                SET {', '.join(updates)}
                                WHERE scenario_item_id = ?
                            """
                            values.append(row['scenario_item_id'])
                            await conn.execute(query, tuple(values))
                            return row['scenario_item_id']
                    else:
                        # Create new override
                        cursor = await conn.execute(
                            """
                            INSERT INTO scenario_inflows_outflows (
                                scenario_id,
                                original_inflow_outflow_id,
                                overrides_annual_amount,
                                annual_amount,
                                overrides_start_year,
                                start_year,
                                overrides_end_year,
                                end_year,
                                apply_inflation,
                                exclude_from_projection
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                scenario_id,
                                inflow_outflow_id,
                                1 if annual_amount is not None else 0,
                                annual_amount,
                                1 if start_year is not None else 0,
                                start_year,
                                1 if end_year is not None else 0,
                                end_year,
                                apply_inflation if apply_inflation is not None else 0,
                                exclude_from_projection
                            )
                        )
                        return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error overriding inflow/outflow: {str(e)}")
            raise

    async def override_retirement_income(
        self,
        scenario_id: int,
        income_plan_id: int,
        annual_income: Optional[float] = None,
        start_age: Optional[int] = None,
        end_age: Optional[int] = None,
        apply_inflation: Optional[bool] = None,
        include_in_nest_egg: Optional[bool] = None,
        exclude_from_projection: bool = False
    ) -> int:
        """
        Create or update a retirement income override for a scenario.

        Args:
            scenario_id: ID of the scenario
            income_plan_id: ID of the retirement income plan to override
            annual_income: New income amount override
            start_age: New start age override
            end_age: New end age override
            apply_inflation: Whether to adjust amount for inflation
            include_in_nest_egg: Whether to include in retirement calculations
            exclude_from_projection: Whether to exclude this income from the scenario

        Returns:
            The ID of the created/updated override

        Raises:
            ValueError: If ages are invalid
            ValueError: If income plan doesn't belong to scenario's plan
        """
        try:
            async with DatabaseConnection.transaction() as conn:
                # Verify income plan belongs to scenario's plan
                query = """
                    SELECT rip.plan_id, s.plan_id as scenario_plan_id,
                           rip.start_age as original_start_age,
                           rip.end_age as original_end_age
                    FROM retirement_income_plans rip
                    JOIN scenarios s ON s.scenario_id = ?
                    WHERE rip.income_plan_id = ?
                """
                async with conn.execute(query, (scenario_id, income_plan_id)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError("Retirement income plan not found")
                    if row['plan_id'] != row['scenario_plan_id']:
                        raise ValueError("Income plan must belong to the scenario's plan")

                    # Validate ages
                    effective_start = start_age if start_age is not None else row['original_start_age']
                    effective_end = end_age if end_age is not None else row['original_end_age']
                    if effective_end is not None and effective_start > effective_end:
                        raise ValueError("Start age must be before or equal to end age")

                # Check if override record exists
                async with conn.execute(
                    """
                    SELECT scenario_item_id 
                    FROM scenario_retirement_income 
                    WHERE scenario_id = ? AND original_income_plan_id = ?
                    """,
                    (scenario_id, income_plan_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        # Update existing override
                        updates = []
                        values = []
                        if annual_income is not None:
                            updates.extend([
                                "overrides_annual_income = 1",
                                "annual_income = ?"
                            ])
                            values.append(annual_income)
                        if start_age is not None:
                            updates.extend([
                                "overrides_start_age = 1",
                                "start_age = ?"
                            ])
                            values.append(start_age)
                        if end_age is not None:
                            updates.extend([
                                "overrides_end_age = 1",
                                "end_age = ?"
                            ])
                            values.append(end_age)
                        if apply_inflation is not None:
                            updates.append("apply_inflation = ?")
                            values.append(apply_inflation)
                        if include_in_nest_egg is not None:
                            updates.append("include_in_nest_egg = ?")
                            values.append(include_in_nest_egg)
                        
                        updates.append("exclude_from_projection = ?")
                        values.append(exclude_from_projection)

                        if updates:
                            query = f"""
                                UPDATE scenario_retirement_income 
                                SET {', '.join(updates)}
                                WHERE scenario_item_id = ?
                            """
                            values.append(row['scenario_item_id'])
                            await conn.execute(query, tuple(values))
                            return row['scenario_item_id']
                    else:
                        # Create new override
                        cursor = await conn.execute(
                            """
                            INSERT INTO scenario_retirement_income (
                                scenario_id,
                                original_income_plan_id,
                                overrides_annual_income,
                                annual_income,
                                overrides_start_age,
                                start_age,
                                overrides_end_age,
                                end_age,
                                apply_inflation,
                                include_in_nest_egg,
                                exclude_from_projection
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                scenario_id,
                                income_plan_id,
                                1 if annual_income is not None else 0,
                                annual_income,
                                1 if start_age is not None else 0,
                                start_age,
                                1 if end_age is not None else 0,
                                end_age,
                                apply_inflation if apply_inflation is not None else 0,
                                include_in_nest_egg if include_in_nest_egg is not None else 1,
                                exclude_from_projection
                            )
                        )
                        return cursor.lastrowid

        except Exception as e:
            logger.error(f"Error overriding retirement income: {str(e)}")
            raise

    async def get_scenario_effective_assumptions(self, scenario_id: int) -> Dict[str, Any]:
        """
        Get the effective assumptions for a scenario, combining base and overridden values.
        Uses the scenario_effective_assumptions view.
        """
        try:
            query = "SELECT * FROM scenario_effective_assumptions WHERE scenario_id = ?"
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (scenario_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else {}

        except Exception as e:
            logger.error(f"Error getting effective assumptions: {str(e)}")
            raise

    async def get_scenario_effective_assets(self, scenario_id: int) -> List[Dict[str, Any]]:
        """
        Get the effective asset values for a scenario, combining base and overridden values.
        Uses the scenario_effective_assets view.
        """
        try:
            query = """
                SELECT sea.*, ac.category_name,
                       GROUP_CONCAT(p.first_name || ' ' || p.last_name) as owner_names,
                       GROUP_CONCAT(p.person_id) as owner_ids
                FROM scenario_effective_assets sea
                JOIN asset_categories ac ON sea.asset_category_id = ac.asset_category_id
                LEFT JOIN asset_owners ao ON sea.asset_id = ao.asset_id
                LEFT JOIN people p ON ao.person_id = p.person_id
                WHERE sea.scenario_id = ?
                GROUP BY sea.asset_id
                ORDER BY ac.category_name, sea.asset_name
            """
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (scenario_id,)) as cursor:
                    rows = await cursor.fetchall()
                    result = []
                    for row in rows:
                        asset_dict = dict(row)
                        if asset_dict.get("owner_ids"):
                            asset_dict["owner_ids"] = [
                                int(id) for id in asset_dict["owner_ids"].split(',')
                            ]
                        result.append(asset_dict)
                    return result

        except Exception as e:
            logger.error(f"Error getting effective assets: {str(e)}")
            raise