# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this directory.

## Project Overview

Week 4 starter application — a "developer's command center" with FastAPI backend, SQLite persistence, and vanilla JS frontend. This is a playground for experimenting with Claude Code automations (slash commands, CLAUDE.md files, SubAgents).

## Common Commands

```bash
# Run from week4 directory
make run        # Start FastAPI server (uvicorn backend.app.main:app --reload)
make test       # Run pytest (PYTHONPATH=. pytest -q backend/tests)
make format     # Run black and ruff --fix
make lint       # Run ruff checks only
make seed       # Initialize SQLite with seed data
```

## Code Architecture

```
week4/
  backend/app/
    main.py        # FastAPI app entry point, router registration
    db.py          # SQLAlchemy setup, SessionLocal, seed logic
    models.py      # SQLAlchemy models (Note, ActionItem)
    schemas.py     # Pydantic schemas (NoteCreate, ActionItemCreate, etc.)
    routers/       # API endpoints
      notes.py
      action_items.py
    services/
      extract.py   # Business logic (LLM extraction)
  backend/tests/   # Pytest test files
  frontend/        # Static assets (index.html, app.js, styles.css)
  data/            # SQLite database and seed.sql
  docs/            # TASKS for agent-driven workflows
```

## API Routes

- `GET /` — serves `frontend/index.html`
- `GET /static/*` — serves static frontend assets
- `POST /notes/` — create a note
- `GET /notes/` — list all notes
- `POST /action-items/` — create an action item
- `GET /action-items/` — list all action items
- `PATCH /action-items/{id}` — update an action item

## Database

- SQLite at `data/app.db` (created on startup if missing)
- Seed data loaded from `data/seed.sql` on first run
- Models: `Note` (id, title, content), `ActionItem` (id, description, completed)

## Testing

Tests use a temporary SQLite database via fixture in `conftest.py`. Run individual test files with:
```bash
PYTHONPATH=. pytest -q backend/tests/test_notes.py
```
