"""
Vercel serverless handler for the FastAPI backend.

This module wraps the FastAPI app from backend.app.main and exposes it
as a Vercel serverless Python function.

The vercel.json configuration routes /api/* requests here while serving
the React frontend for all other routes.
"""

import sys
from pathlib import Path

# Ensure the backend module can be imported
_backend_path = Path(__file__).parent / "backend"
if _backend_path.exists():
    sys.path.insert(0, str(Path(__file__).parent))

from backend.app.main import app

# Vercel serverless handler
handler = app
