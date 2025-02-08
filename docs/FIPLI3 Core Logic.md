# CORE_LOGIC.md

# Overview
FIPLI is a financial planning system enabling comparison of multiple scenarios against base financial facts. The system processes user-defined assets, liabilities, cash flows, and spending to compute evolving nest egg balances and final position projections. All calculations follow a hierarchical, rules-based approach with clear tracking of growth and surplus components.

# Time Handling

## Storage Philosophy
- Store native values (DOBs, specific years, ages) exactly as users input them
- Calculate temporal relationships at runtime
- All stored temporal values map to any reference point (years, ages, events)

## Timeline Structure
- Plans begin at creation_date with pro-rated first year
- Each person's DOB establishes their age progression
- Reference person's final_age determines projection endpoint
- Example mapping: Year 2030 = Reference Person Age 45 = Spouse Age 47

## Temporal Calculations
First Year:
- Pro-rate all values from creation_date to December 31st
- Example: Plan created March 2024 uses 9/12 of annual amounts

Subsequent Years:
- Full calendar years (January 1st to December 31st)
- Ages increment January 1st
- Calendar years map to specific ages for both household members

## Reference Person Framework
- User-selected reference person determines:
  - Timeline endpoint (their final_age)
  - Retirement trigger points
  - Primary age-based calculations
- All timing points translate between:
  - Calendar years
  - Reference person age
  - Spouse age

## Scenario Time Consistency
- All scenarios inherit same temporal framework
- Events must translate between years and ages for both people

# Financial Components Structure

## Base Facts Layer
- Households: Demographic and relationship framework
- Plans: Container for financial inputs and assumptions
- Categories: Organizational grouping for assets and liabilities
- Base Assumptions: Core parameters including growth rates and inflation

## Asset Framework
Core Properties:
- Value: Base amount for growth calculations
- Include in Nest Egg: Controls participation in retirement projections
- Growth Control: Hierarchical system for rate application
- Ownership: Single or joint attribution

Growth Rate Hierarchy:
1. Asset-Level Stepwise Adjustments (highest priority)
  - Time-bound growth rate modifications
  - Override all other rates during specified period

2. Asset-Specific Override Rate
  - Independent growth rate that opts out of nest egg growth
  - Constant unless modified by stepwise adjustments

3. Scenario-Level Growth Rate
  - Applied to all assets without independent rates
  - Can be modified by scenario-level stepwise adjustments

4. Base Growth Rate (lowest priority)
  - Default rate from base assumptions
  - Applies when no other rates are specified

## Liability Framework
- Fixed Value: Point-in-time obligations
- Interest-Bearing: Annual compounding
- Inclusion Control: Optional impact on nest egg
- Categories: Organizational without computational impact

## Cashflow Components
Inflows:
- Scheduled Income: Regular contributions
- Retirement Income: Age-based benefits
- Asset-Generated Income: Property rentals, dividends

Outflows:
- Scheduled Expenses: Regular withdrawals
- Retirement Spending: Age-triggered withdrawals
- Liability Servicing: Interest and principal

# Calculation Engine

## Nest Egg Calculation Sequence

1. Prior Year Position
  - Previous nest egg balance
  - Prior year surplus components
  - Individual asset positions

2. Growth Application (Hierarchical)
  a. Asset-Level Processing:
     - Apply stepwise adjustments if active
     - Apply asset-specific override rates
     - Apply scenario growth rate
     - Apply default growth rate
  
  b. Surplus Growth:
     - Apply nest egg growth rate to prior_year_surplus
     - Track growth as surplus_growth

3. Cash Flow Processing
  - Apply inflation adjustments where specified
  - Process scheduled inflows
  - Add retirement income
  - Subtract scheduled outflows
  - Apply retirement spending withdrawal
  - Calculate new_surplus from net cash flow

4. Position Recording
  - Update nest egg_balance
  - Store surplus components:
    * prior_year_surplus
    * surplus_growth
    * new_surplus
  - Track final year projections:
    * final_year_balance
    * final_year_surplus

## Surplus Tracking Framework

Components:
- prior_year_surplus: Previous year's accumulated surplus
- surplus_growth: Growth earned on prior surplus
- new_surplus: Current year's net positive cash flow
- final_year_surplus: Projected ending surplus
- final_year_balance: Projected ending nest egg balance

Purpose:
- Track compound effect of reinvested surpluses
- Distinguish between investment growth and cash flow accumulation
- Project final positions for scenario comparison
- Support maximum spending rate calculations

## Scenario System

Design Philosophy:
- Delta storage: Record only modified values
- Complete inheritance: Start with base fact values
- Targeted modifications: Override specific components
- Position tracking: Maintain separate yearly values

Override Capabilities:
1. Growth Rates
  - Asset-specific rates
  - Scenario-level rates
  - Stepwise adjustments

2. Financial Components
  - Asset values and inclusion
  - Liability balances
  - Income sources
  - Spending levels

3. Timeline Parameters
  - Retirement ages
  - Final ages
  - Event timing

  # Implementation Framework

## Data Storage Strategy

### Base Layer
- Complete financial fact storage
- Timeline and relationship framework
- Category and organizational structure
- Core assumption baseline

### Scenario Layer
- Delta storage for modifications
- Override flags and values
- Temporal adjustments
- Component exclusions

### Calculation Results
Table: nest_egg_yearly_values
- Comprehensive yearly positions
- Detailed surplus tracking
- Final year projections
- Component-level detail

### Strategic Views
1. scenario_complete_state
  - Combined base + override values
  - Current effective rates
  - Active adjustments

2. yearly_cashflow_components
  - Year-by-year breakdown
  - All cash flow sources
  - Growth components
  - Net position changes

3. scenario_final_positions
  - End-of-plan projections
  - Surplus accumulation
  - Final balances
  - Comparative metrics

## Validation Framework

### Timeline Integrity
- Valid age progressions
- Consistent scenario spans
- Sequential adjustments
- Event ordering

### Financial Logic
- Value constraints (non-negative where appropriate)
- Rate application hierarchy
- Growth calculation sequence
- Surplus accumulation rules

### Relationship Validation
- Household member connections
- Category assignments
- Scenario references
- Ownership attribution

## Output & Visualization

### Position Tracking
- Year-by-year nest egg values
- Surplus component progression
- Growth source attribution
- Final position projections

### Scenario Comparison
- Multiple scenario overlay
- Growth rate effectiveness
- Surplus accumulation patterns
- Withdrawal sustainability

### Component Analysis
- Asset growth breakdown
- Cash flow patterns
- Liability progression
- Income source impact

## Runtime Processing Model

### Calculation Sequence
1. Base fact assembly
2. Scenario override application
3. Year-by-year processing
4. Position and surplus tracking
5. Final projections

### Performance Optimization
- View-based scenario assembly
- Cached calculation results
- Efficient surplus tracking
- Strategic indexing

### Data Access Patterns
- Complete scenario state
- Yearly position details
- Final projections
- Component breakdowns

### Error Handling
- Timeline validation
- Growth rate conflicts
- Cash flow imbalances
- Projection completeness