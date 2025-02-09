-- FIPLI SCHEMA 
-- the database is located in the backend\database\FIPLI.db file
-- the information below is for you to see the precise structure of the database, it is not for you to use in your code.

-- Core Tables ------------------------------------------------------------------

CREATE TABLE households (
    household_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_households_timestamp AFTER UPDATE ON households BEGIN UPDATE households SET updated_at = CURRENT_TIMESTAMP WHERE household_id = NEW.household_id; END;

CREATE TABLE people (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    dob DATE NOT NULL,
    retirement_age INTEGER NOT NULL CHECK (retirement_age > 0),
    final_age INTEGER NOT NULL CHECK (final_age > retirement_age),
    FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE
);

CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    plan_name TEXT NOT NULL,
    reference_person_id INTEGER NOT NULL,
    plan_creation_year INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE,
    FOREIGN KEY (reference_person_id) REFERENCES people(person_id) ON DELETE CASCADE
);

CREATE TRIGGER update_plans_timestamp AFTER UPDATE ON plans BEGIN UPDATE plans SET updated_at = CURRENT_TIMESTAMP WHERE plan_id = NEW.plan_id; END;

CREATE TABLE base_assumptions (
    plan_id INTEGER PRIMARY KEY,
    nest_egg_growth_rate REAL DEFAULT 6.0 CHECK (nest_egg_growth_rate >= -200 AND nest_egg_growth_rate <= 200),
    inflation_rate REAL NOT NULL CHECK (inflation_rate >= -200 AND inflation_rate <= 200),
    annual_retirement_spending REAL DEFAULT 0 CHECK (annual_retirement_spending >= 0),
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);


-- ASSETS & LIABILITIES ---------

-- Defines asset types (e.g., Stocks, Real Estate, Bonds) for classification purposes
CREATE TABLE asset_categories ( 
   asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
   household_id INTEGER NOT NULL,
   category_name TEXT NOT NULL,
   FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE
);

CREATE TABLE assets (
   asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
   plan_id INTEGER NOT NULL,
   asset_category_id INTEGER NOT NULL,
   asset_name TEXT NOT NULL,  -- Name of the asset (e.g., "401(k)", "Primary Home")
   value REAL NOT NULL CHECK (value >= 0),  -- Initial asset value
   include_in_nest_egg INTEGER DEFAULT 1,  -- Whether this asset is included in retirement projections
   independent_growth_rate REAL NULL CHECK (independent_growth_rate >= -200 AND independent_growth_rate <= 200),  -- If set, this asset uses its own growth rate instead of the default nest egg rate
   FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
   FOREIGN KEY (asset_category_id) REFERENCES asset_categories(asset_category_id) ON DELETE CASCADE
);

CREATE TABLE asset_owners (
   asset_id INTEGER NOT NULL,
   person_id INTEGER NOT NULL,
   PRIMARY KEY (asset_id, person_id),  -- An asset can have multiple owners, and a person can own multiple assets
   FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE,
   FOREIGN KEY (person_id) REFERENCES people(person_id) ON DELETE CASCADE
   -- Querying ownership: 
   -- - Group by asset_id to determine if multiple people own the same asset (joint ownership)
   -- - Application logic should interpret ownership relationships when displaying financial projections
);

