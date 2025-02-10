# crud/tests/test_scenario.py


"""
Test suite for scenario CRUD operations.
Tests scenario creation, overrides, and effective value calculations.
"""
import asyncio
import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple

from ..scenarios import ScenariosCRUD
from ..households import HouseholdsCRUD
from ..people import PeopleCRUD
from ..plans import PlansCRUD
from ..assets import AssetsCRUD
from ..liabilities import LiabilitiesCRUD
from ...connection import DatabaseConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data constants
TEST_BASE_ASSUMPTIONS = {
    "nest_egg_growth_rate": 6.0,
    "inflation_rate": 3.0,
    "annual_retirement_spending": 50000.0
}

TEST_ASSET_DATA = {
    "asset_name": "Test Asset",
    "value": 100000.0,
    "independent_growth_rate": 7.0
}

TEST_LIABILITY_DATA = {
    "liability_name": "Test Liability",
    "value": 250000.0,
    "interest_rate": 4.5
}

TEST_CASH_FLOW_DATA = {
    "name": "Test Income",
    "type": "INFLOW",
    "annual_amount": 75000.0,
    "start_year": 2025,
    "end_year": 2030
}

async def setup_test_data() -> Tuple[int, int, int, int, int, int]:
    """
    Create test household, people, plan, and basic financial entries.
    
    Returns:
        Tuple of (household_id, person1_id, person2_id, plan_id, asset_category_id, liability_category_id)
    """
    try:
        # Create household
        households = HouseholdsCRUD()
        household_id = await households.create_household("Test Family")

        # Create two people for testing joint scenarios
        people = PeopleCRUD()
        person1_id = await people.create_person(
            household_id=household_id,
            first_name="John",
            last_name="Doe",
            dob=date(1980, 1, 1),
            retirement_age=65,
            final_age=95
        )
        person2_id = await people.create_person(
            household_id=household_id,
            first_name="Jane",
            last_name="Doe",
            dob=date(1982, 1, 1),
            retirement_age=65,
            final_age=95
        )

        # Create plan
        plans = PlansCRUD()
        plan_id = await plans.create_plan(
            household_id=household_id,
            plan_name="Test Plan",
            reference_person_id=person1_id,
            base_assumptions=TEST_BASE_ASSUMPTIONS
        )

        # Create asset category
        assets = AssetsCRUD()
        asset_category_id = await assets.create_asset_category(household_id, "Test Assets")

        # Create liability category
        liabilities = LiabilitiesCRUD()
        liability_category_id = await liabilities.create_liability_category(household_id, "Test Liabilities")

        return household_id, person1_id, person2_id, plan_id, asset_category_id, liability_category_id

    except Exception as e:
        logger.error(f"Error in test setup: {str(e)}")
        raise

async def create_test_scenario(
    plan_id: int,
    scenario_name: str = "Test Scenario",
    assumption_overrides: Optional[Dict[str, Any]] = None
) -> int:
    """
    Create a basic test scenario with optional overrides.
    
    Args:
        plan_id: ID of the plan to create scenario for
        scenario_name: Name for the scenario
        assumption_overrides: Optional overrides for base assumptions
        
    Returns:
        The ID of the created scenario
    """
    scenarios = ScenariosCRUD()
    return await scenarios.create_scenario(
        plan_id=plan_id,
        scenario_name=scenario_name,
        assumption_overrides=assumption_overrides
    )

