"""Publishing service handling approval workflows and state changes."""

from typing import Optional, Tuple
from app.database.models import PostStatus
from app.database.repository import Repository
from app.instagram.publisher import instagram_publisher
from app.logging_config import logger


class PublishingService:
    """Handles post approval lifecycle and publishing triggers."""

    def __init__(self, repository: Optional[Repository] = None):
        self.repo = repository or Repository()

    def approve_post(self, post_id: int) -> Tuple[bool, str]:
        """Mark post as approved by human reviewer."""
        post = self.repo.get_post(post_id)
        if not post:
            return False, f"Post #{post_id} does not exist."
        if post.status == PostStatus.PUBLISHED:
            return False, "Cannot approve an already published post."

        self.repo.update_post_status(post_id, PostStatus.APPROVED)
        logger.info(f"Post #{post_id} approved for publication.")
        return True, f"Post #{post_id} approved."

    def reject_post(self, post_id: int, reason: Optional[str] = None) -> Tuple[bool, str]:
        """Mark post as rejected with optional reason."""
        post = self.repo.get_post(post_id)
        if not post:
            return False, f"Post #{post_id} does not exist."

        self.repo.update_post_status(post_id, PostStatus.REJECTED, error=reason or "Rejected by user")
        logger.info(f"Post #{post_id} rejected: {reason}")
        return True, f"Post #{post_id} rejected."

    def publish_now(self, post_id: int, force: bool = False) -> Tuple[bool, str]:
        """Trigger immediate publishing (dry-run or live)."""
        return instagram_publisher.publish_post(post_id, force=force)


# Global instance
publishing_service = PublishingService()
