from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.db.deps import get_db
from backend.app.models.user import User
from backend.app.core.deps import get_current_user
from backend.app.schemas.auth import RegisterRequest
from backend.app.core.security import hash_password
from backend.app.core.service_deps import get_auth_service
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User registered successfully"}
    except Exception as e:
        db.rollback()
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.login(form_data.username, form_data.password)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.post("/refresh")
def refresh(
    data: dict,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = data.get("refresh_token")
    return auth_service.refresh_access_token(refresh_token)


@router.post("/logout")
def logout(
    data: dict,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = data.get("refresh_token")
    return auth_service.logout(refresh_token)