-- Temporarily overrides an asset's growth rate for a defined period.
-- If no adjustment exists for a given period, the asset follows its default growth rate.
CREATE TABLE asset_growth_adjustments (
   adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
   asset_id INTEGER NOT NULL,  -- The asset receiving a temporary growth rate change
   start_year INTEGER NOT NULL,  -- First year the override applies
   end_year INTEGER NOT NULL,  -- Last year the override applies
   growth_rate REAL NOT NULL CHECK (growth_rate >= -200 AND growth_rate <= 200),  -- Custom growth rate applied during this period
   CHECK (start_year <= end_year),
   FOREIGN KEY (asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
   -- Querying growth rate: 
   -- - If an asset has a matching record for a given year range, use growth_rate from this table.
   -- - Otherwise, fallback to the asset's independent_growth_rate, or the default nest egg rate.
);

CREATE TABLE liability_categories (
   liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
   household_id INTEGER NOT NULL,
   category_name TEXT NOT NULL,  -- Example: "Mortgage", "Student Loans", "Credit Cards"
   FOREIGN KEY (household_id) REFERENCES households(household_id) ON DELETE CASCADE
);

CREATE TABLE liabilities (
   liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
   plan_id INTEGER NOT NULL,
   liability_category_id INTEGER NOT NULL,
   liability_name TEXT NOT NULL,  -- Example: "Primary Home Mortgage", "Car Loan"
   value REAL NOT NULL CHECK (value >= 0),  -- Current outstanding balance
   interest_rate REAL NOT NULL CHECK (interest_rate >= -200 AND interest_rate <= 200),  -- Annual interest rate applied to this liability
   include_in_nest_egg INTEGER DEFAULT 1,
   FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
   FOREIGN KEY (liability_category_id) REFERENCES liability_categories(liability_category_id) ON DELETE CASCADE
);


-- CASHFLOWS ------------

-- Defines scheduled inflows and outflows for testing financial scenarios. Allows users to model events like future home purchases, asset sales, inheritances, and other planned changes.
CREATE TABLE inflows_outflows (
    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('INFLOW', 'OUTFLOW')),  -- 'INFLOW' (income, asset sales) or 'OUTFLOW' (expenses, purchases)
    name TEXT NOT NULL,  -- Description (e.g., "Car Purchase", "Rental Income")
    annual_amount REAL NOT NULL,  -- Fixed annual amount (subject to inflation if enabled)
    start_year INTEGER NOT NULL,  -- Year when this inflow/outflow starts
    end_year INTEGER NOT NULL,  -- Year when this inflow/outflow ends
    apply_inflation INTEGER DEFAULT 0,  -- If 1, amount grows with inflation assumptions
    CHECK (start_year <= end_year),
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
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
    CHECK (end_age IS NULL OR start_age <= end_age),
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);

-- Defines ownership of retirement income sources. Allows individual or joint ownership
CREATE TABLE retirement_income_owners (
    income_plan_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    PRIMARY KEY (income_plan_id, person_id),  -- Supports joint ownership (e.g., spousal benefits)
    FOREIGN KEY (income_plan_id) REFERENCES retirement_income_plans(income_plan_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(person_id) ON DELETE CASCADE
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
    overrides_nest_egg_growth_rate INTEGER DEFAULT 0,  -- 1 if overridden
    nest_egg_growth_rate REAL NULL CHECK (nest_egg_growth_rate >= -200 AND nest_egg_growth_rate <= 200),

    overrides_inflation_rate INTEGER DEFAULT 0,
    inflation_rate REAL NULL CHECK (inflation_rate >= -200 AND inflation_rate <= 200),

    overrides_annual_retirement_spending INTEGER DEFAULT 0,
    annual_retirement_spending REAL NULL CHECK (annual_retirement_spending IS NULL OR annual_retirement_spending >= 0),

    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE
);

-- Allows temporary modifications to the nest egg growth rate in specific years
CREATE TABLE scenario_growth_adjustments (
    adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    start_year INTEGER NOT NULL,  -- Year adjustment begins
    end_year INTEGER NOT NULL,  -- Year adjustment ends
    growth_rate REAL NOT NULL CHECK (growth_rate >= -200 AND growth_rate <= 200),  -- New temporary growth rate for this period
    CHECK (start_year <= end_year),
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    UNIQUE(scenario_id, start_year)  -- Prevents multiple adjustments for the same year in a scenario
);

-- Handle retirement age overrides per scenario per person
CREATE TABLE scenario_person_overrides (
    scenario_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    overrides_retirement_age INTEGER DEFAULT 0,
    retirement_age INTEGER CHECK (retirement_age > 0),
    overrides_final_age INTEGER DEFAULT 0,
    final_age INTEGER,
    CHECK (final_age IS NULL OR final_age > retirement_age),
    PRIMARY KEY (scenario_id, person_id),
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(person_id) ON DELETE CASCADE
);


-- Stores asset-specific scenario overrides (e.g., different valuation or exclusion)
CREATE TABLE scenario_assets (
    scenario_asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_asset_id INTEGER NOT NULL,

    overrides_value INTEGER DEFAULT 0,  -- 1 if overridden
    value REAL NULL CHECK (value IS NULL OR value >= 0),

    overrides_independent_growth_rate INTEGER DEFAULT 0,
    independent_growth_rate REAL NULL CHECK (independent_growth_rate IS NULL OR (independent_growth_rate >= -200 AND independent_growth_rate <= 200)),

    include_in_nest_egg INTEGER DEFAULT 1,  -- If 1, asset remains in projections
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, asset is ignored in this scenario

    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_asset_id) REFERENCES assets(asset_id) ON DELETE CASCADE
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

    CHECK (end_year IS NULL OR start_year IS NULL OR start_year <= end_year),
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_inflow_outflow_id) REFERENCES inflows_outflows(inflow_outflow_id) ON DELETE CASCADE
);

