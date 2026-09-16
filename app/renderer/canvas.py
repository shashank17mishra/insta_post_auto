"""Notebook paper canvas generator with ruled lines, spiral binder, and margin lines."""

from PIL import Image, ImageDraw

# Design Constants
DESIGN_TOKENS = {
    # Paper Background
    "paper_bg": (252, 251, 248),  # Warm off-white / light cream
    "ruled_line": (214, 226, 237),  # Soft notebook blue line
    "margin_red": (229, 115, 115),  # Soft red vertical margin line
    # Ink Colors
    "ink_body": (20, 40, 65),  # Ballpoint ink dark blue
    "ink_heading_num": (26, 86, 180),  # Blue for section numbers (e.g. '39.')
    "ink_heading_title": (15, 23, 42),  # Deep navy/black for section title
    "ink_accent_red": (220, 38, 38),  # Vibrant red for underlines and 'Note:'
    "ink_annotation": (45, 55, 72),  # Graphite/slate for side annotations
    "ink_code": (15, 23, 42),  # Clean dark monospace text
    # Box & Shapes
    "box_border": (71, 85, 105),  # Slate/blue stroke for code/formula boxes
    "box_fill": (248, 250, 252),  # Light grey/white box fill
    "callout_fill": (254, 243, 199),  # Subtle warm amber for exam tips
    # Layout Coordinates
    "width": 1080,
    "height": 1350,
    "content_x_start": 140,  # Content starts comfortably right of the red margin
    "content_x_end": 1020,  # Right content boundary (width = 880px)
    "content_y_start": 80,  # Top margin
    "content_y_end": 1280,  # Bottom boundary before footer
    "line_height_notebook": 38,  # Distance between horizontal ruled lines
    "margin_line_x": 105,  # Vertical red margin line position
}


def create_notebook_canvas(
    width: int = 1080,
    height: int = 1350,
    show_spiral: bool = True,
    show_ruled_lines: bool = True,
    show_margin_line: bool = True,
) -> Image.Image:
    """Create a high-resolution notebook paper canvas with authentic notebook aesthetics."""
    # 1. Base cream paper image
    img = Image.new("RGB", (width, height), DESIGN_TOKENS["paper_bg"])
    draw = ImageDraw.Draw(img)

    # 2. Horizontal ruled lines (college notebook style)
    if show_ruled_lines:
        line_y = 76
        while line_y < height - 50:
            draw.line(
                [(0, line_y), (width, line_y)],
                fill=DESIGN_TOKENS["ruled_line"],
                width=1,
            )
            line_y += DESIGN_TOKENS["line_height_notebook"]

    # 3. Vertical red margin line
    if show_margin_line:
        margin_x = DESIGN_TOKENS["margin_line_x"]
        draw.line(
            [(margin_x, 0), (margin_x, height)],
            fill=DESIGN_TOKENS["margin_red"],
            width=2,
        )

    # 4. Spiral binder rings on left edge
    if show_spiral:
        _draw_spiral_binder(draw, height)

    return img


def _draw_spiral_binder(draw: ImageDraw.ImageDraw, height: int) -> None:
    """Draw realistic spiral binder holes and wire loops along the left margin."""
    hole_w = 16
    hole_h = 24
    hole_x = 28
    step = 44  # Vertical distance between spiral rings

    y = 50
    while y < height - 60:
        # Spiral hole (black/dark grey with soft edge)
        draw.rounded_rectangle(
            [hole_x, y, hole_x + hole_w, y + hole_h],
            radius=4,
            fill=(25, 25, 25),
            outline=(60, 60, 60),
            width=1,
        )

        # Wire coil entering from edge into hole
        wire_y = y + hole_h // 2
        # Wire shadow
        draw.line([(0, wire_y + 2), (hole_x + hole_w // 2, wire_y + 2)], fill=(180, 180, 180), width=3)
        # Silver wire ring
        draw.line([(0, wire_y), (hole_x + hole_w // 2, wire_y)], fill=(70, 70, 75), width=3)
        # Highlight on wire
        draw.line([(2, wire_y - 1), (hole_x, wire_y - 1)], fill=(130, 130, 135), width=1)

        y += step
