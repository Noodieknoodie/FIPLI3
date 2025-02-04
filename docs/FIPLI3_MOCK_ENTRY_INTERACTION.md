# FIPLI3_MOCK_ENTRY_INTERACTION.md

## Overview
This document outlines the mock entry interaction for FIPLI, Showcasing a Household with two plans and a variety of configurations. It is a guide to show user entry and database handling for the application.




# Standard Database Formatting Used Throughout Application in Backend and Database:
Dates: YYYY-MM-DD  
Percents: Decimal  
Money: Decimal, two decimal places  
Boolean: 1/0 or true/false  


---------------------------------------------------
# HOUSEHOLD 
---------------------------------------------------

### User Entry:
- household_name: Smith Family
- person1_first_name: John
- person1_last_name: Smith
- person1_dob: 1975-06-15
- person2_first_name: Jane
- person2_last_name: Smith
- person2_dob: 1978-09-22

### Database Handling:
**Table: households**
- household_id: (Auto-generated)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: household_name, person1_first_name, person1_last_name, person1_dob, person2_first_name, person2_last_name, person2_dob


---------------------------------------------------
# PLANS
---------------------------------------------------

### User Entry:
Plan 1:
- plan_name: Liquid Assets, RE Sale in 2040, SS Included, Max Spend to 95

Plan 2:
- plan_name: Liquid Assets, No RE, No SS, Retire at 70, Max Spend to 100

### Database Handling:
**Table: plans**
- plan_id: (Auto-generated)
- household_id: (Auto-linked)
- plan_creation_year: (Auto-generated)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: plan_name


---------------------------------------------------
# BASE ASSUMPTIONS
---------------------------------------------------

### User Entry:
Plan 1:
- default_growth_rate: 5.0%
- inflation_rate: 2.5%
- retirement_age_1: 65
- retirement_age_2: 63
- final_age_1: 95
- final_age_2: 92
- reference_person: John (John’s Final Age is used)

Plan 2:
- default_growth_rate: 4.2%
- inflation_rate: 3.0%
- retirement_age_1: 70
- retirement_age_2: 68
- final_age_1: 100
- final_age_2: 97
- reference_person: Jane (Jane’s Final Age is used)

### Database Handling:
**Table: base_assumptions**
- plan_id: (Linked)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: default_growth_rate, inflation_rate, retirement_age_1, retirement_age_2, final_age_1, final_age_2


**Table: plans**
- reference_person: (Stored here)


---------------------------------------------------
# ASSETS
---------------------------------------------------

### User Entry:
Plan 1:
- category_name: Non-Qualified
  - asset_name: Joint | owner: Joint | value: 800000 | include_in_nest_egg: ✅ | configuration_type: Default
  - asset_name: John's Individual | owner: John | value: 500000 | include_in_nest_egg: ✅ | configuration_type: Override | growth_rate: 8.0%
  - asset_name: Jane's Individual | owner: Jane | value: 400000 | include_in_nest_egg: ❌ | configuration_type: Stepwise | stepwise_periods: (2025-2029: 10.0%, 2037-2052: 3.0%)

- category_name: Qualified
  - asset_name: John's IRA | owner: John | value: 350000 | include_in_nest_egg: ✅ | configuration_type: Default
  - asset_name: John's 401K | owner: John | value: 600000 | include_in_nest_egg: ✅ | configuration_type: Override | growth_rate: 7.5%
  - asset_name: Jane's 403B | owner: Jane | value: 450000 | include_in_nest_egg: ✅ | configuration_type: Stepwise | stepwise_periods: (2026-2030: 9.0%, 2035-2050: 4.0%)

- category_name: Real Estate
  - asset_name: Primary Home | owner: Joint | value: 700000 | include_in_nest_egg: ✅ | configuration_type: Override | growth_rate: 9.0%

Plan 2:
- category_name: Non-Qualified
  - asset_name: Joint | owner: Joint | value: 825000 | include_in_nest_egg: ✅ | configuration_type: Default
  - asset_name: John's Individual | owner: John | value: 515000 | include_in_nest_egg: ✅ | configuration_type: Override | growth_rate: 7.8%

- category_name: Qualified
  - asset_name: John's IRA | owner: John | value: 365000 | include_in_nest_egg: ✅ | configuration_type: Default
  - asset_name: John's 401K | owner: John | value: 625000 | include_in_nest_egg: ✅ | configuration_type: Override | growth_rate: 7.8%

