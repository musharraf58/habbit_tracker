from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def register_and_login(email="completion@example.com"):
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


def create_habit(token, name="Gym"):
    response = client.post(
        "/habits/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": name
        }
    )

    return response.json()["id"]


def test_create_completion():
    token = register_and_login()
    habit_id = create_habit(token)

    response = client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "date": "2026-09-22"
        }
    )

    assert response.status_code == 200
    assert response.json()["habit_id"] == habit_id
    assert response.json()["date"] == "2026-09-22"


def test_duplicate_completion():
    token = register_and_login()
    habit_id = create_habit(token)

    data = {
        "date": "2026-09-22"
    }

    client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=data
    )

    response = client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=data
    )

    assert response.status_code == 400


def test_get_completion_history():
    token = register_and_login()
    habit_id = create_habit(token)

    client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "date": "2026-09-22"
        }
    )

    response = client.get(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


def test_get_completion_history_pagination():
    token = register_and_login()
    habit_id = create_habit(token)

    for day in ["2026-09-20", "2026-09-21", "2026-09-22"]:
        client.post(
            f"/completions/{habit_id}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "date": day
            }
        )

    response = client.get(
        f"/completions/{habit_id}?skip=1&limit=1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 1
    assert response.json()["skip"] == 1
    assert response.json()["limit"] == 1


def test_get_streak():
    token = register_and_login()
    habit_id = create_habit(token)

    for day in ["2026-09-20", "2026-09-21", "2026-09-22"]:
        client.post(
            f"/completions/{habit_id}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "date": day
            }
        )

    response = client.get(
        f"/completions/{habit_id}/streak",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_longest_streak():
    token = register_and_login()
    habit_id = create_habit(token)

    for day in ["2026-09-18", "2026-09-19", "2026-09-20"]:
        client.post(
            f"/completions/{habit_id}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "date": day
            }
        )

    response = client.get(
        f"/completions/{habit_id}/longest-streak",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_completion_stats():
    token = register_and_login()
    habit_id = create_habit(token)

    client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "date": "2026-09-20"
        }
    )

    response = client.get(
        f"/completions/{habit_id}/stats",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_get_completion_stats_date_range():
    token = register_and_login()
    habit_id = create_habit(token)

    client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "date": "2026-09-20"
        }
    )

    response = client.get(
        f"/completions/{habit_id}/stats"
        "?start_date=2026-09-01&end_date=2026-09-30",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_delete_completion():
    token = register_and_login()
    habit_id = create_habit(token)

    client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "date": "2026-09-22"
        }
    )

    response = client.delete(
        f"/completions/{habit_id}/2026-09-22",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    history_response = client.get(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert history_response.json()["total"] == 0


def test_user_cannot_access_another_users_completions():
    token1 = register_and_login("completion_user1@example.com")
    habit_id = create_habit(token1)

    client.post(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token1}"
        },
        json={
            "date": "2026-09-22"
        }
    )

    token2 = register_and_login("completion_user2@example.com")

    response = client.get(
        f"/completions/{habit_id}",
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert response.status_code == 404