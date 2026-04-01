# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this directory.

## Project Overview

Week 4 starter application — a "developer's command center" with FastAPI backend, SQLite persistence, and vanilla JS frontend. This is a playground for experimenting with Claude Code automations (slash commands, CLAUDE.md files, SubAgents).

## Common Commands

**Windows requires Conda environment activation via cmd.exe:**
```bash
# Run from week4 directory
cmd.exe //c "conda activate cs146s && uvicorn backend.app.main:app --reload"
cmd.exe //c "conda activate cs146s && set PYTHONPATH=. && pytest -q backend/tests/"
cmd.exe //c "conda activate cs146s && black backend/app/ frontend/"
```

Note: Makefile targets don't work directly because `conda activate` must run inside `cmd.exe`. Use the commands above instead.

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
cmd.exe //c "conda activate cs146s && set PYTHONPATH=. && pytest -q backend/tests/test_notes.py"
```
