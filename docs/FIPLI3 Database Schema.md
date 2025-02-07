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
    household_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE people (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    dob DATE,
    FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE
);



CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for the financial plan
    household_id INTEGER NOT NULL,  -- Household associated with this plan
    plan_name TEXT NOT NULL,  -- Name of the financial plan
    reference_person_id INTEGER,  -- Person whose details anchor projections (e.g., retirement start)
    plan_creation_year INTEGER NOT NULL,  -- Year the plan was created, serving as a fixed reference point for projections
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the plan was created
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the plan was last updated
    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE,
    FOREIGN KEY (reference_person_id) REFERENCES people (person_id) ON DELETE SET NULL  -- Allows the plan to persist if reference person is removed
);



CREATE TABLE base_assumptions (
    plan_id INTEGER PRIMARY KEY,  -- Tied to a specific financial plan
    person_1_id INTEGER,  -- First person in the household
    person_2_id INTEGER,  -- Second person in the household (nullable for single-person households)
    retirement_age_1 INTEGER,  -- Retirement age for person 1
    retirement_age_2 INTEGER,  -- Retirement age for person 2
    nest_egg_growth_rate REAL DEFAULT 6.0,  -- Default growth rate for assets unless overridden
    final_age_1 INTEGER,  -- final age person 1
    final_age_2 INTEGER,  -- final age person 2
    inflation_rate REAL,  -- Inflation rate 
    annual_retirement_spending REAL DEFAULT 0,  -- annual spending in retirement
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (person_1_id) REFERENCES people (person_id) ON DELETE CASCADE,
    FOREIGN KEY (person_2_id) REFERENCES people (person_id) ON DELETE SET NULL  -- Allows for single-person plans
);


-- ASSETS & LIABILITIES ---------

-- Purely categorical table for organizing assets by type within a plan.
CREATE TABLE asset_categories ( 
    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    category_name TEXT,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);


CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    asset_category_id INTEGER NOT NULL,
    asset_name TEXT,
    value REAL,
    include_in_nest_egg INTEGER DEFAULT 1, -
    independent_growth_rate REAL NULL,  -- If set, asset grows at this rate instead of default nest egg GR
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE
);

CREATE TABLE asset_owners (
    asset_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    PRIMARY KEY (asset_id, person_id),
    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people (person_id) ON DELETE CASCADE
    -- Backend: When querying ownership, group by asset_id; if multiple person_ids exist, treat it as joint ownership in application logic.
);


-- Temporarily overrides an asset’s growth rate for a defined period. 
-- Reverts to the default rate after the end_year.
CREATE TABLE asset_growth_adjustments (
    adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    growth_rate REAL NOT NULL,  
    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE
);

CREATE TABLE liability_categories (
    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    category_name TEXT,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);


CREATE TABLE liabilities (
    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    liability_category_id INTEGER NOT NULL,
    liability_name TEXT,
    value REAL,
    interest_rate REAL,
    include_in_nest_egg INTEGER DEFAULT 1,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE
);


-- CASHFLOWS ------------


-- Defines scheduled inflows and outflows for testing financial scenarios. Allows users to model events like future home purchases, asset sales, inheritances, and other planned changes.
CREATE TABLE inflows_outflows (
    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    type TEXT,  -- 'INFLOW' or 'OUTFLOW'
    name TEXT,
    annual_amount REAL,
    start_year INTEGER,
    end_year INTEGER,
    apply_inflation INTEGER DEFAULT 0,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);


-- Functions like 'INFLOW' in inflows_outflows but specifically for Social Security, pensions, and defined benefits. Uses start_age and end_age instead of start_year and end_year for timing, but Python treats them the same.
CREATE TABLE retirement_income_plans (
    income_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    annual_income REAL NOT NULL,
    start_age INTEGER NOT NULL,
    end_age INTEGER,
    apply_inflation INTEGER DEFAULT 0,
    include_in_nest_egg INTEGER DEFAULT 1,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);