async def cleanup_test_data(household_id: int):
    """Clean up all test data through cascading delete."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_scenario_creation():
    """Test basic scenario creation with and without assumption overrides."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Test basic creation
        logger.info("Testing basic scenario creation...")
        scenario_id = await create_test_scenario(plan_id)
        assert scenario_id is not None, "Failed to create basic scenario"
        logger.info(f"✓ Created basic scenario with ID: {scenario_id}")

        # Test creation with assumption overrides
        logger.info("Testing scenario creation with assumption overrides...")
        overrides = {
            "nest_egg_growth_rate": 5.0,
            "inflation_rate": 4.0,
            "annual_retirement_spending": 60000.0
        }
        scenario_id = await create_test_scenario(
            plan_id,
            scenario_name="Override Test",
            assumption_overrides=overrides
        )
        assert scenario_id is not None, "Failed to create scenario with overrides"

        # Verify overrides
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario is not None, "Failed to retrieve scenario"
        assert scenario["nest_egg_growth_rate"] == overrides["nest_egg_growth_rate"], "Growth rate override not applied"
        assert scenario["inflation_rate"] == overrides["inflation_rate"], "Inflation rate override not applied"
        assert scenario["annual_retirement_spending"] == overrides["annual_retirement_spending"], "Spending override not applied"
        logger.info("✓ Created and verified scenario with overrides")

        # Test invalid growth rate
        logger.info("Testing growth rate validation...")
        try:
            await create_test_scenario(
                plan_id,
                assumption_overrides={"nest_egg_growth_rate": 250.0}  # Invalid
            )
            assert False, "Should have rejected invalid growth rate"
        except ValueError:
            logger.info("✓ Correctly rejected invalid growth rate")

        # Test invalid plan ID
        logger.info("Testing invalid plan ID validation...")
        try:
            await create_test_scenario(999999)  # Invalid plan_id
            assert False, "Should have rejected invalid plan ID"
        except ValueError:
            logger.info("✓ Correctly rejected invalid plan ID")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_scenario_retrieval():
    """Test scenario retrieval with all related information."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create scenario with overrides
        logger.info("Creating test scenario...")
        overrides = {
            "nest_egg_growth_rate": 5.0,
            "inflation_rate": 4.0
        }
        scenario_id = await create_test_scenario(
            plan_id,
            assumption_overrides=overrides
        )

        # Test basic retrieval
        logger.info("Testing scenario retrieval...")
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario is not None, "Failed to retrieve scenario"
        assert scenario["plan_id"] == plan_id, "Incorrect plan ID"
        assert scenario["scenario_name"] == "Test Scenario", "Incorrect scenario name"
        assert scenario["nest_egg_growth_rate"] == overrides["nest_egg_growth_rate"], "Incorrect growth rate"
        assert scenario["inflation_rate"] == overrides["inflation_rate"], "Incorrect inflation rate"
        logger.info("✓ Retrieved scenario successfully")

        # Test retrieval of non-existent scenario
        logger.info("Testing non-existent scenario retrieval...")
        non_existent = await scenarios.get_scenario(999999)
        assert non_existent is None, "Should return None for non-existent scenario"
        logger.info("✓ Correctly handled non-existent scenario")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_scenario_update():
    """Test scenario updates including assumption changes."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create base scenario
        logger.info("Creating test scenario...")
        scenario_id = await create_test_scenario(plan_id)

        # Test name update
        logger.info("Testing scenario name update...")
        new_name = "Updated Scenario"
        success = await scenarios.update_scenario(
            scenario_id,
            scenario_name=new_name
        )
        assert success, "Failed to update scenario name"
        updated = await scenarios.get_scenario(scenario_id)
        assert updated["scenario_name"] == new_name, "Name not updated"
        logger.info("✓ Updated scenario name successfully")

        # Test assumption updates
        logger.info("Testing assumption updates...")
        new_overrides = {
            "nest_egg_growth_rate": 5.5,
            "inflation_rate": 3.5,
            "annual_retirement_spending": 55000.0
        }
        success = await scenarios.update_scenario(
            scenario_id,
            assumption_overrides=new_overrides
        )
        assert success, "Failed to update assumptions"
        updated = await scenarios.get_scenario(scenario_id)
        assert updated["nest_egg_growth_rate"] == new_overrides["nest_egg_growth_rate"], "Growth rate not updated"
        assert updated["inflation_rate"] == new_overrides["inflation_rate"], "Inflation rate not updated"
        assert updated["annual_retirement_spending"] == new_overrides["annual_retirement_spending"], "Spending not updated"
        logger.info("✓ Updated assumptions successfully")

        # Test invalid updates
        logger.info("Testing invalid updates...")
        try:
            await scenarios.update_scenario(
                scenario_id,
                assumption_overrides={"nest_egg_growth_rate": 250.0}  # Invalid
            )
            assert False, "Should have rejected invalid growth rate"
        except ValueError:
            logger.info("✓ Correctly rejected invalid growth rate")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_scenario_creation())
    asyncio.run(test_scenario_retrieval())
    asyncio.run(test_scenario_update())


