from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.deps import get_db
from backend.app.models.user import User
from backend.app.core.permissions import require_permission

router = APIRouter(prefix="/admin", tags=["Admin"])

class SetRoleRequest(BaseModel):
    user_id: int
    role: str  # "user" или "admin"

@router.post("/set-role")
def set_role(
    data: SetRoleRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("users:manage_roles")),
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = data.role
    db.commit()
    return {"message": "Role updated", "user_id": user.id, "role": user.role}