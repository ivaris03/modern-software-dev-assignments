# Repository Guidelines

## Project Structure & Module Organization
This repository is organized by assignment week. `week1/` contains standalone Python exercises plus small data files in `week1/data/`. `week2/` introduces the app layout with `app/`, `frontend/`, and `tests/`. From `week4/` through `week7/`, each week follows a consistent full-stack pattern: `backend/app/` for FastAPI code, `backend/tests/` for pytest suites, `frontend/` for static assets, `data/seed.sql` for SQLite seed data, and `docs/` for task notes. Root files such as `pyproject.toml` and `poetry.lock` define shared dependencies and tool settings.

## Build, Test, and Development Commands
Install shared dependencies once from the repository root:

```bash
poetry install --no-interaction
poetry run pre-commit install
```

Run standalone week 1 scripts directly, for example:

```bash
poetry run python week1/rag.py
```

For app-based weeks, work inside the target folder, for example `week7/`:

```bash
make run    # start FastAPI with reload
make test   # run backend pytest suite
make format # run black and ruff --fix
make lint   # run ruff checks only
make seed   # initialize SQLite seed data
```

## Coding Style & Naming Conventions
Use 4-space indentation and keep Python lines within 100 characters, matching the root Black and Ruff configuration. Prefer `snake_case` for files, functions, and variables, and `PascalCase` for Pydantic or SQLAlchemy models. Keep API routes in `routers/`, reusable logic in `services/`, and persistence/schema code in `db.py`, `models.py`, and `schemas.py`. Frontend assets stay simple and framework-free: `index.html`, `app.js`, and `styles.css`.

## Testing Guidelines
Pytest is the standard test runner. Name test files `test_*.py` and mirror the feature under test, such as `test_notes.py` or `test_action_items.py`. Use `poetry run pytest week2/tests -q` for earlier weeks, or `cd week7 && make test` for the later backend template. Any change to routes, extraction logic, database behavior, or schemas should include matching test updates.

## Commit & Pull Request Guidelines
Recent commits use short, direct subjects such as `week7`, `update quickstart`, and `edit assignment.md`. Keep commit titles concise, imperative, and, when useful, scoped by week. Pull requests should identify the affected week(s), summarize user-visible or API-visible changes, list the commands run for validation, and include screenshots only when frontend behavior changes.
