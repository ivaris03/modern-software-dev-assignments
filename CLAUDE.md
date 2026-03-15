# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the course assignment repository for **CS146S: The Modern Software Developer** at Stanford University (Fall 2025). The repository contains weekly assignments covering various modern software development topics, from LLM prompting techniques to full-stack web development.

## Environment Setup

1. Install Anaconda (Python 3.12)
2. Create and activate a Conda environment:
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```
3. Install Poetry: `curl -sSL https://install.python-poetry.org | python -`
4. Install dependencies: `poetry install --no-interaction`

## Common Commands

```bash
# Run the server (from project root or specific week directory)
poetry run uvicorn week2.app.main:app --reload

# Run tests
poetry run pytest -q

# Format code
poetry run black .
poetry run ruff check . --fix
```

For weeks 4-7 that have their own Makefile:
```bash
make run        # Start the server with uvicorn
make test       # Run pytest
make format     # Run black and ruff
make lint       # Run ruff only
make seed       # Seed the database
```

## Code Architecture

### Week 1: Prompting Techniques
- Contains 6 Python files demonstrating different LLM prompting methods: `k_shot_prompting.py`, `chain_of_thought.py`, `tool_calling.py`, `self_consistency_prompting.py`, `rag.py`, `reflexion.py`
- Uses **Ollama** for local LLM inference (models: `mistral-nemo:12b`, `llama3.1:8b`)
- Run individual files with: `poetry run python week1/<filename>.py`

### Weeks 2-7: Full-Stack Development
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Vanilla JS with simple HTML/CSS
- Structure varies by week but generally follows:
  ```
  weekN/
    backend/app/
      main.py       # FastAPI app entry point
      db.py        # Database setup and models
      routers/     # API endpoint definitions
      services/    # Business logic (e.g., extract.py)
      schemas.py   # Pydantic schemas
    frontend/
      index.html
      app.js
      styles.css
    tests/         # Pytest test files
  ```

### Week 8: Multi-Stack AI-Accelerated Build
- Three separate project folders with different technology stacks
- At least one built with **bolt.new** (AI app generator)
- At least one uses a non-JavaScript language (e.g., Django, Ruby on Rails)

## Key Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Ollama** - Local LLM runtime
- **OpenAI** - LLM API client
- **pytest** - Testing framework
- **black/ruff** - Code formatting and linting