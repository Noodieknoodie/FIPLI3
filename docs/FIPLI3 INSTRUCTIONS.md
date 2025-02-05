# instructions.md

# Overview
FIPLI is a deterministic financial projection system for scenario analysis and comparative modeling. It processes user-defined assets, liabilities, cash flows, and retirement spending to generate structured, time-based nest egg projections. Calculations operate strictly on annual periods with no intra-year processing.

(ps. the db file /backend/database/FIPLI.db, is created and fully populated with usable mock data. No need to create or populate the db from scratch, or to create any tables manually. The db is ready to use as is.)

# Implementation Order
1. Establish direct database access using SQLite. No ORM, no unnecessary abstraction.
2. Implement core read queries first. Validate database relationships before writing logic.
3. Implement controlled write operations for user input features. No premature CRUD scaffolding.
4. Implement projection logic in a structured, single-flow function. Stepwise growth, liabilities, inflows, and spending must be handled in correct sequence.
5. Apply scenario overrides as adjustments to the projection engine. No scenario-specific functions; all modifications extend the base calculations.
6. Ensure data validation aligns with FIPLI's logic. Enforce only necessary constraints.
7. Introduce visualization after projections are correct. No UI or API before validation.

# Database Access Rules
- Direct queries using `sqlite3` and `pandas.read_sql()`.
- Queries exist within their functional domain, not in a separate database layer.
- Transactions are only used where necessary for data integrity.

# Calculation Execution Flow
1. Retrieve base facts for time handling and projection constraints.
2. Process all assets flagged for nest egg inclusion.
3. Apply growth rate logic (default, override, stepwise).
4. Process liabilities and apply interest accrual if applicable.
5. Process scheduled inflows and outflows, adjusting for inflation when required.
6. Process retirement income and apply inflation adjustments where enabled.
7. Process retirement spending as an aggregated withdrawal applied to the nest egg.
8. Compute the final year-end balance per iteration.
9. Apply scenario overrides dynamically where defined.
10. Validate projections for consistency and alignment with business logic.

# Scenario System
- Scenarios inherit base assumptions but allow overrides.
- Overrides affect the core projection flow, not separate calculations.
- Scenarios maintain timeline consistency with the base plan for comparability.

# Validation Strategy
- Ensure timeline integrity (no invalid retirement year placement).
- Prevent invalid stepwise growth configurations.
- Enforce logical ordering of inflows, outflows, and liability application.
- Validate that nest egg projections remain within defined constraints.

# Output Requirements
- Nest egg projections output as structured annual periods.
- Scenario comparisons aligned to base timeline.
- No intra-year breakdowns or unnecessary granularity.
- Visualization components to be generated from final structured data.

# Workflow for Cursor
- Build in the exact sequence defined. Do not modularize prematurely.
- No unnecessary helper functions unless structure exceeds maintainability limits.
- No placeholder files or scaffolding before logic is implemented.
- No excessive test writing before core logic is verified with real database data.

# Testing Guidelines
- No mock data in test files. Use real seeded database entries.
- Tests validate projection integrity, not isolated function outputs.
- Ensure correct growth application, liability accrual, and spending deductions.
- Verify scenario adjustments modify calculations as expected.

# Deployment Considerations
- Maintain raw SQLite database format for simplicity.
- Ensure database schema is fully documented and stored separately.
- Allow for JSON output for API compatibility but prioritize structured in-memory processing.

# Do Not
- Do not break calculations into excessive micro-modules.
- Do not generate redundant validation layers.
- Do not introduce ORMs or data access abstractions.
- Do not pre-build API layers before projections are validated.
