# CORE_LOGIC.md

# Overview
FIPLI is a financial planning system that enables comparison of multiple growth scenarios against base financial facts. The core purpose is to visualize how different growth rates and assumptions affect long-term nest egg values through structured, deterministic projections.

# Time Handling
- Reference Person: Determines which household member's age drives timing calculations
- Plan Creation Year: Establishes the starting point for all projections
- Annual Periods Only: All calculations occur on a yearly basis
- Fixed Timeline: Scenarios maintain consistency with base plan timeline for valid comparisons

# Base Facts Structure
- Household Details: Basic demographic information for up to two people
- Plans: Container for all financial inputs and assumptions
- Asset Categories: Organizational grouping of assets
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

# Cash Flow Components
- Inflows/Outflows: Scheduled annual amounts
- Retirement Income: Age-based income streams
- Liabilities: Tracked separately with individual interest rates
- Optional Inflation Adjustment: Available for all cash flows

# Scenario System
- Inherits Base Facts: Starting point for all scenarios
- Selective Override: Modify only desired values
- Delta Storage: Maintains only changed values
- Real-time Updates: Changes to base facts cascade to scenarios

# Nest Egg Calculation Sequence
1. Start with previous year's balance
2. Apply scenario-specific growth rate
3. Process any growth adjustments
4. Add inflows and retirement income
5. Subtract outflows and retirement spending
6. Store yearly values for visualization

# Optimization Features
- Max Spend Analysis: Calculates optimal retirement spending
- Growth Rate Comparison: Visualizes multiple growth scenarios
- Timeline Consistency: Ensures valid scenario comparisons

# Data Storage Strategy
- Base Facts: Complete financial picture
- Scenario Deltas: Store only modified values
- Yearly Values: Cache calculated results for performance
- Views: Combine base and scenario data efficiently

# Validation Requirements
1. Timeline Integrity
   - Valid retirement ages
   - Consistent scenario timelines
   - Sequential growth adjustments

2. Financial Logic
   - Non-negative values where appropriate
   - Valid growth rate ranges
   - Proper inflation application

3. Data Relationships
   - Scenario references to base facts
   - Category assignments
   - Plan ownership

# Output and Visualization
- Yearly nest egg values
- Multiple scenario overlay
- Growth comparison charts
- Contribution/withdrawal tracking