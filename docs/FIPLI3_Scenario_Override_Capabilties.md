# SCENARIO OVERRIDE CAPABILITIES

## Quick Reference
Assets:
- Add new assets
- Remove existing assets (via exclude flag)
- Modify value
- Change growth behavior (DEFAULT/OVERRIDE/STEPWISE)
- Toggle nest egg inclusion

Liabilities:
- Add new liabilities  
- Remove existing liabilities (via exclude flag)
- Modify value, interest rate
- Toggle nest egg inclusion

Inflows/Outflows:
- Add new inflows/outflows
- Remove existing inflows/outflows (via exclude flag)  
- Modify amount, start/end years
- Toggle inflation adjustment
- Change type

Retirement Income:
- Add new income streams
- Remove existing income (via exclude flag)
- Modify amount, start/end ages
- Change growth behavior (DEFAULT/OVERRIDE/STEPWISE)
- Toggle inflation adjustment
- Toggle nest egg inclusion

Core Assumptions:
- Modify retirement ages
- Change default growth rate (fixed or stepwise)
- Adjust inflation rate
- Set annual retirement spending

## Detailed Capabilities

1. CORE ASSUMPTIONS (via scenario_assumptions)
   modify:
   - retirement_age_1: INTEGER
   - retirement_age_2: INTEGER
   - default_growth_rate: REAL 
   - growth_rate_type: 'fixed' | 'stepwise'
   - inflation_rate: REAL
   - annual_retirement_spending: REAL

   if growth_rate_type = 'stepwise': 
   - manage periods via scenario_growth_rate_configurations
   - periods cannot overlap
   - each period has: start_year, end_year, growth_rate

2. ASSETS (via scenario_assets)
   add new:
   - create new scenario-specific asset
   - original_asset_id will be NULL
   - must specify valid asset_category_id
   
   modify existing:
   - value: REAL
   - include_in_nest_egg: INTEGER (0/1)
   - growth_control_type: 'DEFAULT' | 'OVERRIDE' | 'STEPWISE'
     if STEPWISE: manage via asset_growth_rate_configurations
   
   exclude:
   - set exclude_from_projection = 1

3. LIABILITIES (via scenario_liabilities)
   add new:
   - create new scenario-specific liability
   - original_liability_id will be NULL
   - must specify valid liability_category_id
   
   modify existing:
   - value: REAL
   - interest_rate: REAL
   - include_in_nest_egg: INTEGER (0/1)
   
   exclude:
   - set exclude_from_projection = 1

4. INFLOWS/OUTFLOWS (via scenario_inflows_outflows)
   add new:
   - create new scenario-specific inflow/outflow
   - original_inflow_outflow_id will be NULL
   
   modify existing:
   - type: TEXT
   - annual_amount: REAL
   - start_year: INTEGER
   - end_year: INTEGER
   - apply_inflation: INTEGER (0/1)
   
   exclude:
   - set exclude_from_projection = 1

5. RETIREMENT INCOME (via scenario_retirement_income)
   add new:
   - create new scenario-specific retirement income
   - original_income_plan_id will be NULL
   
   modify existing:
   - annual_income: REAL
   - start_age: INTEGER
   - end_age: INTEGER
   - apply_inflation: INTEGER (0/1)
   - include_in_nest_egg: INTEGER (0/1)
   - growth_control_type: 'DEFAULT' | 'OVERRIDE' | 'STEPWISE'
     if STEPWISE: manage via scenario_growth_rate_configurations
   
   exclude:
   - set exclude_from_projection = 1

## Important Notes
- All scenario items include created_at timestamps
- Category IDs must be valid when creating new items
- Growth rates can be managed at:
  * Scenario level (affects all DEFAULT items)
  * Individual item level (when set to OVERRIDE or STEPWISE)
- Stepwise periods cannot overlap
- Excluded items (exclude_from_projection = 1) are hidden but preserved in database
