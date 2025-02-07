# FIPLI SCHEMA 

/*
Financial Planning Database Schema
Purpose: Manages household financial plans and scenario projections
Core concepts:
- Plans contain base financial facts
- Scenarios model different growth rates and assumptions
- Nest egg represents assets included in retirement projections
- All monetary values stored as REAL (floating point)
*/

-- Core Tables ------------------------------------------------------------------


CREATE TABLE households (
    household_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_name TEXT NOT NULL,  -- Name of the household
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE people (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,  
    last_name TEXT NOT NULL,  
    dob DATE NOT NULL,  -- Date of birth for financial planning
    retirement_age INTEGER NOT NULL,  -- Planned retirement age for this person
    final_age INTEGER NOT NULL,  -- Expected lifespan (used for end-of-plan projections)
    FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE
);


CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    plan_name TEXT NOT NULL,  
    reference_person_id INTEGER NOT NULL,  -- The person whose timeline is used for projections
    plan_creation_year INTEGER NOT NULL,  -- Static reference year for financial projections
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE,
    FOREIGN KEY (reference_person_id) REFERENCES people(person_id) ON DELETE CASCADE
);


CREATE TABLE base_assumptions (
    plan_id INTEGER PRIMARY KEY,  -- One per plan, serving as a reference for all scenarios
    nest_egg_growth_rate REAL DEFAULT 6.0,  -- Default investment growth rate (unless overridden)
    inflation_rate REAL NOT NULL,  -- Assumed inflation rate (affects projections)
    annual_retirement_spending REAL DEFAULT 0,  -- Expected spending during retirement
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);


-- ASSETS & LIABILITIES ---------

-- Defines asset types (e.g., Stocks, Real Estate, Bonds) for classification purposes
CREATE TABLE asset_categories ( 
    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,  -- Name of the asset category (e.g., "Real Estate")
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    asset_category_id INTEGER NOT NULL,
    asset_name TEXT NOT NULL,  -- Name of the asset (e.g., "401(k)", "Primary Home")
    value REAL NOT NULL,  -- Initial asset value
    include_in_nest_egg INTEGER DEFAULT 1,  -- Whether this asset is included in retirement projections
    independent_growth_rate REAL NULL,  -- If set, this asset uses its own growth rate instead of the default nest egg rate
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE
);

CREATE TABLE asset_owners (
    asset_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    PRIMARY KEY (asset_id, person_id),  -- An asset can have multiple owners, and a person can own multiple assets
    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people (person_id) ON DELETE CASCADE
    -- Querying ownership: 
    -- - Group by asset_id to determine if multiple people own the same asset (joint ownership)
    -- - Application logic should interpret ownership relationships when displaying financial projections
);

-- Temporarily overrides an asset’s growth rate for a defined period.
-- If no adjustment exists for a given period, the asset follows its default growth rate.
CREATE TABLE asset_growth_adjustments (
    adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,  -- The asset receiving a temporary growth rate change
    start_year INTEGER NOT NULL,  -- First year the override applies
    end_year INTEGER NOT NULL,  -- Last year the override applies
    growth_rate REAL NOT NULL,  -- Custom growth rate applied during this period
    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE
    -- Querying growth rate: 
    -- - If an asset has a matching record for a given year range, use `growth_rate` from this table.
    -- - Otherwise, fallback to the asset’s `independent_growth_rate`, or the default nest egg rate.
);


