import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.db.deps import get_db
from backend.app.core.permissions import require_permission
from backend.app.models.user import User
from backend.app.models.entry import Entry as EntryModel
from backend.app.models.entry_file import EntryFile

router = APIRouter(prefix="/entry-files", tags=["Entry Files"])

UPLOAD_DIR = "uploads/entries"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain",
}


@router.post("/{entry_id}")
async def upload_entry_file(
    entry_id: int,
    uploaded_file: UploadFile = File(...),
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

    if uploaded_file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")

    content = await uploaded_file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл превышает допустимый размер")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(uploaded_file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    with open(file_path, "wb") as f:
      f.write(content)

    db_file = EntryFile(
        entry_id=entry.id,
        user_id=current_user.id,
        original_name=uploaded_file.filename,
        stored_name=stored_name,
        file_path=file_path,
        content_type=uploaded_file.content_type,
        file_size=len(content),
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "id": db_file.id,
        "entry_id": db_file.entry_id,
        "original_name": db_file.original_name,
        "content_type": db_file.content_type,
        "file_size": db_file.file_size,
        "created_at": db_file.created_at,
    }


@router.get("/{entry_id}")
def list_entry_files(
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

    files = (
        db.query(EntryFile)
        .filter(
            EntryFile.entry_id == entry_id,
            EntryFile.user_id == current_user.id,
        )
        .order_by(EntryFile.created_at.desc())
        .all()
    )

    return [
        {
            "id": f.id,
            "entry_id": f.entry_id,
            "original_name": f.original_name,
            "content_type": f.content_type,
            "file_size": f.file_size,
            "created_at": f.created_at,
        }
        for f in files
    ]


@router.get("/download/{file_id}")
def download_entry_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:read_own")),
):
    db_file = (
        db.query(EntryFile)
        .filter(
            EntryFile.id == file_id,
            EntryFile.user_id == current_user.id,
        )
        .first()
    )

    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="Файл отсутствует в хранилище")

    return FileResponse(
        path=db_file.file_path,
        media_type=db_file.content_type,
        filename=db_file.original_name,
    )


@router.delete("/{file_id}")
def delete_entry_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("entries:update_own")),
):
    db_file = (
        db.query(EntryFile)
        .filter(
            EntryFile.id == file_id,
            EntryFile.user_id == current_user.id,
        )
        .first()
    )

    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    db.delete(db_file)
    db.commit()

    return {"message": "Файл удалён"}