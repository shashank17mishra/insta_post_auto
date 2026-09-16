"""System settings API routes."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings
from app.database.repository import Repository
from app.services.scheduling_service import scheduling_service

router = APIRouter(prefix="/api", tags=["Settings"])
repo = Repository()


class UpdateSettingsRequest(BaseModel):
    posting_cron: Optional[str] = None
    default_category: Optional[str] = None
    dry_run: Optional[bool] = None
    publish_enabled: Optional[bool] = None


@router.get("/settings")
def get_settings():
    """Retrieve safe system settings (secrets are never exposed)."""
    schedule = scheduling_service.get_schedule_status()
    return {
        "settings": {
            "app_env": settings.app_env,
            "gemini_model": settings.gemini_model,
            "gemini_configured": bool(settings.gemini_api_key),
            "instagram_configured": bool(settings.instagram_access_token and settings.instagram_user_id),
            "instagram_publish_enabled": settings.instagram_publish_enabled,
            "dry_run": settings.dry_run,
            "public_base_url": settings.public_base_url,
            "posting_cron": schedule["cron_expression"],
            "default_category": schedule["default_category"],
        }
    }


@router.post("/settings")
def update_settings(req: UpdateSettingsRequest):
    """Update configurable settings."""
    if req.posting_cron is not None:
        repo.set_setting("posting_cron", req.posting_cron)
    if req.default_category is not None:
        repo.set_setting("default_category", req.default_category)
    if req.dry_run is not None:
        settings.dry_run = req.dry_run
    if req.publish_enabled is not None:
        settings.instagram_publish_enabled = req.publish_enabled

    return {"message": "Settings updated successfully"}
