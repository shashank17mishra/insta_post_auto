"""Media URL resolution for Meta Graph API."""

from pathlib import Path
from typing import Union
from app.config import settings


def resolve_public_image_url(file_path: Union[str, Path]) -> str:
    """Resolve local image path to public URL accessible by Meta crawlers."""
    p = Path(file_path)
    # Ensure relative path from project root
    try:
        rel = p.resolve().relative_to(settings.project_root.resolve())
    except Exception:
        rel = p

    # Clean path separators for URL
    url_path = str(rel).replace("\\", "/")
    if not url_path.startswith("/"):
        url_path = f"/{url_path}"

    base = settings.public_base_url.rstrip("/")
    return f"{base}{url_path}"
