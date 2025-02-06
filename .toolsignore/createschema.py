import sqlite3
import os

# Get the absolute path to the project root (one level up from .toolsignore)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths relative to project root
DB_PATH = os.path.join(PROJECT_ROOT, 'backend', 'database', 'FIPLI_DB.db')
SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'backend', 'database', 'schema.sql')

def generate_schema():
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Rest of your code stays exactly the same
    schema_query = """
    SELECT CASE 
        WHEN type = 'table' AND name = 'households' THEN '1'
        WHEN type = 'table' AND name = 'sqlite_sequence' THEN '2'
        WHEN type = 'table' AND name IN ('plans', 'asset_categories', 'liability_categories') THEN '3'
        WHEN type = 'table' AND name IN ('assets', 'liabilities', 'inflows_outflows', 'retirement_income_plans', 'base_assumptions') THEN '4'
        WHEN type = 'table' AND name = 'asset_growth_rate_configurations' THEN '5'
        WHEN type = 'table' AND name LIKE 'scenario_%' THEN '6'
        WHEN type = 'table' AND name IN ('projection_output', 'nest_egg_yearly_values') THEN '7'
        WHEN type = 'view' THEN '8'
        WHEN type = 'index' THEN '9'
        ELSE '10'
    END || ' - ' || 
    CASE type 
        WHEN 'table' THEN '📋 Table: '
        WHEN 'view' THEN '👁️ View: '
        WHEN 'index' THEN '🔍 Index: '
        ELSE type || ': '
    END || name AS ordered_name,
    sql
    FROM sqlite_master 
    WHERE sql IS NOT NULL
    ORDER BY 1;
    """

    cursor.execute(schema_query)
    
    schema_content = "-- Auto-generated schema from FIPLI_DB.db\n\n"
    
    for _, sql in cursor.fetchall():
        schema_content += f"{sql};\n\n"

    with open(SCHEMA_PATH, 'w') as f:
        f.write(schema_content)

    conn.close()

if __name__ == "__main__":
    try:
        generate_schema()
        print(f"Schema successfully written to {SCHEMA_PATH}")
    except Exception as e:
        print(f"Error generating schema: {e}")