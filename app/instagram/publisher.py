"""High-level Instagram publishing coordinator."""

from typing import Optional, Tuple
from app.config import settings
from app.database.models import PostStatus, PublishAttemptModel
from app.database.repository import Repository
from app.instagram.client import InstagramClient
from app.instagram.exceptions import InstagramException
from app.instagram.media import resolve_public_image_url
from app.logging_config import logger
from app.utils.files import copy_post_files


class InstagramPublisher:
    """Coordinates post approval and publishing via official Graph API."""

    def __init__(
        self,
        repository: Optional[Repository] = None,
        client: Optional[InstagramClient] = None,
    ):
        self.repo = repository or Repository()
        self.client = client or InstagramClient()

    def publish_post(self, post_id: int, force: bool = False) -> Tuple[bool, str]:
        """Publish an approved post to Instagram (or simulate in dry-run mode)."""
        post = self.repo.get_post(post_id)
        if not post:
            return False, f"Post #{post_id} not found."

        if not force and post.status not in (PostStatus.APPROVED, PostStatus.DRAFT):
            return False, f"Post #{post_id} has status '{post.status.value}'. Must be 'approved' to publish."

        pages = self.repo.get_pages_for_post(post_id)
        if not pages:
            return False, f"No pages found for post #{post_id}."

        logger.info(
            f"Initiating Instagram publication for post #{post_id} ('{post.title}'), "
            f"Slides: {len(pages)}, DryRun: {self.client.dry_run}"
        )

        # Readiness check
        ready, reason = self.client.is_ready_for_publishing()
        if not ready:
            err_msg = f"Instagram publishing blocked: {reason}"
            logger.warning(err_msg)
            self._record_attempt(post_id, "FAILED", error_message=err_msg)
            return False, err_msg

        try:
            # 1. Resolve URLs for all pages
            image_urls = [
                resolve_public_image_url(settings.project_root / p.file_path)
                for p in pages
            ]

            # 2. Publish as single image or carousel
            if len(image_urls) == 1:
                container_id = self.client.create_single_photo_container(
                    image_url=image_urls[0],
                    caption=post.caption,
                )
                self.client.wait_for_container_ready(container_id)
                media_id = self.client.publish_media_container(container_id)
            else:
                slide_ids = []
                for img_url in image_urls:
                    s_id = self.client.create_carousel_item_container(img_url)
                    slide_ids.append(s_id)

                parent_id = self.client.create_carousel_parent_container(
                    children_ids=slide_ids,
                    caption=post.caption,
                )
                self.client.wait_for_container_ready(parent_id)
                media_id = self.client.publish_media_container(parent_id)

            # 3. Update Post in DB
            self.repo.set_post_published(post_id, instagram_media_id=media_id, dry_run=self.client.dry_run)

            # 4. Copy files to generated/published
            src_dir = settings.output_dir / "drafts" / str(post_id)
            pub_dir = settings.output_dir / "published" / str(post_id)
            if src_dir.exists():
                copy_post_files(src_dir, pub_dir)

            # 5. Record Attempt
            self._record_attempt(post_id, "SUCCESS", payload=f"Media ID: {media_id}")
            logger.info(f"Post #{post_id} successfully published to Instagram! Media ID: {media_id}")

            return True, f"Published successfully! Media ID: {media_id}"

        except InstagramException as e:
            err_str = f"Instagram API Error: {e}"
            logger.error(err_str)
            self.repo.update_post_status(post_id, PostStatus.FAILED, error=err_str)
            self._record_attempt(post_id, "FAILED", error_message=err_str)
            return False, err_str
        except Exception as e:
            err_str = f"Unexpected error publishing post #{post_id}: {e}"
            logger.error(err_str)
            self.repo.update_post_status(post_id, PostStatus.FAILED, error=err_str)
            self._record_attempt(post_id, "FAILED", error_message=err_str)
            return False, err_str

    def _record_attempt(
        self,
        post_id: int,
        status: str,
        payload: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Helper to write audit log in publish_attempts."""
        attempt = PublishAttemptModel(
            post_id=post_id,
            status=status,
            response_payload=payload,
            error_message=error_message,
        )
        self.repo.record_publish_attempt(attempt)


# Global publisher instance
instagram_publisher = InstagramPublisher()
