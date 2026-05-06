import io


def register_and_login(client, email="fileuser@example.com", password="123456"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )

    tokens = login_response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def create_entry(client, headers):
    response = client.post(
        "/api/v1/entries/",
        json={
            "text": "Запись для файла",
            "tags": ["file"]
        },
        headers=headers,
    )
    return response.json()["id"]


def test_upload_file_success(client):
    headers = register_and_login(client, "upload_success@example.com", "123456")
    entry_id = create_entry(client, headers)

    file_content = b"hello test file"
    response = client.post(
        f"/api/v1/entry-files/{entry_id}",
        headers=headers,
        files={
            "uploaded_file": ("test.txt", io.BytesIO(file_content), "text/plain")
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["entry_id"] == entry_id
    assert data["original_name"] == "test.txt"
    assert data["content_type"] == "text/plain"


def test_list_files_success(client):
    headers = register_and_login(client, "list_files@example.com", "123456")
    entry_id = create_entry(client, headers)

    client.post(
        f"/api/v1/entry-files/{entry_id}",
        headers=headers,
        files={
            "uploaded_file": ("list.txt", io.BytesIO(b"content"), "text/plain")
        },
    )

    response = client.get(f"/api/v1/entry-files/{entry_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["original_name"] == "list.txt"


def test_download_file_success(client):
    headers = register_and_login(client, "download_file@example.com", "123456")
    entry_id = create_entry(client, headers)

    upload_response = client.post(
        f"/api/v1/entry-files/{entry_id}",
        headers=headers,
        files={
            "uploaded_file": ("download.txt", io.BytesIO(b"download content"), "text/plain")
        },
    )

    file_id = upload_response.json()["id"]

    response = client.get(f"/api/v1/entry-files/download/{file_id}", headers=headers)

    assert response.status_code == 200
    assert response.content == b"download content"


def test_delete_file_success(client):
    headers = register_and_login(client, "delete_file@example.com", "123456")
    entry_id = create_entry(client, headers)

    upload_response = client.post(
        f"/api/v1/entry-files/{entry_id}",
        headers=headers,
        files={
            "uploaded_file": ("delete.txt", io.BytesIO(b"delete me"), "text/plain")
        },
    )

    file_id = upload_response.json()["id"]

    delete_response = client.delete(f"/api/v1/entry-files/{file_id}", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Файл удалён"


def test_upload_invalid_file_type(client):
    headers = register_and_login(client, "invalid_type@example.com", "123456")
    entry_id = create_entry(client, headers)

    response = client.post(
        f"/api/v1/entry-files/{entry_id}",
        headers=headers,
        files={
            "uploaded_file": ("bad.exe", io.BytesIO(b"binary"), "application/octet-stream")
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Недопустимый тип файла"