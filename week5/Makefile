.PHONY: run test format lint seed web-install web-dev web-build

# Build the React frontend first
web-build:
	cd frontend/ui && npm install && npm run build

# Install npm dependencies (without building)
web-install:
	cd frontend/ui && npm install

# Run Vite dev server (requires backend to be running separately)
web-dev:
	cd frontend/ui && npm run dev

# Run the FastAPI backend (builds web bundle if not present)
run: web-build
	PYTHONPATH=. uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	PYTHONPATH=. pytest -q backend/tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	PYTHONPATH=. python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
