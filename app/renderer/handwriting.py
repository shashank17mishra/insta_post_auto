"""Organic hand-drawn variations and wobble utilities."""

import random
from typing import Sequence
from PIL import ImageDraw


def draw_organic_line(
    draw: ImageDraw.ImageDraw,
    points: Sequence[tuple[float, float]],
    fill: tuple[int, int, int],
    width: int = 2,
    wobble: float = 0.5,
) -> None:
    """Draw a line with slight organic micro-wobble to simulate human hand drawing."""
    if len(points) < 2:
        return

    # If simple 2-point horizontal or vertical line, add intermediate points with subtle jitter
    (x1, y1), (x2, y2) = points[0], points[1]
    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    steps = max(2, int(length // 40))

    jittered_points = [(x1, y1)]
    for i in range(1, steps):
        t = i / steps
        base_x = x1 + t * (x2 - x1)
        base_y = y1 + t * (y2 - y1)
        # Apply slight perpendicular jitter
        jitter_x = base_x + (random.random() - 0.5) * wobble
        jitter_y = base_y + (random.random() - 0.5) * wobble
        jittered_points.append((jitter_x, jitter_y))
    jittered_points.append((x2, y2))

    draw.line(jittered_points, fill=fill, width=width)
