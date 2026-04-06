from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import ActionItemCreate, ActionItemRead, BulkCompleteRequest, PaginatedActionItemsResponse

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=PaginatedActionItemsResponse)
def list_items(
    completed: bool | None = Query(None, description="Filter by completion status"),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
) -> PaginatedActionItemsResponse:
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size < 1:
        raise HTTPException(status_code=400, detail="page_size must be > 0")
    if page_size > 100:
        raise HTTPException(status_code=400, detail="page_size must be <= 100")

    # Build base query
    stmt = select(ActionItem)
    if completed is not None:
        stmt = stmt.where(ActionItem.completed == completed)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    rows = db.execute(stmt.offset(offset).limit(page_size)).scalars().all()
    items = [ActionItemRead.model_validate(row) for row in rows]

    return PaginatedActionItemsResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.post("/bulk-complete", response_model=list[ActionItemRead])
def bulk_complete_items(
    payload: BulkCompleteRequest, db: Session = Depends(get_db)
) -> list[ActionItemRead]:
    if not payload.ids:
        return []
    items = db.query(ActionItem).filter(ActionItem.id.in_(payload.ids)).all()
    if len(items) != len(payload.ids):
        found_ids = {item.id for item in items}
        missing = [id for id in payload.ids if id not in found_ids]
        raise HTTPException(status_code=404, detail=f"Action items not found: {missing}")
    for item in items:
        item.completed = True
    db.flush()
    for item in items:
        db.refresh(item)
    return [ActionItemRead.model_validate(item) for item in items]
