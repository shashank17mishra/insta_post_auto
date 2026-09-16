"""Official Meta / Instagram Graph API client."""

import time
import uuid
from typing import Any, Optional
import httpx
from app.config import settings
from app.instagram.exceptions import (
    InstagramAPIError,
    InstagramMediaUploadError,
    InstagramTokenExpiredError,
)
from app.logging_config import logger

GRAPH_API_VERSION = "v20.0"
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class InstagramClient:
    """Official Meta Graph API client for carousel and image posting."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        user_id: Optional[str] = None,
        dry_run: Optional[bool] = None,
        timeout: float = 30.0,
    ):
        self.access_token = access_token or settings.instagram_access_token
        self.user_id = user_id or settings.instagram_user_id
        self.dry_run = settings.dry_run if dry_run is None else dry_run
        self.timeout = timeout

    def is_ready_for_publishing(self) -> tuple[bool, str]:
        """Verify credentials and readiness."""
        if not settings.instagram_publish_enabled and not self.dry_run:
            return False, "INSTAGRAM_PUBLISH_ENABLED is set to false in settings."
        if not self.dry_run:
            if not self.access_token:
                return False, "INSTAGRAM_ACCESS_TOKEN is missing."
            if not self.user_id:
                return False, "INSTAGRAM_USER_ID is missing."
        return True, "Ready"

    def create_single_photo_container(self, image_url: str, caption: str) -> str:
        """Create container for single photo post."""
        if self.dry_run:
            simulated_id = f"dryrun_single_{uuid.uuid4().hex[:12]}"
            logger.info(f"[DRY RUN] Created single photo container: {simulated_id} for {image_url}")
            return simulated_id

        url = f"{GRAPH_API_BASE_URL}/{self.user_id}/media"
        params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        res_data = self._post_request(url, params)
        return res_data["id"]

    def create_carousel_item_container(self, image_url: str) -> str:
        """Create media container for an individual slide in a carousel."""
        if self.dry_run:
            simulated_id = f"dryrun_item_{uuid.uuid4().hex[:12]}"
            logger.info(f"[DRY RUN] Created carousel slide container: {simulated_id} for {image_url}")
            return simulated_id

        url = f"{GRAPH_API_BASE_URL}/{self.user_id}/media"
        params = {
            "image_url": image_url,
            "is_carousel_item": "true",
            "access_token": self.access_token,
        }
        res_data = self._post_request(url, params)
        return res_data["id"]

    def create_carousel_parent_container(self, children_ids: list[str], caption: str) -> str:
        """Combine slide container IDs into a single carousel container."""
        if self.dry_run:
            simulated_id = f"dryrun_carousel_{uuid.uuid4().hex[:12]}"
            logger.info(
                f"[DRY RUN] Created carousel parent container: {simulated_id} with {len(children_ids)} slides"
            )
            return simulated_id

        url = f"{GRAPH_API_BASE_URL}/{self.user_id}/media"
        params = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": self.access_token,
        }
        res_data = self._post_request(url, params)
        return res_data["id"]

    def wait_for_container_ready(self, container_id: str, max_wait: int = 30) -> bool:
        """Poll container status until FINISHED or timeout."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Container {container_id} status: FINISHED")
            return True

        url = f"{GRAPH_API_BASE_URL}/{container_id}"
        start = time.time()

        while time.time() - start < max_wait:
            res_data = self._get_request(url, {"fields": "status_code", "access_token": self.access_token})
            status = res_data.get("status_code")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                raise InstagramMediaUploadError(f"Container {container_id} processing failed on Meta servers.")
            time.sleep(2)

        return False

    def publish_media_container(self, container_id: str) -> str:
        """Publish the finalized media container to the user's feed."""
        if self.dry_run:
            media_id = f"dryrun_media_{uuid.uuid4().hex[:14]}"
            logger.info(f"[DRY RUN] Successfully published container {container_id} -> Media ID: {media_id}")
            return media_id

        url = f"{GRAPH_API_BASE_URL}/{self.user_id}/media_publish"
        params = {
            "creation_id": container_id,
            "access_token": self.access_token,
        }
        res_data = self._post_request(url, params)
        published_id = res_data["id"]
        logger.info(f"Published Instagram post successfully! Media ID: {published_id}")
        return published_id

    def _post_request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute HTTP POST request with structured error handling."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, data=params)
                data = res.json()

                if res.status_code >= 400 or "error" in data:
                    self._handle_api_error(data.get("error", {}), res.status_code)

                return data
        except httpx.RequestError as e:
            logger.error(f"Network error calling Meta API: {e}")
            raise InstagramAPIError(f"Network request to Meta Graph API failed: {e}")

    def _get_request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute HTTP GET request with structured error handling."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params)
                data = res.json()

                if res.status_code >= 400 or "error" in data:
                    self._handle_api_error(data.get("error", {}), res.status_code)

                return data
        except httpx.RequestError as e:
            logger.error(f"Network error calling Meta API: {e}")
            raise InstagramAPIError(f"Network request to Meta Graph API failed: {e}")

    @staticmethod
    def _handle_api_error(err: dict[str, Any], status_code: int) -> None:
        """Inspect Meta API error payload and raise appropriate exception."""
        code = err.get("code", 0)
        subcode = err.get("error_subcode", 0)
        message = err.get("message", "Unknown Meta Graph API error")

        logger.error(f"Meta Graph API Error [HTTP {status_code}] Code: {code}, Subcode: {subcode}: {message}")

        if code == 190:  # Invalid or expired token
            raise InstagramTokenExpiredError(f"Instagram Access Token has expired or is invalid: {message}", status_code, subcode)

        raise InstagramAPIError(f"Meta API Error ({code}): {message}", status_code, subcode)
