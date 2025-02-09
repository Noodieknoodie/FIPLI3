"""
Test suite for people CRUD operations.
"""

import asyncio
import logging
from datetime import date, datetime
from ..people import PeopleCRUD
from ..households import HouseholdsCRUD
from ...connection import DatabaseConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_test_household() -> int:
    """Create a test household for person tests."""
    households = HouseholdsCRUD()
    return await households.create_household("Test Family")

async def cleanup_test_household(household_id: int):
    """Clean up the test household."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_person_crud():
    """Test basic CRUD operations for people."""
    crud = PeopleCRUD()
    household_id = None
    
    try:
        # Setup test household
        household_id = await setup_test_household()
        logger.info(f"Created test household with ID: {household_id}")
        
        # Test data
        test_data = {
            "first_name": "John",
            "last_name": "Doe",
            "dob": date(1980, 1, 1),
            "retirement_age": 65,
            "final_age": 95
        }
        
        # Test Create
        logger.info("Testing person creation...")
        person_id = await crud.create_person(
            household_id=household_id,
            **test_data
        )
        assert person_id is not None, "Failed to create person"
        logger.info(f"✓ Created person with ID: {person_id}")
        
        # Test Read
        logger.info("Testing person retrieval...")
        person = await crud.get_person(person_id)
        assert person is not None, "Failed to retrieve person"
        assert person["first_name"] == test_data["first_name"], "Incorrect first name"
        assert person["last_name"] == test_data["last_name"], "Incorrect last name"
        assert datetime.fromisoformat(person["dob"]).date() == test_data["dob"], "Incorrect DOB"
        logger.info("✓ Retrieved person successfully")
        
        # Test Update
        logger.info("Testing person update...")
        update_data = {
            "first_name": "Jane",
            "retirement_age": 67
        }
        update_success = await crud.update_person(
            person_id,
            first_name=update_data["first_name"],
            retirement_age=update_data["retirement_age"]
        )
        assert update_success, "Failed to update person"
        
        # Verify Update
        updated_person = await crud.get_person(person_id)
        assert updated_person["first_name"] == update_data["first_name"], "Update first name failed"
        assert updated_person["retirement_age"] == update_data["retirement_age"], "Update retirement age failed"
        assert updated_person["last_name"] == test_data["last_name"], "Last name changed unexpectedly"
        logger.info("✓ Updated person successfully")
        
        # Test List
        logger.info("Testing people listing...")
        people = await crud.list_people(household_id=household_id)
        assert len(people) > 0, "No people found in list"
        assert any(p["person_id"] == person_id for p in people), "Created person not in list"
        logger.info(f"✓ Listed {len(people)} people")
        
        # Test Delete
        logger.info("Testing person deletion...")
        delete_success = await crud.delete_person(person_id)
        assert delete_success, "Failed to delete person"
        
        # Verify Deletion
        deleted_person = await crud.get_person(person_id)
        assert deleted_person is None, "Person still exists after deletion"
        logger.info("✓ Deleted person successfully")
        
        logger.info("All basic CRUD tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if household_id:
            await cleanup_test_household(household_id)
        await DatabaseConnection.close_connection()

async def test_person_validation():
    """Test validation rules for people."""
    crud = PeopleCRUD()
    household_id = None
    
    try:
        # Setup test household
        household_id = await setup_test_household()
        
        # Test invalid retirement age
        logger.info("Testing invalid retirement age validation...")
        try:
            await crud.create_person(
                household_id=household_id,
                first_name="Test",
                last_name="Person",
                dob=date(1980, 1, 1),
                retirement_age=0,  # Invalid
                final_age=90
            )
            assert False, "Should have raised ValueError for invalid retirement age"
        except ValueError as e:
            logger.info("✓ Correctly rejected invalid retirement age")
        
        # Test invalid final age relationship
        logger.info("Testing retirement/final age relationship validation...")
        try:
            await crud.create_person(
                household_id=household_id,
                first_name="Test",
                last_name="Person",
                dob=date(1980, 1, 1),
                retirement_age=70,
                final_age=65  # Invalid: less than retirement age
            )
            assert False, "Should have raised ValueError for invalid age relationship"
        except ValueError as e:
            logger.info("✓ Correctly rejected invalid age relationship")
        
        logger.info("All validation tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if household_id:
            await cleanup_test_household(household_id)
        await DatabaseConnection.close_connection()

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_person_crud())
    asyncio.run(test_person_validation()) 