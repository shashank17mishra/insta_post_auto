"""Tests for FastAPI REST API endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns valid structure."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "gemini" in data
    assert "instagram" in data
    assert "stats" in data


def test_list_topics():
    """Verify topic listing endpoint."""
    res = client.get("/api/topics?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "topics" in data
    assert isinstance(data["topics"], list)


def test_create_topic():
    """Verify creating a new topic via API."""
    payload = {
        "name": "Breadth First Search",
        "category": "Algorithms",
        "difficulty": "beginner",
        "priority": 75,
    }
    res = client.post("/api/topics", json=payload)
    # May return 200 or 409 if already exists
    assert res.status_code in (200, 409)


def test_generate_endpoint_mock():
    """Verify triggering note generation via API in mock mode."""
    import uuid
    unique_topic = f"test-topic-{uuid.uuid4().hex[:6]}"
    res = client.post(f"/api/generate/{unique_topic}?force_mock=true")
    assert res.status_code == 200
    data = res.json()
    assert "post_id" in data
    assert data["status"] == "draft"


def test_posts_lifecycle_endpoints():
    """Verify post review, approval, and dry-run publishing via API."""
    # 1. Fetch posts
    res = client.get("/api/posts?limit=10")
    assert res.status_code == 200
    posts = res.json()["posts"]
    assert len(posts) > 0

    first_post_id = posts[0]["id"]

    # 2. Approve post
    res_approve = client.post(f"/api/posts/{first_post_id}/approve")
    # Might be already published or approved
    assert res_approve.status_code in (200, 400)

    # 3. Publish post (dry-run)
    res_pub = client.post(f"/api/posts/{first_post_id}/publish?force=true")
    assert res_pub.status_code in (200, 400)


def test_settings_endpoints():
    """Verify retrieving and updating system settings."""
    res_get = client.get("/api/settings")
    assert res_get.status_code == 200
    data = res_get.json()["settings"]
    assert "dry_run" in data
    assert "gemini_model" in data

    # Update settings
    res_post = client.post("/api/settings", json={"posting_cron": "0 14 * * *"})
    assert res_post.status_code == 200
