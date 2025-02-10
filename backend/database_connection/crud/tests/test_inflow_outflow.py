
# tests/test_inflows_outflows.py

"""
Test suite for inflow/outflow CRUD operations.
"""
import asyncio
import logging
from datetime import date
from typing import Tuple
from ..inflows_outflows import InflowsOutflowsCRUD
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

async def setup_test_data() -> Tuple[int, int]:
    """Create test household, person, and plan for inflow/outflow tests."""
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
        logger.error(f"Error in test setup: {str(e)}")
        raise

async def cleanup_test_data(household_id: int):
    """Clean up test data through cascading delete."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_create_inflow_outflow():
    """Test basic creation of inflow/outflow entries."""
    crud = InflowsOutflowsCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()

        # Test inflow creation
        logger.info("Testing inflow creation...")
        inflow_data = {
            "plan_id": plan_id,
            "type": "INFLOW",
            "name": "Test Salary",
            "annual_amount": 75000.0,
            "start_year": 2025,
            "end_year": 2030,
            "apply_inflation": True
        }
        inflow_id = await crud.create_inflow_outflow(**inflow_data)
        assert inflow_id is not None, "Failed to create inflow"

        # Verify inflow
        inflow = await crud.get_inflow_outflow(inflow_id)
        assert inflow is not None, "Failed to retrieve inflow"
        assert inflow["type"] == "INFLOW", "Incorrect type"
        assert inflow["name"] == inflow_data["name"], "Incorrect name"
        assert inflow["annual_amount"] == inflow_data["annual_amount"], "Incorrect amount"
        assert inflow["apply_inflation"] == inflow_data["apply_inflation"], "Incorrect inflation flag"
        logger.info("✓ Created and verified inflow successfully")

        # Test outflow creation
        logger.info("Testing outflow creation...")
        outflow_data = {
            "plan_id": plan_id,
            "type": "OUTFLOW",
            "name": "Test Expense",
            "annual_amount": 25000.0,
            "start_year": 2025,
            "end_year": 2025,  # One-time expense
            "apply_inflation": False
        }
        outflow_id = await crud.create_inflow_outflow(**outflow_data)
        assert outflow_id is not None, "Failed to create outflow"

        # Verify outflow
        outflow = await crud.get_inflow_outflow(outflow_id)
        assert outflow is not None, "Failed to retrieve outflow"
        assert outflow["type"] == "OUTFLOW", "Incorrect type"
        assert outflow["name"] == outflow_data["name"], "Incorrect name"
        assert outflow["annual_amount"] == outflow_data["annual_amount"], "Incorrect amount"
        assert outflow["apply_inflation"] == outflow_data["apply_inflation"], "Incorrect inflation flag"
        logger.info("✓ Created and verified outflow successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_create_inflow_outflow_invalid():
    """Test validation rules for inflow/outflow creation."""
    crud = InflowsOutflowsCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()

        # Test invalid type
        logger.info("Testing invalid type validation...")
        try:
            await crud.create_inflow_outflow(
                plan_id=plan_id,
                type="INVALID",  # Invalid type
                name="Test Invalid",
                annual_amount=1000.0,
                start_year=2025,
                end_year=2026
            )
            assert False, "Should have rejected invalid type"
        except ValueError:
            logger.info("✓ Correctly rejected invalid type")

        # Test invalid year range
        logger.info("Testing invalid year range validation...")
        try:
            await crud.create_inflow_outflow(
                plan_id=plan_id,
                type="INFLOW",
                name="Test Invalid",
                annual_amount=1000.0,
                start_year=2026,
                end_year=2025  # Invalid: end before start
            )
            assert False, "Should have rejected invalid year range"
        except ValueError:
            logger.info("✓ Correctly rejected invalid year range")

        # Test invalid plan ID
        logger.info("Testing invalid plan ID validation...")
        try:
            await crud.create_inflow_outflow(
                plan_id=999999,  # Invalid plan_id
                type="INFLOW",
                name="Test Invalid",
                annual_amount=1000.0,
                start_year=2025,
                end_year=2026
            )
            assert False, "Should have rejected invalid plan ID"
        except ValueError:
            logger.info("✓ Correctly rejected invalid plan ID")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_update_inflow_outflow():
    """Test updating inflow/outflow entries."""
    crud = InflowsOutflowsCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()
        inflow_id = await crud.create_inflow_outflow(
            plan_id=plan_id,
            type="INFLOW",
            name="Test Income",
            annual_amount=50000.0,
            start_year=2025,
            end_year=2030
        )

        # Test partial update
        logger.info("Testing partial update...")
        new_amount = 55000.0
        success = await crud.update_inflow_outflow(
            inflow_id,
            annual_amount=new_amount
        )
        assert success, "Failed to update inflow"

        # Verify update
        updated = await crud.get_inflow_outflow(inflow_id)
        assert updated["annual_amount"] == new_amount, "Amount not updated"
        assert updated["name"] == "Test Income", "Name changed unexpectedly"
        logger.info("✓ Partial update successful")

        # Test full update
        logger.info("Testing full update...")
        update_data = {
            "type": "OUTFLOW",
            "name": "Updated Entry",
            "annual_amount": 60000.0,
            "start_year": 2026,
            "end_year": 2031,
            "apply_inflation": True
        }
        success = await crud.update_inflow_outflow(inflow_id, **update_data)
        assert success, "Failed to perform full update"

        # Verify full update
        updated = await crud.get_inflow_outflow(inflow_id)
        assert updated["type"] == update_data["type"], "Type not updated"
        assert updated["name"] == update_data["name"], "Name not updated"
        assert updated["annual_amount"] == update_data["annual_amount"], "Amount not updated"
        assert updated["start_year"] == update_data["start_year"], "Start year not updated"
        assert updated["end_year"] == update_data["end_year"], "End year not updated"
        assert updated["apply_inflation"] == update_data["apply_inflation"], "Inflation flag not updated"
        logger.info("✓ Full update successful")

        # Test invalid updates
        logger.info("Testing invalid updates...")
        try:
            await crud.update_inflow_outflow(
                inflow_id,
                start_year=2030,
                end_year=2025  # Invalid range
            )
            assert False, "Should have rejected invalid year range"
        except ValueError:
            logger.info("✓ Correctly rejected invalid year range")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_delete_inflow_outflow():
    """Test deleting inflow/outflow entries."""
    crud = InflowsOutflowsCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()
        inflow_id = await crud.create_inflow_outflow(
            plan_id=plan_id,
            type="INFLOW",
            name="Test Income",
            annual_amount=50000.0,
            start_year=2025,
            end_year=2030
        )

        # Test deletion
        logger.info("Testing entry deletion...")
        success = await crud.delete_inflow_outflow(inflow_id)
        assert success, "Failed to delete entry"

        # Verify deletion
        deleted = await crud.get_inflow_outflow(inflow_id)
        assert deleted is None, "Entry still exists after deletion"
        logger.info("✓ Deleted entry successfully")

        # Test deletion of non-existent entry
        logger.info("Testing non-existent entry deletion...")
        success = await crud.delete_inflow_outflow(999999)
        assert not success, "Should return False for non-existent entry"
        logger.info("✓ Correctly handled non-existent entry deletion")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_list_inflows_outflows():
    """Test listing inflow/outflow entries with filters."""
    crud = InflowsOutflowsCRUD()
    household_id = None
    try:
        # Setup
        household_id, plan_id = await setup_test_data()

        # Create multiple entries
        logger.info("Creating test entries...")
        entries = [
            {
                "plan_id": plan_id,
                "type": "INFLOW",
                "name": "Salary",
                "annual_amount": 75000.0,
                "start_year": 2025,
                "end_year": 2030
            },
            {
                "plan_id": plan_id,
                "type": "OUTFLOW",
                "name": "Expense",
                "annual_amount": 25000.0,
                "start_year": 2025,
                "end_year": 2025
            },
            {
                "plan_id": plan_id,
                "type": "INFLOW",
                "name": "Bonus",
                "annual_amount": 10000.0,
                "start_year": 2026,
                "end_year": 2026
            }
        ]
        for entry in entries:
            await crud.create_inflow_outflow(**entry)

        # Test basic listing
        logger.info("Testing basic listing...")
        all_entries = await crud.list_inflows_outflows(plan_id=plan_id)
        assert len(all_entries) == 3, "Incorrect number of entries"
        logger.info("✓ Listed all entries successfully")

        # Test type filter
        logger.info("Testing type filter...")
        inflows = await crud.list_inflows_outflows(plan_id=plan_id, type="INFLOW")
        assert len(inflows) == 2, "Incorrect number of inflows"
        assert all(e["type"] == "INFLOW" for e in inflows), "Non-inflow in filtered list"
        logger.info("✓ Type filter working correctly")

        # Test year filter
        logger.info("Testing year filter...")
        year_2026 = await crud.list_inflows_outflows(
            plan_id=plan_id,
            start_year=2026
        )
        assert len(year_2026) == 2, "Incorrect number of entries for 2026"
        logger.info("✓ Year filter working correctly")

        # Test cash flow grouping
        logger.info("Testing cash flow grouping...")
        cash_flows = await crud.get_plan_cash_flows(plan_id)
        assert len(cash_flows["inflows"]) == 2, "Incorrect number of inflows"
        assert len(cash_flows["outflows"]) == 1, "Incorrect number of outflows"
        logger.info("✓ Cash flow grouping working correctly")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_create_inflow_outflow())
    asyncio.run(test_create_inflow_outflow_invalid())
    asyncio.run(test_update_inflow_outflow())
    asyncio.run(test_delete_inflow_outflow())
    asyncio.run(test_list_inflows_outflows())