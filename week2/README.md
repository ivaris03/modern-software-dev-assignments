# Action Item Extractor

A FastAPI-based web application that extracts actionable items from plain text or meeting notes. Supports both rule-based extraction and LLM-powered extraction via Ollama.

## Project Overview

This project is part of CS146S: The Modern Software Developer (Stanford, Fall 2025). It demonstrates full-stack development with FastAPI, SQLite, and vanilla JavaScript.

## Features

- **Rule-based extraction**: Identifies action items from bullet points, checkbox markers (`[ ]`, `[todo]`), and keyword prefixes (`TODO:`, `action:`, `next:`)
- **LLM-powered extraction**: Uses Ollama (local LLM) for more intelligent action item extraction
- **Note storage**: Persists notes and extracted action items to SQLite
- **Mark as done**: Track completion status of action items

## Setup and Run

### 1. Install Dependencies

```bash
# From the project root
poetry install --no-interaction
```

### 2. Configure Environment (optional)

Create a `.env` file in the week2 directory to customize the Ollama model:

```env
OLLAMA_MODEL=llama3.1:8b
```

### 3. Start the Server

```bash
poetry run uvicorn week2.app.main:app --reload
```

The application will be available at `http://localhost:8000`.

## API Endpoints

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/{note_id}` | Get a specific note |

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/action-items/extract` | Extract action items (rule-based) |
| `POST` | `/action-items/extract-llm` | Extract action items (LLM-powered) |
| `GET` | `/action-items` | List all action items |
| `GET` | `/action-items?note_id={id}` | List action items for a specific note |
| `POST` | `/action-items/{id}/done` | Mark an action item as done/not done |

### Request/Response Examples

**Extract action items:**

```bash
curl -X POST http://localhost:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "- [ ] Set up database\n- Implement extract endpoint", "save_note": true}'
```

**Response:**

```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "Set up database"},
    {"id": 2, "text": "Implement extract endpoint"}
  ]
}
```

**Mark action item as done:**

```bash
curl -X POST http://localhost:8000/action-items/1/done \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

## Running the Test Suite

```bash
poetry run pytest -q
```

## Project Structure

```
week2/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── db.py             # SQLite database operations
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── routers/
│   │   ├── notes.py      # Notes API endpoints
│   │   └── action_items.py # Action items API endpoints
│   └── services/
│       └── extract.py    # Rule-based and LLM extraction logic
├── frontend/
│   └── index.html        # Single-page web interface
├── tests/
│   └── test_extract.py   # Pytest tests for extraction logic
├── data/                 # SQLite database (created at runtime)
└── README.md
```

## Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** / **sqlite3** - Database
- **Pydantic** - Data validation
- **Ollama** - Local LLM inference (for LLM extraction)
- **pytest** - Testing framework
