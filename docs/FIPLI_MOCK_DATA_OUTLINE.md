# FIPLI Test Data Documentation

// THIS DATA IS IN THE DATABASE backend\database\FIPLI.db AND READY FOR TESTING 

## Core Structure

### Base Household (household_id: 1)
- Name: TEST_HOUSEHOLD
- Members:
  - PERSON_1 (person_id: 1): Born 1979, Base retirement 65, Final age 95
  - PERSON_2 (person_id: 2): Born 1981, Base retirement 65, Final age 95

### Base Plan (plan_id: 1)
- Name: TEST_PLAN
- Reference Person: PERSON_1 (person_id: 1)
- Creation Year: 2025
- Base Assumptions:
  - Nest Egg Growth Rate: 6.0%
  - Inflation Rate: 2.5%
  - Annual Retirement Spending: $100,000

### Asset Categories
- CATEGORY_1 (asset_category_id: 1, household_id: 1)

## Asset Groups

### Base Scenario Assets (plan_id: 1)
1. ASSET_1 (asset_id: 1)
   - Value: $100,000
   - Owner: PERSON_1
   - Category: CATEGORY_1
   - Base growth rate
   - Used in: Scenario 1

2. ASSET_2 & ASSET_3 (asset_ids: 2, 3)
   - Values: $200,000, $300,000
   - Owner: PERSON_1
   - Category: CATEGORY_1
   - Base growth rate
   - Used in: Scenario 2

3. ASSET_4 (asset_id: 4)
   - Value: $100,000
   - Owner: PERSON_1
   - Excluded from nest egg
   - Used in: Scenario 3

4. ASSET_5 (asset_id: 5)
   - Value: $100,000
   - Owner: PERSON_1
   - Independent growth: 2.0%
   - Used in: Scenario 4

### Growth Test Assets (plan_id: 1)
5. GROWTH_1 through GROWTH_5 (asset_ids: 6-10)
   - All $100,000 base value
   - Owner: PERSON_1
   - Growth variations:
     - GROWTH_2 (id: 7): 8.0% independent rate
     - GROWTH_4 (id: 9): 6.0% base, 8.0% adjustment 2025
     - GROWTH_5 (id: 10): 7.0% base, 9.0% adjustment 2025-2026
   - Used in: Scenarios 6-10

### Timeline Test Assets (plan_id: 1)
6. TIME_1 through TIME_5 (asset_ids: 11-15)
   - All $100,000 base value
   - Ownership patterns:
     - TIME_1 (id: 11): PERSON_1
     - TIME_2 (id: 12): PERSON_1
     - TIME_3 (id: 13): Both persons
     - TIME_4 (id: 14): PERSON_1
     - TIME_5 (id: 15): Both persons
   - Growth adjustment:
     - TIME_5: 4.0% for 2025-2026
   - Used in: Scenarios 11-15

### Override Test Assets (plan_id: 1)
7. OVERRIDE_1 through OVERRIDE_5 (asset_ids: 16-20)
   - All $100,000 base value
   - Owner: PERSON_1
   - Scenario overrides:
     - OVERRIDE_1: Value to $150,000
     - OVERRIDE_2: Value to $200,000, 9.0% growth
     - OVERRIDE_3: Value to $250,000, 10.0% growth
     - OVERRIDE_4: Value to $300,000, 8.0% growth
     - OVERRIDE_5: Value to $350,000, 11.0% growth
   - Used in: Scenarios 16-20

### Complex Test Assets (plan_id: 1)
8. COMPLEX_1 through COMPLEX_5 (asset_ids: 21-25)
   - Values:
     - COMPLEX_1: $100,000
     - COMPLEX_2: $200,000
     - COMPLEX_3: $300,000
     - COMPLEX_4: $150,000
     - COMPLEX_5: $250,000
   - Ownership:
     - COMPLEX_1: Both persons
     - COMPLEX_2: PERSON_1
     - COMPLEX_3: Both persons
     - COMPLEX_4: PERSON_2
     - COMPLEX_5: Both persons
   - Used in: Scenarios 21-25

