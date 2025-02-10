# crud/tests/test_liabilities.py

"""
Test suite for liability CRUD operations.
Tests liability creation, updates, and category management.
"""
import asyncio
import logging
from datetime import date
from ..liabilities import LiabilitiesCRUD
from ..households import HouseholdsCRUD
from ..people import PeopleCRUD
from ..plans import PlansCRUD
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

async def setup_test_data() -> tuple[int, int]:
    """Create test household, person, and plan for liability tests."""
    try:
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

        # Create plan
        plans = PlansCRUD()
        plan_id = await plans.create_plan(
            household_id=household_id,
            plan_name="Test Plan",
            reference_person_id=person_id,
            base_assumptions=TEST_BASE_ASSUMPTIONS
        )

        return household_id, plan_id
    except Exception as e:
        logger.error(f"Error in setup: {str(e)}")
        raise

async def cleanup_test_data(household_id: int):
    """Clean up test data (cascades to all related records)."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_liability_categories():
    """Test liability category operations."""
    crud = LiabilitiesCRUD()
    household_id = None
    try:
        # Setup
        household_id, _ = await setup_test_data()
        
        # Test category creation
        logger.info("Testing liability category creation...")
        category_name = "Test Category"
        category_id = await crud.create_liability_category(household_id, category_name)
        assert category_id is not None, "Failed to create liability category"
        logger.info(f"✓ Created liability category with ID: {category_id}")

        # Test category listing
        logger.info("Testing liability category listing...")
        categories = await crud.get_liability_categories(household_id)
        assert len(categories) > 0, "No categories found"
        assert any(c["category_name"] == category_name for c in categories), "Created category not found in list"
        logger.info("✓ Listed liability categories successfully")

        # Test category deletion
        logger.info("Testing liability category deletion...")
        delete_success = await crud.delete_liability_category(category_id)
        assert delete_success, "Failed to delete liability category"
        
        # Verify deletion
        categories = await crud.get_liability_categories(household_id)
        assert not any(c["liability_category_id"] == category_id for c in categories), "Category still exists after deletion"
        logger.info("✓ Deleted liability category successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_liability_crud():
    """Test basic CRUD operations for liabilities."""
    crud = LiabilitiesCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()
        category_id = await crud.create_liability_category(household_id, "Test Category")

        # Test liability creation
        logger.info("Testing liability creation...")
        liability_data = {
            "plan_id": plan_id,
            "liability_category_id": category_id,
            "liability_name": "Test Liability",
            "value": 250000.0,
            "interest_rate": 4.5,
            "include_in_nest_egg": True
        }
        liability_id = await crud.create_liability(**liability_data)
        assert liability_id is not None, "Failed to create liability"
        logger.info(f"✓ Created liability with ID: {liability_id}")

        # Test liability retrieval
        logger.info("Testing liability retrieval...")
        liability = await crud.get_liability(liability_id)
        assert liability is not None, "Failed to retrieve liability"
        assert liability["liability_name"] == liability_data["liability_name"], "Incorrect liability name"
        assert liability["value"] == liability_data["value"], "Incorrect value"
        assert liability["interest_rate"] == liability_data["interest_rate"], "Incorrect interest rate"
        logger.info("✓ Retrieved liability successfully")

        # Test liability update
        logger.info("Testing liability update...")
        new_value = 200000.0
        new_rate = 4.0
        update_success = await crud.update_liability(
            liability_id,
            value=new_value,
            interest_rate=new_rate
        )
        assert update_success, "Failed to update liability"

        # Verify update
        updated_liability = await crud.get_liability(liability_id)
        assert updated_liability["value"] == new_value, "Value not updated"
        assert updated_liability["interest_rate"] == new_rate, "Interest rate not updated"
        logger.info("✓ Updated liability successfully")

        # Test liability listing
        logger.info("Testing liability listing...")
        liabilities = await crud.list_liabilities(plan_id=plan_id)
        assert len(liabilities) > 0, "No liabilities found in list"
        assert any(l["liability_id"] == liability_id for l in liabilities), "Created liability not in list"
        logger.info("✓ Listed liabilities successfully")

        # Test liability deletion
        logger.info("Testing liability deletion...")
        delete_success = await crud.delete_liability(liability_id)
        assert delete_success, "Failed to delete liability"

        # Verify deletion
        deleted_liability = await crud.get_liability(liability_id)
        assert deleted_liability is None, "Liability still exists after deletion"
        logger.info("✓ Deleted liability successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_validation():
    """Test liability validation rules."""
    crud = LiabilitiesCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()
        category_id = await crud.create_liability_category(household_id, "Test Category")

        # Test negative value prevention
        logger.info("Testing negative value prevention...")
        try:
            await crud.create_liability(
                plan_id=plan_id,
                liability_category_id=category_id,
                liability_name="Invalid Liability",
                value=-1000.0,  # Invalid
                interest_rate=4.5
            )
            assert False, "Should have prevented negative value"
        except ValueError:
            logger.info("✓ Successfully prevented negative value")

        # Test interest rate range validation
        logger.info("Testing interest rate range validation...")
        try:
            await crud.create_liability(
                plan_id=plan_id,
                liability_category_id=category_id,
                liability_name="Invalid Liability",
                value=1000.0,
                interest_rate=250.0  # Invalid
            )
            assert False, "Should have prevented invalid interest rate"
        except ValueError:
            logger.info("✓ Successfully prevented invalid interest rate")

        # Test category existence validation
        logger.info("Testing category validation...")
        try:
            await crud.create_liability(
                plan_id=plan_id,
                liability_category_id=999999,  # Non-existent category
                liability_name="Invalid Liability",
                value=1000.0,
                interest_rate=4.5
            )
            assert False, "Should have prevented invalid category"
        except Exception:
            logger.info("✓ Successfully prevented invalid category")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_liability_categories())
    asyncio.run(test_liability_crud())
    asyncio.run(test_validation())