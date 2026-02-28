"""Tests for Mergington High School API

Covers all endpoints: GET activities, POST signup, DELETE signup.
"""

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


class TestGetEndpoints:
    """Test GET endpoints for listing and redirects."""

    def test_get_activities_returns_all(self):
        """GET /activities should return the activities dict."""
        r = client.get("/activities")
        assert r.status_code == 200
        data = r.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12

    def test_get_activities_has_participants(self):
        """Each activity should have a participants list."""
        r = client.get("/activities")
        data = r.json()
        for name, details in data.items():
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_root_redirects_to_static(self):
        """GET / should redirect to /static/index.html."""
        r = client.get("/", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == "/static/index.html"


class TestPostSignup:
    """Test POST signup endpoint."""

    @classmethod
    def setup_class(cls):
        """Create a test activity before all tests in this class."""
        activities["_test_post"] = {
            "description": "Test",
            "schedule": "Test",
            "max_participants": 5,
            "participants": []
        }

    def test_signup_success(self):
        """POST signup should add email to participants."""
        email = "alice@test.com"
        r = client.post(
            "/activities/_test_post/signup",
            params={"email": email}
        )
        assert r.status_code == 200
        assert email in activities["_test_post"]["participants"]
        assert f"Signed up {email}" in r.json()["message"]

    def test_signup_duplicate_email(self):
        """POST signup with existing email should return 400."""
        email = "bob@test.com"
        # first signup
        r1 = client.post(
            "/activities/_test_post/signup",
            params={"email": email}
        )
        assert r1.status_code == 200
        # second signup with same email
        r2 = client.post(
            "/activities/_test_post/signup",
            params={"email": email}
        )
        assert r2.status_code == 400
        assert "already signed up" in r2.json()["detail"]

    def test_signup_invalid_activity(self):
        """POST signup for non-existent activity should return 404."""
        r = client.post(
            "/activities/no-such-activity/signup",
            params={"email": "test@test.com"}
        )
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()


class TestDeleteSignup:
    """Test DELETE signup endpoint."""

    @classmethod
    def setup_class(cls):
        """Create a test activity with a participant."""
        activities["_test_delete"] = {
            "description": "Test",
            "schedule": "Test",
            "max_participants": 5,
            "participants": ["charlie@test.com", "diana@test.com"]
        }

    def test_delete_success(self):
        """DELETE should remove email from participants."""
        email = "charlie@test.com"
        assert email in activities["_test_delete"]["participants"]
        r = client.delete(
            "/activities/_test_delete/signup",
            params={"email": email}
        )
        assert r.status_code == 200
        assert email not in activities["_test_delete"]["participants"]
        assert f"Removed {email}" in r.json()["message"]

    def test_delete_nonexistent_participant(self):
        """DELETE non-existent email should return 404."""
        r = client.delete(
            "/activities/_test_delete/signup",
            params={"email": "nothere@test.com"}
        )
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_delete_from_invalid_activity(self):
        """DELETE from non-existent activity should return 404."""
        r = client.delete(
            "/activities/no-such-activity/signup",
            params={"email": "test@test.com"}
        )
        assert r.status_code == 404


class TestIntegration:
    """Integration tests combining multiple operations."""

    @classmethod
    def setup_class(cls):
        """Create a test activity."""
        activities["_test_integration"] = {
            "description": "Integration test",
            "schedule": "Test",
            "max_participants": 3,
            "participants": []
        }

    def test_signup_then_view(self):
        """After signup, participant should appear in GET /activities."""
        email = "eve@test.com"
        # signup
        client.post(
            "/activities/_test_integration/signup",
            params={"email": email}
        )
        # fetch activities
        r = client.get("/activities")
        assert email in r.json()["_test_integration"]["participants"]

    def test_signup_delete_signup(self):
        """Signup, delete, then signup again should work."""
        email = "frank@test.com"
        # signup
        r1 = client.post(
            "/activities/_test_integration/signup",
            params={"email": email}
        )
        assert r1.status_code == 200
        # delete
        r2 = client.delete(
            "/activities/_test_integration/signup",
            params={"email": email}
        )
        assert r2.status_code == 200
        # signup again
        r3 = client.post(
            "/activities/_test_integration/signup",
            params={"email": email}
        )
        assert r3.status_code == 200
        assert email in activities["_test_integration"]["participants"]