-- Stores scenario-specific overrides for liabilities (e.g., adjusted interest rate)
CREATE TABLE scenario_liabilities (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_liability_id INTEGER NOT NULL,

    overrides_value INTEGER DEFAULT 0,  -- 1 if overridden
    value REAL NULL CHECK (value IS NULL OR value >= 0),

    overrides_interest_rate INTEGER DEFAULT 0,  -- 1 if overridden
    interest_rate REAL NULL CHECK (interest_rate IS NULL OR (interest_rate >= -200 AND interest_rate <= 200)),

    include_in_nest_egg INTEGER DEFAULT 1,  -- If 1, liability remains in projections
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, liability is ignored in this scenario

    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_liability_id) REFERENCES liabilities(liability_id) ON DELETE CASCADE
);

-- Stores scenario-specific overrides for retirement income (e.g., adjusted benefit start age)
CREATE TABLE scenario_retirement_income (
    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    original_income_plan_id INTEGER NOT NULL,

    overrides_annual_income INTEGER DEFAULT 0,  -- 1 if overridden
    annual_income REAL NULL CHECK (annual_income IS NULL OR annual_income >= 0),

    overrides_start_age INTEGER DEFAULT 0,  -- 1 if overridden
    start_age INTEGER NULL,

    overrides_end_age INTEGER DEFAULT 0,  -- 1 if overridden
    end_age INTEGER NULL,

    apply_inflation INTEGER DEFAULT 0,  -- If 1, benefit increases with inflation
    include_in_nest_egg INTEGER DEFAULT 1,  -- If 1, income is included in projections
    exclude_from_projection INTEGER DEFAULT 0,  -- If 1, retirement income is ignored in this scenario

    CHECK (end_age IS NULL OR start_age IS NULL OR start_age <= end_age),
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (original_income_plan_id) REFERENCES retirement_income_plans(income_plan_id) ON DELETE CASCADE
);

