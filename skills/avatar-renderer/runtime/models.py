"""Data models for avatar rendering."""

from __future__ import annotations

from dataclasses import dataclass, field

from config import (
    DEFAULT_BG_COLOR,
    DEFAULT_CANVAS_HEIGHT,
    DEFAULT_CANVAS_WIDTH,
    DEFAULT_LINE_COLOR,
    DEFAULT_LINE_WIDTH,
    DEFAULT_SKIN_COLOR,
)


@dataclass
class ExpressionParams:
    """Parameters defining a facial expression."""

    eyebrow_angle: float = 0.0  # Radians, positive = raised outer end
    eyebrow_height: float = 0.0  # Vertical offset, positive = raised
    eye_openness: float = 1.0  # 0.0 = closed, 1.0 = normal, >1.0 = wide
    pupil_size: float = 1.0  # Multiplier on default pupil size
    mouth_curve: float = 0.0  # Positive = smile, negative = frown
    mouth_openness: float = 0.0  # 0.0 = closed, 1.0 = fully open
    head_tilt: float = 0.0  # Degrees, positive = tilt right


@dataclass
class AvatarConfig:
    """Configuration for avatar rendering dimensions and colors."""

    width: int = DEFAULT_CANVAS_WIDTH
    height: int = DEFAULT_CANVAS_HEIGHT
    bg_color: tuple[int, ...] = field(default_factory=lambda: DEFAULT_BG_COLOR)
    skin_color: tuple[int, ...] = field(default_factory=lambda: DEFAULT_SKIN_COLOR)
    line_color: tuple[int, ...] = field(default_factory=lambda: DEFAULT_LINE_COLOR)
    line_width: int = DEFAULT_LINE_WIDTH


@dataclass
class RenderRequest:
    """A request to render an avatar frame."""

    emotion: str = "neutral"
    intensity: float = 0.8
    config: AvatarConfig | None = None
