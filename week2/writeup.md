# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Analyze the existing `extract_action_items()` function in `week2/app/services/extract.py`, which currently extracts action items using predefined heuristics.

Your task is to implement an **LLM-powered** alternative, `extract_action_items_llm()`, that utilizes Ollama to perform action item extraction via a large language model.

Some  tips:
- To produce structured outputs (i.e. JSON array of strings), refer to this documentation: https://ollama.com/blog/structured-outputs
- To browse available Ollama models, refer to this documentation: https://ollama.com/library. Note that larger models will be more resource-intensive, so start small. To pull and run a model: `ollama run {MODEL_NAME}`
```

Generated Code Snippets:
```python
# File: week2/app/services/extract.py (lines 92-124)

def extract_action_items_llm(text: str) -> List[str]:
    """Extract action items using LLM with structured output via Ollama."""
    model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

    format_schema = {
        "type": "array",
        "items": {"type": "string"},
    }

    try:
        response = chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that extracts action items from text. "
                        "Return a JSON array of strings, where each string is an action item. "
                        "Action items typically start with verbs like 'Set up', 'Write', 'Fix', 'Create', etc."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Extract all action items from this text:\n\n{text}",
                },
            ],
            format=format_schema,
            options={"temperature": 0},
        )
        items = json.loads(response.message.content)
        return items
    except (json.JSONDecodeError, Exception):
        return []
```

Modified files:
- `week2/app/services/extract.py` (lines 92-124): Added `extract_action_items_llm()` function using Ollama structured outputs

### Exercise 2: Add Unit Tests
Prompt:
```
Write unit tests for `extract_action_items_llm()` covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in `week2/tests/test_extract.py`.
```

Generated Code Snippets:
```python
# File: week2/tests/test_extract.py (lines 1-5, 23-75)

import os
import pytest
from unittest.mock import patch, MagicMock

from ..app.services.extract import extract_action_items, extract_action_items_llm


class TestExtractActionItemsLLM:
    """Tests for extract_action_items_llm with mocked LLM responses."""

    @patch("week2.app.services.extract.chat")
    def test_bullet_list_input(self, mock_chat):
        """Test LLM extraction with bullet list format."""
        mock_response = MagicMock()
        mock_response.message.content = '["Set up database", "implement API endpoint", "Write tests"]'
        mock_chat.return_value = mock_response

        text = """
        Notes from meeting:
        - Set up database
        * implement API endpoint
        1. Write tests
        """
        items = extract_action_items_llm(text)

        assert items == ["Set up database", "implement API endpoint", "Write tests"]
        mock_chat.assert_called_once()

    @patch("week2.app.services.extract.chat")
    def test_keyword_prefixed_lines(self, mock_chat):
        """Test LLM extraction with keyword-prefixed lines."""
        mock_response = MagicMock()
        mock_response.message.content = '["TODO: Fix login bug", "ACTION: Update docs", "NEXT: Deploy to prod"]'
        mock_chat.return_value = mock_response

        text = """
        TODO: Fix login bug
        ACTION: Update docs
        NEXT: Deploy to prod
        """
        items = extract_action_items_llm(text)

        assert items == ["TODO: Fix login bug", "ACTION: Update docs", "NEXT: Deploy to prod"]

    @patch("week2.app.services.extract.chat")
    def test_empty_input(self, mock_chat):
        """Test LLM extraction with empty input returns empty list."""
        mock_response = MagicMock()
        mock_response.message.content = "[]"
        mock_chat.return_value = mock_response

        items = extract_action_items_llm("")

        assert items == []
        mock_chat.assert_called_once()

    @patch("week2.app.services.extract.chat")
    def test_invalid_json_response(self, mock_chat):
        """Test that invalid JSON from LLM returns empty list."""
        mock_response = MagicMock()
        mock_response.message.content = "Sorry, I couldn't extract any items."
        mock_chat.return_value = mock_response

        items = extract_action_items_llm("Some text without clear action items")

        assert items == []

    @patch("week2.app.services.extract.chat")
    def test_llm_model_config(self, mock_chat):
        """Test that correct model is used when OLLAMA_MODEL is set."""
        mock_response = MagicMock()
        mock_response.message.content = '["Test item"]'
        mock_chat.return_value = mock_response

        with patch.dict(os.environ, {"OLLAMA_MODEL": "mistral-nemo:12b"}):
            extract_action_items_llm("Test input")

        call_kwargs = mock_chat.call_args
        assert call_kwargs.kwargs["model"] == "mistral-nemo:12b"
        assert call_kwargs.kwargs["options"]["temperature"] == 0
```

Modified files:
- `week2/tests/test_extract.py` (lines 1-5, 23-75): Added `TestExtractActionItemsLLM` class with 5 unit tests for `extract_action_items_llm()`

### Exercise 3: Refactor Existing Code for Clarity
Prompt:
```
Refactor the week2 backend for clarity. Focus on:
1. Well-defined API contracts/schemas (Pydantic models)
2. Database layer cleanup
3. App lifecycle/configuration (move init_db to lifespan context manager)
4. Error handling (add existence checks in mark_done endpoint)
```

Generated/Modified Code Snippets:

**1. `week2/app/schemas.py` (NEW FILE)**

Created Pydantic schemas for all request/response payloads:

```python
# week2/app/schemas.py (lines 1-39)

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, strip_whitespace=True)

