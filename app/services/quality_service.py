"""Visual quality control and automated image verification."""

from pathlib import Path
from typing import Tuple
from PIL import Image, ImageStat
from app.content.schemas import NotePostContent
from app.logging_config import logger


class QualityControlService:
    """Automated validator ensuring rendered note images meet publication standards."""

    def __init__(
        self,
        expected_width: int = 1080,
        expected_height: int = 1350,
        min_file_size_bytes: int = 30000,  # 30 KB
    ):
        self.expected_width = expected_width
        self.expected_height = expected_height
        self.min_file_size_bytes = min_file_size_bytes

    def validate_rendered_page(self, image_path: Path) -> Tuple[bool, list[str]]:
        """Run structural and visual checks on a single rendered note page."""
        issues: list[str] = []

        if not image_path.exists():
            return False, [f"Image file does not exist: {image_path}"]

        file_size = image_path.stat().st_size
        if file_size < self.min_file_size_bytes:
            issues.append(
                f"File size suspiciously small ({file_size} bytes < {self.min_file_size_bytes}), possible empty render."
            )

        try:
            with Image.open(image_path) as img:
                # 1. Format verification
                if img.format != "PNG":
                    issues.append(f"Invalid format {img.format}; expected PNG.")

                # 2. Dimension verification (1080x1350)
                if img.size != (self.expected_width, self.expected_height):
                    issues.append(
                        f"Invalid dimensions {img.size}; expected ({self.expected_width}, {self.expected_height})."
                    )

                # 3. Non-emptiness / Variance check (detect completely blank or solid images)
                stat = ImageStat.Stat(img)
                # Standard deviation across bands
                std_dev = sum(stat.stddev) / len(stat.stddev)
                if std_dev < 1.0:
                    issues.append("Image appears completely uniform / blank (variance < 1.0).")

        except Exception as e:
            issues.append(f"Image corruption check failed: {e}")

        is_valid = len(issues) == 0
        if not is_valid:
            logger.warning(f"Quality check failed for {image_path.name}: {issues}")
        return is_valid, issues

    def validate_carousel_post(
        self,
        content: NotePostContent,
        page_paths: list[Path],
    ) -> Tuple[bool, list[str]]:
        """Validate an entire carousel post against content and visual standards."""
        all_issues: list[str] = []

        # Content checks
        if not content.topic or not content.title:
            all_issues.append("Post must have non-empty topic and title.")

        if not page_paths:
            all_issues.append("Post contains zero rendered page images.")
            return False, all_issues

        if len(page_paths) != len(content.pages):
            all_issues.append(
                f"Page count mismatch: rendered {len(page_paths)} images for {len(content.pages)} content pages."
            )

        # Individual page image checks
        for path in page_paths:
            valid, issues = self.validate_rendered_page(path)
            if not valid:
                all_issues.extend(issues)

        is_valid = len(all_issues) == 0
        return is_valid, all_issues


# Global singleton
quality_service = QualityControlService()
