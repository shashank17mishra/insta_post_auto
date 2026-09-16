"""Health check and system diagnostics endpoint."""

from fastapi import APIRouter
from app.config import settings
from app.database.repository import Repository
from app.ai.gemini_client import GeminiClient
from app.instagram.client import InstagramClient

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def get_health_status():
    """Return comprehensive system health and API integration statuses."""
    repo = Repository()
    stats = repo.get_dashboard_stats()

    gemini_client = GeminiClient()
    gemini_ok = gemini_client.is_configured()

    ig_client = InstagramClient()
    ig_ready, ig_reason = ig_client.is_ready_for_publishing()

    return {
        "status": "healthy",
        "environment": settings.app_env,
        "gemini": {
            "configured": gemini_ok,
            "model": settings.gemini_model,
        },
        "instagram": {
            "publish_enabled": settings.instagram_publish_enabled,
            "dry_run": settings.dry_run,
            "ready": ig_ready,
            "status_message": ig_reason,
        },
        "stats": stats,
    }
