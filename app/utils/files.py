"""File operations and safe path utilities."""

import json
import re
import shutil
from pathlib import Path
from typing import Any, Union
from PIL import Image


def sanitize_filename(name: str) -> str:
    """Sanitize a string for safe use in file and directory names."""
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r"\s+", "_", clean).strip(" ._-")
    return clean[:80] or "untitled"


def save_json(data: Any, path: Union[str, Path], indent: int = 2) -> Path:
    """Save serializable data to JSON file atomically."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    temp_path.replace(target)
    return target


def load_json(path: Union[str, Path], default: Any = None) -> Any:
    """Load JSON file safely with default fallback."""
    target = Path(path)
    if not target.exists():
        return default
    try:
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def copy_post_files(src_dir: Path, dst_dir: Path) -> list[Path]:
    """Copy all post files (PNGs, metadata.json, caption.txt) to destination."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for item in src_dir.iterdir():
        if item.is_file() and not item.name.startswith("."):
            dest_file = dst_dir / item.name
            shutil.copy2(item, dest_file)
            copied.append(dest_file)
    return copied


def validate_image_file(path: Union[str, Path], expected_w: int = 1080, expected_h: int = 1350) -> tuple[bool, str]:
    """Verify that an image exists, is valid PNG, and matches expected dimensions."""
    p = Path(path)
    if not p.exists():
        return False, f"File does not exist: {p}"
    try:
        with Image.open(p) as img:
            img.verify()
        with Image.open(p) as img:
            if img.format != "PNG":
                return False, f"Expected PNG format, got {img.format}"
            if img.size != (expected_w, expected_h):
                return False, f"Expected dimensions ({expected_w}, {expected_h}), got {img.size}"
            return True, "Valid"
    except Exception as e:
        return False, f"Image verification failed: {e}"
