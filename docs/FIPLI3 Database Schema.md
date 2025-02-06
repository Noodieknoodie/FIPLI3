-- Auto-generated schema from FIPLI_DB.db

CREATE TABLE households (

    household_id INTEGER PRIMARY KEY AUTOINCREMENT,

    household_name TEXT,

    person1_first_name TEXT,

    person1_last_name TEXT,

    person1_dob DATE,

    person2_first_name TEXT,

    person2_last_name TEXT,

    person2_dob DATE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE asset_categories (

    asset_category_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    category_name TEXT,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE liability_categories (

    liability_category_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    category_name TEXT,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE plans (

    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,

    household_id INTEGER NOT NULL,

    plan_name TEXT,

    reference_person INTEGER DEFAULT 1,

    plan_creation_year INTEGER,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE

);

CREATE TABLE assets (

    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    asset_category_id INTEGER NOT NULL,

    asset_name TEXT,

    owner TEXT,

    value REAL,

    include_in_nest_egg INTEGER DEFAULT 1,

    growth_control_type TEXT DEFAULT 'DEFAULT'

        CHECK(growth_control_type IN ('DEFAULT', 'OVERRIDE', 'STEPWISE')),

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,

    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE

);

CREATE TABLE base_assumptions (

    plan_id INTEGER PRIMARY KEY,

    retirement_age_1 INTEGER,

    retirement_age_2 INTEGER,

    final_age_1 INTEGER,

    final_age_2 INTEGER,

    inflation_rate REAL,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE inflows_outflows (

    inflow_outflow_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    type TEXT,

    name TEXT,

    annual_amount REAL,

    start_year INTEGER,

    end_year INTEGER,

    apply_inflation INTEGER DEFAULT 0,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE liabilities (

    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    liability_category_id INTEGER NOT NULL,

    liability_name TEXT,

    owner TEXT,

    value REAL,

    interest_rate REAL,

    include_in_nest_egg INTEGER DEFAULT 1,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE retirement_income_plans (

    income_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    name TEXT NOT NULL,

    owner TEXT NOT NULL,

    annual_income REAL NOT NULL,

    start_age INTEGER NOT NULL,

    end_age INTEGER,

    apply_inflation INTEGER DEFAULT 0,

    include_in_nest_egg INTEGER DEFAULT 1,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE asset_growth_rate_configurations (

    asset_growth_rate_id INTEGER PRIMARY KEY AUTOINCREMENT,

    asset_id INTEGER NOT NULL,

    start_year INTEGER NOT NULL,

    end_year INTEGER NOT NULL,

    growth_rate REAL NOT NULL,

    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE

);

CREATE TABLE scenario_assets (

    scenario_asset_id INTEGER PRIMARY KEY AUTOINCREMENT,

    scenario_id INTEGER NOT NULL,

    original_asset_id INTEGER,

    value REAL,

    include_in_nest_egg INTEGER DEFAULT 1,

    growth_control_type TEXT DEFAULT 'DEFAULT' 

        CHECK(growth_control_type IN ('DEFAULT', 'OVERRIDE', 'STEPWISE')),

    exclude_from_projection INTEGER DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,

    FOREIGN KEY (original_asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE

);

CREATE TABLE scenario_assumptions (

    scenario_id INTEGER PRIMARY KEY,

    retirement_age_1 INTEGER,

    retirement_age_2 INTEGER,

    default_growth_rate REAL,  -- Default rate used when stepwise is OFF

    growth_rate_type TEXT NOT NULL DEFAULT 'fixed'

        CHECK(growth_rate_type IN ('fixed', 'stepwise')),

    inflation_rate REAL,

    annual_retirement_spending REAL,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE

);

CREATE TABLE scenario_growth_rate_configurations (

    scenario_growth_rate_id INTEGER PRIMARY KEY AUTOINCREMENT,

    scenario_id INTEGER NOT NULL,

    start_year INTEGER NOT NULL,

    end_year INTEGER NOT NULL,

    growth_rate REAL NOT NULL,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE

);

CREATE TABLE scenario_inflows_outflows (

    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,

    scenario_id INTEGER NOT NULL,

    original_inflow_outflow_id INTEGER,

    type TEXT NOT NULL,

    annual_amount REAL NOT NULL,

    start_year INTEGER NOT NULL,

    end_year INTEGER,

    apply_inflation INTEGER DEFAULT 0,

    exclude_from_projection INTEGER DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,

    FOREIGN KEY (original_inflow_outflow_id) REFERENCES inflows_outflows (inflow_outflow_id) ON DELETE CASCADE

);

CREATE TABLE scenario_liabilities (

    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,

    scenario_id INTEGER NOT NULL,

    original_liability_id INTEGER,

    value REAL NOT NULL,

    interest_rate REAL,

    include_in_nest_egg INTEGER DEFAULT 1,

    exclude_from_projection INTEGER DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,

    FOREIGN KEY (original_liability_id) REFERENCES liabilities (liability_id) ON DELETE CASCADE

);

CREATE TABLE scenario_retirement_income (

    scenario_item_id INTEGER PRIMARY KEY AUTOINCREMENT,

    scenario_id INTEGER NOT NULL,

    original_income_plan_id INTEGER,

    annual_income REAL NOT NULL,

    start_age INTEGER NOT NULL,

    end_age INTEGER,

    apply_inflation INTEGER DEFAULT 0,

    include_in_nest_egg INTEGER DEFAULT 1,

    growth_control_type TEXT DEFAULT 'DEFAULT'

        CHECK(growth_control_type IN ('DEFAULT', 'OVERRIDE', 'STEPWISE')),

    exclude_from_projection INTEGER DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,

    FOREIGN KEY (original_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE

);

CREATE TABLE scenarios (

    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    scenario_name TEXT,

    scenario_color TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE

);

CREATE TABLE nest_egg_yearly_values (

    nest_egg_id INTEGER PRIMARY KEY AUTOINCREMENT,

    plan_id INTEGER NOT NULL,

    scenario_id INTEGER,  -- NULL if base projection

    year INTEGER NOT NULL,

    nest_egg_balance REAL NOT NULL,

    withdrawals REAL NOT NULL DEFAULT 0,

    contributions REAL NOT NULL DEFAULT 0,

    investment_growth REAL NOT NULL DEFAULT 0,

    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,

    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE

);

CREATE VIEW asset_final_growth_rates AS

SELECT 

    asset_id,

    start_year,

    end_year,

    growth_rate

FROM asset_growth_rate_configurations;

CREATE VIEW scenario_final_assets AS

SELECT 

    COALESCE(sa.scenario_asset_id, a.asset_id) AS asset_id,

    sa.scenario_id,

    COALESCE(sa.value, a.value) AS value,

    COALESCE(sa.include_in_nest_egg, a.include_in_nest_egg) AS include_in_nest_egg,

    COALESCE(sa.growth_control_type, a.growth_control_type) AS growth_control_type

FROM assets a

LEFT JOIN scenario_assets sa 

    ON a.asset_id = sa.original_asset_id 

    AND sa.scenario_id IS NOT NULL

WHERE sa.exclude_from_projection = 0 OR sa.exclude_from_projection IS NULL;

CREATE VIEW scenario_final_assumptions AS

SELECT 

    sa.scenario_id,

    COALESCE(sa.retirement_age_1, ba.retirement_age_1) AS retirement_age_1,

    COALESCE(sa.retirement_age_2, ba.retirement_age_2) AS retirement_age_2,

    COALESCE(sa.default_growth_rate, 6.0) AS default_growth_rate,

    sa.growth_rate_type,

    COALESCE(sa.inflation_rate, ba.inflation_rate) AS inflation_rate,

    sa.annual_retirement_spending

FROM base_assumptions ba

LEFT JOIN scenario_assumptions sa 

    ON ba.plan_id = sa.scenario_id;

CREATE VIEW scenario_final_growth_rates AS

SELECT 

    scenario_id,

    start_year,

    end_year,

    growth_rate

FROM scenario_growth_rate_configurations;

CREATE VIEW scenario_final_inflows_outflows AS

SELECT 

    COALESCE(sio.scenario_item_id, io.inflow_outflow_id) AS inflow_outflow_id,

    sio.scenario_id,

    COALESCE(sio.type, io.type) AS type,

    COALESCE(sio.annual_amount, io.annual_amount) AS annual_amount,

    COALESCE(sio.start_year, io.start_year) AS start_year,

    COALESCE(sio.end_year, io.end_year) AS end_year,

    COALESCE(sio.apply_inflation, io.apply_inflation) AS apply_inflation

FROM inflows_outflows io

LEFT JOIN scenario_inflows_outflows sio 

    ON io.inflow_outflow_id = sio.original_inflow_outflow_id 

    AND sio.scenario_id IS NOT NULL

WHERE sio.exclude_from_projection = 0 OR sio.exclude_from_projection IS NULL;

CREATE VIEW scenario_final_liabilities AS

SELECT 

    COALESCE(sl.scenario_item_id, l.liability_id) AS liability_id,

    sl.scenario_id,

    COALESCE(sl.value, l.value) AS value,

    COALESCE(sl.interest_rate, l.interest_rate) AS interest_rate,

    COALESCE(sl.include_in_nest_egg, l.include_in_nest_egg) AS include_in_nest_egg

FROM liabilities l

LEFT JOIN scenario_liabilities sl 

    ON l.liability_id = sl.original_liability_id 

    AND sl.scenario_id IS NOT NULL

WHERE sl.exclude_from_projection = 0 OR sl.exclude_from_projection IS NULL;

CREATE VIEW scenario_final_retirement_income AS

SELECT 

    COALESCE(sri.scenario_item_id, rip.income_plan_id) AS income_plan_id,

    sri.scenario_id,

    COALESCE(sri.annual_income, rip.annual_income) AS annual_income,

    COALESCE(sri.start_age, rip.start_age) AS start_age,

    COALESCE(sri.end_age, rip.end_age) AS end_age,

    COALESCE(sri.apply_inflation, rip.apply_inflation) AS apply_inflation,

    COALESCE(sri.include_in_nest_egg, rip.include_in_nest_egg) AS include_in_nest_egg,

    COALESCE(sri.growth_control_type, 'DEFAULT') AS growth_control_type

FROM retirement_income_plans rip

LEFT JOIN scenario_retirement_income sri 

    ON rip.income_plan_id = sri.original_income_plan_id 

    AND sri.scenario_id IS NOT NULL

WHERE sri.exclude_from_projection = 0 OR sri.exclude_from_projection IS NULL;

CREATE INDEX idx_asset_categories_plan_id ON asset_categories (plan_id);

CREATE INDEX idx_asset_growth_configurations ON asset_growth_rate_configurations (asset_id, start_year, end_year);

CREATE INDEX idx_assets_category_id ON assets (asset_category_id);

CREATE INDEX idx_assets_nest_egg ON assets (include_in_nest_egg);

CREATE INDEX idx_assets_plan_id ON assets (plan_id);

CREATE INDEX idx_inflows_outflows_plan_id ON inflows_outflows (plan_id);

CREATE INDEX idx_inflows_outflows_years ON inflows_outflows (start_year, end_year);

CREATE INDEX idx_liabilities_category_id ON liabilities (liability_category_id);

CREATE INDEX idx_liabilities_plan_id ON liabilities (plan_id);

CREATE INDEX idx_liability_categories_plan_id ON liability_categories (plan_id);

CREATE INDEX idx_nest_egg_yearly_values 

ON nest_egg_yearly_values (plan_id, scenario_id, year);

CREATE INDEX idx_plans_household_id ON plans (household_id);

CREATE INDEX idx_retirement_income_plans_ages ON retirement_income_plans (start_age, end_age);

CREATE INDEX idx_retirement_income_plans_plan_id ON retirement_income_plans (plan_id);

CREATE INDEX idx_scenario_assets_original_asset_id ON scenario_assets (original_asset_id);

CREATE INDEX idx_scenario_assets_scenario_id ON scenario_assets (scenario_id);

CREATE INDEX idx_scenario_assumptions_scenario_id ON scenario_assumptions (scenario_id);

CREATE INDEX "idx_scenario_growth_rate_configs" ON "scenario_growth_rate_configurations" (
	"scenario_id",
	"start_year",
	"end_year",
	"growth_rate"
);

CREATE INDEX idx_scenario_inflows_outflows_original_id ON scenario_inflows_outflows (original_inflow_outflow_id);

CREATE INDEX idx_scenario_inflows_outflows_scenario_id ON scenario_inflows_outflows (scenario_id);

CREATE INDEX idx_scenario_liabilities_original_liability_id ON scenario_liabilities (original_liability_id);

CREATE INDEX idx_scenario_liabilities_scenario_id ON scenario_liabilities (scenario_id);

CREATE INDEX idx_scenarios_plan_id ON scenarios (plan_id);

