from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Response envelope schemas
# ---------------------------------------------------------------------------


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    ok: bool = False
    error: ErrorDetail


class SuccessEnvelope(BaseModel):
    ok: bool = True
    data: BaseModel | list | dict | str | None = None


# ---------------------------------------------------------------------------
# Domain schemas
# ---------------------------------------------------------------------------


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=10000)


class NoteUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = Field(None, min_length=1, max_length=10000)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    tags: list[TagRead] = []

    class Config:
        from_attributes = True


class PaginatedNotesResponse(BaseModel):
    items: list[NoteRead]
    total: int
    page: int
    page_size: int


class ActionItemCreate(BaseModel):
    description: str = Field(min_length=1)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True


class BulkCompleteRequest(BaseModel):
    ids: list[int]


class ExtractionResult(BaseModel):
    hashtags: list[str]
    action_items: list[str]
