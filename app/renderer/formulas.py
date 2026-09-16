"""Mathematical formula rendering engine using Matplotlib mathtext with matrix support."""

import io
import re
from typing import Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from app.logging_config import logger

# LaTeX symbol normalizations for matplotlib mathtext compatibility
LATEX_REPLACEMENTS = {
    r"\implies": r"\Rightarrow",
    r"\iff": r"\Leftrightarrow",
    r"\to": r"\rightarrow",
    r"\gets": r"\leftarrow",
    r"\le": r"\leq",
    r"\ge": r"\geq",
    r"\ne": r"\neq",
}


def normalize_latex(formula: str) -> str:
    """Normalize common unsupported LaTeX macros for matplotlib mathtext."""
    s = formula.strip()
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()

    for old, new in LATEX_REPLACEMENTS.items():
        s = s.replace(old, new)

    return s


def render_matrix_box(
    rows: list[list[str]],
    fontsize: int = 24,
    color: tuple[int, int, int] = (16, 42, 67),
    cell_pad: int = 24,
) -> Image.Image:
    """Render a clean mathematical bracket matrix with aligned columns."""
    from app.renderer.typography import font_manager
    font = font_manager.load_font(
        ["SegoePrint-Bold.ttf", "PatrickHand-Regular.ttf", "Consolas-Bold.ttf", "arialbd.ttf"],
        size=fontsize,
    )
    
    # Measure columns
    temp_img = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(temp_img)
    n_cols = max(len(r) for r in rows)
    col_widths = [0] * n_cols

    for r in rows:
        for j, val in enumerate(r):
            bb = draw.textbbox((0, 0), str(val).strip(), font=font)
            w = bb[2] - bb[0]
            if w > col_widths[j]:
                col_widths[j] = w

    row_h = draw.textbbox((0, 0), "Ag", font=font)[3] + 18
    total_w = sum(col_widths) + (n_cols - 1) * cell_pad + 44
    total_h = len(rows) * row_h + 20

    img = Image.new("RGBA", (total_w, total_h), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    # Draw left square bracket [
    d.line([(14, 6), (6, 6), (6, total_h - 6), (14, total_h - 6)], fill=color, width=3)
    # Draw right square bracket ]
    d.line([(total_w - 14, 6), (total_w - 6, 6), (total_w - 6, total_h - 6), (total_w - 14, total_h - 6)], fill=color, width=3)

    y = 10
    for r in rows:
        x = 22
        for j, val in enumerate(r):
            # Center in column
            text_str = str(val).strip()
            bb = draw.textbbox((0, 0), text_str, font=font)
            item_w = bb[2] - bb[0]
            offset_x = (col_widths[j] - item_w) // 2
            d.text((x + offset_x, y), text_str, fill=color, font=font)
            x += col_widths[j] + cell_pad
        y += row_h

    return img


def parse_and_render_matrix(formula: str, fontsize: int = 24) -> Optional[Image.Image]:
    """Check if formula represents a LaTeX matrix and render it."""
    # Matches \begin{pmatrix} a & b \\ c & d \end{pmatrix} or \begin{matrix} ... \end{matrix}
    matrix_match = re.search(r"\\begin\{(?:p|b|v|V)?matrix\}(.*?)\\end\{(?:p|b|v|V)?matrix\}", formula, re.DOTALL)
    if not matrix_match:
        return None

    content = matrix_match.group(1).strip()
    raw_rows = [r.strip() for r in content.split(r"\\") if r.strip()]
    rows = []
    for r in raw_rows:
        cols = [c.strip() for c in r.split("&") if c.strip()]
        if cols:
            rows.append(cols)

    if not rows:
        return None

    return render_matrix_box(rows, fontsize=fontsize)


def render_formula_image(
    formula: str,
    fontsize: int = 24,
    color: str = "#102A43",
    dpi: int = 200,
    max_width: int = 800,
) -> Optional[Image.Image]:
    """Render a LaTeX mathematical formula or matrix to a transparent PIL Image."""
    clean_formula = normalize_latex(formula)

    # 1. Handle explicit matrices if present
    matrix_img = parse_and_render_matrix(clean_formula, fontsize=fontsize)
    if matrix_img:
        return matrix_img

    # 2. Render with Matplotlib mathtext
    mathtext_str = f"${clean_formula}$"
    try:
        fig = plt.figure(figsize=(8, 2), dpi=dpi)
        fig.patch.set_alpha(0.0)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.patch.set_alpha(0.0)

        ax.text(
            0.5,
            0.5,
            mathtext_str,
            fontsize=fontsize,
            color=color,
            ha="center",
            va="center",
            math_fontfamily="cm",
        )

        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            transparent=True,
            bbox_inches="tight",
            pad_inches=0.04,
            dpi=dpi,
        )
        plt.close(fig)
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")

        # Autocrop empty transparent borders
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        # Scale down if exceeds max_width
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_h = max(10, int(img.height * ratio))
            img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)

        return img

    except Exception as e:
        logger.warning(f"Mathtext failed for formula '{formula}': {e}. Falling back to text.")
        return _render_formula_fallback(clean_formula, fontsize, color, max_width)


def _render_formula_fallback(
    formula: str, fontsize: int, color: str, max_width: int
) -> Image.Image:
    """Fallback renderer for formulas that fail LaTeX parsing."""
    u_text = formula
    replacements = {
        r"\lambda": "λ",
        r"\sigma": "σ",
        r"\mu": "μ",
        r"\theta": "θ",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\sum": "Σ",
        r"\int": "∫",
        r"\infty": "∞",
        r"\dots": "...",
        r"\cdot": "·",
        r"\times": "×",
        r"\Rightarrow": "=>",
        r"\rightarrow": "->",
        "^2": "²",
        "^3": "³",
        "^n": "ⁿ",
    }
    for k, v in replacements.items():
        u_text = u_text.replace(k, v)

    font = ImageFont.load_default()
    img = Image.new("RGBA", (min(max_width, len(u_text) * 16 + 40), fontsize + 20), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), u_text, fill=color, font=font)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    return img
