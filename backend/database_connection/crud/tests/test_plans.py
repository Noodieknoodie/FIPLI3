"""
Test suite for financial plans CRUD operations.
"""

import asyncio
import logging
from datetime import date
from ..plans import PlansCRUD
from ..households import HouseholdsCRUD
from ..people import PeopleCRUD
from ...connection import DatabaseConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data constants
TEST_BASE_ASSUMPTIONS = {
    "nest_egg_growth_rate": 7.0,
    "inflation_rate": 3.0,
    "annual_retirement_spending": 50000.0
}

async def setup_test_data() -> tuple[int, int]:
    """Create test household and person for plan tests."""
    # Create household
    households = HouseholdsCRUD()
    household_id = await households.create_household("Test Family")
    
    # Create reference person
    people = PeopleCRUD()
    person_id = await people.create_person(
        household_id=household_id,
        first_name="John",
        last_name="Doe",
        dob=date(1980, 1, 1),
        retirement_age=65,
        final_age=95
    )
    
    return household_id, person_id

async def cleanup_test_data(household_id: int):
    """Clean up test data (cascades to people and plans)."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_plan_crud():
    """Test basic CRUD operations for plans."""
    crud = PlansCRUD()
    household_id = None
    
    try:
        # Setup test data
        household_id, person_id = await setup_test_data()
        logger.info(f"Created test household {household_id} and person {person_id}")
        
        # Test Create
        logger.info("Testing plan creation...")
        plan_id = await crud.create_plan(
            household_id=household_id,
            plan_name="Test Plan",
            reference_person_id=person_id,
            base_assumptions=TEST_BASE_ASSUMPTIONS
        )
        assert plan_id is not None, "Failed to create plan"
        logger.info(f"✓ Created plan with ID: {plan_id}")
        
        # Test Read
        logger.info("Testing plan retrieval...")
        plan = await crud.get_plan(plan_id)
        assert plan is not None, "Failed to retrieve plan"
        assert plan["plan_name"] == "Test Plan", "Incorrect plan name"
        assert plan["household_id"] == household_id, "Incorrect household ID"
        assert plan["reference_person_id"] == person_id, "Incorrect reference person"
        logger.info("✓ Retrieved plan successfully")
        
        # Test Update
        logger.info("Testing plan update...")
        update_success = await crud.update_plan(
            plan_id,
            plan_name="Updated Plan Name"
        )
        assert update_success, "Failed to update plan"
        
        # Verify Update
        updated_plan = await crud.get_plan(plan_id)
        assert updated_plan["plan_name"] == "Updated Plan Name", "Update verification failed"
        logger.info("✓ Updated plan successfully")
        
        # Test List
        logger.info("Testing plans listing...")
        plans = await crud.list_plans(household_id=household_id)
        assert len(plans) > 0, "No plans found in list"
        assert any(p["plan_id"] == plan_id for p in plans), "Created plan not in list"
        logger.info(f"✓ Listed {len(plans)} plans")
        
        # Test Delete
        logger.info("Testing plan deletion...")
        delete_success = await crud.delete_plan(plan_id)
        assert delete_success, "Failed to delete plan"
        
        # Verify Deletion
        deleted_plan = await crud.get_plan(plan_id)
        assert deleted_plan is None, "Plan still exists after deletion"
        logger.info("✓ Deleted plan successfully")
        
        logger.info("All basic CRUD tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if household_id:
            await cleanup_test_data(household_id)
        await DatabaseConnection.close_connection()

async def test_plan_validation():
    """Test validation rules for plans."""
    crud = PlansCRUD()
    household_id = None
    
    try:
        # Setup test data
        household_id, person_id = await setup_test_data()
        
        # Test missing inflation rate
        logger.info("Testing missing inflation rate validation...")
        try:
            invalid_assumptions = {
                "nest_egg_growth_rate": 7.0,
                # Missing inflation_rate
                "annual_retirement_spending": 50000.0
            }
            
            await crud.create_plan(
                household_id=household_id,
                plan_name="Invalid Plan",
                reference_person_id=person_id,
                base_assumptions=invalid_assumptions
            )
            assert False, "Should have raised ValueError for missing inflation rate"
        except ValueError as e:
            logger.info("✓ Correctly rejected missing inflation rate")
        
        # Test invalid reference person (from different household)
        logger.info("Testing reference person validation...")
        other_household_id = await HouseholdsCRUD().create_household("Other Family")
        try:
            # Create person in different household
            other_person_id = await PeopleCRUD().create_person(
                household_id=other_household_id,
                first_name="Jane",
                last_name="Smith",
                dob=date(1985, 1, 1),
                retirement_age=65,
                final_age=95
            )
            
            # Try to create plan with reference person from wrong household
            await crud.create_plan(
                household_id=household_id,
                plan_name="Invalid Plan",
                reference_person_id=other_person_id,
                base_assumptions=TEST_BASE_ASSUMPTIONS
            )
            assert False, "Should have raised ValueError for invalid reference person"
        except ValueError as e:
            logger.info("✓ Correctly rejected invalid reference person")
        finally:
            # Clean up other household
            await HouseholdsCRUD().delete_household(other_household_id)
        
        logger.info("All validation tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if household_id:
            await cleanup_test_data(household_id)
        await DatabaseConnection.close_connection()

async def test_plan_relationships():
    """Test plan relationships with scenarios and assumptions."""
    crud = PlansCRUD()
    household_id = None
    
    try:
        # Setup test data
        household_id, person_id = await setup_test_data()
        plan_id = await crud.create_plan(
            household_id=household_id,
            plan_name="Test Plan",
            reference_person_id=person_id,
            base_assumptions=TEST_BASE_ASSUMPTIONS
        )
        
        # Test getting base assumptions
        logger.info("Testing base assumptions retrieval...")
        assumptions = await crud.get_plan_base_assumptions(plan_id)
        assert assumptions is not None, "Failed to get base assumptions"
        assert assumptions["nest_egg_growth_rate"] == TEST_BASE_ASSUMPTIONS["nest_egg_growth_rate"], "Incorrect growth rate"
        assert assumptions["inflation_rate"] == TEST_BASE_ASSUMPTIONS["inflation_rate"], "Incorrect inflation rate"
        assert assumptions["annual_retirement_spending"] == TEST_BASE_ASSUMPTIONS["annual_retirement_spending"], "Incorrect spending"
        logger.info("✓ Retrieved base assumptions successfully")
        
        # Test getting scenarios (empty list expected)
        logger.info("Testing scenarios retrieval...")
        scenarios = await crud.get_plan_scenarios(plan_id)
        assert isinstance(scenarios, list), "Expected list of scenarios"
        logger.info("✓ Retrieved scenarios successfully")
        
        logger.info("All relationship tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if household_id:
            await cleanup_test_data(household_id)
        await DatabaseConnection.close_connection()

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_plan_crud())
    asyncio.run(test_plan_validation())
    asyncio.run(test_plan_relationships()) 