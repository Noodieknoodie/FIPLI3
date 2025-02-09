"""
Test script for database connection.
"""

import asyncio
from connection import DatabaseConnection, test_connection, get_db_version

async def run_tests():
    """Run all database connection tests."""
    try:
        # Test basic connection
        print("Testing database connection...")
        connection_ok = await test_connection()
        print("✓ Database connection successful")
        
        # Get SQLite version
        version = await get_db_version()
        print(f"✓ SQLite Version: {version}")
        
        # Test transaction
        print("\nTesting transaction management...")
        async with DatabaseConnection.transaction() as conn:
            await conn.execute("SELECT 1")
        print("✓ Transaction management working")
        
        print("\nAll tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        raise
    finally:
        # Clean up
        await DatabaseConnection.close_connection()

if __name__ == "__main__":
    asyncio.run(run_tests()) 