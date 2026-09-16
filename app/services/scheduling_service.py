"""Scheduling and automation service."""

from typing import Any
from app.config import settings
from app.database.repository import Repository


class SchedulingService:
    """Manages automation settings and schedule diagnostics."""

    def __init__(self, repository: Repository = None):
        self.repo = repository or Repository()

    def get_schedule_status(self) -> dict[str, Any]:
        """Return configured schedule details and GitHub Actions status."""
        cron_expression = self.repo.get_setting("posting_cron", "0 12 * * *")  # Daily at 12:00 UTC
        category_filter = self.repo.get_setting("default_category", "All")

        return {
            "cron_expression": cron_expression,
            "description": "Daily at 12:00 PM UTC (Configured via GitHub Actions)",
            "default_category": category_filter,
            "dry_run": settings.dry_run,
            "publish_enabled": settings.instagram_publish_enabled,
            "environment": settings.app_env,
        }


# Global instance
scheduling_service = SchedulingService()
