### **Phase 1: Core Data Infrastructure**  
**Objective:** *Establish bulletproof data layer with validation*  

1. Implement CRUD for all critical tables:  
   - **Households:** Manage households (`households.py`).
   - **Plans:** Attach financial plans to households (`plans.py`).
   - **Scenarios:** Store scenario variations (`scenarios.py`).
   - **Assets:** Track investments and retirement assets (`assets.py`).
   - **Liabilities:** Manage debts and obligations (`liabilities.py`).
   - **Inflows/Outflows:** Record scheduled income and expenses (`inflows_outflows.py`).
   
2. Enforce SQL constraints & indexing for integrity and performance.  
3. Validate view `scenario_complete_state` inheritance logic.  
4. Build data merger helper (base + scenario deltas).  
5. Add logging for data pipeline monitoring.  

**✓ Check:** Modified scenario returns merged data without breaking base records.  

---

### **Phase 2: Financial Engine Skeleton**  
**Objective:** *Create working year-over-year progression*  

1. Implement `process_year()` function:
   - Retrieve prior year position from `nest_egg_yearly_values`.
   - Apply growth rates using hierarchy (`combined_growth_adjustments`).
   - Process cash flows (`yearly_cashflow_components`).
   - Compute new surplus (excess inflows after spending).
   - Update nest egg balance and surplus components in `nest_egg_yearly_values`.
   
2. Connect to `nest_egg_yearly_values` table.  
3. Add basic cash flow collector (inflows/outflows).  
4. Implement timeline validation helper.  

**✓ Check:** Empty scenario produces identical annual values.  

---

### **Phase 3: Growth Rate System**  
**Objective:** *Implement rate hierarchy with override capabilities*  

1. Establish growth rate priority:
   - Stepwise → Asset-specific → Scenario → Base.
2. Add growth audit trail to yearly values.
3. Build conflict detection for overlapping rates.

**✓ Check:** Modified rates alter projections predictably.  

---

### **Phase 4: Scenario Inheritance Engine**  
**Objective:** *Enable scenario modifications without base corruption*  

1. Implement delta storage system.
2. Build override merger helper (priority: scenario > asset > base).
3. Add age-based timeline alignment.
4. Develop scenario comparison endpoints.

**✓ Check:** Modified scenarios show deltas while preserving original data.  

---

### **Phase 5: Cash Flow & Surplus Calculus**  
**Objective:** *Handle money movement with precision*  

1. Implement inflation-adjusted cash flows.
2. Add surplus compounding logic.
3. Build deficit handling (nest egg withdrawals).
4. Connect retirement spending triggers.

**✓ Check:** Surpluses grow balances, deficits reduce nest egg.  

---

### **Phase 6: Temporal Alignment**  
**Objective:** *Sync financial events with reference timeline*  

1. Implement partial-year proration logic.
2. Add age-based milestone triggers.
3. Validate timeline continuity checks.
4. Synchronize multi-person household calculations.

**✓ Check:** Mid-year starts produce proportional first-year results.  

---

### **Phase 7: System Armoring**  
**Objective:** *Harden against edge cases & failures*  

1. Add negative balance prevention.
2. Implement growth rate boundary checks.
3. Build cash flow collision detection.
4. Add fallback values for missing data.

**✓ Check:** Invalid inputs fail cleanly with audit trails.  

---

### **Phase 8: Final Integration**  
**Objective:** *End-to-end validation with real data*  

1. Wire all systems together.  
2. Implement comprehensive test scenario:
   - Modified growth rates.
   - Overridden asset values.
   - Timeline adjustments.
3. Optimize SQL view performance.
4. Finalize API endpoints.  

**✓ Check:** Complex scenario shows distinct progression from base.

