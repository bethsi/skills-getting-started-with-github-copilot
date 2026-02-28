from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

def test_signup_and_cancel():
    # make a fresh activity
    activities["unit-test"] = {
        "description": "",
        "schedule": "",
        "max_participants": 2,
        "participants": ["u1@example.com"]
    }

    # cancel existing participant
    r = client.delete("/activities/unit-test/signup", params={"email": "u1@example.com"})
    assert r.status_code == 200
    assert "Removed u1@example.com" in r.json()["message"]
    assert "u1@example.com" not in activities["unit-test"]["participants"]

    # cancelling again should give 404
    r2 = client.delete("/activities/unit-test/signup", params={"email": "u1@example.com"})
    assert r2.status_code == 404

    # signup back and check existing email prevention
    r3 = client.post("/activities/unit-test/signup", params={"email": "u1@example.com"})
    assert r3.status_code == 200
    r4 = client.post("/activities/unit-test/signup", params={"email": "u1@example.com"})
    assert r4.status_code == 400