- category_name: Real Estate
  - asset_name: Primary Home | owner: Joint | value: 750000 | include_in_nest_egg: ❌ | configuration_type: Override | growth_rate: 9.0%
  - asset_name: Hawaii Condo | owner: Joint | value: 300000 | include_in_nest_egg: ❌ | configuration_type: Stepwise | stepwise_periods: (2026-2040: 6.0%, 2041-2050: 12.0%)

- category_name: Tax-Free
  - asset_name: Charitable Remainder Trust | owner: Joint | value: 100000 | include_in_nest_egg: ❌ | configuration_type: Override | growth_rate: 3.0%
  - asset_name: Cash | owner: Joint | value: 45000 | include_in_nest_egg: ✅ | configuration_type: Default

### Database Handling:
**Table: asset_categories**  
- asset_category_id: (Auto-generated)  
- plan_id: (Linked)  
- User Entries: category_name  

**Table: assets**
- asset_id: (Auto-generated)
- plan_id: (Linked)
- asset_category_id: (Linked)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: asset_name, owner, value, include_in_nest_egg, configuration_type

**Table: growth_rate_configurations** (Only if configuration_type is Override or Stepwise)
- growth_rate_id: (Auto-generated)
- asset_id: (Linked)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: configuration_type, stepwise_periods (for stepwise: start_year, end_year, growth_rate)


---------------------------------------------------
# LIABILITIES
---------------------------------------------------

### User Entry:
Plan 1:
- category_name: Personal
  - liability_name: Mortgage, Primary Home | owner: Joint | value: 300000 | interest_rate: 6.5% | include_in_nest_egg: ✅
  - liability_name: Credit Card Balance | owner: Joint | value: 50000 | interest_rate: 11.0% | include_in_nest_egg: ❌

- category_name: Business
  - liability_name: Business Loan | owner: Joint | value: 70000 | interest_rate: 4.0% | include_in_nest_egg: ✅

Plan 2:
- category_name: Personal
  - liability_name: Mortgage, Primary Home | owner: Joint | value: 215000 | interest_rate: 6.5% | include_in_nest_egg: ✅
  - liability_name: Credit Card Balance | owner: Joint | value: 15000 | interest_rate: 11.0% | include_in_nest_egg: ❌

- category_name: Business
  - liability_name: Business Loan | owner: Joint | value: 15000 | interest_rate: 4.0% | include_in_nest_egg: ✅
  - liability_name: Office Furniture | owner: Joint | value: 10000 | interest_rate: 7.0% | include_in_nest_egg: ❌

### Database Handling:
**Table: liability_categories**
- liability_category_id: (Auto-generated)
- plan_id: (Linked)
- User Entries: category_name

**Table: liabilities**
- liability_id: (Auto-generated)
- plan_id: (Linked)
- liability_category_id: (Linked)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: liability_name, owner, value, interest_rate, include_in_nest_egg


---------------------------------------------------
# INFLOWS & OUTFLOWS
---------------------------------------------------

### User Entry:
Plan 1:
- category_name: Inflows
  - type: Inflow | name: Structured Settlement | annual_amount: 10000 | start_year: 2026 | end_year: 2028 | apply_inflation: ❌
  - type: Inflow | name: Inheritance | annual_amount: 800000 | start_year: 2038 | end_year: 2038 | apply_inflation: ❌
  - type: Inflow | name: Rental Income | annual_amount: 24000 | start_year: 2028 | end_year: 2048 | apply_inflation: ✅

- category_name: Outflows
  - type: Outflow | name: Wedding | annual_amount: 20000 | start_year: 2029 | end_year: 2029 | apply_inflation: ❌
  - type: Outflow | name: Child Support | annual_amount: 30000 | start_year: 2025 | end_year: 2035 | apply_inflation: ✅
  - type: Outflow | name: Mom’s Retirement Home | annual_amount: 60000 | start_year: 2043 | end_year: 2047 | apply_inflation: ✅

Plan 2:
- category_name: Inflows
  - type: Inflow | name: Structured Settlement | annual_amount: 12000 | start_year: 2026 | end_year: 2028 | apply_inflation: ❌
  - type: Inflow | name: Inheritance | annual_amount: 900000 | start_year: 2035 | end_year: 2035 | apply_inflation: ❌
  - type: Inflow | name: Rental Income | annual_amount: 26000 | start_year: 2028 | end_year: 2045 | apply_inflation: ✅
  - type: Inflow | name: Business Sale | annual_amount: 500000 | start_year: 2040 | end_year: 2040 | apply_inflation: ❌

