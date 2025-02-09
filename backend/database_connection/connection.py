"""
Database connection module for FIPLI3.
Provides async connection management and connection pooling for SQLite.
"""

import os
import logging
import aiosqlite
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'FIPLI.db')

class DatabaseConnection:
    _connection_pool: Optional[aiosqlite.Connection] = None
    
    @classmethod
    async def get_connection(cls) -> aiosqlite.Connection:
        """
        Get a database connection from the pool.
        Creates a new connection if none exists.
        """
        if cls._connection_pool is None:
            try:
                logger.info(f"Establishing new database connection to {DB_PATH}")
                cls._connection_pool = await aiosqlite.connect(
                    DB_PATH,
                    isolation_level=None  # Enable autocommit mode
                )
                # Enable foreign keys
                await cls._connection_pool.execute("PRAGMA foreign_keys = ON")
                
                # Configure connection
                cls._connection_pool.row_factory = aiosqlite.Row
                
            except Exception as e:
                logger.error(f"Failed to establish database connection: {str(e)}")
                raise ConnectionError(f"Database connection failed: {str(e)}")
            
        return cls._connection_pool
    
    @classmethod
    async def close_connection(cls) -> None:
        """
        Close the database connection pool.
        """
        if cls._connection_pool is not None:
            try:
                await cls._connection_pool.close()
                cls._connection_pool = None
                logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
                raise
    
    @classmethod
    @asynccontextmanager
    async def transaction(cls) -> AsyncGenerator[aiosqlite.Connection, None]:
        """
        Context manager for database transactions.
        Automatically handles commit/rollback.
        
        Usage:
            async with DatabaseConnection.transaction() as conn:
                await conn.execute("INSERT INTO ...")
        """
        conn = await cls.get_connection()
        try:
            await conn.execute("BEGIN")
            yield conn
            await conn.execute("COMMIT")
        except Exception as e:
            await conn.execute("ROLLBACK")
            logger.error(f"Transaction failed, rolling back: {str(e)}")
            raise
    
    @classmethod
    @asynccontextmanager
    async def connection(cls) -> AsyncGenerator[aiosqlite.Connection, None]:
        """
        Context manager for database connections.
        Provides a connection without transaction management.
        
        Usage:
            async with DatabaseConnection.connection() as conn:
                await conn.execute("SELECT ...")
        """
        conn = await cls.get_connection()
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise

# Example usage functions
async def test_connection() -> bool:
    """
    Test the database connection.
    Returns True if successful, raises an exception otherwise.
    """
    try:
        async with DatabaseConnection.connection() as conn:
            await conn.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        raise

async def get_db_version() -> str:
    """
    Get the SQLite version.
    """
    try:
        async with DatabaseConnection.connection() as conn:
            async with conn.execute("SELECT sqlite_version()") as cursor:
                version = await cursor.fetchone()
                return version[0] if version else "Unknown"
    except Exception as e:
        logger.error(f"Failed to get database version: {str(e)}")
        raise
