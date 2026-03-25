"""Tests for face rendering."""

from PIL import Image

from config import SUPPORTED_EMOTIONS
from expression_map import EXPRESSION_MAP
from face_renderer import FaceRenderer
from models import AvatarConfig


def test_render_returns_image() -> None:
    """render() should return a PIL Image."""
    renderer = FaceRenderer()
    params = EXPRESSION_MAP["neutral"]
    result = renderer.render(params)
    assert isinstance(result, Image.Image)


def test_render_correct_size() -> None:
    """Rendered image should match configured dimensions."""
    config = AvatarConfig(width=256, height=256)
    renderer = FaceRenderer(config)
    params = EXPRESSION_MAP["neutral"]
    result = renderer.render(params)
    assert result.size == (256, 256)


def test_render_all_emotions() -> None:
    """All supported emotions should render without error."""
    renderer = FaceRenderer()
    for emotion in SUPPORTED_EMOTIONS:
        img = renderer.render_emotion(emotion, 0.8)
        assert isinstance(img, Image.Image)
        assert img.size == (512, 512)


def test_render_emotion_convenience() -> None:
    """render_emotion convenience method should produce valid images."""
    renderer = FaceRenderer()
    img = renderer.render_emotion("satisfied", 0.5)
    assert isinstance(img, Image.Image)
    assert img.mode == "RGBA"
