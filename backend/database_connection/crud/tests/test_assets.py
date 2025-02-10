
# crud/tests/test_assets.py

"""
Test suite for asset CRUD operations.
Tests asset creation, ownership, categories, and growth adjustments.
"""
import asyncio
import logging
from datetime import date
from ..assets import AssetsCRUD
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

async def setup_test_data() -> tuple[int, int, int, int]:
    """Create test household, people, and plan for asset tests."""
    try:
        # Create household
        households = HouseholdsCRUD()
        household_id = await households.create_household("Test Family")

        # Create two people (for testing joint ownership)
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
        logger.error(f"Error in setup: {str(e)}")
        raise

async def cleanup_test_data(household_id: int):
    """Clean up test data (cascades to all related records)."""
    households = HouseholdsCRUD()
    await households.delete_household(household_id)

async def test_asset_categories():
    """Test asset category operations."""
    crud = AssetsCRUD()
    household_id = None
    try:
        # Setup
        household_id, _, _, _ = await setup_test_data()
        
        # Test category creation
        logger.info("Testing asset category creation...")
        category_name = "Test Category"
        category_id = await crud.create_asset_category(household_id, category_name)
        assert category_id is not None, "Failed to create asset category"
        logger.info(f"✓ Created asset category with ID: {category_id}")

        # Test category listing
        logger.info("Testing asset category listing...")
        categories = await crud.get_asset_categories(household_id)
        assert len(categories) > 0, "No categories found"
        assert any(c["category_name"] == category_name for c in categories), "Created category not found in list"
        logger.info("✓ Listed asset categories successfully")

        # Test category deletion
        logger.info("Testing asset category deletion...")
        delete_success = await crud.delete_asset_category(category_id)
        assert delete_success, "Failed to delete asset category"
        
        # Verify deletion
        categories = await crud.get_asset_categories(household_id)
        assert not any(c["asset_category_id"] == category_id for c in categories), "Category still exists after deletion"
        logger.info("✓ Deleted asset category successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_asset_crud():
    """Test basic CRUD operations for assets."""
    crud = AssetsCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, person2_id, plan_id = await setup_test_data()
        category_id = await crud.create_asset_category(household_id, "Test Category")

        # Test asset creation
        logger.info("Testing asset creation...")
        asset_data = {
            "plan_id": plan_id,
            "asset_category_id": category_id,
            "asset_name": "Test Asset",
            "value": 100000.0,
            "owner_ids": [person1_id, person2_id],  # Test joint ownership
            "include_in_nest_egg": True,
            "independent_growth_rate": 7.5
        }
        asset_id = await crud.create_asset(**asset_data)
        assert asset_id is not None, "Failed to create asset"
        logger.info(f"✓ Created asset with ID: {asset_id}")

        # Test asset retrieval
        logger.info("Testing asset retrieval...")
        asset = await crud.get_asset(asset_id)
        assert asset is not None, "Failed to retrieve asset"
        assert asset["asset_name"] == asset_data["asset_name"], "Incorrect asset name"
        assert asset["value"] == asset_data["value"], "Incorrect value"
        assert len(asset["owner_ids"]) == 2, "Incorrect number of owners"
        assert all(id in asset["owner_ids"] for id in asset_data["owner_ids"]), "Missing owners"
        logger.info("✓ Retrieved asset successfully")

        # Test asset update
        logger.info("Testing asset update...")
        new_value = 150000.0
        update_success = await crud.update_asset(
            asset_id,
            value=new_value,
            owner_ids=[person1_id]  # Test ownership update
        )
        assert update_success, "Failed to update asset"

        # Verify update
        updated_asset = await crud.get_asset(asset_id)
        assert updated_asset["value"] == new_value, "Value not updated"
        assert len(updated_asset["owner_ids"]) == 1, "Owners not updated"
        assert updated_asset["owner_ids"][0] == person1_id, "Incorrect owner after update"
        logger.info("✓ Updated asset successfully")

        # Test asset listing
        logger.info("Testing asset listing...")
        assets = await crud.list_assets(plan_id=plan_id)
        assert len(assets) > 0, "No assets found in list"
        assert any(a["asset_id"] == asset_id for a in assets), "Created asset not in list"
        logger.info("✓ Listed assets successfully")

        # Test asset deletion
        logger.info("Testing asset deletion...")
        delete_success = await crud.delete_asset(asset_id)
        assert delete_success, "Failed to delete asset"

        # Verify deletion
        deleted_asset = await crud.get_asset(asset_id)
        assert deleted_asset is None, "Asset still exists after deletion"
        logger.info("✓ Deleted asset successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_growth_adjustments():
    """Test asset growth adjustment operations."""
    crud = AssetsCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, _, plan_id = await setup_test_data()
        category_id = await crud.create_asset_category(household_id, "Test Category")
        asset_id = await crud.create_asset(
            plan_id=plan_id,
            asset_category_id=category_id,
            asset_name="Test Asset",
            value=100000.0,
            owner_ids=[person1_id]
        )

        # Test adding growth adjustment
        logger.info("Testing growth adjustment creation...")
        adjustment_data = {
            "asset_id": asset_id,
            "start_year": 2025,
            "end_year": 2027,
            "growth_rate": 8.5
        }
        adjustment_id = await crud.add_growth_adjustment(**adjustment_data)
        assert adjustment_id is not None, "Failed to create growth adjustment"
        logger.info(f"✓ Created growth adjustment with ID: {adjustment_id}")

        # Test getting adjustments
        logger.info("Testing growth adjustment retrieval...")
        adjustments = await crud.get_growth_adjustments(asset_id)
        assert len(adjustments) > 0, "No adjustments found"
        adjustment = adjustments[0]
        assert adjustment["growth_rate"] == adjustment_data["growth_rate"], "Incorrect growth rate"
        assert adjustment["start_year"] == adjustment_data["start_year"], "Incorrect start year"
        assert adjustment["end_year"] == adjustment_data["end_year"], "Incorrect end year"
        logger.info("✓ Retrieved growth adjustments successfully")

        # Test overlapping adjustment prevention
        logger.info("Testing overlapping adjustment prevention...")
        try:
            await crud.add_growth_adjustment(
                asset_id=asset_id,
                start_year=2026,  # Overlaps with existing adjustment
                end_year=2028,
                growth_rate=7.0
            )
            assert False, "Should have prevented overlapping adjustment"
        except ValueError:
            logger.info("✓ Successfully prevented overlapping adjustment")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

async def test_validation():
    """Test asset validation rules."""
    crud = AssetsCRUD()
    household_id = None
    try:
        # Setup
        household_id, person1_id, _, plan_id = await setup_test_data()
        category_id = await crud.create_asset_category(household_id, "Test Category")

        # Test negative value prevention
        logger.info("Testing negative value prevention...")
        try:
            await crud.create_asset(
                plan_id=plan_id,
                asset_category_id=category_id,
                asset_name="Invalid Asset",
                value=-1000.0,  # Invalid
                owner_ids=[person1_id]
            )
            assert False, "Should have prevented negative value"
        except ValueError:
            logger.info("✓ Successfully prevented negative value")

        # Test growth rate range validation
        logger.info("Testing growth rate range validation...")
        try:
            await crud.create_asset(
                plan_id=plan_id,
                asset_category_id=category_id,
                asset_name="Invalid Asset",
                value=1000.0,
                owner_ids=[person1_id],
                independent_growth_rate=250.0  # Invalid
            )
            assert False, "Should have prevented invalid growth rate"
        except ValueError:
            logger.info("✓ Successfully prevented invalid growth rate")

        # Test owner validation
        logger.info("Testing owner validation...")
        try:
            await crud.create_asset(
                plan_id=plan_id,
                asset_category_id=category_id,
                asset_name="Invalid Asset",
                value=1000.0,
                owner_ids=[999999]  # Non-existent owner
            )
            assert False, "Should have prevented invalid owner"
        except ValueError:
            logger.info("✓ Successfully prevented invalid owner")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        if household_id:
            await cleanup_test_data(household_id)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(test_asset_categories())
    asyncio.run(test_asset_crud())
    asyncio.run(test_growth_adjustments())
    asyncio.run(test_validation())