CREATE TABLE liability_categories (
    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,  -- Example: "Mortgage", "Student Loans", "Credit Cards"
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

CREATE TABLE liabilities (
    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    liability_category_id INTEGER NOT NULL,
    liability_name TEXT NOT NULL,  -- Example: "Primary Home Mortgage", "Car Loan"
    value REAL NOT NULL,  -- Current outstanding balance
    interest_rate REAL NOT NULL,  -- Annual interest rate applied to this liability
    include_in_nest_egg INTEGER DEFAULT 1,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE
);

-- CASHFLOWS ------------


-- Defines scheduled inflows and outflows for testing financial scenarios. Allows users to model events like future home purchases, asset sales, inheritances, and other planned changes.
CREATE TABLE inflows_outflows (
    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- 'INFLOW' (income, asset sales) or 'OUTFLOW' (expenses, purchases)
    name TEXT NOT NULL,  -- Description (e.g., "Car Purchase", "Rental Income")
    annual_amount REAL NOT NULL,  -- Fixed annual amount (subject to inflation if enabled)
    start_year INTEGER NOT NULL,  -- Year when this inflow/outflow starts
    end_year INTEGER NOT NULL,  -- Year when this inflow/outflow ends
    apply_inflation INTEGER DEFAULT 0,  -- If 1, amount grows with inflation assumptions
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- Functions like 'INFLOW' in inflows_outflows but specifically for Social Security, pensions, and defined benefits. Uses start_age and end_age instead of start_year and end_year for timing, but Python treats them the same.
CREATE TABLE retirement_income_plans (
    income_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    name TEXT NOT NULL,  -- Description (e.g., "Social Security", "Company Pension")
    annual_income REAL NOT NULL,  -- Fixed annual payout (adjusted for inflation if enabled)
    start_age INTEGER NOT NULL,  -- Age when the person starts receiving this income
    end_age INTEGER,  -- Age when payments stop (NULL means lifetime benefit)
    apply_inflation INTEGER DEFAULT 0,  -- If 1, annual_income increases with inflation
    include_in_nest_egg INTEGER DEFAULT 1,  -- If 1, included in net worth and retirement projections
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

-- Defines ownership of retirement income sources. Allows individual or joint ownership
CREATE TABLE retirement_income_owners (
    income_plan_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    PRIMARY KEY (income_plan_id, person_id),  -- Supports joint ownership (e.g., spousal benefits)
    FOREIGN KEY (income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people (person_id) ON DELETE CASCADE
);


-- Scenario Tables -------------------------------------------------------------

-- Represents alternative financial projections based on modified assumptions.
CREATE TABLE scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_name TEXT NOT NULL,  -- Name of the scenario (e.g., "Early Retirement", "Market Crash")
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);

-- Stores scenario-specific overrides for base assumptions (e.g., growth rate, inflation)
CREATE TABLE scenario_assumptions (
    scenario_id INTEGER PRIMARY KEY,
    plan_id INTEGER NOT NULL,

    overrides_nest_egg_growth_rate INTEGER DEFAULT 0,  -- 1 if overridden
    nest_egg_growth_rate REAL NULL,  

    overrides_inflation_rate INTEGER DEFAULT 0,  
    inflation_rate REAL NULL,

    overrides_annual_retirement_spending INTEGER DEFAULT 0,  
    annual_retirement_spending REAL NULL,

    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);

-- Allows temporary modifications to the nest egg growth rate in specific years
CREATE TABLE scenario_growth_adjustments (
    adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    start_year INTEGER NOT NULL,  -- Year adjustment begins
    end_year INTEGER NOT NULL,  -- Year adjustment ends
    growth_rate REAL NOT NULL,  -- New temporary growth rate for this period
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
	UNIQUE(scenario_id, start_year)  -- Prevents multiple adjustments for the same year in a scenario
);

-- Stores asset-specific scenario overrides (e.g., different valuation or exclusion)
CREATE TABLE scenario_assets (
    scenario_asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_asset_id INTEGER NOT NULL,

    overrides_value INTEGER DEFAULT 0,  -- 1 if overridden
    value REAL NULL,  

    overrides_independent_growth_rate INTEGER DEFAULT 0,
    independent_growth_rate REAL NULL,  

    include_in_nest_egg INTEGER DEFAULT 1,  -- If 1, asset remains in projections
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, asset is ignored in this scenario

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE
);

-- Stores scenario-specific overrides for inflows and outflows
CREATE TABLE scenario_inflows_outflows (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_inflow_outflow_id INTEGER NOT NULL,

    overrides_annual_amount INTEGER DEFAULT 0,  -- 1 if annual amount is overridden
    annual_amount REAL NULL,

    overrides_start_year INTEGER DEFAULT 0,  -- 1 if start year is overridden
    start_year INTEGER NULL,

    overrides_end_year INTEGER DEFAULT 0,  -- 1 if end year is overridden
    end_year INTEGER NULL,

    apply_inflation INTEGER DEFAULT 0,  -- If 1, amount adjusts with inflation
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, this inflow/outflow is ignored in this scenario

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_inflow_outflow_id) REFERENCES inflows_outflows (inflow_outflow_id) ON DELETE CASCADE
);

-- Stores scenario-specific overrides for liabilities (e.g., adjusted interest rate)
CREATE TABLE scenario_liabilities (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_liability_id INTEGER NOT NULL,

    overrides_value INTEGER DEFAULT 0,  -- 1 if overridden
    value REAL NULL,  

    overrides_interest_rate INTEGER DEFAULT 0,  -- 1 if overridden
    interest_rate REAL NULL,

    include_in_nest_egg INTEGER DEFAULT 1,  -- If 1, liability remains in projections
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, liability is ignored in this scenario

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_liability_id) REFERENCES liabilities (liability_id) ON DELETE CASCADE
);

-- Stores scenario-specific overrides for retirement income (e.g., adjusted benefit start age)
CREATE TABLE scenario_retirement_income (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_income_plan_id INTEGER NOT NULL,

    overrides_annual_income INTEGER DEFAULT 0,  -- 1 if overridden
    annual_income REAL NULL,

    overrides_start_age INTEGER DEFAULT 0,  -- 1 if overridden
    start_age INTEGER NULL,

    overrides_end_age INTEGER DEFAULT 0,  -- 1 if overridden
    end_age INTEGER NULL,

    apply_inflation INTEGER DEFAULT 0,  -- If 1, benefit increases with inflation
    include_in_nest_egg INTEGER NULL DEFAULT 1,  -- If 1, income is included in projections
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, retirement income is ignored in this scenario

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE
);

-- Stores yearly projections of nest egg balance, contributions, withdrawals, and growth
CREATE TABLE nest_egg_yearly_values (
    nest_egg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_id INTEGER,  -- NULL for base projection, set for scenario-specific projections
    year INTEGER NOT NULL,  -- Year of projection
    nest_egg_balance REAL NOT NULL,  -- Total assets in the retirement fund
    withdrawals REAL NULL,  -- Amount withdrawn this year
    contributions REAL NULL,  -- Amount contributed this year
    investment_growth REAL NULL,  -- Investment gains/losses for the year
    surplus REAL DEFAULT 0,  -- Surplus cash flow reinvested into the nest egg
    surplus_contributions REAL DEFAULT 0,  -- New surplus added this year
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
);



-- Views ----------------------------------------------------------------------

CREATE VIEW scenario_effective_assets AS
SELECT 
    s.scenario_id,
    s.plan_id,
    COALESCE(sa.scenario_asset_id, a.asset_id) AS asset_id,
    a.asset_name,
    a.asset_category_id,

    -- Use scenario value only if overridden
    CASE WHEN sa.overrides_value = 1 THEN sa.value ELSE a.value END AS value,
    CASE WHEN sa.overrides_independent_growth_rate = 1 THEN sa.independent_growth_rate ELSE a.independent_growth_rate END AS independent_growth_rate,
    
    -- Keep existing include/exclude logic
    sa.exclude_from_projection,
    COALESCE(sa.include_in_nest_egg, a.include_in_nest_egg) AS include_in_nest_egg

FROM scenarios s
LEFT JOIN assets a ON a.plan_id = s.plan_id
LEFT JOIN scenario_assets sa ON sa.scenario_id = s.scenario_id 
    AND sa.original_asset_id = a.asset_id
WHERE sa.exclude_from_projection = 0 OR sa.exclude_from_projection IS NULL;


CREATE VIEW scenario_effective_assumptions AS
SELECT 
    s.scenario_id,
    s.plan_id,

    -- Use overridden retirement ages if set
    CASE WHEN sa.overrides_retirement_age_1 = 1 THEN sa.retirement_age_1 ELSE ba.retirement_age_1 END AS retirement_age_1,
    CASE WHEN sa.overrides_retirement_age_2 = 1 THEN sa.retirement_age_2 ELSE ba.retirement_age_2 END AS retirement_age_2,

    -- Handle other assumption overrides
    CASE WHEN sa.overrides_nest_egg_growth_rate = 1 THEN sa.nest_egg_growth_rate ELSE ba.nest_egg_growth_rate END AS nest_egg_growth_rate,
    CASE WHEN sa.overrides_inflation_rate = 1 THEN sa.inflation_rate ELSE ba.inflation_rate END AS inflation_rate,
    CASE WHEN sa.overrides_annual_retirement_spending = 1 THEN sa.annual_retirement_spending ELSE ba.annual_retirement_spending END AS annual_retirement_spending,

    -- Final age always comes from base assumptions
    ba.final_age_1,
    ba.final_age_2

FROM scenarios s
JOIN base_assumptions ba ON ba.plan_id = s.plan_id
LEFT JOIN scenario_assumptions sa ON sa.scenario_id = s.scenario_id;

CREATE VIEW combined_growth_adjustments AS
SELECT 
    s.scenario_id,
    a.asset_id,

    -- Use scenario growth rate if overridden
    CASE WHEN sa.overrides_independent_growth_rate = 1 THEN sa.independent_growth_rate ELSE a.independent_growth_rate END AS independent_growth_rate,

    -- Growth rate adjustments
    sga.start_year AS scenario_adj_start,
    sga.end_year AS scenario_adj_end,
    sga.growth_rate AS scenario_adj_rate,
    aga.start_year AS asset_adj_start,
    aga.end_year AS asset_adj_end,
    aga.growth_rate AS asset_adj_rate

FROM scenarios s
JOIN scenario_effective_assets sea ON sea.scenario_id = s.scenario_id
JOIN assets a ON a.asset_id = sea.asset_id
LEFT JOIN scenario_growth_adjustments sga ON sga.scenario_id = s.scenario_id
LEFT JOIN asset_growth_adjustments aga ON aga.asset_id = a.asset_id;

CREATE VIEW scenario_projection_inputs AS
SELECT 
    s.scenario_id,
    s.plan_id,
    sea.asset_id,
    
    -- Use overridden asset values when applicable
    CASE WHEN sa.overrides_value = 1 THEN sa.value ELSE sea.value END AS value,
    CASE WHEN sa.overrides_independent_growth_rate = 1 THEN sa.independent_growth_rate ELSE sea.independent_growth_rate END AS independent_growth_rate,

    -- Other assumptions
    CASE WHEN sa.overrides_nest_egg_growth_rate = 1 THEN sa.nest_egg_growth_rate ELSE ba.nest_egg_growth_rate END AS nest_egg_growth_rate,
    CASE WHEN sa.overrides_inflation_rate = 1 THEN sa.inflation_rate ELSE ba.inflation_rate END AS inflation_rate,
    CASE WHEN sa.overrides_annual_retirement_spending = 1 THEN sa.annual_retirement_spending ELSE ba.annual_retirement_spending END AS annual_retirement_spending,

    -- Retirement ages
    CASE WHEN sa.overrides_retirement_age_1 = 1 THEN sa.retirement_age_1 ELSE ba.retirement_age_1 END AS retirement_age_1,
    CASE WHEN sa.overrides_retirement_age_2 = 1 THEN sa.retirement_age_2 ELSE ba.retirement_age_2 END AS retirement_age_2,

    -- Fixed plan-level data
    p.reference_person_id,
    p.plan_creation_year

FROM scenarios s
JOIN scenario_effective_assets sea ON sea.scenario_id = s.scenario_id
LEFT JOIN scenario_effective_assumptions sa ON sa.scenario_id = s.scenario_id
JOIN plans p ON p.plan_id = s.plan_id
JOIN base_assumptions ba ON ba.plan_id = s.plan_id
WHERE sea.exclude_from_projection = 0;

-- Indexes --------------------------------------------------------------------

-- Core relationship indexes
CREATE INDEX idx_plans_household ON plans(household_id);
CREATE INDEX idx_scenarios_plan ON scenarios(plan_id);

-- Timeline optimization indexes
CREATE INDEX idx_nest_egg_lookup 
ON nest_egg_yearly_values(plan_id, scenario_id, year, surplus);

CREATE INDEX idx_scenario_growth_timeline 
ON scenario_growth_adjustments(scenario_id, start_year, end_year) 
WHERE growth_rate IS NOT NULL;

CREATE INDEX idx_asset_growth_timeline 
ON asset_growth_adjustments(asset_id, start_year, end_year) 
WHERE growth_rate IS NOT NULL;

-- Scenario inheritance indexes 
CREATE INDEX idx_scenario_assets 
ON scenario_assets(scenario_id, original_asset_id, overrides_value, overrides_independent_growth_rate);

CREATE INDEX idx_scenario_inflows 
ON scenario_inflows_outflows(scenario_id, original_inflow_outflow_id, overrides_annual_amount, overrides_start_year, overrides_end_year);

CREATE INDEX idx_scenario_retirement 
ON scenario_retirement_income(scenario_id, original_income_plan_id, overrides_annual_income, overrides_start_age, overrides_end_age);

CREATE INDEX idx_scenario_liabilities 
ON scenario_liabilities(scenario_id, original_liability_id, overrides_value, overrides_interest_rate);

-- View optimization indexes
CREATE INDEX idx_scenario_assumptions_lookup 
ON scenario_assumptions(scenario_id, plan_id, 
    overrides_nest_egg_growth_rate, overrides_inflation_rate, overrides_annual_retirement_spending);

CREATE INDEX idx_base_assumptions_plan ON base_assumptions(plan_id);

-- Inflows and Retirement Timeline Indexes
CREATE INDEX idx_inflows_timeline 
ON inflows_outflows(plan_id, start_year, end_year);

CREATE INDEX idx_retirement_income_timeline 
ON retirement_income_plans(plan_id, start_age, end_age);
