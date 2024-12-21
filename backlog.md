### Issue 1: Update the check logic of `is_resolved`

**Description**  
Refine or replace the current `is_resolved` function/condition so it accurately reflects when an item (e.g., a bug ticket, work item) is truly resolved.

**Why**  
- Existing logic may fail in certain edge cases or not account for newly introduced states.  
- Ensuring accurate resolution status improves clarity for both developers and stakeholders.

**Acceptance Criteria**  
- [ ] `is_resolved` correctly identifies resolved vs. unresolved items in all relevant scenarios.  
- [ ] Existing and new tests pass without errors.  
- [ ] Code is documented with any new logic and edge cases.

**Labels**  
- `enhancement`  
- `backend`  
- `priority: high`  


### Issue 2: Create a script to clean log files for a specific task ID

**Description**  
Develop a script to handle cleaning (removing or archiving) old or large log files after a particular task ID finishes running.

**Why**  
- Prevents log files from growing unchecked.  
- Automates file cleanup once a task is complete.

**Acceptance Criteria**  
- [ ] Script locates and removes/archives logs specific to the provided task ID.  
- [ ] Script integrates with the existing workflow, triggering automatically or via a CLI call.  
- [ ] Sufficient logging or console output to confirm cleanup actions.

**Labels**  
- `enhancement`  
- `devops`  
- `priority: medium`

**Tasks or Checklists**  
   Use Markdown checkboxes to track sub-tasks:
   ```markdown
   - [ ] Sub-task 1
   - [ ] Sub-task 2
