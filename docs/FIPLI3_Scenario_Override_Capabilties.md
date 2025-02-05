# SCENARIO OVERRIDE CAPABILITIES

1. CORE ASSUMPTIONS  
  modify:

  - retirement_age_1     : INTEGER
  - retirement_age_2     : INTEGER 
  - default_growth_rate  : REAL
  - growth_rate_type    : 'fixed' | 'stepwise'
  - inflation_rate      : REAL
  - annual_ret_spending : REAL
  
  if stepwise: add/modify/remove periods via growth_rate_configurations

2. ASSETS
  add new:
  - create new asset with all properties + growth control
  
  modify existing:
  - value: REAL
  - include_in_nest_egg: 0/1
  - growth: DEFAULT | OVERRIDE | STEPWISE
    if stepwise: add/modify/remove periods via growth_rate_configurations
  
  remove:
  - remove entire asset from scenario

3. LIABILITIES 
  add new:
  - create new liability with all properties
  
  modify existing:
  - value: REAL
  - interest_rate: REAL
  - include_in_nest_egg: 0/1
  
  remove:
  - remove entire liability from scenario

4. INFLOWS/OUTFLOWS
  add new:
  - create new inflow/outflow with all properties
  
  modify existing:
  - annual_amount: REAL
  - start_year: INTEGER
  - end_year: INTEGER
  - apply_inflation: 0/1
  
  remove:
  - remove entire inflow/outflow from scenario

5. RETIREMENT INCOME
  add new:
  - create new retirement income with all properties + growth control
  
  modify existing:
  - annual_income: REAL
  - start_age: INTEGER
  - end_age: INTEGER
  - apply_inflation: 0/1
  - include_in_nest_egg: 0/1
  - growth: DEFAULT | OVERRIDE | STEPWISE
    if stepwise: add/modify/remove periods via growth_rate_configurations
  
  remove:
  - remove entire retirement income from scenario