- category_name: Outflows
  - type: Outflow | name: Wedding | annual_amount: 25000 | start_year: 2029 | end_year: 2029 | apply_inflation: ❌
  - type: Outflow | name: Child Support | annual_amount: 32000 | start_year: 2025 | end_year: 2035 | apply_inflation: ✅
  - type: Outflow | name: Mom’s Retirement Home | annual_amount: 65000 | start_year: 2043 | end_year: 2047 | apply_inflation: ✅
  - type: Outflow | name: Vacation Home Purchase | annual_amount: 300000 | start_year: 2032 | end_year: 2032 | apply_inflation: ❌

### Database Handling:
**Table: inflows_outflows**
- inflow_outflow_id: (Auto-generated)
- plan_id: (Linked)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: type, name, annual_amount, start_year, end_year, apply_inflation


---------------------------------------------------
# RETIREMENT INCOME PLANS
---------------------------------------------------

### User Entry:
Plan 1:
- category_name: Retirement Income
  - name: Social Security | owner: John | annual_income: 36000 | start_age: 67 | end_age: None | apply_inflation: ✅ | include_in_nest_egg: ✅
  - name: Social Security | owner: Jane | annual_income: 32000 | start_age: 65 | end_age: None | apply_inflation: ✅ | include_in_nest_egg: ✅

Plan 2:
(No retirement income entries)

### Database Handling:
**Table: retirement_income_plans**
- income_plan_id: (Auto-generated)
- plan_id: (Linked)
- created_at: (Auto-generated)
- updated_at: (Auto-generated)
- User Entries: name, owner, annual_income, start_age, end_age, apply_inflation, include_in_nest_egg


---------------------------------------------------
# SCENARIOS
---------------------------------------------------

### User Entry:
Plan 1:

#### Scenario 1: Early Retirement, Higher Growth, No Real Estate
- Modify Core Assumptions:
  - retirement_age_1: 60
  - retirement_age_2: 58
  - default_growth_rate: 6.5%
  - growth_rate_type: stepwise
  - inflation_rate: 2.0%
  - annual_ret_spending: 85000
- Modify Assets:
  - Remove: Primary Home (Real Estate)
  - Modify: 
    - John's Individual → growth_rate: 9.0%
    - Jane's Individual → growth changed to Override, growth_rate: 7.5%
- Modify Liabilities:
  - Remove: Mortgage, Primary Home
- Modify Inflows/Outflows:
  - Remove: Rental Income
  - Modify: Structured Settlement → annual_amount: 12000, end_year: 2030
- Modify Retirement Income:
  - Social Security (John) → start_age: 62, annual_income: 30000
  - Social Security (Jane) → start_age: 60, annual_income: 28000

### Database Handling:
**Table: scenarios**
- scenario_id: (Auto-generated)
- plan_id: (Linked)
- scenario_name: Early Retirement, Higher Growth, No Real Estate
- created_at: (Auto-generated)

**Table: scenario_assumptions**
- scenario_id: (Linked)
- retirement_age_1: 60
- retirement_age_2: 58
- default_growth_rate: 6.5%
- growth_rate_type: stepwise
- inflation_rate: 2.0%
- annual_retirement_spending: 85000

**Table: growth_rate_configurations**
- scenario_id: (Linked)
- asset_id: NULL (scenario-wide stepwise growth)
- configuration_type: stepwise
- start_year: 2025, end_year: 2035, growth_rate: 7.0%
- start_year: 2036, end_year: 2050, growth_rate: 5.0%

**Table: scenario_assets**
- Remove Primary Home
- Modify John's Individual (growth_rate → 9.0%)
- Modify Jane's Individual (growth_rate → Override, 7.5%)

**Table: scenario_liabilities**
- Remove Mortgage, Primary Home

**Table: scenario_inflows_outflows**
- Remove Rental Income
- Modify Structured Settlement (annual_amount → 12000, end_year → 2030)

**Table: scenario_retirement_income**
- Modify Social Security (John) (start_age → 62, annual_income → 30000)
- Modify Social Security (Jane) (start_age → 60, annual_income → 28000)


---

### User Entry:
Plan 1:

#### Scenario 2: Delayed Retirement, Conservative Growth, Higher Spending
- Modify Core Assumptions:
  - retirement_age_1: 70
  - retirement_age_2: 68
  - default_growth_rate: 4.0%
  - growth_rate_type: fixed
  - inflation_rate: 3.0%
  - annual_ret_spending: 100000
