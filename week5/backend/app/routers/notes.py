from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import NoteCreate, NoteRead, NoteUpdate, PaginatedNotesResponse, TagCreate, TagRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=PaginatedNotesResponse)
def search_notes(
    q: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    sort: Optional[str] = "created_desc",
    db: Session = Depends(get_db),
) -> PaginatedNotesResponse:
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size < 1:
        raise HTTPException(status_code=400, detail="page_size must be > 0")
    if page_size > 100:
        raise HTTPException(status_code=400, detail="page_size must be <= 100")

    # Validate sort parameter
    valid_sorts = {"created_desc", "created_asc", "title_asc", "title_desc"}
    if sort is not None and sort not in valid_sorts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort value: '{sort}'. Must be one of: {', '.join(sorted(valid_sorts))}",
        )

    # Build base query
    query = select(Note)

    # Apply case-insensitive search filter
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            (func.lower(Note.title).like(func.lower(search_pattern)))
            | (func.lower(Note.content).like(func.lower(search_pattern)))
        )

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Apply sorting
    sort_mapping = {
        "created_desc": Note.id.desc(),
        "created_asc": Note.id.asc(),
        "title_asc": Note.title.asc(),
        "title_desc": Note.title.desc(),
    }
    order_clause = sort_mapping[sort]
    query = query.order_by(order_clause)

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    rows = db.execute(query).scalars().all()
    items = [NoteRead.model_validate(row) for row in rows]

    return PaginatedNotesResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)


@router.post("/{note_id}/tags", response_model=NoteRead)
def attach_tag(note_id: int, payload: TagCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Find or create the tag
    tag = db.execute(select(Tag).where(Tag.name == payload.name)).scalars().first()
    if not tag:
        tag = Tag(name=payload.name)
        db.add(tag)
        db.flush()
        db.refresh(tag)

    # Attach tag to note if not already attached
    if tag not in note.tags:
        note.tags.append(tag)
        db.flush()
        db.refresh(note)

    return NoteRead.model_validate(note)


@router.delete("/{note_id}/tags/{tag_id}", status_code=204)
def detach_tag(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag in note.tags:
        note.tags.remove(tag)
        db.flush()
