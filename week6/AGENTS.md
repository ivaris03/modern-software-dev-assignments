# AGENTS.md

Guidance for Codex and other coding agents working in `week6/`.

## Project Scope

Week 6 is a Semgrep security assignment. The app is a small FastAPI + SQLAlchemy +
SQLite backend with a vanilla HTML/CSS/JS frontend. The goal is to run Semgrep,
triage findings, and fix at least three security issues while keeping the app and
tests working.

## Directory Layout

```text
week6/
  backend/
    app/
      main.py          # FastAPI app setup
      db.py            # SQLite engine/session helpers and seed loading
      models.py        # SQLAlchemy models
      routers/         # API route modules
      schemas.py       # Pydantic schemas
      services/        # Reusable backend logic
    tests/             # Pytest tests
  data/
    seed.sql
  frontend/
    index.html
    app.js
    styles.css
  requirements.txt     # Intentionally old dependencies for Semgrep SCA findings
  Makefile
  writeup.md           # Assignment write-up
```

## Environment

Use the Conda environment named `cs146s` for verification on this machine.

From `week6/`, run tests with:

```powershell
conda run -n cs146s python -m pytest -q backend\tests
```

The `Makefile` also defines:

```bash
make run
make test
make format
make lint
make seed
```

On Windows, `make test` may fail before pytest starts because of Git Bash signal
pipe issues. Prefer the `conda run -n cs146s ... pytest` command above when that
happens.

## Semgrep

Run the assignment scan from the repository root, not from `week6/`:

```powershell
semgrep ci --subdir week6
```

Semgrep scans only git-tracked files in CI mode. If a new file should be scanned,
make sure it is tracked before relying on `semgrep ci` results.

## Security Fix Guidelines

- Prefer SQLAlchemy ORM expressions or bound parameters. Do not build SQL with
  f-strings, `%` formatting, or string concatenation using request data.
- Do not use `eval`, `exec`, or dynamic import paths for user-controlled input.
- Do not pass user-controlled strings to `subprocess` with `shell=True`. Prefer
  fixed command allowlists and argument arrays.
- Restrict filesystem access to explicit safe directories; never open arbitrary
  user-provided paths directly.
- Treat dynamic URL fetches as SSRF-sensitive. Validate scheme, host, and purpose
  before fetching.
- Keep CORS wildcard origins limited to local development only. For production,
  configure explicit allowed origins.
- Dependency upgrades can fix Semgrep SCA findings, but this assignment includes
  very old pinned versions. Upgrade carefully and run the tests after any change.

## Current Code Notes

- Route order matters in FastAPI/Starlette. Register fixed routes such as
  `/notes/unsafe-search` before catch-all parameter routes like `/notes/{note_id}`.
- `backend/app/routers/notes.py` contains security-sensitive debug endpoints used
  by the assignment. Keep fixes minimal and covered by tests.
- `backend/tests/test_notes.py` includes regression tests for safe arithmetic
  evaluation, command allowlisting, and SQL-injection-safe search behavior.

## Style

- Keep Python code formatted with Black and lintable with Ruff.
- Use 4-space indentation and `snake_case` names.
- Keep route code small; place reusable business logic in `services/` when it
  grows beyond simple CRUD behavior.
- Preserve the assignment's teaching intent: make targeted security fixes and
  document them in `writeup.md` rather than doing broad rewrites.
