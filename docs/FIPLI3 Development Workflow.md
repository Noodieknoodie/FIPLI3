# DEVELOPMENT_WORKFLOW.md

# Development Sequence

!!!! The database is POPULATED WITH COMPLETE MOCK DATA - TESTING SHOULD BE DONE WITH THIS DATA. !!!! 

## 1. Data Foundation Layer
Build this first - everything depends on solid data access.

### Step 1: Basic View Integration
1. Start with scenario_complete_state
  - First just verify you can get a complete scenario state
  - Don't worry about calculations yet
  - Just confirm the data is combining correctly

2. Move to yearly_cashflow_components
  - Pull basic yearly breakdowns
  - Verify all cash flows appear
  - Confirm timeline alignment

3. Test scenario_final_positions
  - Get end-state projections working
  - Verify surplus tracking fields
  - Check age/year mappings

### Step 2: Scenario System Foundation
1. Create a basic scenario
2. Verify override inheritance
3. Modify some values
4. Confirm changes appear in views

### Step 3: Timeline Testing
Create test scenarios that validate:
- Partial first year handling
- Age progression
- Event scheduling
- End point determination

## 2. Calculation Engine Construction
Build this after data access is solid.

### Step 1: Basic Tracking
1. Implement simple nest egg balance tracking
2. Add basic growth application
3. Get cash flows working
4. Test with simple scenarios

### Step 2: Growth System
1. Start with just base growth rate
2. Add asset-specific overrides
3. Implement stepwise adjustments
4. Test the full hierarchy

### Step 3: Surplus System
1. Build basic surplus tracking
2. Add growth on surplus
3. Implement new surplus accumulation
4. Test full surplus lifecycle

### Step 4: Full Integration
1. Combine all calculations
2. Test complex scenarios
3. Verify all components work together
4. Validate against expected results

## 3. Scenario Management
Only build this after calculations work perfectly.

### Step 1: Creation & Modification
1. Build scenario creation
2. Implement override system
3. Test modification patterns
4. Verify inheritance

### Step 2: Comparison System
1. Build side-by-side comparison
2. Test multiple scenarios
3. Verify timeline alignment
4. Validate calculations

### Step 3: Advanced Features
1. Add scenario cloning
2. Implement batch updates
3. Build comparison tooling
4. Test edge cases

## 4. Testing & Validation
Comprehensive testing after core features work.

### Step 1: Base Testing
1. Test all calculation paths
2. Verify scenario inheritance
3. Validate timeline handling
4. Check data integrity

### Step 2: Integration Testing
1. Test full workflows
2. Verify complex scenarios
3. Validate long projections
4. Check performance

### Step 3: Edge Cases
1. Test partial years
2. Verify extreme values
3. Check error handling
4. Validate boundaries

## 5. Output Generation
Final stage - only after everything else works.

### Step 1: Basic Output
1. Implement yearly data
2. Build comparison outputs
3. Create summary data
4. Test formatting

### Step 2: Advanced Output
1. Add detailed breakdowns
2. Implement filtering
3. Build aggregation tools
4. Test all formats

# Checkpoint Requirements

## After Data Foundation
- All views returning correct data
- Scenario inheritance working
- Timeline mapping accurate
- Base facts retrievable

## After Calculations
- Growth rates applying correctly
- Surplus tracking accurate
- Cash flows processing properly
- Final positions calculating

## After Scenario System
- Overrides working perfectly
- Comparisons functioning
- Timeline consistent
- Modifications tracking

## Before Release
- All calculations verified
- Performance acceptable
- Edge cases handled
- Output validated