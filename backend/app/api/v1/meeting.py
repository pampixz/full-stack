from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.deps import get_db
from backend.app.models.meeting import Meeting
from backend.app.schemas.meeting import MeetingCreate, MeetingOut
from backend.app.core.permissions import require_permission
from backend.app.models.user import User

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", response_model=MeetingOut)
def create_meeting(
    data: MeetingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("meetings:create")),
):
    meeting = Meeting(**data.dict())
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/", response_model=list[MeetingOut])
def get_meetings(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("meetings:read")),
):
    return db.query(Meeting).order_by(Meeting.meeting_date).all()


@router.delete("/{meeting_id}")
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("meetings:create")),
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Встреча не найдена")

    db.delete(meeting)
    db.commit()

    return {"message": "Встреча удалена"}