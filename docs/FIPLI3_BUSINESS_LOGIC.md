# BUSINESS_LOGIC.md

## 1. Database & Data Flow

### **1.1 Database Overview**
- **Location:** `/backend/database/FIPLI.db`
- **Status:** Fully populated with mock data.
- **No Manual Setup Required:** Tables are predefined and populated.

### **1.2 Application Data Flow**
- **SQL Views**: Efficiently combine related data, particularly for base facts, overrides, and adjustments.
- **Backend:** FastAPI handles API logic, while Python performs financial calculations.
- **Frontend:** React Query manages data fetching.

---

## 2. Core Financial Rules


- **Monetary values** are stored as `REAL` and should be formatted to **4 decimal places** (e.g., `12345.6789`).  
- **Percentage-based values** (e.g., growth rates, interest rates) are stored as `REAL` and should be formatted to **2 decimal places** (e.g., `5.25`).  
- **Timestamps** use `DATETIME DEFAULT CURRENT_TIMESTAMP` for creation and are updated with a **BEFORE UPDATE trigger**.  
- **Rounding** follows **ROUND_HALF_UP** in Python and SQLite’s `ROUND(value, X)` for queries.  
- **SQLite does not enforce decimal precision**, so formatting is handled in the application layer.



### **2.1 Growth Rate Constraints**
#### **Rules**
```sql
CHECK (nest_egg_growth_rate >= -200 AND nest_egg_growth_rate <= 200)
CHECK (inflation_rate >= -200 AND inflation_rate <= 200)
```

#### **Growth Rate Precedence**
1. Stepwise asset overrides (most specific)
2. Asset’s independent growth rate
3. Scenario growth rate
4. Base growth rate (least specific)

#### **Conflict Prevention**
- No overlapping stepwise adjustments for the same asset.
- Fallback behavior ensures correct rate application when gaps exist.

### **2.2 Timeline & Validation Rules**

#### **Age & Year Constraints**
```sql
CHECK (final_age > retirement_age)
CHECK (end_age IS NULL OR start_age <= end_age)
CHECK (start_year <= end_year)
```

#### **Handling Dates**
- First year is prorated based on scenario creation_date.
- Full calendar years are used thereafter.
- Age changes occur on January 1st.
- All dates align with the reference person’s timeline.
- Reference person determines final_age and projection endpoint.
- Example mapping: Year 2030 = Reference Person Age 45 = Spouse Age 47.

---

## 3. Asset & Cash Flow Management

### **3.1 Asset Rules**

#### **Value & Ownership Constraints**
```sql
CHECK (value >= 0)
```
- Single or joint ownership is allowed.
- Ownership must be clearly attributed for calculations.
- Consistent handling across scenarios.

#### **Growth Application**
- Growth follows hierarchical precedence (stepwise → independent → scenario → base).
- Growth is separated from contributions.
- Partial years are handled correctly (prorated from scenario creation date).

### **3.2 Annual Cash Flow Processing**

#### **Cash Flow Components**
- **Inflows:**
  - `inflows_outflows.annual_amount` (general inflows)
  - `retirement_income_plans.annual_income` (structured retirement income)
- **Outflows:**
  - `inflows_outflows.annual_amount` (general outflows)
  - `base_assumptions.annual_retirement_spending` (retirement spending)

#### **Processing Logic**
1. Sum all inflows (`inflows_outflows` + `retirement_income_plans`).
2. Sum all outflows (`inflows_outflows` + `base_assumptions.annual_retirement_spending`).
3. Calculate net cash flow:
   **Inflows - Outflows - Retirement Spending**

#### **Surplus Handling**
- Any surplus (excess cash flow) is saved and tracked.
- Growth on surplus follows the applicable nest egg growth rate.
- Surplus-retaining inflows are stored in `nest_egg_yearly_values.surplus`.

#### **Deficit Handling**
- All inflows are spent first, including surplus-retaining ones.
- Deficits are covered by withdrawals from the nest egg.
- Withdrawals are recorded in `nest_egg_yearly_values.withdrawals`.

---

## 4. Scenario Management

### **4.1 Override & Inheritance Rules**

#### **Delta Storage**
- Only modified values are stored.
- Override flags are tracked explicitly.
- Modification history is maintained.

#### **Inheritance Behavior**
1. Start with base fact values.
2. Apply overrides in strict order.
3. Missing values follow fallback hierarchy.
4. Referential integrity is preserved.

#### **Validation Requirements**
- Cross-scenario consistency.
- Timeline alignment.
- Rate hierarchy preservation.
- Complete audit trail.

---

## 5. Position Calculation

### **5.1 Processing Order**

#### **Yearly Processing Sequence**
```python
def process_year(prior_position):
    # 1. Start with prior position
    position = prior_position.copy()
    
    # 2. Apply growth
    position.apply_growth_rates()
    
    # 3. Process cash flows
    position.handle_cash_flows()
    
    # 4. Calculate surplus
    position.update_surplus()
    
    # 5. Store results
    position.save()
```

---

## 6. SQL vs Python Handling

### **6.1 Handled in SQL**
✅ Retirement Age Must Be Before Final Age
```sql
CHECK (final_age > retirement_age)
```
✅ Start Year Must Be Before or Equal to End Year
```sql
CHECK (start_year <= end_year)
```
✅ Growth & Inflation Rate Limits
```sql
CHECK (nest_egg_growth_rate >= -200 AND nest_egg_growth_rate <= 200)
CHECK (inflation_rate >= -200 AND inflation_rate <= 200)
```
✅ Assets & Liabilities Cannot Be Negative
```sql
CHECK (value >= 0)
```
✅ Scenario Exclusion Works Properly
```sql
exclude_from_projection INTEGER DEFAULT 0
```

### **6.2 Handled in Python**
🚨 Partial-Year Calculation for First Year (SQL does not support partial-year calculations)
🚨 Overlapping Asset Growth Adjustments Must Be Prevented
🚨 Fallback Behavior for Missing Growth Rate Adjustments (stepwise → independent → scenario → base)

---

## 7. Summary of Cash Flow Components

| Category | Field | Purpose |
|----------|------------------------------|--------------------------------|
| **Inflows** | `inflows_outflows.annual_amount` | General inflows |
| | `retirement_income_plans.annual_income` | Structured retirement income |
| **Outflows** | `inflows_outflows.annual_amount` | General outflows |
| | `base_assumptions.annual_retirement_spending` | Retirement spending |
| **Surplus** | `inflows_outflows.retain_surplus` | Determines if inflow contributes to surplus |
| | `nest_egg_yearly_values.surplus` | Stores surplus for future growth |
| **Deficit** | `nest_egg_yearly_values.withdrawals` | Reflects drawdown from nest egg |

---

## 8. Output & Visualization

### **Position Tracking**
- Year-by-year nest egg values
- Surplus component progression
- Growth source attribution
- Final position projections

### **Scenario Comparison**
- Multiple scenario overlay
- Growth rate effectiveness
- Surplus accumulation patterns
- Withdrawal sustainability

### **Component Analysis**
- Asset growth breakdown
- Cash flow patterns
- Liability progression
- Income source impact

