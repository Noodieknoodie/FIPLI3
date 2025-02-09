"""
Test suite for households CRUD operations.
"""

import asyncio
import logging
from ..households import HouseholdsCRUD
from ...connection import DatabaseConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_households_crud():
    """Test basic CRUD operations for households."""
    crud = HouseholdsCRUD()
    test_household_name = "Test Family"
    updated_name = "Updated Family Name"
    
    try:
        # Test Create
        logger.info("Testing household creation...")
        household_id = await crud.create_household(test_household_name)
        assert household_id is not None, "Failed to create household"
        logger.info(f"✓ Created household with ID: {household_id}")
        
        # Test Read
        logger.info("Testing household retrieval...")
        household = await crud.get_household(household_id)
        assert household is not None, "Failed to retrieve household"
        assert household["household_name"] == test_household_name, "Incorrect household name"
        logger.info("✓ Retrieved household successfully")
        
        # Test Update
        logger.info("Testing household update...")
        update_success = await crud.update_household(household_id, updated_name)
        assert update_success, "Failed to update household"
        
        # Verify Update
        updated_household = await crud.get_household(household_id)
        assert updated_household["household_name"] == updated_name, "Update verification failed"
        logger.info("✓ Updated household successfully")
        
        # Test List
        logger.info("Testing households listing...")
        households = await crud.list_households()
        assert len(households) > 0, "No households found in list"
        logger.info(f"✓ Listed {len(households)} households")
        
        # Test Delete
        logger.info("Testing household deletion...")
        delete_success = await crud.delete_household(household_id)
        assert delete_success, "Failed to delete household"
        
        # Verify Deletion
        deleted_household = await crud.get_household(household_id)
        assert deleted_household is None, "Household still exists after deletion"
        logger.info("✓ Deleted household successfully")
        
        logger.info("All household CRUD tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Clean up
        await DatabaseConnection.close_connection()

if __name__ == "__main__":
    asyncio.run(test_households_crud()) 