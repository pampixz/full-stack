from fastapi import Depends, HTTPException, status
from backend.app.core.deps import get_current_user
from backend.app.core.rbac import ROLE_PERMISSIONS
from backend.app.models.user import User

def require_permission(permission: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        role = current_user.role or "user"
        allowed = ROLE_PERMISSIONS.get(role, set())
        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: insufficient permissions",
            )
        return current_user
    return checker