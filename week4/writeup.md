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
