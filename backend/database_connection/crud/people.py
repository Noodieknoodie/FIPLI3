"""
CRUD operations for people table.
Handles person records and their relationships with households, assets, and retirement income.
"""

from typing import Dict, Any, List, Optional
from datetime import date
from .base_crud import BaseCRUD
from ..connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class PeopleCRUD(BaseCRUD):
    def __init__(self):
        super().__init__("people")
        self.id_field = "person_id"
    
    async def create_person(
        self,
        household_id: int,
        first_name: str,
        last_name: str,
        dob: date,
        retirement_age: int,
        final_age: int
    ) -> int:
        """
        Create a new person record.
        
        Args:
            household_id: ID of the household this person belongs to
            first_name: Person's first name
            last_name: Person's last name
            dob: Date of birth
            retirement_age: Age at which the person plans to retire
            final_age: Final age for financial projections
            
        Returns:
            The ID of the created person record
            
        Raises:
            ValueError: If retirement_age >= final_age
            ValueError: If either age is <= 0
        """
        # Validate ages according to business rules
        if retirement_age <= 0 or final_age <= 0:
            raise ValueError("Retirement age and final age must be positive")
        if retirement_age >= final_age:
            raise ValueError("Final age must be greater than retirement age")
            
        try:
            data = {
                "household_id": household_id,
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob.isoformat(),
                "retirement_age": retirement_age,
                "final_age": final_age
            }
            return await self.create(data)
        except Exception as e:
            logger.error(f"Error creating person record: {str(e)}")
            raise
    
    async def get_person(self, person_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a person's details by ID.
        Returns None if not found.
        """
        return await self.read(person_id, self.id_field)
    
    async def update_person(
        self,
        person_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        retirement_age: Optional[int] = None,
        final_age: Optional[int] = None
    ) -> bool:
        """
        Update a person's details.
        Only updates the fields that are provided (not None).
        
        Args:
            person_id: ID of the person to update
            first_name: New first name (optional)
            last_name: New last name (optional)
            retirement_age: New retirement age (optional)
            final_age: New final age (optional)
            
        Returns:
            True if successful, False if person not found
            
        Raises:
            ValueError: If retirement_age >= final_age
            ValueError: If either age is <= 0
        """
        try:
            # Get current data to validate age changes
            current_data = await self.get_person(person_id)
            if not current_data:
                return False
                
            # Build update data
            data = {}
            if first_name is not None:
                data["first_name"] = first_name
            if last_name is not None:
                data["last_name"] = last_name
                
            # Handle retirement age update
            effective_retirement_age = retirement_age if retirement_age is not None else current_data["retirement_age"]
            effective_final_age = final_age if final_age is not None else current_data["final_age"]
            
            # Validate ages if either is being updated
            if retirement_age is not None or final_age is not None:
                if effective_retirement_age <= 0 or effective_final_age <= 0:
                    raise ValueError("Retirement age and final age must be positive")
                if effective_retirement_age >= effective_final_age:
                    raise ValueError("Final age must be greater than retirement age")
                    
                if retirement_age is not None:
                    data["retirement_age"] = retirement_age
                if final_age is not None:
                    data["final_age"] = final_age
            
            return await self.update(person_id, data, self.id_field)
            
        except Exception as e:
            logger.error(f"Error updating person record: {str(e)}")
            raise
    
    async def delete_person(self, person_id: int) -> bool:
        """
        Delete a person record.
        This will cascade to delete their asset ownership and retirement income records.
        Returns True if successful, False if person not found.
        """
        return await self.delete(person_id, self.id_field)
    
    async def list_people(
        self,
        household_id: Optional[int] = None,
        order_by: str = "last_name, first_name"
    ) -> List[Dict[str, Any]]:
        """
        List people with optional filtering by household.
        
        Args:
            household_id: Optional filter for specific household
            order_by: SQL ORDER BY clause, defaults to "last_name, first_name"
            
        Returns:
            List of person records
        """
        filters = {"household_id": household_id} if household_id is not None else None
        return await self.list(filters=filters, order_by=order_by)
    
    async def get_person_assets(self, person_id: int) -> List[Dict[str, Any]]:
        """
        Get all assets owned by a person.
        Includes both solely and jointly owned assets.
        """
        try:
            query = """
                SELECT a.*, ac.category_name,
                       GROUP_CONCAT(p.first_name || ' ' || p.last_name) as owner_names
                FROM assets a
                JOIN asset_owners ao ON a.asset_id = ao.asset_id
                JOIN asset_categories ac ON a.asset_category_id = ac.asset_category_id
                JOIN asset_owners ao2 ON a.asset_id = ao2.asset_id
                JOIN people p ON ao2.person_id = p.person_id
                WHERE ao.person_id = ?
                GROUP BY a.asset_id
                ORDER BY ac.category_name, a.asset_name
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (person_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting person's assets: {str(e)}")
            raise
    
    async def get_person_retirement_income(self, person_id: int) -> List[Dict[str, Any]]:
        """
        Get all retirement income plans where this person is a beneficiary.
        Includes both sole and joint benefits.
        """
        try:
            query = """
                SELECT rip.*,
                       GROUP_CONCAT(p.first_name || ' ' || p.last_name) as beneficiary_names
                FROM retirement_income_plans rip
                JOIN retirement_income_owners rio ON rip.income_plan_id = rio.income_plan_id
                JOIN retirement_income_owners rio2 ON rip.income_plan_id = rio2.income_plan_id
                JOIN people p ON rio2.person_id = p.person_id
                WHERE rio.person_id = ?
                GROUP BY rip.income_plan_id
                ORDER BY rip.name
            """
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (person_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting person's retirement income: {str(e)}")
            raise 