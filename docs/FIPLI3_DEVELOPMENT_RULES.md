# Development Guide

## Core Architecture
Desktop financial planning app built with FastAPI backend and React frontend. Uses SQLite with direct queries (no ORM). Complex data combinations, particularly for scenarios, are handled through SQL views because scenarios require consistent combining of base facts with various overrides - this is better handled in SQL than building these combinations repeatedly in Python.

## Development Principles
Group code by financial planning domains, keeping calculations separate from API/UI layers. Database views handle complex data relationships (especially scenario overrides) to keep Python code focused on financial calculations rather than data assembly. Data fetching matches natural workflow.

## Project Dependencies
Backend: Python, FastAPI, SQLite
Frontend: React, Vite, Tailwind
Development: DB Browser for SQLite


## Data Management
FIPLI.db exists and is populated with mock data if needed for read/calculation testing
THIS app must have a way to:
- Create households, financial plans, and all related entries (assets, liabilities, cash flows, etc.).
- Read those entries from the database.
- Update them when users make changes.
- Delete things like outdated scenarios, removed assets, or incorrect data.


Database views are crucial - they handle the complex task of combining base facts with scenario overrides, making Python code cleaner and more focused on business logic rather than data assembly. Review schema.sql to understand this pattern. The user will evaluate suggested schema modifications and update the database through DB Browser for SQLite if needed.

## Data Flow
Database views combine related data efficiently, particularly for scenarios where base facts, overrides, and adjustments need consistent combining. FastAPI manages API layer while Python focuses on financial calculations. React Query handles frontend data fetching


### Handled in SQL
✅ Retirement Age Must Be Before Final Age  
  CHECK (final_age > retirement_age)

✅ Start Year Must Be Before or Equal to End Year  
  CHECK (start_year <= end_year)

✅ Growth Rates & Inflation Rates Must Be Within Valid Ranges  
  CHECK (nest_egg_growth_rate >= -200 AND nest_egg_growth_rate <= 200)  
  CHECK (inflation_rate >= -200 AND inflation_rate <= 200)

✅ Retirement Income Start Age Cannot Be After End Age  
  CHECK (end_age IS NULL OR start_age <= end_age)

✅ Assets & Liabilities Cannot Be Negative  
  CHECK (value >= 0)

✅ Scenario Overrides for Retirement Age Only Apply to Reference Person  
  scenario_person_overrides (scenario_id, person_id, overrides_retirement_age)

✅ Exclusion from Scenario Works as Intended  
  exclude_from_projection INTEGER DEFAULT 0

### Handled in Python
🚨 Partial-Year Calculation for First Year  
  - First-year financial values must be prorated based on the scenario creation date.  
  - SQL does not handle partial-year calculations.

🚨 Overlapping Asset Growth Adjustments Must Be Prevented  
  - Prevent conflicting stepwise growth adjustments for the same asset in overlapping years.  
  - SQL does not enforce this.

🚨 Fallback Behavior for Lapses in Growth Rate Adjustments  
  - If no stepwise growth, use the independent growth rate.  
  - If no independent growth rate, use the scenario/default growth rate.  
  - SQL does not enforce fallback hierarchy.




# BACKEND STRUCTURE FOUNDATION

backend/                         # Root directory for all backend code
    database/                     # Database-related files
        migrations/               # For managing database schema changes
        FIPLI.db                 # SQLite database file
        FIPLI.sqbpro             # SQLite Browser project file
        schema.sql               # Database schema definitions
    
    database_connection/          # Database connectivity layer
        crud/                    # Directory for CRUD operations
        connection.py            # Database connection management
    
    endpoints/                   # FastAPI route definitions
    logic/                      # Business/Financial calculation logic
    models/                     # Data models and structures
    utils/                      # Utility functions and helpers
    myenv/                      # Python virtual environment
    requirements.txt            # Project dependencies



### High-Level Database Structure

High-Level Database Structure
The schema is designed for a financial planning application with several core components:
Core Entities
households: Root entity representing family units
people: Individual members of households
plans: Financial plans associated with households
base_assumptions: Core financial assumptions for each plan
Asset Management
asset_categories: Classification system for assets
assets: Individual assets with values and growth rates
asset_owners: Many-to-many relationship between assets and people
asset_growth_adjustments: Temporary growth rate modifications
Liability Management
liability_categories: Classification system for debts
liabilities: Individual debts with balances and interest rates
Cash Flow Management
inflows_outflows: Scheduled financial events (income/expenses)
retirement_income_plans: Retirement-specific income sources
retirement_income_owners: Links income plans to beneficiaries
Scenario Planning
scenarios: Alternative financial projections
scenario_assumptions: Overrides for base assumptions
scenario_growth_adjustments: Temporary growth rate changes
Multiple scenario override tables for assets, liabilities, etc.
Projection Tracking
nest_egg_yearly_values: Year-by-year financial projections
Several views for effective values and final positions
Key Constraints and Business Rules
Financial Validation
Growth rates must be between -200% and +200%
Asset and liability values must be non-negative
Retirement age must be positive
Final age must be greater than retirement age
Temporal Logic
All date ranges (start/end years, ages) must be valid (start ≤ end)
Automatic timestamp updates on key tables via triggers
Growth adjustments cannot overlap for the same period
Referential Integrity
Cascading deletes throughout the hierarchy
Strong foreign key relationships maintaining data consistency
Proper indexing for efficient querying of temporal and relationship data
Scenario Management
Granular override system with boolean flags for each overridden field
Clear separation between base values and scenario-specific changes
Comprehensive view system for effective values
Asset/Income Ownership
Support for joint ownership of assets and retirement income
Flexible categorization system for assets and liabilities
Clear inclusion/exclusion rules for nest egg calculations
Notable Design Patterns
Override Pattern
Consistent use of override flags (e.g., overrides_value, overrides_growth_rate)
Base values with scenario-specific modifications
Views to calculate effective values
Temporal Tracking
Year-based tracking for projections
Age-based tracking for retirement events
Support for temporary adjustments and modifications
Optimization Features
Comprehensive indexing strategy
Materialized views for common calculations
Efficient lookup patterns for temporal data