# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this directory.

## Project Overview

Week 4 starter application — a "developer's command center" with FastAPI backend, SQLite persistence, and vanilla JS frontend. This is a playground for experimenting with Claude Code automations (slash commands, CLAUDE.md files, SubAgents).

## Common Commands

```bash
make run        # Start server at http://127.0.0.1:8000
make test       # Run all tests
make format     # Format code with black
make lint       # Run ruff check
make seed       # Seed the database
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
- `GET /notes/search/?q=...` — search notes (case-insensitive)
- `PUT /notes/{id}` — update a note
- `DELETE /notes/{id}` — delete a note
- `POST /notes/{id}/extract` — extract action items from note
- `POST /action-items/` — create an action item
- `GET /action-items/` — list all action items
- `PUT /action-items/{id}/complete` — mark action item as complete

## Database

- SQLite at `data/app.db` (created on startup if missing)
- Seed data loaded from `data/seed.sql` on first run
- Models: `Note` (id, title, content), `ActionItem` (id, description, completed)

## Testing

```bash
make test       # Run all tests
```
