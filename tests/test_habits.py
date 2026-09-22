from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def register_and_login(email="habit@example.com"):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123"
        }
    )

    return response.json()["access_token"]


def test_create_habit():
    token = register_and_login()

    response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Gym"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Gym"
    assert response.json()["frequency"] == "daily"


def test_create_weekly_habit():
    token = register_and_login()

    response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Football",
            "frequency": "weekly"
        }
    )

    assert response.status_code == 200
    assert response.json()["frequency"] == "weekly"


def test_create_habit_invalid_frequency():
    token = register_and_login()

    response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Gym",
            "frequency": "monthly"
        }
    )

    assert response.status_code == 422


def test_create_habit_empty_name():
    token = register_and_login()

    response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": ""
        }
    )

    assert response.status_code == 422


def test_create_habit_without_authentication():
    response = client.post(
        "/habits/",
        json={
            "name": "Gym"
        }
    )

    assert response.status_code == 401


def test_get_habits():
    token = register_and_login()

    client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Gym"
        }
    )

    response = client.get(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


def test_get_habit_by_id():
    token = register_and_login()

    create_response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Study"
        }
    )

    habit_id = create_response.json()["id"]

    response = client.get(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == habit_id
    assert response.json()["name"] == "Study"


def test_get_nonexistent_habit():
    token = register_and_login()

    response = client.get(
        "/habits/99999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_update_habit_name():
    token = register_and_login()

    create_response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Study"
        }
    )

    habit_id = create_response.json()["id"]

    response = client.put(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Study German"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Study German"


def test_update_habit_frequency():
    token = register_and_login()

    create_response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Gym"
        }
    )

    habit_id = create_response.json()["id"]

    response = client.put(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "frequency": "weekly"
        }
    )

    assert response.status_code == 200
    assert response.json()["frequency"] == "weekly"


def test_update_habit_empty_body():
    token = register_and_login()

    create_response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Gym"
        }
    )

    habit_id = create_response.json()["id"]

    response = client.put(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={}
    )

    assert response.status_code == 422


def test_delete_habit():
    token = register_and_login()

    create_response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Gym"
        }
    )

    habit_id = create_response.json()["id"]

    response = client.delete(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    get_response = client.get(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert get_response.status_code == 404


def test_user_cannot_access_another_users_habit():
    token1 = register_and_login("user1@example.com")

    create_response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token1}"
        },
        json={
            "name": "Private habit"
        }
    )

    habit_id = create_response.json()["id"]

    token2 = register_and_login("user2@example.com")

    response = client.get(
        f"/habits/{habit_id}",
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert response.status_code == 404