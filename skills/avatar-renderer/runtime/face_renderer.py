"""Core face rendering using Pillow."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from config import (
    DEFAULT_EYE_WHITE_COLOR,
    DEFAULT_EYEBROW_COLOR,
    DEFAULT_EYEBROW_WIDTH,
    DEFAULT_FACE_LINE_WIDTH,
    DEFAULT_MOUTH_COLOR,
    DEFAULT_MOUTH_WIDTH,
    DEFAULT_PUPIL_COLOR,
    EYE_HEIGHT_RATIO,
    EYE_SPACING_RATIO,
    EYE_WIDTH_RATIO,
    EYE_Y_RATIO,
    EYEBROW_WIDTH_RATIO,
    EYEBROW_Y_OFFSET_RATIO,
    FACE_CENTER_X_RATIO,
    FACE_CENTER_Y_RATIO,
    FACE_HEIGHT_RATIO,
    FACE_WIDTH_RATIO,
    MOUTH_WIDTH_RATIO,
    MOUTH_Y_RATIO,
    PUPIL_SIZE_RATIO,
)
from expression_map import EXPRESSION_MAP, interpolate_expression
from models import AvatarConfig, ExpressionParams


class FaceRenderer:
    """Renders avatar faces with configurable expressions."""

    def __init__(self, config: AvatarConfig | None = None) -> None:
        self.config = config or AvatarConfig()

    def render(self, params: ExpressionParams) -> Image.Image:
        """Render a face image from expression parameters.

        Args:
            params: The facial expression parameters to render.

        Returns:
            A PIL Image with the rendered face.
        """
        w, h = self.config.width, self.config.height
        img = Image.new("RGBA", (w, h), self.config.bg_color)
        draw = ImageDraw.Draw(img)

        # Draw face oval
        self._draw_face(draw, w, h)

        # Draw eyes
        self._draw_eyes(draw, w, h, params)

        # Draw eyebrows
        self._draw_eyebrows(draw, w, h, params)

        # Draw mouth
        self._draw_mouth(draw, w, h, params)

        # Apply head tilt via rotation
        if abs(params.head_tilt) > 0.1:
            img = img.rotate(
                -params.head_tilt,
                resample=Image.Resampling.BICUBIC,
                center=(int(w * FACE_CENTER_X_RATIO), int(h * FACE_CENTER_Y_RATIO)),
                fillcolor=self.config.bg_color,
            )

        return img

    def render_emotion(self, emotion: str, intensity: float = 0.8) -> Image.Image:
        """Convenience method to render an emotion by name.

        Args:
            emotion: Name of the emotion (e.g., 'neutral', 'surprised').
            intensity: Expression intensity from 0.0 to 1.0.

        Returns:
            A PIL Image with the rendered face.

        Raises:
            ValueError: If the emotion is not recognized.
        """
        if emotion not in EXPRESSION_MAP:
            raise ValueError(f"Unknown emotion '{emotion}'. Supported: {list(EXPRESSION_MAP.keys())}")
        base_params = EXPRESSION_MAP[emotion]
        params = interpolate_expression(base_params, intensity)
        return self.render(params)

    def _draw_face(self, draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        """Draw the face oval."""
        cx = int(w * FACE_CENTER_X_RATIO)
        cy = int(h * FACE_CENTER_Y_RATIO)
        fw = int(w * FACE_WIDTH_RATIO)
        fh = int(h * FACE_HEIGHT_RATIO)
        bbox = (cx - fw // 2, cy - fh // 2, cx + fw // 2, cy + fh // 2)
        draw.ellipse(bbox, fill=self.config.skin_color, outline=self.config.line_color, width=DEFAULT_FACE_LINE_WIDTH)

    def _draw_eyes(self, draw: ImageDraw.ImageDraw, w: int, h: int, params: ExpressionParams) -> None:
        """Draw both eyes with pupils."""
        cx = int(w * FACE_CENTER_X_RATIO)
        ey = int(h * EYE_Y_RATIO)
        spacing = int(w * EYE_SPACING_RATIO)
        ew = int(w * EYE_WIDTH_RATIO)
        eh = int(h * EYE_HEIGHT_RATIO * params.eye_openness)

        for side in (-1, 1):
            ex = cx + side * spacing
            eye_bbox = (ex - ew, ey - eh, ex + ew, ey + eh)
            draw.ellipse(eye_bbox, fill=DEFAULT_EYE_WHITE_COLOR, outline=self.config.line_color, width=2)

            # Pupil
            ps = int(w * PUPIL_SIZE_RATIO * params.pupil_size)
            pupil_bbox = (ex - ps, ey - ps, ex + ps, ey + ps)
            draw.ellipse(pupil_bbox, fill=DEFAULT_PUPIL_COLOR)

    def _draw_eyebrows(self, draw: ImageDraw.ImageDraw, w: int, h: int, params: ExpressionParams) -> None:
        """Draw eyebrows as angled lines."""
        cx = int(w * FACE_CENTER_X_RATIO)
        ey = int(h * EYE_Y_RATIO)
        spacing = int(w * EYE_SPACING_RATIO)
        brow_y_offset = int(h * EYEBROW_Y_OFFSET_RATIO) + int(params.eyebrow_height * h * 0.03)
        brow_w = int(w * EYEBROW_WIDTH_RATIO)

        for side in (-1, 1):
            bx = cx + side * spacing
            by = ey - brow_y_offset

            # Angle: positive raises outer end
            angle = params.eyebrow_angle * side
            dx = brow_w
            dy = int(math.sin(angle) * brow_w * 0.5)

            x1 = bx - dx
            y1 = by + dy
            x2 = bx + dx
            y2 = by - dy

            draw.line([(x1, y1), (x2, y2)], fill=DEFAULT_EYEBROW_COLOR, width=DEFAULT_EYEBROW_WIDTH)

    def _draw_mouth(self, draw: ImageDraw.ImageDraw, w: int, h: int, params: ExpressionParams) -> None:
        """Draw the mouth using a bezier-approximated curve."""
        cx = int(w * FACE_CENTER_X_RATIO)
        my = int(h * MOUTH_Y_RATIO)
        mw = int(w * MOUTH_WIDTH_RATIO)

        curve_offset = int(params.mouth_curve * h * 0.06)
        openness_offset = int(params.mouth_openness * h * 0.05)

        # Upper lip line (bezier approximated with points)
        left = (cx - mw, my)
        right = (cx + mw, my)
        mid_top = (cx, my + curve_offset)

        # Draw upper lip as smooth curve via intermediate points
        points = _bezier_points(left, mid_top, right, steps=20)
        draw.line(points, fill=DEFAULT_MOUTH_COLOR, width=DEFAULT_MOUTH_WIDTH)

        # If mouth is open, draw lower lip
        if openness_offset > 2:
            mid_bottom = (cx, my + curve_offset + openness_offset)
            bottom_points = _bezier_points(left, mid_bottom, right, steps=20)
            draw.line(bottom_points, fill=DEFAULT_MOUTH_COLOR, width=DEFAULT_MOUTH_WIDTH)

            # Fill mouth interior
            fill_points = points + list(reversed(bottom_points))
            draw.polygon(fill_points, fill=(120, 50, 50, 255))
            # Redraw outlines
            draw.line(points, fill=DEFAULT_MOUTH_COLOR, width=DEFAULT_MOUTH_WIDTH)
            draw.line(bottom_points, fill=DEFAULT_MOUTH_COLOR, width=DEFAULT_MOUTH_WIDTH)


def _bezier_points(
    p0: tuple[int, int],
    p1: tuple[int, int],
    p2: tuple[int, int],
    steps: int = 20,
) -> list[tuple[int, int]]:
    """Generate points along a quadratic bezier curve."""
    points: list[tuple[int, int]] = []
    for i in range(steps + 1):
        t = i / steps
        inv = 1 - t
        x = int(inv * inv * p0[0] + 2 * inv * t * p1[0] + t * t * p2[0])
        y = int(inv * inv * p0[1] + 2 * inv * t * p1[1] + t * t * p2[1])
        points.append((x, y))
    return points
