from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.repositories.refresh_token_repository import RefreshTokenRepository
from backend.app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.refresh_repo = RefreshTokenRepository(db)

    def login(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # сохраняем refresh token в БД
        self.refresh_repo.create(refresh_token, user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")

        db_token = self.refresh_repo.get_by_token(refresh_token)
        if not db_token or db_token.is_revoked:
            raise HTTPException(
                status_code=401,
                detail="Refresh token revoked or not found"
            )

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # ротация refresh token:
        # старый помечаем как отозванный
        self.refresh_repo.revoke(refresh_token)

        new_access_token = create_access_token({"sub": str(user_id)})
        new_refresh_token = create_refresh_token({"sub": str(user_id)})

        # сохраняем новый refresh token
        self.refresh_repo.create(new_refresh_token, int(user_id))

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }

    def logout(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")

        self.refresh_repo.revoke(refresh_token)
        return {"message": "Logged out"}