from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag, note_tags
from ..schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    rows = db.execute(
        select(Tag)
        .join(note_tags, note_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
        .distinct()
    ).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.post("/", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    # Check if tag already exists
    existing = db.execute(select(Tag).where(Tag.name == payload.name)).scalars().first()
    if existing:
        raise HTTPException(status_code=409, detail="Tag already exists")
    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
