# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Week 5: Full-stack note-taking app with content extraction. Supports notes with tags (many-to-many), action items, and regex-based extraction of hashtags/action items from note content.

## Common Commands

From the `week5/` directory:

```bash
# Backend (FastAPI + SQLite)
make run          # Start uvicorn server (requires PYTHONPATH=.)
make test         # Run pytest
make seed         # Seed database with sample data
make format       # Run black and ruff
make lint         # Run ruff only

# Single test
cd backend && PYTHONPATH=. pytest tests/test_notes.py -v

# Frontend (React + Vite)
cd frontend/ui
npm run dev       # Start dev server
npm run build     # Build for production (outputs to ../dist)
npm run test      # Run Vitest tests
npm run lint      # Run ESLint
```

## Architecture

### Backend (`week5/backend/`)

- **FastAPI** app with SQLAlchemy ORM and SQLite
- **Models**: `Note`, `ActionItem`, `Tag` (many-to-many via `note_tags` join table)
- **Routers**: `/notes`, `/action-items`, `/tags` — all under API prefix
- **Services**: `extract.py` — regex extraction of `#hashtags` and action items (lines starting with `- [ ]` or `- [x]`)
- **Response envelope**: API wraps responses in `{ok: true, data: ...}` or `{ok: false, error: {...}}` via `SuccessEnvelope`/`ErrorEnvelope` Pydantic schemas

### Frontend (`week5/frontend/ui/`)

- **React 19** with Vite 8, no framework router
- **Components**: `NoteForm`, `NoteList`, `ActionItemForm`, `ActionItemList`
- **API client**: `src/services/api.js` — axios-like fetch wrapper
- **Testing**: Vitest + Testing Library, test files co-located with components (`*.test.jsx`)
- **Build output**: `week5/frontend/dist/` (not committed to source)

### API Design

- Notes support pagination (`page`, `page_size`), search (`q`), tag filtering (`tag_id`), and sorting (`sort`: `created_desc|created_asc|title_asc|title_desc`)
- `POST /notes/{note_id}/extract?apply=false` — extracts hashtags and action items from note content without persisting. Set `apply=true` to persist tags and create action items.
- `POST /action-items/bulk-complete` — accepts `{ids: [...]}` to complete multiple items at once
