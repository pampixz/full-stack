from backend.app.models.user import User
from backend.app.core.security import hash_password


def login_user(client, email: str, password: str):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def create_user_in_db(db_session, email: str, password: str, role: str):
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_user_cannot_create_meeting(client, db_session):
    create_user_in_db(
        db_session,
        email="user_meeting@example.com",
        password="123456",
        role="user",
    )

    headers = login_user(client, "user_meeting@example.com", "123456")

    response = client.post(
        "/api/v1/meetings/",
        json={
            "title": "User meeting",
            "description": "Should fail",
            "meeting_date": "2026-05-01T12:00:00"
        },
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_can_create_meeting(client, db_session):
    create_user_in_db(
        db_session,
        email="admin_meeting@example.com",
        password="123456",
        role="admin",
    )

    headers = login_user(client, "admin_meeting@example.com", "123456")

    response = client.post(
        "/api/v1/meetings/",
        json={
            "title": "Admin meeting",
            "description": "Should pass",
            "meeting_date": "2026-05-01T12:00:00"
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Admin meeting"
    assert data["description"] == "Should pass"


def test_authorized_user_can_read_meetings(client, db_session):
    # admin creates meeting
    create_user_in_db(
        db_session,
        email="admin_reader@example.com",
        password="123456",
        role="admin",
    )
    admin_headers = login_user(client, "admin_reader@example.com", "123456")

    client.post(
        "/api/v1/meetings/",
        json={
            "title": "Visible meeting",
            "description": "Can be read",
            "meeting_date": "2026-05-01T14:00:00"
        },
        headers=admin_headers,
    )

    # regular user reads meetings
    create_user_in_db(
        db_session,
        email="reader_user@example.com",
        password="123456",
        role="user",
    )
    user_headers = login_user(client, "reader_user@example.com", "123456")

    response = client.get("/api/v1/meetings/", headers=user_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "Visible meeting"


def test_admin_can_delete_meeting(client, db_session):
    create_user_in_db(
        db_session,
        email="admin_delete@example.com",
        password="123456",
        role="admin",
    )

    headers = login_user(client, "admin_delete@example.com", "123456")

    create_response = client.post(
        "/api/v1/meetings/",
        json={
            "title": "Meeting to delete",
            "description": "delete me",
            "meeting_date": "2026-05-02T10:00:00"
        },
        headers=headers,
    )

    meeting_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/meetings/{meeting_id}",
        headers=headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Встреча удалена"