-- Defines ownership of retirement income sources. Allows individual or joint ownership by referencing the people table.
CREATE TABLE retirement_income_owners (
    income_plan_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    PRIMARY KEY (income_plan_id, person_id),
    FOREIGN KEY (income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people (person_id) ON DELETE CASCADE
);


-- Scenario Tables -------------------------------------------------------------

CREATE TABLE scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_name TEXT,
    scenario_color TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

CREATE TABLE scenario_assumptions (
    scenario_id INTEGER PRIMARY KEY,
    plan_id INTEGER NOT NULL,
    retirement_age_1 INTEGER NULL,  -- NULL inherits from base assumptions
    retirement_age_2 INTEGER NULL,
    nest_egg_growth_rate REAL NOT NULL,  -- Primary growth rate for this scenario
    inflation_rate REAL NULL,
    annual_retirement_spending REAL NULL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
);

CREATE TABLE scenario_growth_adjustments (
    adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NOT NULL,
    growth_rate REAL NOT NULL,  -- Temporarily modifies scenario's nest egg growth rate
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
);

CREATE TABLE scenario_assets (
    scenario_asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_asset_id INTEGER NOT NULL,
    value REAL NULL,  -- NULL inherits from base asset
    include_in_nest_egg INTEGER DEFAULT 1,
    independent_growth_rate REAL NULL,  -- NULL uses scenario's nest egg rate
    exclude_from_projection INTEGER DEFAULT 0,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE
);

CREATE TABLE scenario_inflows_outflows (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_inflow_outflow_id INTEGER NOT NULL,
    annual_amount REAL NULL,  -- NULL inherits from base
    start_year INTEGER NULL,
    end_year INTEGER NULL,
    apply_inflation INTEGER DEFAULT 0,
    exclude_from_projection INTEGER DEFAULT 0,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_inflow_outflow_id) REFERENCES inflows_outflows (inflow_outflow_id) ON DELETE CASCADE
);

CREATE TABLE scenario_liabilities (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_liability_id INTEGER NOT NULL,
    value REAL NULL,  -- NULL inherits from base liability
    interest_rate REAL NULL,
    include_in_nest_egg INTEGER DEFAULT 1,
    exclude_from_projection INTEGER DEFAULT 0,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_liability_id) REFERENCES liabilities (liability_id) ON DELETE CASCADE
);


CREATE TABLE scenario_retirement_income (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_income_plan_id INTEGER NOT NULL,
    annual_income REAL NULL,  -- NULL inherits from base plan
    start_age INTEGER NULL,
    end_age INTEGER NULL,
    apply_inflation INTEGER DEFAULT 0,
    include_in_nest_egg INTEGER DEFAULT 1,
    exclude_from_projection INTEGER DEFAULT 0,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE
);