- Modify Assets:
  - Modify: 
    - Joint → value: 850000
    - John's 401K → growth_rate: 6.0%
    - Jane's 403B → growth_rate: 5.5%
- Modify Liabilities:
  - Modify: 
    - Mortgage, Primary Home → value: 250000, interest_rate: 5.5%
- Modify Inflows/Outflows:
  - Add: Consulting Work → annual_amount: 40000, start_year: 2026, end_year: 2035, apply_inflation: ✅
- Modify Retirement Income:
  - Social Security (John) → start_age: 70, annual_income: 42000
  - Social Security (Jane) → start_age: 68, annual_income: 38000

### Database Handling:
**Table: scenarios**
- scenario_id: (Auto-generated)
- plan_id: (Linked)
- scenario_name: Delayed Retirement, Conservative Growth, Higher Spending
- created_at: (Auto-generated)

**Table: scenario_assumptions**
- scenario_id: (Linked)
- retirement_age_1: 70
- retirement_age_2: 68
- default_growth_rate: 4.0%
- growth_rate_type: fixed
- inflation_rate: 3.0%
- annual_retirement_spending: 100000

**Table: scenario_assets**
- Modify Joint (value → 850000)
- Modify John's 401K (growth_rate → 6.0%)
- Modify Jane's 403B (growth_rate → 5.5%)

**Table: scenario_liabilities**
- Modify Mortgage, Primary Home (value → 250000, interest_rate → 5.5%)

**Table: scenario_inflows_outflows**
- Add Consulting Work (annual_amount → 40000, start_year → 2026, end_year → 2035, apply_inflation → ✅)

**Table: scenario_retirement_income**
- Modify Social Security (John) (start_age → 70, annual_income → 42000)
- Modify Social Security (Jane) (start_age → 68, annual_income → 38000)


---

### User Entry:
Plan 1:

#### Scenario 3: Aggressive Investment, No Retirement Spending, High Passive Income
- Modify Core Assumptions:
  - retirement_age_1: 65
  - retirement_age_2: 63
  - default_growth_rate: 8.0%
  - growth_rate_type: stepwise
  - inflation_rate: 2.5%
  - annual_ret_spending: 0
- Modify Assets:
  - Modify: 
    - John's Individual → growth changed to Stepwise, periods: (2025-2030: 12.0%, 2031-2040: 6.0%)
    - Jane's 403B → growth changed to Stepwise, periods: (2026-2035: 10.0%, 2036-2050: 5.0%)
  - Add:
    - Private Equity Investment | owner: Joint | value: 500000 | include_in_nest_egg: ✅ | configuration_type: Override | growth_rate: 15.0%
- Modify Liabilities:
  - Remove: Business Loan
- Modify Inflows/Outflows:
  - Add: Dividend Portfolio | annual_amount: 30000 | start_year: 2025 | end_year: None | apply_inflation: ✅
  - Modify: Rental Income → annual_amount: 30000, end_year: 2055

### Database Handling:
**Table: scenarios**
- scenario_id: (Auto-generated)
- plan_id: (Linked)
- scenario_name: Aggressive Investment, No Retirement Spending, High Passive Income
- created_at: (Auto-generated)

**Table: scenario_assumptions**
- scenario_id: (Linked)
- retirement_age_1: 65
- retirement_age_2: 63
- default_growth_rate: 8.0%
- growth_rate_type: stepwise
- inflation_rate: 2.5%
- annual_retirement_spending: 0

**Table: growth_rate_configurations**
- scenario_id: (Linked)
- asset_id: NULL (scenario-wide stepwise growth)
- configuration_type: stepwise
- start_year: 2025, end_year: 2035, growth_rate: 9.0%
- start_year: 2036, end_year: 2050, growth_rate: 5.5%

**Table: scenario_assets**
- Modify John's Individual (growth → Stepwise, periods: 2025-2030: 12.0%, 2031-2040: 6.0%)
- Modify Jane's 403B (growth → Stepwise, periods: 2026-2035: 10.0%, 2036-2050: 5.0%)
- Add Private Equity Investment (value → 500000, growth → Override, 15.0%)

**Table: scenario_liabilities**
- Remove Business Loan

**Table: scenario_inflows_outflows**
- Add Dividend Portfolio (annual_amount → 30000, start_year → 2025, apply_inflation → ✅)
- Modify Rental Income (annual_amount → 30000, end_year → 2055)

