	1.	Start with last year’s values – Nest egg balance, asset values, and surplus from the prior year.
	2.	Apply growth to individual assets per hierarchy:
	•	If asset-level stepwise period is active, apply that first.
	•	Else, if asset override is active, apply that next.
	•	Else, follow default nest egg growth settings, which could be:
	•	A fixed default rate, or
	•	A scenario-level stepwise injection, if one is active for the nest egg.
	3.	Apply default nest egg growth rate to prior-year surplus – Treat the surplus from last year as an asset and apply nest egg growth rules to it.
	4.	Combine all assets after growth is applied – Sum all updated asset values.
	5.	Inflate relevant cash flows – Adjust income, expenses, and retirement spending based on inflation settings.
	6.	Apply inflows and outflows – Add income and other inflows, subtract expenses and withdrawals.
	7.	Add surplus cash flow into the nest egg – If inflows exceed outflows, the remaining amount is reinvested into the nest egg.
	8.	Store updated values for next year – Save the new nest egg balance, updated asset values, and surplus amount for the next cycle.


# How each step maps to the schema:

1. LAST YEAR'S VALUES
```
-- nest_egg_yearly_values table stores these exactly as needed
nest_egg_balance
surplus
-- Plus individual asset values from scenario_complete_state view
```

2. GROWTH HIERARCHY
The schema supports this exact priority chain:
```
-- asset_growth_adjustments for stepwise periods
-- scenario_assets for asset-specific overrides
-- scenario_assumptions for default nest egg rates
-- scenario_growth_adjustments for stepwise nest egg adjustments
```

3. SURPLUS GROWTH
```
-- nest_egg_yearly_values tracks both:
surplus
surplus_contributions
-- Allowing differentiation between old and new surplus
```

4-8. CASHFLOW PROCESSING
The `yearly_cashflow_components` view  supports this by providing:
```
-- All components needed for the calculation:
nest_egg_balance
withdrawals
contributions
investment_growth
scheduled_inflows
scheduled_outflows
retirement_income
```

