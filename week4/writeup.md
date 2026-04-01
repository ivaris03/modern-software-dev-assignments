# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **杨开泰** \
SUNet ID: **20241140206** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.


## YOUR RESPONSES
### Automation #1

**Automation: Auto-generate CLAUDE.md for Projects**

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> - Claude Code CLAUDE.md best practices: contextual guidance files that provide project-specific instructions to AI assistants
> - The `docs/TASKS.md` file in this project, which defines standard tasks that can be automated

b. Design of each automation, including goals, inputs/outputs, steps

**Goal**: Automatically generate a comprehensive CLAUDE.md file for a project directory by analyzing its structure and tech stack.

**Inputs**:
- Project directory path
- Existing source files (to detect language/framework)
- Standard project conventions (e.g., Makefile, package.json, pyproject.toml)

**Outputs**:
- A generated `CLAUDE.md` file with:
  - Project overview
  - Common commands (install, run, test, lint)
  - Code architecture/directory structure
  - API routes (if applicable)
  - Key dependencies
  - Coding style conventions

**Steps**:
1. Scan project directory structure (recursively list files)
2. Detect tech stack via file extensions and config files:
   - Python: `pyproject.toml`, `requirements.txt`, `setup.py`
   - JavaScript/TypeScript: `package.json`, `tsconfig.json`
   - Go: `go.mod`
   - Rust: `Cargo.toml`
3. Parse `Makefile` (if exists) to extract standard commands
4. Detect API framework (FastAPI, Express, Django, etc.)
5. Generate appropriate sections based on detected stack
6. Write CLAUDE.md to project root

c. How to run it (exact commands), expected outputs, and rollback/safety notes

**How to run**:
```bash
# Start Claude Code in the project directory
cd /path/to/project
claude

# In the Claude Code session, use /init to trigger CLAUDE.md generation
/init
```

Or trigger directly via command line:
```bash
claude "Analyze this project and write a CLAUDE.md file for: $(pwd)"
```

**Expected output**:
- A `CLAUDE.md` file is created in the project root
- The file contains project-specific guidance based on detected stack
- If CLAUDE.md already exists, it is overwritten (with backup)

**Rollback/Safety notes**:
- Before overwriting, backup existing CLAUDE.md to `CLAUDE.md.bak`
- The automation only writes to `CLAUDE.md`, never deletes files
- If generation fails, the original file (if any) remains intact

d. Before vs. after (i.e. manual workflow vs. automated workflow)

| Aspect | Before (Manual) | After (Automated) |
|--------|-----------------|-------------------|
| Time to create CLAUDE.md | 15-30 minutes | 30-60 seconds |
| Consistency | Varies by developer skill | Uniform structure and content |
| Coverage | Often incomplete (misses key commands) | Comprehensive based on detected stack |
| Maintenance | Easy to neglect updates | Can re-run to refresh |

**Before**:
1. Developer manually researches project structure
2. Writes CLAUDE.md from scratch or copies from another project
3. May miss important commands or conventions
4. Time: 15-30 minutes per project

**After**:
1. Run automation command
2. Claude Code analyzes project and generates CLAUDE.md
3. Developer reviews and refines if needed
4. Time: under 1 minute

e. How you used the automation to enhance the starter application

This automation was used to create the `CLAUDE.md` file for the Week 4 starter application. The generated file:

1. **Documents the project structure**: The backend/app/ organization (main.py, db.py, models.py, schemas.py, routers/, services/)
2. **Captures Makefile commands**: Instead of manually running `uvicorn` commands, users simply run `make run`, `make test`, etc.
3. **Documents the API routes**: All endpoints (notes, action-items) are documented with their HTTP methods and paths
4. **Records the tech stack**: FastAPI + SQLAlchemy + SQLite backend, vanilla JS frontend
5. **Provides testing guidance**: Shows how to run tests with the correct `PYTHONPATH` setting

The CLAUDE.md serves as the single source of truth for Claude Code when working in this project directory, enabling more context-aware assistance and reducing repetitive clarification questions.


### Automation #2

**Automation: Automated Code Review with Superpower's Code Reviewer Agent**

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> - Claude Code SubAgent framework: specialized agents that can be spawned to handle specific tasks autonomously
> - The `superpowers:code-reviewer` agent — a pre-built review agent that validates implementations against plans and coding standards
> - Code review best practices: systematic validation at logical chunk boundaries, not just at the end of development

b. Design of each automation, including goals, inputs/outputs, steps

**Goal**: Automatically trigger a code review after completing a significant project step, validating the implementation against the original plan and coding standards.

**Inputs**:
- Description of the completed project step (e.g., "finished implementing user authentication")
- Reference plan (e.g., TASKS.md, planning documents, or task list)
- Coding standards (e.g., CLAUDE.md conventions, style guides)
- Modified code files and their paths

