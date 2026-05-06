from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.app.db.database import Base


class EntryFile(Base):
    __tablename__ = "entry_files"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), unique=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)