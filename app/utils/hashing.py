"""Content hashing and deduplication utilities."""

import hashlib
import json
from pathlib import Path
from typing import Any, Union


def compute_text_hash(text: str) -> str:
    """Compute SHA-256 hash of a normalized text string."""
    normalized = " ".join(text.strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_content_hash(data: Union[dict[str, Any], list[Any], str]) -> str:
    """Compute deterministic SHA-256 hash of a structured JSON object or string."""
    if isinstance(data, str):
        return compute_text_hash(data)
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def compute_file_hash(file_path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    path = Path(file_path)
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()
