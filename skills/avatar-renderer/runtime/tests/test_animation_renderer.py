"""Tests for animation rendering."""

from pathlib import Path

from PIL import Image

from animation_renderer import AnimationRenderer
from face_renderer import FaceRenderer


def test_render_sequence(tmp_path: Path) -> None:
    """render_sequence should generate the correct number of frame files."""
    renderer = FaceRenderer()
    anim = AnimationRenderer(renderer)

    script = [
        {"emotion": "neutral", "intensity": 0.8, "frames": 2},
        {"emotion": "surprised", "intensity": 1.0, "frames": 3},
    ]

    output_dir = str(tmp_path / "frames")
    paths = anim.render_sequence(script, output_dir)

    assert len(paths) == 5
    for p in paths:
        assert Path(p).exists()
        img = Image.open(p)
        assert img.size == (512, 512)


def test_sprite_sheet_size() -> None:
    """Sprite sheet should have correct dimensions based on emotions and columns."""
    renderer = FaceRenderer()
    anim = AnimationRenderer(renderer)

    emotions = ["neutral", "attentive", "surprised"]
    sheet = anim.render_sprite_sheet(emotions=emotions, cols=2)

    # 3 emotions, 2 cols -> 2 rows
    expected_w = 512 * 2
    expected_h = 512 * 2
    assert sheet.size == (expected_w, expected_h)


def test_interpolate_frames() -> None:
    """interpolate_frames should produce the correct number of transition frames."""
    renderer = FaceRenderer()
    anim = AnimationRenderer(renderer)

    frames = anim.interpolate_frames("neutral", "surprised", steps=7)
    assert len(frames) == 7
    for frame in frames:
        assert isinstance(frame, Image.Image)
        assert frame.size == (512, 512)
