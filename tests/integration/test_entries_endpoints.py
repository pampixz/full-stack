def register_and_login(client, email="entryuser@example.com", password="123456"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )

    tokens = login_response.json()
    access_token = tokens["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def test_create_entry_success(client):
    headers = register_and_login(client)

    response = client.post(
        "/api/v1/entries/",
        json={
            "text": "Моя первая запись",
            "tags": ["тест", "дневник"]
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Моя первая запись"
    assert data["tags"] == ["тест", "дневник"]
    assert "id" in data


def test_get_entries_returns_only_own_entries(client):
    headers_user1 = register_and_login(client, "user1@example.com", "123456")
    headers_user2 = register_and_login(client, "user2@example.com", "123456")

    client.post(
        "/api/v1/entries/",
        json={"text": "Запись user1", "tags": ["one"]},
        headers=headers_user1,
    )

    client.post(
        "/api/v1/entries/",
        json={"text": "Запись user2", "tags": ["two"]},
        headers=headers_user2,
    )

    response = client.get("/api/v1/entries/", headers=headers_user1)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["text"] == "Запись user1"


def test_update_entry_success(client):
    headers = register_and_login(client, "updateuser@example.com", "123456")

    create_response = client.post(
        "/api/v1/entries/",
        json={"text": "Старая запись", "tags": ["old"]},
        headers=headers,
    )
    entry_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/entries/{entry_id}",
        json={"text": "Новая запись", "tags": ["new", "updated"]},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Новая запись"
    assert data["tags"] == ["new", "updated"]


def test_delete_entry_success(client):
    headers = register_and_login(client, "deleteuser@example.com", "123456")

    create_response = client.post(
        "/api/v1/entries/",
        json={"text": "Удаляемая запись", "tags": ["delete"]},
        headers=headers,
    )
    entry_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/entries/{entry_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/entries/{entry_id}", headers=headers)
    assert get_response.status_code == 404


def test_get_nonexistent_entry_returns_404(client):
    headers = register_and_login(client, "notfounduser@example.com", "123456")

    response = client.get("/api/v1/entries/9999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись не найдена"