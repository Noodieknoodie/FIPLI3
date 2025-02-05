INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE households (
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
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE sqlite_sequence(name,seq)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER NOT NULL,
    plan_name TEXT,
    reference_person INTEGER DEFAULT 1,
    plan_creation_year INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES households (household_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE base_assumptions (
    plan_id INTEGER PRIMARY KEY,
    retirement_age_1 INTEGER,
    retirement_age_2 INTEGER,
    final_age_1 INTEGER,
    final_age_2 INTEGER,
    default_growth_rate REAL,
    inflation_rate REAL,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    scenario_name TEXT,
    scenario_color TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE scenario_overrides (
    override_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    asset_id INTEGER,
    liability_id INTEGER,
    inflow_outflow_id INTEGER,
    retirement_income_plan_id INTEGER,
    override_field TEXT,
    override_value TEXT,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_id) REFERENCES liabilities (liability_id) ON DELETE CASCADE,
    FOREIGN KEY (inflow_outflow_id) REFERENCES inflows_outflows (inflow_outflow_id) ON DELETE CASCADE,
    FOREIGN KEY (retirement_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    asset_category_id INTEGER NOT NULL,
    asset_name TEXT,
    owner TEXT,
    value REAL,
    include_in_nest_egg INTEGER DEFAULT 1, growth_control_type TEXT
    DEFAULT ''DEFAULT''
    CHECK(growth_control_type IN (''DEFAULT'', ''OVERRIDE'', ''STEPWISE'')),
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (asset_category_id) REFERENCES asset_categories (asset_category_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE liabilities (
    liability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    liability_category_id INTEGER NOT NULL,
    liability_name TEXT,
    owner TEXT,
    value REAL,
    interest_rate REAL,
    include_in_nest_egg INTEGER DEFAULT 1,
    FOREIGN KEY (plan_id) REFERENCES plans (plan_id) ON DELETE CASCADE,
    FOREIGN KEY (liability_category_id) REFERENCES liability_categories (liability_category_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE growth_rate_configurations (
    growth_rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    retirement_income_plan_id INTEGER,
    scenario_id INTEGER,
    configuration_type TEXT,
    start_year INTEGER,
    end_year INTEGER,
    growth_rate REAL,
    FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE,
    FOREIGN KEY (retirement_income_plan_id) REFERENCES retirement_income_plans (income_plan_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_plans_household_id ON plans (household_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_scenarios_plan_id ON scenarios (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_scenario_overrides_scenario_id ON scenario_overrides (scenario_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_assets_plan_id ON assets (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_assets_category_id ON assets (asset_category_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_liabilities_plan_id ON liabilities (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_liabilities_category_id ON liabilities (liability_category_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE "inflows_outflows" (
	"inflow_outflow_id"	INTEGER,
	"plan_id"	INTEGER NOT NULL,
	"type"	TEXT,
	"name"	TEXT,
	"annual_amount"	REAL,
	"start_year"	INTEGER,
	"end_year"	INTEGER,
	"apply_inflation"	INTEGER DEFAULT 0,
	PRIMARY KEY("inflow_outflow_id" AUTOINCREMENT),
	FOREIGN KEY("plan_id") REFERENCES "plans"("plan_id") ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_inflows_outflows_plan_id ON inflows_outflows (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_inflows_outflows_years ON inflows_outflows (start_year, end_year)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE retirement_income_plans (
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
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE "asset_categories" (
	"asset_category_id"	INTEGER,
	"plan_id"	INTEGER NOT NULL,
	"category_name"	TEXT,
	PRIMARY KEY("asset_category_id" AUTOINCREMENT),
	FOREIGN KEY("plan_id") REFERENCES "plans"("plan_id") ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_asset_categories_plan_id ON asset_categories (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE "liability_categories" (
	"liability_category_id"	INTEGER,
	"plan_id"	INTEGER NOT NULL,
	"category_name"	TEXT,
	PRIMARY KEY("liability_category_id" AUTOINCREMENT),
	FOREIGN KEY("plan_id") REFERENCES "plans"("plan_id") ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_liability_categories_plan_id ON liability_categories (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE TABLE scenario_assumptions (
    scenario_id INTEGER PRIMARY KEY,
    retirement_age_1 INTEGER,
    retirement_age_2 INTEGER,
    default_growth_rate REAL,
    growth_rate_type TEXT NOT NULL DEFAULT ''fixed'' CHECK(growth_rate_type IN (''fixed'', ''stepwise'')),
    inflation_rate REAL,
    annual_retirement_spending REAL,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (scenario_id) ON DELETE CASCADE
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_growth_configs ON growth_rate_configurations(
    scenario_id,
    asset_id,
    retirement_income_plan_id,
    configuration_type,
    start_year
)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_retirement_income_plans_plan_id ON retirement_income_plans (plan_id)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_assets_owner_nest_egg ON assets (owner, include_in_nest_egg)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_liabilities_owner ON liabilities (owner)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_retirement_income_plans_owner_ages ON retirement_income_plans (owner, start_age, end_age)');
INSERT INTO "main"."" ("sql") VALUES ('CREATE INDEX idx_base_assumptions_retirement_ages ON base_assumptions (retirement_age_1, retirement_age_2)');
