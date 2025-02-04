

# CORE_LOGIC.md

# Overview
FIPLI operates on structured, deterministic financial projections with strict annual tracking. The system processes user-defined assets, liabilities, cash flows, and spending to compute an evolving nest egg balance. All calculations follow a sequential, rules-based approach.

# Time Handling
- DOB → Plan Creation Year: Determines the absolute year start.
- Years ↔ Age Conversion: Dynamically derived where needed.
- Annual Periods Only: No intra-year processing.
- Fixed Timeline Across Scenarios: Ensures consistency for comparisons.

# Base Facts Aggregation
- Default Growth Rate: Plan-wide assumption.
- Inflation Rate: Global or asset-specific adjustment.
- Retirement Year & End Year: Governs projection duration.
- Asset Categories: Groupings for organization, not calculations.

# Asset Growth Models
- Default Growth Rate: Uses plan-wide assumption if no overrides.
- Override Growth Rate: Asset-specific rate replacing the default.
- Stepwise Growth Rate: Time-segmented growth with fallback logic.
- Inflation Toggle: Adjusts based on global or asset-level inflation.

# Liability Handling
- Fixed Value Liabilities: No interest accrual.
- Interest-Based Liabilities: Compounded annually.
- Scheduled Repayments: Reduce liability balance over time.

# Scheduled Inflows & Outflows
- Inflows: User-defined sources (salary, rental, other income).
- Outflows: User-defined expenses (loans, lifestyle costs).
- Inflation Adjustment: Applied if enabled per entry.
- Time-Based Execution: Adjusted annually within projection range.
- Net Cash Flow Calculation: Total inflows minus total outflows.

# Retirement Income Processing
- Fixed or Inflation-Adjusted Payouts.
- Start & End Years Based on User Input.
- Integrated Directly into Annual Cash Flow Calculation.

# Retirement Spending Logic
- Scenario-Specific Parameter: Does not exist in base facts.
- Applied as Annual Nest Egg Withdrawal.
- Inflation-Adjusted Over Time.
- Sustainable Spending Model: Determines safe withdrawal rate.

# Nest Egg Projection Sequence
1. Retrieve prior year-end nest egg balance.
2. Apply scheduled inflows and outflows.
3. Add retirement income.
4. Deduct retirement spending (scenarios only).
5. Compute asset growth per the selected model.
6. Deduct liability interest and repayments.
7. Compute final year-end balance.

# Scenario System
- Base Plan Cloning: Scenarios start with inherited values.
- Targeted Overrides: Modify specific parameters without affecting the base.
- Consistent Timeline: Ensures valid comparisons.
- Adjustments Apply in Real Time: Directly impact projection output.

# Validation Rules
- Enforce Logical Chronology: Start year < retirement year < end year.
- Stepwise Growth Periods Must Be Sequential & Non-Overlapping.
- No Negative Nest Egg Values: Prevents unrealistic projections.
- Ensure Cash Flow Consistency: Inflows and outflows correctly applied.
- Liability Interest Calculations Must Match Expected Accrual.

# Projection Output
- Structured Annual Nest Egg Values.
- Scenario Comparisons Maintain Fixed Timeline.
- Visualization-Ready Format.
