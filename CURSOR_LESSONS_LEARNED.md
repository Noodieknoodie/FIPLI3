# LESSONS_LEARNED

## Format:
🔴 Issue/Trap
✅ Correct Approach
📝 Context (optional, only if needed)

## Database Operations
🔴 Plan creation initially failed because base assumptions weren't created in the same transaction
✅ Always create related required records (like base_assumptions) in the same transaction as the main record
📝 SQLite's foreign key constraints require base_assumptions to exist for each plan