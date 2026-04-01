from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import ActionItemExtract, ActionItemResponse, ExtractResponse, MarkDoneRequest
from ..services.extract import extract_action_items, extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract")
def extract(payload: ActionItemExtract) -> ExtractResponse:
    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items)],
    )


@router.post("/extract-llm")
def extract_llm(payload: ActionItemExtract) -> ExtractResponse:
    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items_llm(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items)],
    )


@router.get("")
def list_all(note_id: int | None = None) -> list[ActionItemResponse]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> ActionItemResponse:
    row = db.get_action_item(action_item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="action item not found")

    db.mark_action_item_done(action_item_id, payload.done)
    return ActionItemResponse(
        id=row["id"],
        note_id=row["note_id"],
        text=row["text"],
        done=payload.done,
        created_at=row["created_at"],
    )
