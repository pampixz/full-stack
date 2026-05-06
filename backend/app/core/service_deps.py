from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.db.deps import get_db
from backend.app.services.auth_service import AuthService


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)