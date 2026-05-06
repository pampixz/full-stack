from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from backend.app.db.deps import get_db
from backend.app.core.permissions import require_permission
from backend.app.models.entry import Entry as EntryModel
from backend.app.models.user import User

router = APIRouter(prefix="/entries", tags=["Entries"])


# ---------- SCHEMAS ----------

class EntryCreate(BaseModel):
    text: str = Field(..., min_length=3, max_length=500)
    tags: List[str] = []


class EntryResponse(BaseModel):
    id: int
    text: str
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EntryListResponse(BaseModel):
    items: List[EntryResponse]
    total: int
    page: int
    page_size: int


def _tags_to_list(tags: str) -> List[str]:
    if not tags:
        return []
    return [t.strip() for t in tags.split(",") if t.strip()]


# ---------- CRUD (RBAC + JWT) ----------

@router.get("/", response_model=EntryListResponse)
def get_all_entries(
    q: str | None = Query(default=None, max_length=100, description="Поиск по тексту"),
    tag: str | None = Query(default=None, max_length=50, description="Фильтр по тегу"),
    date_from: datetime | None = Query(default=None, description="Дата от"),
    date_to: datetime | None = Query(default=None, description="Дата до"),
    sort: Literal["created_at", "-created_at", "text", "-text"] = Query(
        default="-created_at",
        description="Сортировка"
    ),
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    page_size: int = Query(default=5, ge=1, le=50, description="Размер страницы"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:read_own")),
):
    query = db.query(EntryModel).filter(EntryModel.user_id == current_user.id)

    # --- поиск по тексту ---
    if q:
        query = query.filter(EntryModel.text.ilike(f"%{q}%"))

    # --- фильтр по тегу ---
    if tag:
        query = query.filter(EntryModel.tags.ilike(f"%{tag}%"))

    # --- фильтр по дате ---
    if date_from:
        query = query.filter(EntryModel.created_at >= date_from)

    if date_to:
        query = query.filter(EntryModel.created_at <= date_to)

    # --- сортировка ---
    if sort == "-created_at":
        query = query.order_by(EntryModel.created_at.desc())
    elif sort == "created_at":
        query = query.order_by(EntryModel.created_at.asc())
    elif sort == "text":
        query = query.order_by(EntryModel.text.asc())
    elif sort == "-text":
        query = query.order_by(EntryModel.text.desc())

    total = query.count()

    offset = (page - 1) * page_size
    entries = query.offset(offset).limit(page_size).all()

    items = [
        EntryResponse(
            id=e.id,
            text=e.text,
            tags=_tags_to_list(e.tags),
            created_at=e.created_at,
        )
        for e in entries
    ]

    return EntryListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:read_own")),
):
    entry = (
        db.query(EntryModel)
        .filter(
            EntryModel.id == entry_id,
            EntryModel.user_id == current_user.id,
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    return EntryResponse(
        id=entry.id,
        text=entry.text,
        tags=_tags_to_list(entry.tags),
        created_at=entry.created_at,
    )


@router.post("/", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    data: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:create")),
):
    entry = EntryModel(
        text=data.text,
        tags=",".join(data.tags),
        user_id=current_user.id,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return EntryResponse(
        id=entry.id,
        text=entry.text,
        tags=_tags_to_list(entry.tags),
        created_at=entry.created_at,
    )


@router.put("/{entry_id}", response_model=EntryResponse)
def update_entry(
    entry_id: int,
    data: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:update_own")),
):
    entry = (
        db.query(EntryModel)
        .filter(
            EntryModel.id == entry_id,
            EntryModel.user_id == current_user.id,
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    entry.text = data.text
    entry.tags = ",".join(data.tags)

    db.commit()
    db.refresh(entry)

    return EntryResponse(
        id=entry.id,
        text=entry.text,
        tags=_tags_to_list(entry.tags),
        created_at=entry.created_at,
    )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:delete_own")),
):
    entry = (
        db.query(EntryModel)
        .filter(
            EntryModel.id == entry_id,
            EntryModel.user_id == current_user.id,
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    db.delete(entry)
    db.commit()
    return None