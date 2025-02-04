# backend/validation/validate_db.py

import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum

# Direct database access within functional domain

DB_PATH = Path(__file__).parent.parent / "database" / "FIPLI.db"

class ValidationResultType(Enum):
    SCHEMA = "Schema"
    RELATIONSHIP = "Relationship"
    BUSINESS_RULE = "Business Rule"
    INDEX = "Index"

@dataclass
class ValidationResult:
    type: ValidationResultType
    is_error: bool
    message: str
    details: Dict = None

# Required tables and their primary/foreign keys
REQUIRED_TABLES = {
    'Households': {
        'primary_keys': ['household_id'],
        'required_fields': ['household_name', 'created_at', 'updated_at'],
        'nullable_fields': ['person2_first_name', 'person2_last_name', 'person2_dob']
    },
    'Plans': {
        'primary_keys': ['plan_id'],
        'foreign_keys': {'household_id': 'Households'},
        'required_fields': ['plan_name', 'reference_person', 'plan_creation_year', 'created_at', 'updated_at']
    },
    'Base_Assumptions': {
        'primary_keys': ['plan_id'],
        'foreign_keys': {'plan_id': 'Plans'},
        'required_fields': ['default_growth_rate', 'inflation_rate', 'retirement_age_1', 'final_age_1', 'final_age_selector']
    },
    'Assets': {
        'primary_keys': ['asset_id'],
        'foreign_keys': {'plan_id': 'Plans', 'asset_category_id': 'Asset_Categories'},
        'required_fields': ['asset_name', 'owner', 'value', 'include_in_nest_egg'],
        'enum_fields': {'owner': ['person1', 'person2', 'joint']}
    }
}

# Required indexes from schema
REQUIRED_INDEXES = {
    'Plans': ['household_id'],
    'Assets': ['plan_id'],
    'Liabilities': ['plan_id'],
    'Scheduled_Inflows_Outflows': ['plan_id'],
    'Retirement_Income_Plans': ['plan_id'],
    'Scenarios': ['plan_id'],
    'Scenario_Overrides': ['scenario_id']
}

def validate_schema() -> List[ValidationResult]:
    """Validate database schema against requirements"""
    results = []
    with sqlite3.connect(DB_PATH) as conn:
        # Get existing tables
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )['name'].tolist()
        
        # Check for missing tables but don't exit early
        missing = set(REQUIRED_TABLES.keys()) - set(tables)
        if missing:
            results.append(ValidationResult(
                type=ValidationResultType.SCHEMA,
                is_error=True,
                message=f"Missing required tables",
                details={'missing_tables': list(missing)}
            ))
        
        # Validate all existing tables, even if some are missing
        for table in set(REQUIRED_TABLES.keys()) & set(tables):
            columns = pd.read_sql_query(f"PRAGMA table_info({table})", conn)
            column_names = columns['name'].tolist()
            
            # Check required columns
            required = set(REQUIRED_TABLES[table]['required_fields'] + REQUIRED_TABLES[table]['primary_keys'])
            missing_cols = required - set(column_names)
            if missing_cols:
                results.append(ValidationResult(
                    type=ValidationResultType.SCHEMA,
                    is_error=True,
                    message=f"Missing required columns in {table}",
                    details={'table': table, 'missing_columns': list(missing_cols)}
                ))
            
            # Validate enum fields if any
            if 'enum_fields' in REQUIRED_TABLES[table]:
                for field, valid_values in REQUIRED_TABLES[table]['enum_fields'].items():
                    invalid_values = pd.read_sql_query(
                        f"SELECT DISTINCT {field} FROM {table} WHERE {field} NOT IN ({','.join(['?']*len(valid_values))})",
                        conn,
                        params=valid_values
                    )
                    if not invalid_values.empty:
                        results.append(ValidationResult(
                            type=ValidationResultType.SCHEMA,
                            is_error=True,
                            message=f"Invalid enum values in {table}.{field}",
                            details={'table': table, 'field': field, 'invalid_values': invalid_values[field].tolist()}
                        ))
    
    return results

def validate_indexes() -> List[ValidationResult]:
    """Validate required indexes exist and have correct fields"""
    results = []
    with sqlite3.connect(DB_PATH) as conn:
        # First check if tables exist before checking indexes
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'", conn
        )['name'].tolist()
        
        for table, required_indexes in REQUIRED_INDEXES.items():
            if table not in tables:
                # Skip index validation for missing tables but log it
                results.append(ValidationResult(
                    type=ValidationResultType.INDEX,
                    is_error=False,  # Warning only since table absence is already an error
                    message=f"Skipping index validation for missing table",
                    details={'table': table}
                ))
                continue
                
            index_info = pd.read_sql_query(f"PRAGMA index_list({table})", conn)
            for required_field in required_indexes:
                found_valid_index = False
                
                # Check each index on the table
                for _, row in index_info.iterrows():
                    index_columns = pd.read_sql_query(f"PRAGMA index_info({row['name']})", conn)
                    
                    # Verify this index actually indexes our required field
                    indexed_columns = index_columns['name'].tolist()
                    if required_field in indexed_columns:
                        # Check if it's the first column (most efficient for queries)
                        if indexed_columns.index(required_field) == 0:
                            found_valid_index = True
                            break
                        else:
                            results.append(ValidationResult(
                                type=ValidationResultType.INDEX,
                                is_error=False,  # Warning only
                                message=f"Index exists but field is not the primary column",
                                details={
                                    'table': table,
                                    'field': required_field,
                                    'index_name': row['name'],
                                    'column_position': indexed_columns.index(required_field) + 1
                                }
                            ))
                
                if not found_valid_index:
                    results.append(ValidationResult(
                        type=ValidationResultType.INDEX,
                        is_error=True,
                        message=f"Missing or invalid index",
                        details={'table': table, 'field': required_field}
                    ))
    return results