**Outputs**:
- Review report identifying:
  - Deviations from the planned implementation
  - Coding standard violations
  - Potential bugs or issues
  - Areas that need refactoring
- Pass/fail status with actionable feedback

**Steps**:
1. Complete a logical chunk of work (feature, bug fix, refactor)
2. Document what was done and what the original plan was
3. Spawn the `superpowers:code-reviewer` agent with context:
   - The completed work description
   - The plan/requirements to validate against
   - Paths to modified files
4. Agent reads the relevant files and compares against the plan
5. Agent produces a structured review with findings
6. Developer addresses feedback or confirms the implementation is correct
7. Agent marks the review as complete

c. How to run it (exact commands), expected outputs, and rollback/safety notes

**How to run**:

Via Claude Code command (when you complete a major step):
```bash
# In Claude Code, after completing a feature:
I've finished implementing step 3 of the plan - please review it with the code-reviewer agent
```

Within a Claude Code session, invoke the agent using one of three patterns:

1. **Natural language** (Claude decides when to delegate):
   Simply name the subagent in your prompt, e.g.: "Please review the action_items.py implementation against TASKS.md using the code-reviewer subagent"

2. **@-mention** (guarantees the subagent runs for one task):
   ```
   @agent-superpowers:code-reviewer Review the action_items.py implementation against TASKS.md
   ```

3. **Session-wide** (whole session uses the subagent's system prompt):
   ```bash
   claude --agent superpowers:code-reviewer
   ```

**Expected output**:
- A structured code review report containing:
  - Summary of what was reviewed
  - List of findings (issues, suggestions, approvals)
  - Specific file/line references for any problems
  - Overall recommendation (approve, needs changes, needs rewrite)
- Example output format:
  ```
  ## Code Review: Action Items Endpoint Implementation

  ### Summary
  Reviewed: backend/app/routers/action_items.py, schemas.py
  Against: Plan in TASKS.md for Automation #2 requirements

  ### Findings
  ✅ PATCH endpoint correctly implements partial update
  ⚠️ Missing input validation for empty description
  ❌ ActionItemCreate schema missing from schemas.py

  ### Recommendation
  Needs changes: Address schema definition before merging.
  ```

**Rollback/Safety notes**:
- The review agent only reads files and produces reports — it never modifies code
- All review findings are suggestions; developer retains full control over whether to act
- If agent produces incorrect findings, document the discrepancy for future agent improvements
- Reviews can be re-run after making corrections to verify fixes

d. Before vs. after (i.e. manual workflow vs. automated workflow)

| Aspect | Before (Manual) | After (Automated) |
|--------|-----------------|-------------------|
| Review timing | Often skipped or done last-minute | Triggered immediately at logical completion points |
| Consistency | Varies by developer diligence | Uniform review criteria via agent |
| Coverage | May miss subtle issues | Thorough line-by-line validation |
| Documentation | Reviews exist only in comments/commits | Structured review report for future reference |
| Speed | Manual review: 15-30 min | Agent review: 1-2 min |

**Before**:
1. Developer finishes coding a feature
2. (Often skipped) Opens code side-by-side with requirements
3. Mentally checks for issues — no systematic approach
4. May miss edge cases, standard violations, or plan deviations
5. No record of what was reviewed or what issues were found
6. Time: 15-30 minutes (if done thoroughly) or skipped entirely

**After**:
1. Developer finishes coding a feature
2. Immediately spawns code-reviewer agent with context
3. Agent systematically validates against plan and standards
4. Structured report is generated in under 2 minutes
5. Developer addresses actionable feedback
6. Re-review can be triggered to confirm fixes
7. Time: 1-2 minutes, with documentation

e. How you used the automation to enhance the starter application

This automation was used to validate the Week 4 starter application's implementation against the original plan:

1. **Router Implementation Review**: After implementing `action_items.py` and `notes.py` routers, the code-reviewer agent validated that all endpoints matched the API specification in the assignment.

2. **Schema Validation**: The agent confirmed that Pydantic schemas (NoteCreate, ActionItemCreate) correctly matched the SQLAlchemy models and API requirements.

3. **Code Standard Enforcement**: The review verified that:
   - All API routes follow RESTful conventions
   - Error handling is consistent across endpoints
   - Database session management is proper (SessionLocal pattern)
   - Frontend static file serving is correctly configured

4. **Catch Issues Early**: The systematic review caught a missing field in the ActionItemCreate schema that would have caused a runtime error — this was caught and fixed before any manual testing.

5. **Documentation**: The review reports serve as an audit trail documenting the code quality at each checkpoint, which is valuable for future maintenance and for demonstrating systematic development practices.

The code-reviewer agent transforms code review from an optional, inconsistent practice into a disciplined, automated checkpoint that runs consistently after every significant implementation step.


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> TODO

b. Design of each automation, including goals, inputs/outputs, steps
> TODO

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> TODO

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

e. How you used the automation to enhance the starter application
> TODO
