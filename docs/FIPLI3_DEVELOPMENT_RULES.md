# Development Guide

## Core Architecture
Desktop financial planning app built with FastAPI backend and React frontend. Uses SQLite with direct queries (no ORM). Complex data combinations, particularly for scenarios, are handled through SQL views because scenarios require consistent combining of base facts with various overrides - this is better handled in SQL than building these combinations repeatedly in Python.

## Development Principles
Group code by financial planning domains, keeping calculations separate from API/UI layers. Database views handle complex data relationships (especially scenario overrides) to keep Python code focused on financial calculations rather than data assembly. Data fetching matches natural workflow.

## Project Dependencies
Backend: Python, FastAPI, SQLite
Frontend: React, Vite, Tailwind
Development: DB Browser for SQLite


- **Monetary values** are stored as `REAL` and should be formatted to **4 decimal places** (e.g., `12345.6789`).  
- **Percentage-based values** (e.g., growth rates, interest rates) are stored as `REAL` and should be formatted to **2 decimal places** (e.g., `5.25`).  
- **Timestamps** use `DATETIME DEFAULT CURRENT_TIMESTAMP` for creation and are updated with a **BEFORE UPDATE trigger**.  
- **Rounding** follows **ROUND_HALF_UP** in Python and SQLite’s `ROUND(value, X)` for queries.  
- **SQLite does not enforce decimal precision**, so formatting is handled in the application layer.




## Structure
```
fipli/
├── backend/
│   ├── database/     # DB, views, and schema
│   ├── endpoints/    # FastAPI routes
│   ├── finance/     # Business logic by domain
│   └── calculations/ # Financial calculation engine
└── frontend/
    └── src/
        ├── pages/    # Main app screens
        ├── services/ # API communication
        └── shared/   # Reusable components
```

## Data Management
The DB file (/backend/database/FIPLI.db) is fully populated with mock data. No need to create, populate, or manually define tables. Ready to use.

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