-- Stores yearly projections of nest egg balance, contributions, withdrawals, and growth
CREATE TABLE nest_egg_yearly_values (
    nest_egg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_id INTEGER,
    year INTEGER NOT NULL,
    
    -- Core balance tracking
    nest_egg_balance REAL NOT NULL,      -- Total balance for this year
    final_year_balance REAL,             -- Projected balance at end of plan
    
    -- Detailed surplus tracking
    prior_year_surplus REAL DEFAULT 0,   -- Last year's leftover
    surplus_growth REAL DEFAULT 0,       -- Growth on prior surplus
    new_surplus REAL DEFAULT 0,          -- This year's additional surplus
    final_year_surplus REAL,             -- Projected surplus at end of plan
    
    -- Component tracking (keeping these from original)
    withdrawals REAL NULL,
    contributions REAL NULL,
    investment_growth REAL NULL,
    
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE
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
    
    -- Growth rate, inflation, and spending assumptions
    CASE WHEN sa.overrides_nest_egg_growth_rate = 1 
         THEN sa.nest_egg_growth_rate 
         ELSE ba.nest_egg_growth_rate 
    END AS nest_egg_growth_rate,
    
    CASE WHEN sa.overrides_inflation_rate = 1 
         THEN sa.inflation_rate 
         ELSE ba.inflation_rate 
    END AS inflation_rate,
    
    CASE WHEN sa.overrides_annual_retirement_spending = 1 
         THEN sa.annual_retirement_spending 
         ELSE ba.annual_retirement_spending 
    END AS annual_retirement_spending

FROM scenarios s
JOIN base_assumptions ba ON ba.plan_id = s.plan_id
LEFT JOIN scenario_assumptions sa ON sa.scenario_id = s.scenario_id;

CREATE VIEW scenario_effective_retirement_info AS
SELECT 
    s.scenario_id,
    s.plan_id,
    p.person_id,
    COALESCE(spo.retirement_age, p.retirement_age) AS effective_retirement_age,
    COALESCE(spo.final_age, p.final_age) AS effective_final_age
FROM scenarios s
CROSS JOIN people p
LEFT JOIN scenario_person_overrides spo ON spo.scenario_id = s.scenario_id 
    AND spo.person_id = p.person_id
WHERE p.household_id = (SELECT household_id FROM plans WHERE plan_id = s.plan_id);

CREATE VIEW combined_growth_adjustments AS
SELECT 
    s.scenario_id,
    a.asset_id,
    CASE 
        WHEN sga.growth_rate IS NOT NULL THEN sga.growth_rate
        WHEN aga.growth_rate IS NOT NULL THEN aga.growth_rate
        WHEN sa.overrides_independent_growth_rate = 1 THEN sa.independent_growth_rate 
        ELSE a.independent_growth_rate 
    END AS effective_growth_rate,
    COALESCE(sga.start_year, aga.start_year) AS adjustment_start_year,
    COALESCE(sga.end_year, aga.end_year) AS adjustment_end_year

FROM scenarios s
JOIN scenario_effective_assets sea ON sea.scenario_id = s.scenario_id
JOIN assets a ON a.asset_id = sea.asset_id
LEFT JOIN scenario_growth_adjustments sga ON sga.scenario_id = s.scenario_id
LEFT JOIN asset_growth_adjustments aga ON aga.asset_id = a.asset_id
LEFT JOIN scenario_assets sa ON sa.scenario_id = s.scenario_id 
    AND sa.original_asset_id = a.asset_id;

CREATE VIEW scenario_projection_inputs AS
SELECT 
    s.scenario_id,
    s.plan_id,
    sea.asset_id,
    sea.value,
    sea.independent_growth_rate,
    sea.effective_growth_rate,
    
    -- Core assumptions
    sa.nest_egg_growth_rate,
    sa.inflation_rate,
    sa.annual_retirement_spending,
    
    -- Retirement info
    sri.effective_retirement_age,
    sri.effective_final_age,
    
    -- Plan reference data
    p.reference_person_id,
    p.plan_creation_year

FROM scenarios s
JOIN scenario_effective_assets sea ON sea.scenario_id = s.scenario_id
JOIN scenario_effective_assumptions sa ON sa.scenario_id = s.scenario_id
JOIN scenario_effective_retirement_info sri ON sri.scenario_id = s.scenario_id 
    AND sri.person_id = p.reference_person_id
JOIN plans p ON p.plan_id = s.plan_id
WHERE sea.exclude_from_projection = 0;

-- Add a view to make final year lookups easy
CREATE VIEW scenario_final_positions AS
SELECT 
    n.scenario_id,
    n.plan_id,
    n.year as final_year,
    n.nest_egg_balance as final_balance,
    n.prior_year_surplus,
    n.surplus_growth,
    n.new_surplus,
    n.final_year_surplus,
    -- Calculate total surplus (might be useful)
    (n.prior_year_surplus + n.surplus_growth + n.new_surplus) as total_surplus
FROM nest_egg_yearly_values n
WHERE n.year = (
    SELECT MAX(year) 
    FROM nest_egg_yearly_values n2 
    WHERE n2.scenario_id = n.scenario_id
);
-- Indexes --------------------------------------------------------------------


-- Asset and liability indexes
CREATE INDEX idx_assets_plan ON assets(plan_id);
CREATE INDEX idx_assets_category ON assets(asset_category_id);
CREATE INDEX idx_asset_owners_asset ON asset_owners(asset_id);
CREATE INDEX idx_asset_owners_person ON asset_owners(person_id);
CREATE INDEX idx_liabilities_plan ON liabilities(plan_id);
CREATE INDEX idx_liabilities_category ON liabilities(liability_category_id);

-- Core relationship indexes
CREATE INDEX idx_plans_household ON plans(household_id);
CREATE INDEX idx_scenarios_plan ON scenarios(plan_id);

-- Timeline optimization indexes
CREATE INDEX idx_nest_egg_lookup 
ON nest_egg_yearly_values(plan_id, scenario_id, year);

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
ON scenario_assumptions(scenario_id, 
    overrides_nest_egg_growth_rate, 
    overrides_inflation_rate, 
    overrides_annual_retirement_spending);

CREATE INDEX idx_base_assumptions_plan 
ON base_assumptions(plan_id);

-- Retirement and People indexes
CREATE INDEX idx_scenario_person_overrides
ON scenario_person_overrides(scenario_id, person_id);

CREATE INDEX idx_people_household
ON people(household_id);

-- Inflows and Retirement Timeline Indexes
CREATE INDEX idx_inflows_timeline 
ON inflows_outflows(plan_id, start_year, end_year);

CREATE INDEX idx_retirement_income_timeline 
ON retirement_income_plans(plan_id, start_age, end_age);

-- Category lookup indexes
CREATE INDEX idx_asset_categories_household
ON asset_categories(household_id);

CREATE INDEX idx_liability_categories_household
ON liability_categories(household_id);

-- Asset and liability ownership indexes
CREATE INDEX idx_asset_owners_lookup
ON asset_owners(asset_id, person_id);

CREATE INDEX idx_retirement_income_owners_lookup
ON retirement_income_owners(income_plan_id, person_id);

