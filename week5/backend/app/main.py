import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router
from .routers import tags as tags_router

app = FastAPI(title="Modern Software Dev Starter (Week 5)")

# CORS middleware for Vercel deployment
_frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

# Mount static frontend assets
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")


# ---------------------------------------------------------------------------
# Exception handlers — return consistent error envelopes
# ---------------------------------------------------------------------------


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
    }
    code = code_map.get(exc.status_code, "ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": {"code": code, "message": exc.detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Flatten validation errors into a single message
    messages = []
    for err in exc.errors():
        loc = ".".join(str(l) for l in err["loc"])
        messages.append(f"{loc}: {err['msg']}")
    return JSONResponse(
        status_code=422,
        content={"ok": False, "error": {"code": "VALIDATION_ERROR", "message": "; ".join(messages)}},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = str(uuid.uuid4())[:8]
    logging.exception("Unhandled exception [request_id=%s]: %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            },
        },
    )


# ---------------------------------------------------------------------------
# Middleware — wrap successful responses in { "ok": true, "data": ... }
# ---------------------------------------------------------------------------


@app.middleware("http")
async def envelope_middleware(request: Request, call_next: Any) -> Response:
    response = await call_next(request)

    # Only wrap 2xx responses
    if not (200 <= response.status_code < 300):
        return response

    # Skip /static and root (HTML) responses
    if request.url.path in ("/", "/static") or request.url.path.startswith("/static/"):
        return response

    # Read body, wrap it, return new response
    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    if not body:
        return JSONResponse(status_code=response.status_code, content={"ok": True, "data": None})

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        # Not JSON — return as-is (e.g., 204 No Content)
        return response

    return JSONResponse(status_code=response.status_code, content={"ok": True, "data": parsed})


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("frontend/dist/index.html")


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
app.include_router(tags_router.router)
