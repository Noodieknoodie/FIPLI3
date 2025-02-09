import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'backend', 'database', 'FIPLI.db')
SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'backend', 'database', 'schema.sql')

def generate_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    schema_query = """
    SELECT CASE 
        -- Core Tables
        WHEN type = 'table' AND name = 'households' THEN '1'
        WHEN type = 'table' AND name = 'people' THEN '2'
        WHEN type = 'table' AND name = 'plans' THEN '3'
        WHEN type = 'table' AND name = 'base_assumptions' THEN '4'
        
        -- Assets & Liabilities
        WHEN type = 'table' AND name IN ('asset_categories', 'assets', 'asset_owners', 'asset_growth_adjustments') THEN '5'
        WHEN type = 'table' AND name IN ('liability_categories', 'liabilities') THEN '6'
        
        -- Cashflows
        WHEN type = 'table' AND name IN ('inflows_outflows', 'retirement_income_plans', 'retirement_income_owners') THEN '7'
        
        -- Scenarios
        WHEN type = 'table' AND name = 'scenarios' THEN '8'
        WHEN type = 'table' AND name LIKE 'scenario_%' THEN '9'
        
        -- Projection Output
        WHEN type = 'table' AND name = 'nest_egg_yearly_values' THEN '10'
        
        -- Views
        WHEN type = 'view' AND name LIKE 'scenario_%' THEN '11'
        WHEN type = 'view' THEN '12'
        
        -- Indexes
        WHEN type = 'index' AND name LIKE 'idx_asset%' THEN '13'
        WHEN type = 'index' AND name LIKE 'idx_liability%' THEN '14'
        WHEN type = 'index' AND name LIKE 'idx_scenario%' THEN '15'
        WHEN type = 'index' THEN '16'
        
        ELSE '99'
    END || ' - ' || 
    CASE type 
        WHEN 'table' THEN '[TABLE] '
        WHEN 'view' THEN '[VIEW] '
        WHEN 'index' THEN '[INDEX] '
        ELSE type || ': '
    END || name AS ordered_name,
    sql
    FROM sqlite_master 
    WHERE sql IS NOT NULL
    ORDER BY 1;
    """

    cursor.execute(schema_query)
    
    schema_content = """-- FIPLI SCHEMA 
-- the database is located in the backend/database/FIPLI.db file
-- the information below is for you to see the precise structure of the database

"""
    
    current_section = None
    for ordered_name, sql in cursor.fetchall():
        # Extract section from ordered name
        section = ordered_name.split(' - ')[1].split(']')[0].strip('[')
        
        # Add section headers
        if section != current_section:
            schema_content += f"\n-- {section}s {''.join(['-' for _ in range(70-len(section))])}\n\n"
            current_section = section
            
        schema_content += f"{sql};\n\n"

    # Write with UTF-8 encoding
    with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
        f.write(schema_content)

    conn.close()

if __name__ == "__main__":
    try:
        generate_schema()
        print(f"Schema successfully written to {SCHEMA_PATH}")
    except Exception as e:
        print(f"Error generating schema: {e}")