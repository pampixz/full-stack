from pydantic import BaseModel
from datetime import datetime
from typing import List

class EntryBase(BaseModel):
    text: str
    tags: List[str]

class EntryCreate(EntryBase):
    pass

class EntryResponse(EntryBase):
    id: int
    text: str
    tags: list[str]
    created_at: datetime

    class Config:
        from_attributes = True