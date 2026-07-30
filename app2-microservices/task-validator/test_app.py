from app import app


def test_root_returns_helpful_message():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["service"] == "task-validator"
    assert "health" in payload["message"]
