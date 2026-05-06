def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "123456"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "badpass"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"