async def test_scenario_deletion():
    """Test scenario deletion and cascading cleanup."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create test scenario with overrides
        logger.info("Creating test scenario...")
        scenario_id = await create_test_scenario(
            plan_id,
            assumption_overrides={"nest_egg_growth_rate": 5.0}
        )

        # Test deletion
        logger.info("Testing scenario deletion...")
        success = await scenarios.delete_scenario(scenario_id)
        assert success, "Failed to delete scenario"

        # Verify deletion
        deleted = await scenarios.get_scenario(scenario_id)
        assert deleted is None, "Scenario still exists after deletion"
        logger.info("✓ Deleted scenario successfully")

        # Test deletion of non-existent scenario
        logger.info("Testing non-existent scenario deletion...")
        success = await scenarios.delete_scenario(999999)
        assert not success, "Should return False for non-existent scenario"
        logger.info("✓ Correctly handled non-existent scenario deletion")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_scenario_listing():
    """Test scenario listing with various filters."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create multiple scenarios
        logger.info("Creating test scenarios...")
        scenario_ids = []
        for i in range(3):
            scenario_id = await create_test_scenario(
                plan_id,
                scenario_name=f"Test Scenario {i+1}",
                assumption_overrides={"nest_egg_growth_rate": 5.0 + i}
            )
            scenario_ids.append(scenario_id)

        # Test basic listing
        logger.info("Testing basic scenario listing...")
        scenarios_list = await scenarios.list_scenarios()
        assert len(scenarios_list) >= 3, "Not all scenarios listed"
        assert all(s["scenario_id"] in scenario_ids for s in scenarios_list), "Missing scenarios in list"
        logger.info("✓ Listed scenarios successfully")

        # Test listing with plan filter
        logger.info("Testing plan-filtered listing...")
        filtered_list = await scenarios.list_scenarios(plan_id=plan_id)
        assert len(filtered_list) == 3, "Incorrect number of scenarios for plan"
        assert all(s["plan_id"] == plan_id for s in filtered_list), "Listed scenarios from wrong plan"
        logger.info("✓ Listed plan-filtered scenarios successfully")

        # Test listing with override counting
        logger.info("Testing listing with override counts...")
        counted_list = await scenarios.list_scenarios(
            plan_id=plan_id,
            include_override_counts=True
        )
        assert len(counted_list) == 3, "Incorrect number of scenarios"
        assert all("num_growth_adjustments" in s for s in counted_list), "Missing override counts"
        logger.info("✓ Listed scenarios with override counts successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_person_retirement_overrides():
    """Test person retirement age overrides in scenarios."""
    household_id = None
    try:
        # Setup
        household_id, person1_id, person2_id, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create test scenario
        logger.info("Creating test scenario...")
        scenario_id = await create_test_scenario(plan_id)

        # Test retirement age override
        logger.info("Testing retirement age override...")
        success = await scenarios.update_person_overrides(
            scenario_id,
            person1_id,
            retirement_age=67,
            final_age=97
        )
        assert success, "Failed to update person overrides"

        # Verify overrides
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario["num_person_overrides"] == 1, "Person override not counted"
        logger.info("✓ Updated person overrides successfully")

        # Test invalid retirement age
        logger.info("Testing invalid retirement age...")
        try:
            await scenarios.update_person_overrides(
                scenario_id,
                person1_id,
                retirement_age=0  # Invalid
            )
            assert False, "Should have rejected invalid retirement age"
        except ValueError:
            logger.info("✓ Correctly rejected invalid retirement age")

        # Test invalid age relationship
        logger.info("Testing invalid age relationship...")
        try:
            await scenarios.update_person_overrides(
                scenario_id,
                person1_id,
                retirement_age=70,
                final_age=65  # Invalid: less than retirement age
            )
            assert False, "Should have rejected invalid age relationship"
        except ValueError:
            logger.info("✓ Correctly rejected invalid age relationship")

        # Test update for person from different household
        logger.info("Testing cross-household validation...")
        other_household_id = await HouseholdsCRUD().create_household("Other Family")
        try:
            other_person_id = await PeopleCRUD().create_person(
                household_id=other_household_id,
                first_name="Other",
                last_name="Person",
                dob=date(1980, 1, 1),
                retirement_age=65,
                final_age=95
            )
            
            try:
                await scenarios.update_person_overrides(
                    scenario_id,
                    other_person_id,
                    retirement_age=67
                )
                assert False, "Should have rejected person from different household"
            except ValueError:
                logger.info("✓ Correctly rejected person from different household")
        finally:
            await HouseholdsCRUD().delete_household(other_household_id)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_asset_overrides():
    """Test asset overrides in scenarios."""
    household_id = None
    try:
        # Setup
        household_id, person1_id, _, plan_id, category_id, _ = await setup_test_data()
        scenarios = ScenariosCRUD()
        assets = AssetsCRUD()

        # Create test asset
        logger.info("Creating test asset...")
        asset_id = await assets.create_asset(
            plan_id=plan_id,
            asset_category_id=category_id,
            asset_name=TEST_ASSET_DATA["asset_name"],
            value=TEST_ASSET_DATA["value"],
            owner_ids=[person1_id],
            independent_growth_rate=TEST_ASSET_DATA["independent_growth_rate"]
        )

        # Create test scenario
        scenario_id = await create_test_scenario(plan_id)

        # Test value override
        logger.info("Testing asset value override...")
        new_value = 150000.0
        override_id = await scenarios.override_asset(
            scenario_id,
            asset_id,
            value=new_value
        )
        assert override_id is not None, "Failed to create asset override"

        # Verify override
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario["num_asset_overrides"] == 1, "Asset override not counted"

        effective_assets = await scenarios.get_scenario_effective_assets(scenario_id)
        assert len(effective_assets) == 1, "Missing effective asset"
        assert effective_assets[0]["value"] == new_value, "Asset value not overridden"
        logger.info("✓ Created asset value override successfully")

        # Test growth rate override
        logger.info("Testing growth rate override...")
        new_growth_rate = 8.0
        override_id = await scenarios.override_asset(
            scenario_id,
            asset_id,
            independent_growth_rate=new_growth_rate
        )
        assert override_id is not None, "Failed to update asset override"

        effective_assets = await scenarios.get_scenario_effective_assets(scenario_id)
        assert effective_assets[0]["independent_growth_rate"] == new_growth_rate, "Growth rate not overridden"
        logger.info("✓ Updated asset growth rate successfully")

        # Test asset exclusion
        logger.info("Testing asset exclusion...")
        override_id = await scenarios.override_asset(
            scenario_id,
            asset_id,
            exclude_from_projection=True
        )
        assert override_id is not None, "Failed to exclude asset"

        effective_assets = await scenarios.get_scenario_effective_assets(scenario_id)
        assert len(effective_assets) == 0, "Asset not excluded from projection"
        logger.info("✓ Excluded asset successfully")

        # Test invalid value
        logger.info("Testing invalid value override...")
        try:
            await scenarios.override_asset(
                scenario_id,
                asset_id,
                value=-1000.0  # Invalid
            )
            assert False, "Should have rejected negative value"
        except ValueError:
            logger.info("✓ Correctly rejected negative value")

        # Test invalid growth rate
        logger.info("Testing invalid growth rate override...")
        try:
            await scenarios.override_asset(
                scenario_id,
                asset_id,
                independent_growth_rate=250.0  # Invalid
            )
            assert False, "Should have rejected invalid growth rate"
        except ValueError:
            logger.info("✓ Correctly rejected invalid growth rate")

        # Test override for asset from different plan
        logger.info("Testing cross-plan validation...")
        other_plan_id = await PlansCRUD().create_plan(
            household_id=household_id,
            plan_name="Other Plan",
            reference_person_id=person1_id,
            base_assumptions=TEST_BASE_ASSUMPTIONS
        )
        other_asset_id = await assets.create_asset(
            plan_id=other_plan_id,
            asset_category_id=category_id,
            asset_name="Other Asset",
            value=100000.0,
            owner_ids=[person1_id]
        )
        
        try:
            await scenarios.override_asset(
                scenario_id,
                other_asset_id,
                value=150000.0
            )
            assert False, "Should have rejected asset from different plan"
        except ValueError:
            logger.info("✓ Correctly rejected asset from different plan")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_scenario_deletion())
    asyncio.run(test_scenario_listing())
    asyncio.run(test_person_retirement_overrides())
    asyncio.run(test_asset_overrides())

