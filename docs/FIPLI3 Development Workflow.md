# DEVELOPMENT_WORKFLOW.md

# Overview
This document defines the structured development workflow for building FIPLI using Cursor. It ensures that implementation follows the correct sequence, avoiding premature modularization and excessive abstraction. Cursor must strictly adhere to the defined execution order and leverage the provided database views for efficient data access.

# General Rules
- No predefined file structure; files are generated as needed following the grouping rules below.
- No excessive function separation unless a file exceeds 400 lines.
- No unnecessary CRUD scaffolding before read operations are confirmed.
- No test generation before database interactions and projections are validated.

# Execution Order

## 1. Database Integration
1. Establish direct SQLite access using `sqlite3`.
2. Utilize provided views for complex data relationships.
3. Implement read queries first, ensuring correct relationships.
4. Validate that all base facts, assets, liabilities, and scheduled cash flows are correctly retrieved.
5. Implement controlled write operations only after read functions are confirmed.

## 2. Core Projection Logic
1. Retrieve base assumptions and establish time tracking using reference_person from Plans table.
2. Process all assets flagged for nest egg inclusion.
3. Apply three-tier growth rate system:
   - Nest egg growth rate as primary driver
   - Independent growth rates for specific assets
   - Time-bound growth adjustments
4. Process liabilities, applying interest accrual where applicable.
5. Process scheduled inflows and outflows, adjusting for inflation if enabled.
6. Process retirement income, applying adjustments as needed.
7. Apply retirement spending per scenario settings.
8. Store results in nest_egg_yearly_values table.

## 3. Scenario Handling
1. Leverage delta table structure for scenario management.
2. Use provided views to combine base facts with scenario overrides.
3. Ensure scenarios align with the base plan's fixed timeline.
4. Validate that scenario comparisons remain structurally meaningful.

## 4. Data Validation & Constraint Enforcement
1. Ensure reference_person timing consistency.
2. Enforce chronological ordering of growth adjustment periods.
3. Prevent negative nest egg values.
4. Validate liability interest calculations and accrual accuracy.
5. Validate cash flow consistency (inflows and outflows applied correctly).
6. Ensure scenario modifications correctly adjust projections.

## 5. Testing Strategy
1. No tests before logic is validated using real seeded database data.
2. No unit tests for isolated functions; all testing focuses on integrated projection results.
3. Verify:
   - Three-tier growth rate system application
   - Liability accrual accuracy
   - Cash flow execution per annual period
   - Scenario delta inheritance working correctly
   - Projection caching in nest_egg_yearly_values

## 6. Visualization & Finalization
1. Introduce visualization only after projections are confirmed correct.
2. Generate structured output:
   - Annual nest egg projections per scenario
   - Growth rate comparison visualizations
   - Liability balance progression
   - Final projection datasets ready for UI/API integration
3. Finalize API layer if applicable, but only after all backend logic is validated.

# Development Constraints
- Cursor must not modularize excessively; functions should remain consolidated until exceeding maintainability limits.
- No placeholder files; only generate files when logic is implemented.
- No unnecessary helper functions that only wrap simple logic.
- All projections must remain deterministic and aligned with business rules.
- Always use provided database views for complex data relationships.

# Summary
Cursor must follow this structured workflow, ensuring efficient, predictable execution without unnecessary fragmentation. Emphasis should be placed on utilizing the provided database structure, particularly the views and delta table approach for scenarios, while maintaining accurate liability processing throughout the system.