## Liability Structure (plan_id: 1)

### Categories (household_id: 1)
- MORTGAGE (liability_category_id: 1)
- PERSONAL_LOANS (liability_category_id: 2)
- CREDIT_CARDS (liability_category_id: 3)

### Liabilities
1. PRIMARY_HOME (liability_id: 1)
   - Value: $300,000
   - Rate: 4.5%
   - Scenario 16 override: $250,000 @ 5.0%

2. CAR_LOAN (liability_id: 2)
   - Value: $25,000
   - Rate: 6.0%
   - Scenario 17 override: $20,000

3. CREDIT_CARD_1 (liability_id: 3)
   - Value: $5,000
   - Rate: 18.0%
   - Scenario 18 override: Rate to 15.0%

## Income Plans (plan_id: 1)

### Retirement Income
1. RET_1 (income_plan_id: 1)
   - Amount: $40,000
   - Start: Age 65
   - Owner: PERSON_1
   - Scenario 13 override: $45,000 starting at 63

2. RET_2 (income_plan_id: 2)
   - Amount: $30,000
   - Start: Age 67
   - Owner: PERSON_2

3. PENSION_1 (income_plan_id: 3)
   - Amount: $50,000
   - Start: Age 65
   - Owner: PERSON_1
   - Scenario 22 override: $55,000

4. SOCIAL_SECURITY_1 (income_plan_id: 4)
   - Amount: $35,000
   - Start: Age 67
   - Owner: PERSON_1
   - Scenario 25 override: $40,000 starting at 70

5. PART_TIME_WORK (income_plan_id: 5)
   - Amount: $20,000
   - Ages: 65-70
   - Owner: PERSON_2

## Cash Flows (plan_id: 1)

### Base Flows
- INFLOW_1 (inflow_outflow_id: 1)
  - Amount: $100,000/year
  - Period: 2025-2044
  - Inflation adjusted

- OUTFLOW_1 (inflow_outflow_id: 2)
  - Amount: $50,000/year
  - Period: 2025-2044
  - Inflation adjusted

### Timeline Test Flows
- TIME_INFLOW_1 (id: 3): $120,000 in 2025
- TIME_INFLOW_2 (id: 4): $100,000/year, 2025-2044
- TIME_INFLOW_3_P1 (id: 5): $80,000/year, 2025-2044
- TIME_INFLOW_3_P2 (id: 6): $60,000/year, 2025-2046
- TIME_EVENT_1 (id: 7): $50,000 outflow in 2030
- TIME_EVENT_2 (id: 8): $30,000 outflow in 2035

## Scenarios Detail (All under plan_id: 1)

### Base Scenarios (1-5)
1. BASE_1 (scenario_id: 1)
   - Purpose: Single asset base test
   - Assets: ASSET_1
   - No assumption overrides

2. BASE_2 (scenario_id: 2)
   - Purpose: Multiple asset test
   - Assets: ASSET_2, ASSET_3
   - No assumption overrides

3. BASE_3 (scenario_id: 3)
   - Purpose: Nest egg exclusion test
   - Assets: ASSET_4 (excluded)
   - No assumption overrides

4. BASE_4 (scenario_id: 4)
   - Purpose: Independent growth test
   - Assets: ASSET_5 (2.0% growth)
   - No assumption overrides

5. BASE_5 (scenario_id: 5)
   - Purpose: Cash flow testing
   - No assumption overrides

### Growth Scenarios (6-10)
6. GROWTH_1 (scenario_id: 6)
   - Purpose: Base growth test
   - Asset: GROWTH_1
   - Uses base 6.0% growth

7. GROWTH_2 (scenario_id: 7)
   - Purpose: Asset-specific growth
   - Asset: GROWTH_2
   - Independent rate: 8.0%

8. GROWTH_3 (scenario_id: 8)
   - Purpose: Scenario override
   - Asset: GROWTH_3
   - Override: 7.0% growth rate