CREATE TABLE nest_egg_yearly_values (
    nest_egg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_id INTEGER,  -- NULL for base projection
    year INTEGER NOT NULL,
    nest_egg_balance REAL NOT NULL,
    withdrawals REAL NULL,
    contributions REAL NULL,
    investment_growth REAL NULL,
    surplus REAL DEFAULT 0,  -- Surplus cash flow reinvested into the nest egg
    surplus_contributions REAL DEFAULT 0,  -- Tracks new surplus added this year
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
    COALESCE(sa.value, a.value) AS value,
    COALESCE(sa.include_in_nest_egg, a.include_in_nest_egg) AS include_in_nest_egg,
    COALESCE(sa.independent_growth_rate, a.independent_growth_rate) AS independent_growth_rate,
    sa.exclude_from_projection
FROM scenarios s
LEFT JOIN assets a ON a.plan_id = s.plan_id
LEFT JOIN scenario_assets sa ON sa.scenario_id = s.scenario_id 
    AND sa.original_asset_id = a.asset_id
WHERE sa.exclude_from_projection = 0 OR sa.exclude_from_projection IS NULL;

CREATE VIEW scenario_effective_assumptions AS
SELECT 
    s.scenario_id,
    s.plan_id,
    COALESCE(sa.retirement_age_1, ba.retirement_age_1) AS retirement_age_1,
    COALESCE(sa.retirement_age_2, ba.retirement_age_2) AS retirement_age_2,
    sa.nest_egg_growth_rate,
    COALESCE(sa.inflation_rate, ba.inflation_rate) AS inflation_rate,
    COALESCE(sa.annual_retirement_spending, ba.annual_retirement_spending) AS annual_retirement_spending,
    ba.final_age_1,
    ba.final_age_2
FROM scenarios s
JOIN base_assumptions ba ON ba.plan_id = s.plan_id
JOIN scenario_assumptions sa ON sa.scenario_id = s.scenario_id;

CREATE VIEW combined_growth_adjustments AS
SELECT 
    s.scenario_id,
    a.asset_id,
    COALESCE(sa.independent_growth_rate, a.independent_growth_rate) AS independent_growth_rate,
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
    sea.value,
    sea.include_in_nest_egg,
    sea.independent_growth_rate,
    sa.nest_egg_growth_rate,
    sa.inflation_rate,
    sa.annual_retirement_spending,
    sa.retirement_age_1,
    sa.retirement_age_2,
    p.reference_person,
    p.plan_creation_year
FROM scenarios s
JOIN scenario_effective_assets sea ON sea.scenario_id = s.scenario_id
JOIN scenario_effective_assumptions sa ON sa.scenario_id = s.scenario_id
JOIN plans p ON p.plan_id = s.plan_id
WHERE sea.exclude_from_projection = 0;

-- Indexes --------------------------------------------------------------------

-- Core relationship indexes
CREATE INDEX idx_plans_household ON plans(household_id);
CREATE INDEX idx_scenarios_plan ON scenarios(plan_id);

-- Timeline optimization indexes
CREATE INDEX idx_nest_egg_lookup 
ON nest_egg_yearly_values(plan_id, scenario_id, year, surplus);
CREATE INDEX idx_growth_adjustments ON scenario_growth_adjustments(scenario_id, start_year, end_year);
CREATE INDEX idx_asset_growth_adjustments ON asset_growth_adjustments(asset_id, start_year, end_year);

-- Scenario inheritance indexes
CREATE INDEX idx_scenario_assets ON scenario_assets(scenario_id, original_asset_id);
CREATE INDEX idx_scenario_inflows ON scenario_inflows_outflows(scenario_id, original_inflow_outflow_id);
CREATE INDEX idx_scenario_retirement ON scenario_retirement_income(scenario_id, original_income_plan_id);
CREATE INDEX idx_scenario_liabilities ON scenario_liabilities(scenario_id, original_liability_id);

-- Asset categorization indexes
CREATE INDEX idx_assets_category ON assets(asset_category_id, plan_id);
CREATE INDEX idx_liabilities_category ON liabilities(liability_category_id, plan_id);

-- View optimization indexes
CREATE INDEX idx_scenario_effective_timeline ON nest_egg_yearly_values(scenario_id, year) 
    WHERE scenario_id IS NOT NULL;

CREATE INDEX idx_base_timeline ON nest_egg_yearly_values(plan_id, year) 
    WHERE scenario_id IS NULL;

CREATE INDEX idx_scenario_growth_timeline ON scenario_growth_adjustments(scenario_id, start_year, end_year);

CREATE INDEX idx_scenario_assumptions_lookup ON scenario_assumptions(scenario_id, plan_id);

CREATE INDEX idx_base_assumptions_plan ON base_assumptions(plan_id);

CREATE INDEX idx_inflows_timeline ON inflows_outflows(plan_id, start_year, end_year);

CREATE INDEX idx_retirement_income_timeline ON retirement_income_plans(plan_id, start_age, end_age);

CREATE INDEX idx_asset_growth_timeline ON asset_growth_adjustments(asset_id, start_year, end_year);