def validate_relationships() -> List[ValidationResult]:
    """Validate core data relationships and integrity"""
    results = []
    with sqlite3.connect(DB_PATH) as conn:
        # Household → Plan relationship
        households_without_plans = pd.read_sql_query("""
            SELECT h.household_id, h.household_name 
            FROM Households h
            LEFT JOIN Plans p ON h.household_id = p.household_id
            WHERE p.plan_id IS NULL
        """, conn)
        if not households_without_plans.empty:
            results.append(ValidationResult(
                type=ValidationResultType.RELATIONSHIP,
                is_error=True,
                message="Found households without plans",
                details={'count': len(households_without_plans), 'households': households_without_plans.to_dict('records')}
            ))

        # Validate stepwise growth periods don't overlap
        overlapping_growth = pd.read_sql_query("""
            SELECT g1.asset_id, g1.start_year, g1.end_year,
                   g2.start_year as overlap_start, g2.end_year as overlap_end
            FROM Growth_Rate_Configurations g1
            JOIN Growth_Rate_Configurations g2 
                ON g1.asset_id = g2.asset_id
                AND g1.growth_rate_id < g2.growth_rate_id
                AND g1.end_year >= g2.start_year
            WHERE g1.configuration_type = 'Stepwise' 
            AND g2.configuration_type = 'Stepwise'
        """, conn)
        if not overlapping_growth.empty:
            results.append(ValidationResult(
                type=ValidationResultType.RELATIONSHIP,
                is_error=True,
                message="Found overlapping stepwise growth periods",
                details={'overlaps': overlapping_growth.to_dict('records')}
            ))

    return results

def validate_business_rules() -> List[ValidationResult]:
    """Validate core business rules and constraints"""
    results = []
    with sqlite3.connect(DB_PATH) as conn:
        # Validate retirement age logic
        invalid_retirement = pd.read_sql_query("""
            SELECT p.plan_id, ba.retirement_age_1, ba.retirement_age_2,
                   ba.final_age_1, ba.final_age_2
            FROM Plans p
            JOIN Base_Assumptions ba ON p.plan_id = ba.plan_id
            WHERE ba.retirement_age_1 >= ba.final_age_1
               OR (ba.retirement_age_2 IS NOT NULL 
                   AND ba.final_age_2 IS NOT NULL 
                   AND ba.retirement_age_2 >= ba.final_age_2)
        """, conn)
        if not invalid_retirement.empty:
            results.append(ValidationResult(
                type=ValidationResultType.BUSINESS_RULE,
                is_error=True,
                message="Found invalid retirement age configurations",
                details={'invalid_plans': invalid_retirement.to_dict('records')}
            ))

        # Validate scheduled cash flows
        invalid_flows = pd.read_sql_query("""
            SELECT * FROM Scheduled_Inflows_Outflows
            WHERE start_year > end_year
            AND end_year IS NOT NULL
        """, conn)
        if not invalid_flows.empty:
            results.append(ValidationResult(
                type=ValidationResultType.BUSINESS_RULE,
                is_error=True,
                message="Found invalid cash flow date ranges",
                details={'invalid_flows': invalid_flows.to_dict('records')}
            ))

    return results

def run_validation() -> Dict[ValidationResultType, List[ValidationResult]]:
    """Run all validations and return grouped results"""
    all_results = {
        ValidationResultType.SCHEMA: validate_schema(),
        ValidationResultType.INDEX: validate_indexes(),
        ValidationResultType.RELATIONSHIP: validate_relationships(),
        ValidationResultType.BUSINESS_RULE: validate_business_rules()
    }
    return all_results

def format_validation_output(results: Dict[ValidationResultType, List[ValidationResult]]) -> str:
    """Format validation results into clear, grouped sections"""
    output = []
    has_errors = False
    
    # First list all errors
    for result_type, validations in results.items():
        errors = [v for v in validations if v.is_error]
        if errors:
            has_errors = True
            output.append(f"\n{result_type.value} Errors:")
            for error in errors:
                output.append(f"  ❌ {error.message}")
                if error.details:
                    for key, value in error.details.items():
                        output.append(f"    • {key}: {value}")
    
    # Then list all warnings
    for result_type, validations in results.items():
        warnings = [v for v in validations if not v.is_error]
        if warnings:
            output.append(f"\n{result_type.value} Warnings:")
            for warning in warnings:
                output.append(f"  ⚠️ {warning.message}")
                if warning.details:
                    for key, value in warning.details.items():
                        output.append(f"    • {key}: {value}")
    
    # Summary section
    total_errors = sum(len([v for v in vals if v.is_error]) for vals in results.values())
    total_warnings = sum(len([v for v in vals if not v.is_error]) for vals in results.values())
    
    summary = [
        "\n=== Validation Summary ===",
        f"Total Errors: {total_errors}",
        f"Total Warnings: {total_warnings}"
    ]
    
    return "\n".join(summary + output)

if __name__ == "__main__":
    print("\nRunning comprehensive database validation...")
    results = run_validation()
    
    # Format and display results
    output = format_validation_output(results)
    print(output)
    
    # Exit with error code if validation failed
    has_errors = any(any(v.is_error for v in validations) for validations in results.values())
    if has_errors:
        print("\n❌ Validation failed. Please fix errors before proceeding.")
        exit(1)
    else:
        print("\n✅ All validations passed successfully!") 