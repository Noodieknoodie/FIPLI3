"""
Base CRUD operations for FIPLI3.
Provides common database operations that can be inherited by specific entity handlers.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from ..connection import DatabaseConnection
import logging

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseCRUD:
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    async def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new record in the database.
        Returns the ID of the created record.
        """
        try:
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())
            
            query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
            
            async with DatabaseConnection.transaction() as conn:
                cursor = await conn.execute(query, values)
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {str(e)}")
            raise
    
    async def read(self, id: int, id_field: str = 'id') -> Optional[Dict[str, Any]]:
        """
        Read a single record by ID.
        Returns None if not found.
        """
        try:
            query = f"SELECT * FROM {self.table_name} WHERE {id_field} = ?"
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
                    return None
                    
        except Exception as e:
            logger.error(f"Error reading record from {self.table_name}: {str(e)}")
            raise
    
    async def update(self, id: int, data: Dict[str, Any], id_field: str = 'id') -> bool:
        """
        Update a record by ID.
        Returns True if successful, False if record not found.
        """
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            values = tuple(data.values()) + (id,)
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_field} = ?"
            
            async with DatabaseConnection.transaction() as conn:
                cursor = await conn.execute(query, values)
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating record in {self.table_name}: {str(e)}")
            raise
    
    async def delete(self, id: int, id_field: str = 'id') -> bool:
        """
        Delete a record by ID.
        Returns True if successful, False if record not found.
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE {id_field} = ?"
            
            async with DatabaseConnection.transaction() as conn:
                cursor = await conn.execute(query, (id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting record from {self.table_name}: {str(e)}")
            raise
    
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List records with optional filtering, ordering, and pagination.
        """
        try:
            query = f"SELECT * FROM {self.table_name}"
            values = []
            
            # Add WHERE clause if filters provided
            if filters:
                conditions = ' AND '.join([f"{k} = ?" for k in filters.keys()])
                values.extend(filters.values())
                query += f" WHERE {conditions}"
            
            # Add ORDER BY clause if specified
            if order_by:
                query += f" ORDER BY {order_by}"
            
            # Add LIMIT and OFFSET if specified
            if limit is not None:
                query += f" LIMIT {limit}"
                if offset is not None:
                    query += f" OFFSET {offset}"
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, tuple(values)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error listing records from {self.table_name}: {str(e)}")
            raise
    
    async def exists(self, id: int, id_field: str = 'id') -> bool:
        """
        Check if a record exists by ID.
        """
        try:
            query = f"SELECT 1 FROM {self.table_name} WHERE {id_field} = ?"
            
            async with DatabaseConnection.connection() as conn:
                async with conn.execute(query, (id,)) as cursor:
                    row = await cursor.fetchone()
                    return row is not None
                    
        except Exception as e:
            logger.error(f"Error checking record existence in {self.table_name}: {str(e)}")
            raise 