class ActionItemExtract(BaseModel):
    text: str = Field(..., min_length=1, strip_whitespace=True)
    save_note: bool = False

class MarkDoneRequest(BaseModel):
    done: bool = True

class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str

class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str

class ExtractResponse(BaseModel):
    note_id: Optional[int]
    items: list[dict]
```

**2. `week2/app/main.py` (lines 1-30)**

Moved `init_db()` from module import to lifespan context manager:

```python
# week2/app/main.py (lines 1-30)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Now runs at server startup, not module import
    yield

app = FastAPI(title="Action Item Extractor", lifespan=lifespan)
```

**3. `week2/app/routers/notes.py` (lines 1-33)**

Replaced `Dict[str, Any]` with Pydantic schemas, added response_model:

```python
# week2/app/routers/notes.py (lines 11-33)

@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreate) -> NoteResponse:
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=500, detail="failed to create note")
    return NoteResponse(id=note["id"], content=note["content"], created_at=note["created_at"])

@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])
```

**4. `week2/app/routers/action_items.py` (lines 1-51)**

Replaced `Dict[str, Any]` with Pydantic schemas, added 404 check in `mark_done`:

```python
# week2/app/routers/action_items.py (lines 14-51)

@router.post("/extract")
def extract(payload: ActionItemExtract) -> ExtractResponse:
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)
    items = extract_action_items(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(note_id=note_id, items=[{"id": i, "text": t} for i, t in zip(ids, items)])

@router.get("")
def list_all(note_id: Optional[int] = None) -> list[ActionItemResponse]:
    rows = db.list_action_items(note_id=note_id)
    return [ActionItemResponse(id=r["id"], note_id=r["note_id"], text=r["text"], done=bool(r["done"]), created_at=r["created_at"]) for r in rows]

@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> ActionItemResponse:
    row = db.get_action_item(action_item_id)  # New: existence check
    if row is None:
        raise HTTPException(status_code=404, detail="action item not found")
    db.mark_action_item_done(action_item_id, payload.done)
    return ActionItemResponse(id=row["id"], note_id=row["note_id"], text=row["text"], done=payload.done, created_at=row["created_at"])
```

**5. `week2/app/db.py` (lines 105-115)**

Added `get_action_item()` function for existence checks:

```python
# week2/app/db.py (lines 105-115)

def get_action_item(action_item_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
            (action_item_id,),
        )
        return cursor.fetchone()
```

**6. `week2/app/services/extract.py` (lines 1-11, 92-124)**

Added logging for LLM failures, removed unused imports, changed `List[str]` to `list[str]`:

```python
# week2/app/services/extract.py (lines 1-11)

from __future__ import annotations

import json
import logging
import os
import re

from dotenv import load_dotenv
from ollama import chat

logger = logging.getLogger(__name__)  # New: logging setup

# week2/app/services/extract.py (lines 92-124)

def extract_action_items_llm(text: str) -> list[str]:  # Changed List -> list
    ...
    except Exception as e:
        logger.warning(f"LLM extraction failed: {e}")  # New: log instead of silent fail
        return []
```

Modified files:
- `week2/app/schemas.py` (lines 1-39): NEW - Created Pydantic schemas for all request/response payloads
- `week2/app/main.py` (lines 1-30): Moved `init_db()` to lifespan context manager
- `week2/app/routers/notes.py` (lines 1-33): Replaced `Dict[str, Any]` with `NoteCreate`/`NoteResponse` schemas
- `week2/app/routers/action_items.py` (lines 1-51): Replaced `Dict[str, Any]` with Pydantic schemas, added 404 existence check in `mark_done`
- `week2/app/db.py` (lines 105-115): Added `get_action_item()` function
- `week2/app/services/extract.py` (lines 1-11, 92-124): Added logging, removed unused imports, modernized type annotations


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt:
```
Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.
Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.
```

Generated Code Snippets:
```
Modified files:
- `week2/app/routers/notes.py` (lines 36-46): NEW - Added `GET /notes` endpoint to list all notes using existing `db.list_notes()`
- `week2/app/routers/action_items.py` (line 9, lines 28-39): Added import of `extract_action_items_llm`, NEW `POST /action-items/extract-llm` endpoint
- `week2/frontend/index.html` (lines 27-28, 31, 38, 75-131): Added "Extract LLM" and "List Notes" buttons with corresponding event handlers
```


### Exercise 5: Generate a README from the Codebase
Prompt:
```
Generate a README.md for the week2 project with:
- Project overview
- Setup and run instructions
- API endpoints documentation
- Test suite instructions
```

Generated Code Snippets:
```
Created: week2/README.md (entire file, 124 lines)

Contents:
- Project overview describing the Action Item Extractor
- Setup instructions (poetry install, uvicorn run)
- API endpoints table for notes and action items
- Request/response examples with curl commands
- Test suite instructions (poetry run pytest -q)
- Project structure tree
- Dependencies list
```

Modified files:
- `week2/README.md` (NEW - 124 lines): Created comprehensive README with project overview, setup/run instructions, API documentation, test instructions, project structure, and dependencies


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 