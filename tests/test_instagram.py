"""Tests for Instagram Graph API client and publisher (mocked and dry-run)."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from app.database.db import init_db
from app.database.models import PageModel, PostModel, PostStatus, TopicModel
from app.database.repository import Repository
from app.instagram.client import InstagramClient
from app.instagram.exceptions import InstagramTokenExpiredError
from app.instagram.publisher import InstagramPublisher


def test_instagram_dry_run_containers():
    """Verify that dry-run mode safely generates simulated container IDs without network calls."""
    client = InstagramClient(dry_run=True)

    single_id = client.create_single_photo_container("http://test.com/img.png", "Caption")
    assert single_id.startswith("dryrun_single_")

    slide_id = client.create_carousel_item_container("http://test.com/slide1.png")
    assert slide_id.startswith("dryrun_item_")

    parent_id = client.create_carousel_parent_container([slide_id], "Caption")
    assert parent_id.startswith("dryrun_carousel_")

    assert client.wait_for_container_ready(parent_id) is True

    media_id = client.publish_media_container(parent_id)
    assert media_id.startswith("dryrun_media_")


@patch("httpx.Client.post")
def test_instagram_mocked_api_calls(mock_post):
    """Verify live API flow using mocked httpx responses."""
    client = InstagramClient(
        access_token="EAABvalid_token_test",
        user_id="17841400000000000",
        dry_run=False,
    )

    # 1. Mock create slide container
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"id": "1800001"},
    )
    slide_id = client.create_carousel_item_container("http://example.com/page_01.png")
    assert slide_id == "1800001"

    # 2. Mock create parent carousel container
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"id": "1800002"},
    )
    parent_id = client.create_carousel_parent_container([slide_id], "Caption #Test")
    assert parent_id == "1800002"

    # 3. Mock publish
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"id": "1799999999"},
    )
    published_id = client.publish_media_container(parent_id)
    assert published_id == "1799999999"


@patch("httpx.Client.post")
def test_instagram_token_expired_error(mock_post):
    """Verify that Meta error subcode 190 correctly raises InstagramTokenExpiredError."""
    client = InstagramClient(
        access_token="expired_token",
        user_id="17841400000000000",
        dry_run=False,
    )

    mock_post.return_value = MagicMock(
        status_code=400,
        json=lambda: {
            "error": {
                "message": "Error validating access token: Session has expired",
                "type": "OAuthException",
                "code": 190,
                "error_subcode": 463,
            }
        },
    )

    with pytest.raises(InstagramTokenExpiredError):
        client.create_single_photo_container("http://example.com/img.png", "Caption")


def test_publisher_dry_run_workflow(tmp_path: Path):
    """Verify end-to-end publisher in dry-run mode."""
    test_db = tmp_path / "pub_test.db"
    init_db(test_db)
    repo = Repository(test_db)

    # Setup topic, post, and pages
    topic = TopicModel(id="test-sql", name="Test SQL", category="SQL")
    repo.create_topic(topic)

    post = PostModel(
        topic_id="test-sql",
        title="Test SQL Post",
        caption="Caption text",
        status=PostStatus.APPROVED,
    )
    post = repo.create_post(post)

    page = PageModel(
        post_id=post.id,
        page_number=1,
        file_path="generated/drafts/test/page_01.png",
    )
    repo.create_page(page)

    client = InstagramClient(dry_run=True)
    publisher = InstagramPublisher(repository=repo, client=client)

    success, msg = publisher.publish_post(post.id)
    assert success is True
    assert "Published successfully" in msg

    # Verify post status updated
    updated_post = repo.get_post(post.id)
    assert updated_post.status == PostStatus.PUBLISHED
    assert updated_post.instagram_media_id is not None
