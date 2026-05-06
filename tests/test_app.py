from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from app import app, activities


client = TestClient(app)


def _snapshot_activities():
    return {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities.items()
    }


def _restore_activities(snapshot):
    activities.clear()
    for name, details in snapshot.items():
        activities[name] = {**details, "participants": list(details["participants"])}


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data


def test_signup_and_unregister():
    snapshot = _snapshot_activities()
    try:
        email = "test.student@mergington.edu"
        response = client.post("/activities/Chess%20Club/signup", params={"email": email})
        assert response.status_code == 200
        assert email in activities["Chess Club"]["participants"]

        response = client.delete(
            "/activities/Chess%20Club/participants", params={"email": email}
        )
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
    finally:
        _restore_activities(snapshot)
