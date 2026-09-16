"""Decorative drawing elements matching handwritten note aesthetic."""

import math
import re
from typing import Optional
from PIL import ImageDraw, ImageFont
from app.renderer.canvas import DESIGN_TOKENS
from app.renderer.typography import font_manager


def draw_star_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 10, color: tuple[int, int, int] = (26, 86, 180)) -> int:
    """Draw a clean 5-pointed star icon vector."""
    points = []
    for i in range(10):
        curr_r = r if i % 2 == 0 else r * 0.45
        angle = i * math.pi / 5 - math.pi / 2
        px = cx + curr_r * math.cos(angle)
        py = cy + curr_r * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=color)
    return r * 2


def draw_heading_with_underline(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    heading_text: str,
    font: Optional[ImageFont.FreeTypeFont] = None,
) -> int:
    """Draw section heading with blue number/star and red/coral underline beneath."""
    f = font or font_manager.get_heading_font(size=30)
    clean_text = font_manager.clean_inline_math(heading_text.strip())

    has_star = clean_text.startswith("★") or clean_text.startswith("*")
    if has_star:
        clean_text = clean_text.lstrip("★*").strip()

    num_part = ""
    title_part = clean_text

    if ". " in clean_text:
        parts = clean_text.split(". ", 1)
        if parts[0].isdigit() or (len(parts[0]) <= 5 and any(c.isdigit() for c in parts[0])):
            num_part = parts[0] + ". "
            title_part = parts[1]

    curr_x = x

    # Draw star if present
    if has_star:
        draw_star_icon(draw, cx=curr_x + 10, cy=y + 16, r=9, color=DESIGN_TOKENS["ink_heading_num"])
        curr_x += 26

    # Draw number part if present
    if num_part:
        draw.text((curr_x, y), num_part, fill=DESIGN_TOKENS["ink_heading_num"], font=f)
        bbox_num = draw.textbbox((curr_x, y), num_part, font=f)
        curr_x = bbox_num[2] + 4

    # Draw title text
    draw.text((curr_x, y), title_part, fill=DESIGN_TOKENS["ink_heading_title"], font=f)
    bbox_title = draw.textbbox((curr_x, y), title_part, font=f)

    # Red/coral underline directly beneath title
    underline_y = bbox_title[3] + 3
    draw.line([(curr_x, underline_y), (bbox_title[2] + 6, underline_y)], fill=DESIGN_TOKENS["ink_accent_red"], width=2)

    height = (bbox_title[3] - y) + 8
    return height


