# CORE_LOGIC.md

# Overview
FIPLI is a financial planning system that enables comparison of multiple growth scenarios against base financial facts. The system processes user-defined assets, liabilities, cash flows, and spending to compute an evolving nest egg balance. All calculations follow a sequential, rules-based approach.

# Time Handling

## Storage Philosophy
- Store native values in database (DOBs, specific years, ages) exactly as users input them
- Calculate temporal relationships at runtime rather than storing derived values
- All stored dates/ages/years can be mapped to any other temporal reference point

## Timeline Fundamentals
- Plan starts at creation_date with partial first year
- Each person's DOB establishes their age progression
- Reference person's final_age determines end of projection timeline
- Example mapping: Year 2030 = Reference Person Age 45 = Spouse Age 47

## Temporal Calculations
First Year:
- Pro-rate all values (growth, income, expenses) from creation_date to December 31st
- Example: Plan created March 2024 uses 9/12 of annual amounts for 2024

Subsequent Years:
- Full calendar years (January 1st to December 31st)
- Ages increment January 1st
- All calendar years map to specific ages for both household members

## Reference Person Controls
- User-selected reference person determines:
  - Timeline end point via their final_age
  - Retirement trigger point for household spending
  - All timing calculations must resolve to both calendar years and ages for either person

## Scenario Consistency
- All scenarios inherit same temporal framework
- All timing points (retirement, income events, etc.) must be translatable between:
  - Calendar years (e.g., 2030)
  - Reference person age (e.g., 45)
  - Spouse age (e.g., 47)
  - 
# Base Facts Structure
- Household Details: Basic demographic information for up to two people
- Plans: Container for all financial inputs and assumptions
- Asset/Liability Categories: Organizational grouping
- Base Assumptions: Core parameters including retirement ages and inflation

# Growth Rate System
Three distinct mechanisms for controlling asset growth:
1. Nest Egg Growth Rate
   - Default rate applied to all included assets
   - Configurable at both base and scenario levels
   - Primary tool for scenario comparison

2. Independent Growth Rate
   - Asset-specific rate that opts out of nest egg growth
   - Remains constant unless modified by adjustments
   - Available in both base facts and scenarios

3. Growth Adjustments
   - Time-bound growth rate modifications
   - Can be applied to individual assets or entire scenarios
   - Override normal growth rates during specified years
   - Return to default rates after adjustment period

# Asset Management
- Include/Exclude from Nest Egg: Controls participation in projections
- Value: Base amount subject to growth calculations
- Growth Control: Multiple options for customizing growth behavior
- Categories: Organizational grouping without computational impact

# Liability Handling
- Fixed Value Liabilities: No interest accrual
- Interest-Based Liabilities: Compounded annually
- Scheduled Repayments: Reduce liability balance over time
- Include/Exclude from Nest Egg: Controls impact on projections

# Scheduled Inflows & Outflows
- Inflows: User-defined sources (salary, rental, other income)
- Outflows: User-defined expenses (loans, lifestyle costs)
- Inflation Adjustment: Applied if enabled per entry
- Time-Based Execution: Adjusted annually within projection range
- Net Cash Flow Calculation: Total inflows minus total outflows

# Retirement Income Processing
- Fixed or Inflation-Adjusted Payouts
- Start & End Years Based on User Input
- Integrated Directly into Annual Cash Flow Calculation

# Retirement Spending Logic
- Scenario-Specific Parameter: Does not exist in base facts
- Applied as Annual Nest Egg Withdrawal
- Inflation-Adjusted Over Time
- Sustainable Spending Model: Determines safe withdrawal rate

# Nest Egg Calculation Sequence
1. Start with previous year's balance
2. Apply scenario-specific growth rate
3. Process any growth adjustments
4. Add inflows and retirement income
5. Subtract outflows and retirement spending
6. Process liability interest and repayments
7. Store yearly values for visualization

# Scenario System
- Delta Table Approach: Store only modified values
- Inheritance: Scenarios start with base fact values
- Targeted Overrides: Modify specific parameters without affecting the base
- Consistent Timeline: Ensures valid comparisons
- Real-time Updates: Changes to base facts cascade to scenarios

# Data Storage Strategy
- Base Facts: Complete financial picture
- Scenario Deltas: Store only modified values
- Yearly Values: Cache calculated results for performance
- Views: Combine base and scenario data efficiently

# Validation Rules
1. Timeline Integrity
   - Valid retirement ages
   - Consistent scenario timelines
   - Sequential growth adjustments

2. Financial Logic
   - Non-negative values where appropriate
   - Valid growth rate ranges
   - Proper inflation application
   - Liability interest calculations must match expected accrual

3. Data Relationships
   - Scenario references to base facts
   - Category assignments
   - Plan ownership

# Output and Visualization
- Yearly nest egg values
- Multiple scenario overlay
- Growth comparison charts
- Contribution/withdrawal tracking
- Liability balance progression
