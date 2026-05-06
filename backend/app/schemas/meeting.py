from datetime import datetime
from pydantic import BaseModel

class MeetingCreate(BaseModel):
    title: str
    description: str | None = None
    meeting_date: datetime

class MeetingOut(MeetingCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True