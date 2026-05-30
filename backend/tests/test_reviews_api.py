"""Integration tests for the Reviews API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


class TestHealthAndRoot:
    """Basic health / readiness checks."""

    def test_root(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_health(self, client: TestClient):
        resp = client.get("/api/health")
        assert resp.status_code == 200


class TestCreateReview:
    """POST /api/reviews."""

    def test_create_github_review(self, client: TestClient):
        payload = {
            "inputType": "github",
            "repoUrl": "https://github.com/octocat/hello-world",
            "branch": "main",
            "perspectives": ["asvs"],
            "depth": "quick",
        }
        resp = client.post("/api/reviews", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert "reviewSessionId" in body
        assert body["status"] in ("queued", "running")

    def test_create_code_review(self, client: TestClient):
        payload = {
            "inputType": "code",
            "code": "import os\nos.system(input())",
            "filename": "vuln.py",
            "perspectives": ["asvs"],
            "depth": "quick",
        }
        resp = client.post("/api/reviews", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert "reviewSessionId" in body

    def test_create_review_no_input_falls_back_to_demo(self, client: TestClient):
        payload = {
            "inputType": "github",
            "perspectives": ["asvs"],
            "depth": "standard",
        }
        resp = client.post("/api/reviews", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        # Falls back to demo ID
        assert "reviewSessionId" in body


class TestGetReview:
    """GET /api/reviews/{id}."""

    def test_get_demo_review(self, client: TestClient):
        # The demo review ID should always return data
        resp = client.get("/api/reviews/demo-001")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == "demo-001"

    def test_get_nonexistent_review_falls_back_to_demo(self, client: TestClient):
        resp = client.get("/api/reviews/nonexistent-id")
        assert resp.status_code == 200


class TestGetFindings:
    """GET /api/reviews/{id}/findings."""

    def test_get_demo_findings(self, client: TestClient):
        resp = client.get("/api/reviews/demo-001/findings")
        assert resp.status_code == 200
        body = resp.json()
        assert "findings" in body
        assert len(body["findings"]) > 0


class TestRerunReview:
    """POST /api/reviews/{id}/rerun."""

    def test_rerun_nonexistent_returns_404(self, client: TestClient):
        resp = client.post("/api/reviews/nonexistent/rerun", json={})
        assert resp.status_code == 404
