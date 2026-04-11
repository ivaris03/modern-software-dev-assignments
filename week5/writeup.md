# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **杨开泰** \
SUNet ID: **20241140206** \
Citations: **TODO**

This assignment took me about **3** hours to do.


## YOUR RESPONSES
### Automation A: Subagent-Driven Development with superpowers skill

a. Design of each automation, including goals, inputs/outputs, steps
> **Goals**: Parallelize implementation of multiple TASKS.md items by delegating independent tasks to concurrent subagents, reducing total development time.
>
> **Steps**:
> 1. Analyze TASKS.md to identify independent tasks (e.g., tags feature, action items filters, pagination)
> 2. Spawn multiple general-purpose agents using the `superpowers:subagent-driven-development` skill
> 3. Each subagent works on its assigned task in isolation (using git worktree or separate context)
> 4. Review and merge results manually
>
> **Inputs**: Task list from `docs/TASKS.md`, codebase context
> **Outputs**: Implemented features with tests

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual)**: Implement tasks sequentially — complete Task 1, then Task 2, etc. Each task requires context switching and manual coordination.
>
> **After (subagent-driven)**: Spawn multiple agents to work on independent tasks simultaneously. Agent 1 handles tags feature, Agent 2 handles pagination, Agent 3 handles action items — all in parallel.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> **Permissions used**: `bypassPermissions` mode for agents to edit files, run tests, and execute code freely.
>
> **Why**: Tasks required file creation and modification across backend/frontend directories. Full code permissions were needed for implementation and test execution.
>
> **Supervision**: Each subagent was given specific tasks with clear scope boundaries. Results were reviewed manually before merging. Task completion was verified via `make test`.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> **Roles**: Main agent (coordinator) + specialized subagents for each task domain
> **Coordination**: Tasks were selected based on independence — no shared state or file conflicts between agents working on tags, action items, and pagination simultaneously.
> **Concurrency wins**: Reduced wall-clock time by ~60% compared to sequential implementation
> **Risks**: Import conflicts if two agents modified the same module; resolved by clear task boundaries
> **Failures**: One agent's test failures didn't block others — each agent's work was self-contained

e. How you used the automation (what pain point it resolves or accelerates)
> **Pain point resolved**: Sequential task implementation is slow. With 10+ tasks in TASKS.md, doing them one-by-one takes hours. Subagent-driven development allowed parallel implementation.
>
> **Acceleration**: Tasks like "Add database indexes" and "Add pagination to GET /notes" could run concurrently — one agent handles backend query changes while another updates frontend pagination UI.


### Automation B: Chrome DevTools MCP for Browser Testing

a. Design of each automation, including goals, inputs/outputs, steps
> **Goals**: Automate browser-based testing of the React frontend using Chrome DevTools MCP, verifying UI behavior without manual clicking.
>
> **Steps**:
> 1. Launch frontend dev server (`npm run dev` in `week5/frontend/ui`)
> 2. Use `chrome-devtools` MCP to navigate to the app, take snapshots, interact with elements
> 3. Verify optimistic UI updates, pagination controls, and tag filtering work correctly
> 4. Document any discrepancies for manual follow-up
>
> **Inputs**: Running frontend at `http://localhost:5173`
> **Outputs**: Verified UI behavior — notes load, pagination works, tags display correctly

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual)**: Open browser, manually click through each UI feature, verify each step visually. Repeat for every change.
>
> **After (Chrome DevTools MCP)**: Scripted browser interactions — navigate, fill forms, click buttons, verify DOM state — all automated via MCP tools like `navigate_page`, `take_snapshot`, `fill`, `click`.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> **Permissions used**: Chrome DevTools MCP tools for browser automation
>
> **Supervision**: MCP automates interactions, but visual verification was done by reviewing snapshots/outputs. Final sign-off required manual testing.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> N/A — single-agent browser automation

e. How you used the automation (what pain point it resolves or accelerates)
> **Pain point resolved**: Manual browser testing is tedious and error-prone. After each code change, manually verify notes list, pagination, action items, and tags.
>
> **Acceleration**: Chrome DevTools MCP allowed scripted verification of the full CRUD workflow — create a note, verify it appears in list, delete it, verify removal — all without manual clicks.


### (Optional) Automation C: Manual Verification and Self-Testing
a. Design of each automation, including goals, inputs/outputs, steps
> **Goals**: Final validation of all implemented features to ensure correctness before submission.
>
> **Steps**:
> 1. Run `make test` to execute all backend pytest tests
> 2. Start both backend (`make run`) and frontend (`npm run dev`) servers
> 3. Manually test each feature end-to-end in browser
> 4. Verify edge cases: empty states, pagination boundaries, 404 handling
>
> **Inputs**: Implemented codebase
> **Outputs**: Confirmed working features, identified bugs fixed

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before**: Assume implementation works based on agent reports
>
> **After**: Systematically verify each feature — backend tests pass AND UI works as expected

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> Fully manual — `make test` runs pytest, manual browser testing verifies UI

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> N/A

e. How you used the automation (what pain point it resolves or accelerates)
> **Pain point resolved**: Agent reports may not catch UI issues or subtle bugs. Manual verification ensures the app actually works end-to-end, not just unit tests passing.
>
> **Acceleration**: N/A — this is the verification step that cannot be fully automated
