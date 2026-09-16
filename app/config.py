"""Application configuration module using Pydantic Settings."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General Environment
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Google Gemini AI
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.8-flash", alias="GEMINI_MODEL")

    # Meta / Instagram Graph API
    instagram_publish_enabled: bool = Field(default=False, alias="INSTAGRAM_PUBLISH_ENABLED")
    dry_run: bool = Field(default=True, alias="DRY_RUN")
    instagram_access_token: Optional[str] = Field(default=None, alias="INSTAGRAM_ACCESS_TOKEN")
    instagram_user_id: Optional[str] = Field(default=None, alias="INSTAGRAM_USER_ID")
    meta_app_id: Optional[str] = Field(default=None, alias="META_APP_ID")
    meta_app_secret: Optional[str] = Field(default=None, alias="META_APP_SECRET")
    public_base_url: str = Field(default="http://localhost:8000", alias="PUBLIC_BASE_URL")

    # File Paths
    project_root: Path = PROJECT_ROOT
    database_path: Path = Field(default=PROJECT_ROOT / "data" / "studynotes.db", alias="DATABASE_PATH")
    topics_file_path: Path = Field(default=PROJECT_ROOT / "data" / "topics.json", alias="TOPICS_FILE_PATH")
    output_dir: Path = Field(default=PROJECT_ROOT / "generated", alias="OUTPUT_DIR")
    log_file_path: Path = Field(default=PROJECT_ROOT / "logs" / "app.log", alias="LOG_FILE_PATH")
    assets_dir: Path = Field(default=PROJECT_ROOT / "assets")

    # Note Canvas Specs (Fixed 4:5 aspect ratio)
    canvas_width: int = 1080
    canvas_height: int = 1350

    def ensure_directories(self) -> None:
        """Ensure necessary runtime directories exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "drafts").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "approved").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "published").mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)


# Global settings singleton instance
settings = Settings()
settings.ensure_directories()
