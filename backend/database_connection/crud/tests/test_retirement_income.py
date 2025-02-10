# tests/test_retirement_income.py

"""
Test suite for retirement income CRUD operations.
Tests creation, updates, and ownership management.
"""
import asyncio
import logging
from datetime import date
from typing import Tuple
from ..retirement_income import RetirementIncomeCRUD
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

async def setup_test_data() -> Tuple[int, int, int, int]:
    """Create test household, people, and plan for retirement income tests."""
    try:
        # Create household
        households = HouseholdsCRUD()
        household_id = await households.create_household("Test Family")

        # Create two people for testing joint benefits
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

        return household_id, person1_id, person2_id, plan_id
    except Exception as e:
        logger.error(f"Error in test setup: {str(e)}")
        raise

async def cleanup_test_data(household_id: int):
    """Clean up test data through cascading delete."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_create_retirement_income():
    """Test creating retirement income plans with owners."""
    crud = RetirementIncomeCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, person2_id, plan_id = await setup_test_data()

        # Test single owner creation
        logger.info("Testing single owner income creation...")
        single_owner_data = {
            "plan_id": plan_id,
            "name": "Social Security",
            "annual_income": 30000.0,
            "start_age": 67,
            "end_age": None,  # Lifetime benefit
            "owner_ids": [person1_id],
            "apply_inflation": True
        }
        income_id = await crud.create_retirement_income(**single_owner_data)
        assert income_id is not None, "Failed to create income plan"

        # Verify creation
        income = await crud.get_retirement_income(income_id)
        assert income is not None, "Failed to retrieve income plan"
        assert income["name"] == single_owner_data["name"], "Incorrect name"
        assert income["annual_income"] == single_owner_data["annual_income"], "Incorrect amount"
        assert len(income["owner_ids"]) == 1, "Incorrect number of owners"
        assert income["owner_ids"][0] == person1_id, "Incorrect owner"
        logger.info("✓ Created single owner income successfully")

        # Test joint benefit creation
        logger.info("Testing joint benefit creation...")
        joint_data = {
            "plan_id": plan_id,
            "name": "Joint Pension",
            "annual_income": 50000.0,
            "start_age": 65,
            "end_age": 90,
            "owner_ids": [person1_id, person2_id],
            "apply_inflation": False
        }
        joint_id = await crud.create_retirement_income(**joint_data)
        assert joint_id is not None, "Failed to create joint benefit"

        # Verify joint benefit
        joint = await crud.get_retirement_income(joint_id)
        assert joint is not None, "Failed to retrieve joint benefit"
        assert len(joint["owner_ids"]) == 2, "Incorrect number of joint owners"
        assert set(joint["owner_ids"]) == {person1_id, person2_id}, "Incorrect joint owners"
        logger.info("✓ Created joint benefit successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_create_retirement_income_invalid():
    """Test validation rules for retirement income creation."""
    crud = RetirementIncomeCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, _, plan_id = await setup_test_data()

        # Test negative income
        logger.info("Testing negative income validation...")
        try:
            await crud.create_retirement_income(
                plan_id=plan_id,
                name="Invalid Income",
                annual_income=-1000.0,  # Invalid
                start_age=65,
                end_age=90,
                owner_ids=[person1_id]
            )
            assert False, "Should have rejected negative income"
        except ValueError:
            logger.info("✓ Correctly rejected negative income")

        # Test invalid age range
        logger.info("Testing invalid age range validation...")
        try:
            await crud.create_retirement_income(
                plan_id=plan_id,
                name="Invalid Ages",
                annual_income=1000.0,
                start_age=70,
                end_age=65,  # Invalid: before start_age
                owner_ids=[person1_id]
            )
            assert False, "Should have rejected invalid age range"
        except ValueError:
            logger.info("✓ Correctly rejected invalid age range")

        # Test no owners
        logger.info("Testing no owners validation...")
        try:
            await crud.create_retirement_income(
                plan_id=plan_id,
                name="No Owners",
                annual_income=1000.0,
                start_age=65,
                end_age=90,
                owner_ids=[]  # Invalid: empty list
            )
            assert False, "Should have rejected empty owner list"
        except ValueError:
            logger.info("✓ Correctly rejected empty owner list")

        # Test invalid owner
        logger.info("Testing invalid owner validation...")
        try:
            await crud.create_retirement_income(
                plan_id=plan_id,
                name="Invalid Owner",
                annual_income=1000.0,
                start_age=65,
                end_age=90,
                owner_ids=[999999]  # Invalid owner_id
            )
            assert False, "Should have rejected invalid owner"
        except ValueError:
            logger.info("✓ Correctly rejected invalid owner")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_update_retirement_income():
    """Test updating retirement income plans."""
    crud = RetirementIncomeCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, person2_id, plan_id = await setup_test_data()
        income_id = await crud.create_retirement_income(
            plan_id=plan_id,
            name="Test Income",
            annual_income=30000.0,
            start_age=65,
            end_age=90,
            owner_ids=[person1_id]
        )

        # Test partial update
        logger.info("Testing partial update...")
        new_amount = 35000.0
        success = await crud.update_retirement_income(
            income_id,
            annual_income=new_amount
        )
        assert success, "Failed to update income"

        # Verify partial update
        updated = await crud.get_retirement_income(income_id)
        assert updated["annual_income"] == new_amount, "Amount not updated"
        assert updated["name"] == "Test Income", "Name changed unexpectedly"
        logger.info("✓ Partial update successful")

        # Test full update with owner change
        logger.info("Testing full update with owner change...")
        update_data = {
            "name": "Updated Income",
            "annual_income": 40000.0,
            "start_age": 67,
            "end_age": None,  # Change to lifetime benefit
            "owner_ids": [person1_id, person2_id],  # Add joint owner
            "apply_inflation": True
        }
        success = await crud.update_retirement_income(income_id, **update_data)
        assert success, "Failed to perform full update"

        # Verify full update
        updated = await crud.get_retirement_income(income_id)
        assert updated["name"] == update_data["name"], "Name not updated"
        assert updated["annual_income"] == update_data["annual_income"], "Amount not updated"
        assert updated["start_age"] == update_data["start_age"], "Start age not updated"
        assert updated["end_age"] == update_data["end_age"], "End age not updated"
        assert len(updated["owner_ids"]) == 2, "Owners not updated"
        assert set(updated["owner_ids"]) == set(update_data["owner_ids"]), "Incorrect owners"
        logger.info("✓ Full update successful")

        # Test invalid updates
        logger.info("Testing invalid updates...")
        try:
            await crud.update_retirement_income(
                income_id,
                start_age=70,
                end_age=65  # Invalid: end before start
            )
            assert False, "Should have rejected invalid age range"
        except ValueError:
            logger.info("✓ Correctly rejected invalid age range")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_delete_retirement_income():
    """Test deleting retirement income plans."""
    crud = RetirementIncomeCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, person2_id, plan_id = await setup_test_data()
        income_id = await crud.create_retirement_income(
            plan_id=plan_id,
            name="Test Income",
            annual_income=30000.0,
            start_age=65,
            end_age=90,
            owner_ids=[person1_id, person2_id]  # Test with multiple owners
        )

        # Test deletion
        logger.info("Testing income plan deletion...")
        success = await crud.delete_retirement_income(income_id)
        assert success, "Failed to delete income plan"

        # Verify deletion
        deleted = await crud.get_retirement_income(income_id)
        assert deleted is None, "Income plan still exists after deletion"

        # Verify owner records deleted
        async with DatabaseConnection.connection() as conn:
            async with conn.execute(
                "SELECT COUNT(*) FROM retirement_income_owners WHERE income_plan_id = ?",
                (income_id,)
            ) as cursor:
                count = (await cursor.fetchone())[0]
                assert count == 0, "Owner records not deleted"
        logger.info("✓ Deleted income plan and owner records successfully")

        # Test deletion of non-existent plan
        logger.info("Testing non-existent plan deletion...")
        success = await crud.delete_retirement_income(999999)
        assert not success, "Should return False for non-existent plan"
        logger.info("✓ Correctly handled non-existent plan deletion")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_list_retirement_income():
    """Test listing retirement income plans with filters."""
    crud = RetirementIncomeCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, person2_id, plan_id = await setup_test_data()

        # Create multiple income plans
        logger.info("Creating test income plans...")
        plans = [
            {
                "plan_id": plan_id,
                "name": "Social Security 1",
                "annual_income": 30000.0,
                "start_age": 67,
                "end_age": None,
                "owner_ids": [person1_id]
            },
            {
                "plan_id": plan_id,
                "name": "Joint Pension",
                "annual_income": 50000.0,
                "start_age": 65,
                "end_age": 90,
                "owner_ids": [person1_id, person2_id]
            },
            {
                "plan_id": plan_id,
                "name": "Social Security 2",
                "annual_income": 25000.0,
                "start_age": 67,
                "end_age": None,
                "owner_ids": [person2_id]
            }
        ]
        for plan_data in plans:
            await crud.create_retirement_income(**plan_data)

        # Test basic listing
        logger.info("Testing basic listing...")
        all_plans = await crud.list_retirement_income(plan_id=plan_id)
        assert len(all_plans) == 3, "Incorrect number of plans"
        logger.info("✓ Listed all plans successfully")

        # Test person filter
        logger.info("Testing person filter...")
        person1_plans = await crud.list_retirement_income(
            plan_id=plan_id,
            person_id=person1_id
        )
        assert len(person1_plans) == 2, "Incorrect number of plans for person1"
        person2_plans = await crud.list_retirement_income(
            plan_id=plan_id,
            person_id=person2_id
        )
        assert len(person2_plans) == 2, "Incorrect number of plans for person2"
        logger.info("✓ Person filter working correctly")

        # Test owner information
        logger.info("Testing owner information...")
        joint_plans = [p for p in all_plans if len(p["owner_ids"]) > 1]
        assert len(joint_plans) == 1, "Incorrect number of joint plans"
        assert len(joint_plans[0]["owner_ids"]) == 2, "Incorrect number of joint owners"
        logger.info("✓ Owner information correct")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_create_retirement_income())
    asyncio.run(test_create_retirement_income_invalid())
    asyncio.run(test_update_retirement_income())
    asyncio.run(test_delete_retirement_income())
    asyncio.run(test_list_retirement_income())