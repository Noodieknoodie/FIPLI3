"""
CRUD operations for households table.
"""

from typing import Dict, Any, List, Optional
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class HouseholdsCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("households")
        self.id_field = "household_id"
    
    async def create_household(self, household_name: str) -> int:
        """
        Create a new household with the given name.
        Returns the household_id of the created record.
        """
        try:
            data = {"household_name": household_name}
            return await self.create(data)
        except Exception as e:
            logger.error(f"Error creating household: {str(e)}")
            raise
    
    async def get_household(self, household_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a household by ID.
        Returns None if not found.
        """
        return await self.read(household_id, self.id_field)
    
    async def update_household(self, household_id: int, household_name: str) -> bool:
        """
        Update a household's name.
        Returns True if successful, False if household not found.
        """
        try:
            data = {"household_name": household_name}
            return await self.update(household_id, data, self.id_field)
        except Exception as e:
            logger.error(f"Error updating household: {str(e)}")
            raise
    
    async def delete_household(self, household_id: int) -> bool:
        """
        Delete a household and all related records (cascading delete).
        Returns True if successful, False if household not found.
        """
        return await self.delete(household_id, self.id_field)
    
    async def list_households(
        self,
        order_by: str = "household_name",
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all households with optional pagination.
        """
        return await self.list(order_by=order_by, limit=limit, offset=offset)
    
    async def get_household_members(self, household_id: int) -> List[Dict[str, Any]]:
        """
        Get all members of a household.
        """
        try:
            query = """
                SELECT p.* 
                FROM people p 
                WHERE p.household_id = ?
                ORDER BY p.last_name, p.first_name
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (household_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting household members: {str(e)}")
            raise
    
    async def get_household_plans(self, household_id: int) -> List[Dict[str, Any]]:
        """
        Get all financial plans associated with a household.
        """
        try:
            query = """
                SELECT p.*, 
                       pe.first_name || ' ' || pe.last_name as reference_person_name
                FROM plans p
                JOIN people pe ON p.reference_person_id = pe.person_id
                WHERE p.household_id = ?
                ORDER BY p.plan_name
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (household_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting household plans: {str(e)}")
            raise 