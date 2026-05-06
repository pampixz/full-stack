import pytest
from fastapi import HTTPException

from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from backend.app.core.security import hash_password


def test_login_success(db_session):
    user = User(
        email="test@example.com",
        password_hash=hash_password("123456"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = AuthService(db_session)
    result = service.login("test@example.com", "123456")

    assert "access_token" in result
    assert "refresh_token" in result


def test_login_invalid_password(db_session):
    user = User(
        email="test2@example.com",
        password_hash=hash_password("123456"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    service = AuthService(db_session)

    with pytest.raises(HTTPException) as exc:
        service.login("test2@example.com", "wrongpass")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


def test_logout_without_refresh_token(db_session):
    service = AuthService(db_session)

    with pytest.raises(HTTPException) as exc:
        service.logout("")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Refresh token required"