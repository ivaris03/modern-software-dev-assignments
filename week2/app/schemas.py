from __future__ import annotations

from pydantic import BaseModel, Field


# Request schemas
class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, strip_whitespace=True)


class ActionItemExtract(BaseModel):
    text: str = Field(..., min_length=1, strip_whitespace=True)
    save_note: bool = False


class MarkDoneRequest(BaseModel):
    done: bool = True


# Response schemas
class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemResponse(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool
    created_at: str


class ExtractResponse(BaseModel):
    note_id: int | None
    items: list[dict]
