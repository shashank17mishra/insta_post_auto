"""Typography and font manager for handwritten note rendering."""

import re
from pathlib import Path
from typing import Optional
from PIL import ImageDraw, ImageFont
from app.config import settings
from app.logging_config import logger

FONTS_DIR = settings.assets_dir / "fonts"


class FontManager:
    """Manages typography, font caching, and line wrapping."""

    def __init__(self, fonts_dir: Optional[Path] = None):
        self.fonts_dir = fonts_dir or FONTS_DIR
        self._font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

    def get_font_path(self, font_name: str) -> Optional[Path]:
        """Locate font file in assets/fonts or Windows system fonts."""
        # 1. Check bundled assets/fonts
        bundled_path = self.fonts_dir / font_name
        if bundled_path.exists():
            return bundled_path

        # 2. Check Windows Fonts folder
        sys_path = Path("C:/Windows/Fonts") / font_name
        if sys_path.exists():
            return sys_path

        return None

    def load_font(self, font_names: list[str], size: int) -> ImageFont.FreeTypeFont:
        """Load the first available font from candidates, caching the result."""
        for name in font_names:
            cache_key = (name, size)
            if cache_key in self._font_cache:
                return self._font_cache[cache_key]

            path = self.get_font_path(name)
            if path:
                try:
                    font = ImageFont.truetype(str(path), size=size)
                    self._font_cache[cache_key] = font
                    return font
                except Exception as e:
                    logger.warning(f"Could not load font {name}: {e}")

        # Fallback to Pillow default
        logger.warning(f"None of {font_names} found; falling back to default font.")
        return ImageFont.load_default()

    # Pre-defined typography roles
    def get_title_font(self, size: int = 42) -> ImageFont.FreeTypeFont:
        """Main note or carousel title font."""
        return self.load_font(
            ["SegoePrint-Bold.ttf", "PatrickHand-Regular.ttf", "InkFree.ttf", "ComicSans-Bold.ttf", "arialbd.ttf"],
            size,
        )

    def get_heading_font(self, size: int = 34) -> ImageFont.FreeTypeFont:
        """Section heading font (e.g. '39. GROUP BY Clause')."""
        return self.load_font(
            ["SegoePrint-Bold.ttf", "PatrickHand-Regular.ttf", "InkFree.ttf", "ComicSans-Bold.ttf", "arialbd.ttf"],
            size,
        )

    def get_body_font(self, size: int = 28) -> ImageFont.FreeTypeFont:
        """Main handwritten body text font."""
        return self.load_font(
            ["SegoePrint.ttf", "PatrickHand-Regular.ttf", "InkFree.ttf", "ComicSans.ttf", "arial.ttf"],
            size,
        )

    def get_annotation_font(self, size: int = 24) -> ImageFont.FreeTypeFont:
        """Casual handwritten note / side comment font."""
        return self.load_font(
            ["InkFree.ttf", "SegoePrint.ttf", "PatrickHand-Regular.ttf", "ComicSans.ttf", "ariali.ttf"],
            size,
        )

    def get_code_font(self, size: int = 24) -> ImageFont.FreeTypeFont:
        """Clean monospace font for SQL and code snippets."""
        return self.load_font(
            ["Consolas-Bold.ttf", "Consolas.ttf", "courbd.ttf", "cour.ttf"],
            size,
        )

    def wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        draw: ImageDraw.ImageDraw,
    ) -> list[str]:
        """Wrap text into multiple lines so that each fits within max_width."""
        lines: list[str] = []
        # Handle explicit newlines first
        paragraphs = text.split("\n")

        for para in paragraphs:
            if not para.strip():
                lines.append("")
                continue

            words = para.split(" ")
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip() if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]

                if w <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines

    @staticmethod
    def get_text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
        """Compute the rendered pixel height of a single line of text."""
        bbox = draw.textbbox((0, 0), text if text.strip() else "Ag", font=font)
        return bbox[3] - bbox[1]

    @staticmethod
    def clean_inline_math(text: str) -> str:
        """Convert raw LaTeX commands in regular text into font-safe readable math."""
        if not text:
            return ""
        s = text
        replacements = [
            (r"\lambda", "λ"),
            (r"\dots", "..."),
            (r"\cdot", "·"),
            (r"\times", "×"),
            (r"==>", "=>"),
            (r"->", "→"),
            (r"\frac{1}{3}", "1/3"),
            (r"\frac{1}{2}", "1/2"),
            (r"A^{-1}", "A^-1"),
            (r"P^{-1}", "P^-1"),
            (r"\lambda^n", "λ^n"),
            (r"\lambda^2", "λ^2"),
            (r"\lambda^{n-1}", "λ^(n-1)"),
            (r"A^{n-1}", "A^(n-1)"),
            (r"c_1", "c1"),
            (r"c_n", "cn"),
            (r"\\", " "),
        ]
        for old, new in replacements:
            s = s.replace(old, new)
        # Strip remaining single backslashes before letters
        s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)
        return s


# Singleton instance
font_manager = FontManager()
