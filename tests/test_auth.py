from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "pytest_user2@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201


def test_register_duplicate_email():
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Email already registered"


def test_register_invalid_email():
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_register_short_password():
    response = client.post(
        "/auth/register",
        json={
            "email": "shortpassword@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422


def test_login_success():
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    print(response.json())

    assert response.status_code == 200, response.json()
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password():
    client.post(
        "/auth/register",
        json={
            "email": "wrongpassword@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_login_nonexistent_email():
    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401


def test_get_current_user():
    client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert "user_id" in response.json()


def test_get_current_user_without_token():
    response = client.get("/auth/me")

    assert response.status_code == 401