def draw_code_box_with_annotation(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    code_text: str,
    side_annotation: Optional[str] = None,
    max_total_width: int = 880,
) -> int:
    """Draw rounded code container on left with handwritten comment on right."""
    code_font = font_manager.get_code_font(size=19)
    annot_font = font_manager.get_annotation_font(size=22)

    code_lines = [line for line in code_text.strip().split("\n")]
    line_h = draw.textbbox((0, 0), "Ag", font=code_font)[3] + 8

    # Measure maximum line width of code
    max_code_w = 0
    for line_item in code_lines:
        w = draw.textbbox((0, 0), line_item, font=code_font)[2]
        if w > max_code_w:
            max_code_w = w

    box_pad_x = 18
    box_pad_y = 12

    # Box width fits code snugly plus padding
    box_w = min(max_code_w + (box_pad_x * 2), max_total_width)
    box_h = len(code_lines) * line_h + (box_pad_y * 2)

    # Draw Code Box
    draw.rounded_rectangle(
        [x, y, x + box_w, y + box_h],
        radius=6,
        fill=DESIGN_TOKENS["box_fill"],
        outline=DESIGN_TOKENS["box_border"],
        width=2,
    )

    # Draw Code Lines
    text_y = y + box_pad_y
    for line in code_lines:
        draw.text((x + box_pad_x, text_y), line, fill=DESIGN_TOKENS["ink_code"], font=code_font)
        text_y += line_h

    # Draw Side Annotation on right side
    if side_annotation:
        annot_x = x + box_w + 22
        annot_max_w = max(180, max_total_width - (box_w + 22))
        clean_annot = font_manager.clean_inline_math(side_annotation)
        annot_lines = font_manager.wrap_text(clean_annot, annot_font, annot_max_w, draw)

        annot_line_h = draw.textbbox((0, 0), "Ag", font=annot_font)[3] + 6
        annot_total_h = len(annot_lines) * annot_line_h
        annot_y = y + max(4, (box_h - annot_total_h) // 2)

        for line_str in annot_lines:
            draw.text((annot_x, annot_y), line_str, fill=DESIGN_TOKENS["ink_annotation"], font=annot_font)
            annot_y += annot_line_h

    return box_h + 10


def draw_callout_note(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    note_type: str,
    note_text: str,
    max_width: int = 880,
) -> int:
    """Draw a note or exam tip callout without repeating prefix words."""
    body_font = font_manager.get_body_font(size=25)

    # Format prefix nicely (e.g. 'Note: ' or 'Exam Tip: ')
    clean_type = note_type.replace("_", " ").title()
    prefix = f"{clean_type}: "

    # Strip existing prefix from text to avoid 'Note: Note: ...'
    clean_text = note_text.strip()
    clean_text = re.sub(r"^(Note|Exam Tip|Important|Tip)\s*:\s*", "", clean_text, flags=re.IGNORECASE)
    clean_text = font_manager.clean_inline_math(clean_text)

    prefix_w = draw.textbbox((0, 0), prefix, font=body_font)[2]

    # Draw prefix in red/coral
    draw.text((x, y), prefix, fill=DESIGN_TOKENS["ink_accent_red"], font=body_font)

    # Wrap note text taking prefix indent into account
    lines = font_manager.wrap_text(clean_text, body_font, max_width - prefix_w, draw)
    line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + 8

    for i, line_str in enumerate(lines):
        draw.text((x + prefix_w, y + (i * line_h)), line_str, fill=DESIGN_TOKENS["ink_body"], font=body_font)

    return (len(lines) * line_h) + 10


def draw_circled_page_number(
    draw: ImageDraw.ImageDraw,
    page_num: int,
    x: int = 970,
    y: int = 1270,
    radius: int = 24,
) -> None:
    """Draw a neat hand-drawn styled circled page number at bottom right."""
    font = font_manager.get_heading_font(size=26)
    draw.ellipse(
        [(x - radius, y - radius), (x + radius, y + radius)],
        outline=DESIGN_TOKENS["ink_body"],
        width=2,
    )
    num_str = str(page_num)
    bbox = draw.textbbox((0, 0), num_str, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(
        (x - w // 2 - 1, y - h // 2 - 6),
        num_str,
        fill=DESIGN_TOKENS["ink_body"],
        font=font,
    )


def draw_bullet_points(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    bullets: list[str],
    max_width: int = 880,
    bullet_symbol: str = "•",
) -> int:
    """Draw neatly indented bullet points in handwritten style."""
    body_font = font_manager.get_body_font(size=25)
    sym_w = draw.textbbox((0, 0), f"{bullet_symbol}  ", font=body_font)[2]
    line_h = draw.textbbox((0, 0), "Ag", font=body_font)[3] + 8

    total_h = 0
    for bullet in bullets:
        clean_bullet = font_manager.clean_inline_math(bullet)
        lines = font_manager.wrap_text(clean_bullet, body_font, max_width - sym_w, draw)
        draw.text((x, y + total_h), bullet_symbol, fill=DESIGN_TOKENS["ink_heading_num"], font=body_font)
        for line_str in lines:
            draw.text((x + sym_w, y + total_h), line_str, fill=DESIGN_TOKENS["ink_body"], font=body_font)
            total_h += line_h
        total_h += 4

    return total_h
