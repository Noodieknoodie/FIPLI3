# instructions.md

# Overview
FIPLI is a deterministic financial projection system focused on comparing multiple growth scenarios against base financial facts. It processes user-defined assets, cash flows, and retirement spending to visualize how different growth rates affect long-term nest egg values. All calculations operate on annual periods with no intra-year processing.

(ps. the db file /backend/database/FIPLI.db, is created and fully populated with usable mock data. No need to create or populate the db from scratch, or to create any tables manually. The db is ready to use as is.)

# Implementation Order
1. Establish direct database access using SQLite. No ORM, no unnecessary abstraction.
2. Utilize the provided views for common data access patterns.
3. Implement controlled write operations for user input features. No premature CRUD scaffolding.
4. Implement projection logic in a structured, single-flow function. Growth rates, adjustments, and cash flows must be handled in correct sequence.
5. Leverage the delta table approach for scenario management.
6. Ensure data validation aligns with FIPLI's logic. Enforce only necessary constraints.
7. Introduce visualization after projections are correct. No UI or API before validation.

# Database Access Rules
- Direct queries using `sqlite3` and `pandas.read_sql()`.
- Utilize provided views for complex joins and scenario inheritance.
- Queries exist within their functional domain, not in a separate database layer.
- Transactions are only used where necessary for data integrity.

# Calculation Execution Flow
1. Retrieve base facts and relevant scenario overrides using view structures.
2. Process all assets flagged for nest egg inclusion.
3. Apply three-tier growth rate system:
   - Nest egg growth rate (default)
   - Independent growth rates (asset-specific)
   - Growth adjustments (time-bound modifications)
4. Process scheduled inflows and outflows, adjusting for inflation when required.
5. Process retirement income and apply inflation adjustments where enabled.
6. Apply retirement spending (scenario-specific).
7. Store results in nest_egg_yearly_values for efficient retrieval.
8. Validate projections for consistency with business logic.

# Scenario System
- Leverages delta table structure for efficient storage
- Only stores modified values; inherits unchanged values from base facts
- Maintains timeline consistency with base plan for valid comparisons
- Changes to base facts automatically cascade to scenarios

# Validation Strategy
- Ensure timeline integrity through reference_person consistency
- Validate growth adjustment periods don't overlap
- Enforce logical ordering of cash flows
- Validate that nest egg projections maintain required relationships

# Output Requirements
- Utilize nest_egg_yearly_values table for storage
- Scenario comparisons aligned to base timeline
- No intra-year breakdowns or unnecessary granularity
- Visualization components to be generated from cached yearly values

# Workflow for Cursor
- Build in the exact sequence defined. Do not modularize prematurely.
- Utilize provided database views for common operations.
- No unnecessary helper functions unless structure exceeds maintainability limits.
- No placeholder files or scaffolding before logic is implemented.

# Testing Guidelines
- No mock data in test files. Use real seeded database entries.
- Tests validate projection integrity, not isolated function outputs.
- Verify correct application of three-tier growth rate system
- Ensure scenario deltas correctly override base facts

# Deployment Considerations
- Maintain raw SQLite database format for simplicity.
- Ensure database schema is fully documented and stored separately.
- Allow for JSON output for API compatibility but prioritize structured in-memory processing.

# Do Not
- Do not break calculations into excessive micro-modules.
- Do not generate redundant validation layers.
- Do not introduce ORMs or data access abstractions.
- Do not pre-build API layers before projections are validated.
- Do not bypass provided database views for complex joins