9. GROWTH_4 (scenario_id: 9)
   - Purpose: Stepwise adjustment
   - Asset: GROWTH_4
   - Adjustment: 8.0% for 2025

10. GROWTH_5 (scenario_id: 10)
    - Purpose: Growth hierarchy
    - Asset: GROWTH_5
    - Multiple rates:
      - Asset base: 7.0%
      - Adjustment: 9.0% (2025-2026)
      - Scenario: 8.0%

### Timeline Scenarios (11-15)
11. TIME_1 (scenario_id: 11)
    - Purpose: Partial year test
    - Asset: TIME_1
    - Flow: TIME_INFLOW_1

12. TIME_2 (scenario_id: 12)
    - Purpose: Mid-year retirement
    - Asset: TIME_2
    - Person override: PERSON_1 retires at 62

13. TIME_3 (scenario_id: 13)
    - Purpose: Two-person timing
    - Asset: TIME_3 (joint)
    - Person overrides:
      - PERSON_1: retire at 65
      - PERSON_2: retire at 67
    - Income override: RET_1 to $45,000 at 63

14. TIME_4 (scenario_id: 14)
    - Purpose: Event scheduling
    - Asset: TIME_4
    - Events: TIME_EVENT_1, TIME_EVENT_2

15. TIME_5 (scenario_id: 15)
    - Purpose: Combined timeline
    - Asset: TIME_5 (joint)
    - Growth: 4.0% 2025-2026

### Override Scenarios (16-20)
16. OVERRIDE_1 (scenario_id: 16)
    - Asset override: OVERRIDE_1 to $150,000
    - Liability override: PRIMARY_HOME to $250,000 @ 5.0%
    - Growth override: 7.0%

17. OVERRIDE_2 (scenario_id: 17)
    - Asset override: OVERRIDE_2 to $200,000 @ 9.0%
    - Liability override: CAR_LOAN to $20,000
    - Growth: 8.0%
    - Inflation: 3.0%

18. OVERRIDE_3 (scenario_id: 18)
    - Asset override: OVERRIDE_3 to $250,000 @ 10.0%
    - Liability override: CREDIT_CARD_1 to 15.0%
    - Growth: 9.0%
    - Inflation: 3.5%

19. OVERRIDE_4 (scenario_id: 19)
    - Asset override: OVERRIDE_4 to $300,000 @ 8.0%
    - Growth: 7.5%

20. OVERRIDE_5 (scenario_id: 20)
    - Asset override: OVERRIDE_5 to $350,000 @ 11.0%
    - Growth: 8.5%
    - Inflation: 4.0%

### Complex Scenarios (21-25)
21. COMPLEX_1 (scenario_id: 21)
    - Purpose: Joint ownership base
    - Asset: COMPLEX_1 (joint)
    - No assumption overrides

22. COMPLEX_2 (scenario_id: 22)
    - Purpose: Different retirement ages
    - Asset: COMPLEX_2 (PERSON_1)
    - Person overrides:
      - PERSON_1: retire at 62
      - PERSON_2: retire at 68
    - Income override: PENSION_1 to $55,000
    - Growth: 7.0%

23. COMPLEX_3 (scenario_id: 23)
    - Purpose: Complex ownership
    - Asset: COMPLEX_3 (joint)
    - Growth: 8.0%

24. COMPLEX_4 (scenario_id: 24)
    - Purpose: Multiple income
    - Asset: COMPLEX_4 (PERSON_2)
    - Growth: 7.5%
    - Inflation: 3.0%

25. COMPLEX_5 (scenario_id: 25)
    - Purpose: Full complexity
    - Asset: COMPLEX_5 (joint)
    - Income override: SOCIAL_SECURITY_1 to $40,000 at 70
    - Growth: 8.5%
    - Inflation: 3.5%

## Testing Validation Points
- Each scenario tests specific combinations of features
- All IDs are explicitly referenced for traceability
- Dates consistently use 2025 as base year
- All monetary values use clean numbers
- Growth rates range from 2.0% to 11.0%
- Clear ownership and relationship patterns