async def test_liability_overrides():
    """Test liability overrides in scenarios."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, category_id = await setup_test_data()
        scenarios = ScenariosCRUD()
        liabilities = LiabilitiesCRUD()

        # Create test liability
        logger.info("Creating test liability...")
        liability_id = await liabilities.create_liability(
            plan_id=plan_id,
            liability_category_id=category_id,
            liability_name=TEST_LIABILITY_DATA["liability_name"],
            value=TEST_LIABILITY_DATA["value"],
            interest_rate=TEST_LIABILITY_DATA["interest_rate"]
        )

        # Create test scenario
        scenario_id = await create_test_scenario(plan_id)

        # Test value override
        logger.info("Testing liability value override...")
        new_value = 200000.0
        override_id = await scenarios.override_liability(
            scenario_id,
            liability_id,
            value=new_value
        )
        assert override_id is not None, "Failed to create liability override"

        # Verify override
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario["num_liability_overrides"] == 1, "Liability override not counted"
        logger.info("✓ Created liability value override successfully")

        # Test interest rate override
        logger.info("Testing interest rate override...")
        new_rate = 5.0
        override_id = await scenarios.override_liability(
            scenario_id,
            liability_id,
            interest_rate=new_rate
        )
        assert override_id is not None, "Failed to update liability override"
        logger.info("✓ Updated liability interest rate successfully")

        # Test liability exclusion
        logger.info("Testing liability exclusion...")
        override_id = await scenarios.override_liability(
            scenario_id,
            liability_id,
            exclude_from_projection=True
        )
        assert override_id is not None, "Failed to exclude liability"
        logger.info("✓ Excluded liability successfully")

        # Test invalid value
        logger.info("Testing invalid value override...")
        try:
            await scenarios.override_liability(
                scenario_id,
                liability_id,
                value=-1000.0  # Invalid
            )
            assert False, "Should have rejected negative value"
        except ValueError:
            logger.info("✓ Correctly rejected negative value")

        # Test invalid interest rate
        logger.info("Testing invalid interest rate override...")
        try:
            await scenarios.override_liability(
                scenario_id,
                liability_id,
                interest_rate=250.0  # Invalid
            )
            assert False, "Should have rejected invalid interest rate"
        except ValueError:
            logger.info("✓ Correctly rejected invalid interest rate")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_inflow_outflow_overrides():
    """Test inflow/outflow overrides in scenarios."""
    household_id = None
    try:
        # Setup
        household_id, _, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create test cash flow
        logger.info("Creating test cash flow...")
        async with DatabaseConnection.transaction() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO inflows_outflows (
                    plan_id, type, name, annual_amount, start_year, end_year
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    TEST_CASH_FLOW_DATA["type"],
                    TEST_CASH_FLOW_DATA["name"],
                    TEST_CASH_FLOW_DATA["annual_amount"],
                    TEST_CASH_FLOW_DATA["start_year"],
                    TEST_CASH_FLOW_DATA["end_year"]
                )
            )
            cash_flow_id = cursor.lastrowid

        # Create test scenario
        scenario_id = await create_test_scenario(plan_id)

        # Test amount override
        logger.info("Testing cash flow amount override...")
        new_amount = 80000.0
        override_id = await scenarios.override_inflow_outflow(
            scenario_id,
            cash_flow_id,
            annual_amount=new_amount
        )
        assert override_id is not None, "Failed to create cash flow override"

        # Verify override
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario["num_inflow_outflow_overrides"] == 1, "Cash flow override not counted"
        logger.info("✓ Created cash flow amount override successfully")

        # Test timing override
        logger.info("Testing cash flow timing override...")
        new_start = 2026
        new_end = 2031
        override_id = await scenarios.override_inflow_outflow(
            scenario_id,
            cash_flow_id,
            start_year=new_start,
            end_year=new_end
        )
        assert override_id is not None, "Failed to update cash flow timing"
        logger.info("✓ Updated cash flow timing successfully")

        # Test invalid timing
        logger.info("Testing invalid timing override...")
        try:
            await scenarios.override_inflow_outflow(
                scenario_id,
                cash_flow_id,
                start_year=2030,
                end_year=2025  # Invalid
            )
            assert False, "Should have rejected invalid timing"
        except ValueError:
            logger.info("✓ Correctly rejected invalid timing")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_retirement_income_overrides():
    """Test retirement income overrides in scenarios."""
    household_id = None
    try:
        # Setup
        household_id, person1_id, _, plan_id, _, _ = await setup_test_data()
        scenarios = ScenariosCRUD()

        # Create test retirement income
        logger.info("Creating test retirement income...")
        async with DatabaseConnection.transaction() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO retirement_income_plans (
                    plan_id, name, annual_income, start_age, end_age
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (plan_id, "Test Pension", 50000.0, 65, 95)
            )
            income_id = cursor.lastrowid

            # Add income owner
            await conn.execute(
                "INSERT INTO retirement_income_owners (income_plan_id, person_id) VALUES (?, ?)",
                (income_id, person1_id)
            )

        # Create test scenario
        scenario_id = await create_test_scenario(plan_id)

        # Test amount override
        logger.info("Testing retirement income amount override...")
        new_amount = 55000.0
        override_id = await scenarios.override_retirement_income(
            scenario_id,
            income_id,
            annual_income=new_amount
        )
        assert override_id is not None, "Failed to create income override"

        # Verify override
        scenario = await scenarios.get_scenario(scenario_id)
        assert scenario["num_retirement_income_overrides"] == 1, "Income override not counted"
        logger.info("✓ Created retirement income override successfully")

        # Test timing override
        logger.info("Testing retirement income timing override...")
        new_start = 67
        new_end = 90
        override_id = await scenarios.override_retirement_income(
            scenario_id,
            income_id,
            start_age=new_start,
            end_age=new_end
        )
        assert override_id is not None, "Failed to update income timing"
        logger.info("✓ Updated retirement income timing successfully")

        # Test invalid timing
        logger.info("Testing invalid timing override...")
        try:
            await scenarios.override_retirement_income(
                scenario_id,
                income_id,
                start_age=70,
                end_age=65  # Invalid
            )
            assert False, "Should have rejected invalid timing"
        except ValueError:
            logger.info("✓ Correctly rejected invalid timing")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_effective_values():
    """Test effective value calculations combining base facts and overrides."""
    household_id = None
    try:
        # Setup
        household_id, person1_id, _, plan_id, category_id, _ = await setup_test_data()
        scenarios = ScenariosCRUD()
        assets = AssetsCRUD()

        # Create test assets
        logger.info("Creating test assets...")
        asset1_id = await assets.create_asset(
            plan_id=plan_id,
            asset_category_id=category_id,
            asset_name="Asset 1",
            value=100000.0,
            owner_ids=[person1_id],
            independent_growth_rate=7.0
        )
        asset2_id = await assets.create_asset(
            plan_id=plan_id,
            asset_category_id=category_id,
            asset_name="Asset 2",
            value=200000.0,
            owner_ids=[person1_id]
        )

        # Create scenario with overrides
        logger.info("Creating test scenario with overrides...")
        scenario_id = await create_test_scenario(
            plan_id,
            assumption_overrides={"nest_egg_growth_rate": 5.0}
        )

        # Override first asset
        await scenarios.override_asset(
            scenario_id,
            asset1_id,
            value=150000.0,
            independent_growth_rate=8.0
        )

        # Test effective assumptions
        logger.info("Testing effective assumptions...")
        assumptions = await scenarios.get_scenario_effective_assumptions(scenario_id)
        assert assumptions["nest_egg_growth_rate"] == 5.0, "Incorrect effective growth rate"
        assert assumptions["inflation_rate"] == TEST_BASE_ASSUMPTIONS["inflation_rate"], "Base inflation rate not preserved"
        logger.info("✓ Retrieved effective assumptions successfully")

        # Test effective assets
        logger.info("Testing effective assets...")
        assets = await scenarios.get_scenario_effective_assets(scenario_id)
        assert len(assets) == 2, "Incorrect number of effective assets"
        
        # Verify overridden asset
        overridden = next(a for a in assets if a["asset_id"] == asset1_id)
        assert overridden["value"] == 150000.0, "Override value not applied"
        assert overridden["independent_growth_rate"] == 8.0, "Override growth rate not applied"
        
        # Verify non-overridden asset
        base = next(a for a in assets if a["asset_id"] == asset2_id)
        assert base["value"] == 200000.0, "Base value not preserved"
        assert base["independent_growth_rate"] is None, "Should use default growth rate"
        logger.info("✓ Retrieved effective assets successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_liability_overrides())
    asyncio.run(test_inflow_outflow_overrides())
    asyncio.run(test_retirement_income_overrides())
    asyncio.run(test_effective_values())