"""Tests for api.py — image validation, generation, loading, and saving."""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from api import generate_images, load_image_as_part, save_images, validate_input_image
from config import DEFAULT_MODEL, MAX_INPUT_SIZE_MB, ApiError, OutputError, ValidationError


def make_test_image(path: Path, size: tuple[int, int] = (10, 10), fmt: str = "PNG") -> Path:
    """Create a small test image file."""
    img = Image.new("RGB", size, color="red")
    img.save(path, format=fmt)
    return path


class TestValidateInputImage:
    def test_valid_png(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.png")
        validate_input_image(img_path)  # should not raise

    def test_valid_jpeg(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.jpg", fmt="JPEG")
        validate_input_image(img_path)  # should not raise

    def test_valid_webp(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.webp", fmt="WEBP")
        validate_input_image(img_path)  # should not raise

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="not found"):
            validate_input_image(tmp_path / "nonexistent.png")

    def test_not_a_file(self, tmp_path: Path):
        with pytest.raises(ValidationError, match="Not a file"):
            validate_input_image(tmp_path)

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.bmp"
        path.write_bytes(b"fake")
        with pytest.raises(ValidationError, match="Unsupported format"):
            validate_input_image(path)

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.png"
        path.write_bytes(b"\x00" * (MAX_INPUT_SIZE_MB * 1024 * 1024 + 1))
        with pytest.raises(ValidationError, match="too large"):
            validate_input_image(path)


class TestLoadImageAsPart:
    def test_returns_part_with_inline_data(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.png")
        part = load_image_as_part(img_path)
        assert part.inline_data is not None
        assert part.inline_data.mime_type == "image/png"
        assert part.inline_data.data is not None
        assert len(part.inline_data.data) > 0

    def test_jpeg_mime_type(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.jpg", fmt="JPEG")
        part = load_image_as_part(img_path)
        assert part.inline_data is not None
        assert part.inline_data.mime_type == "image/jpeg"


class TestSaveImages:
    def test_saves_single_image(self, tmp_path: Path):
        img = Image.new("RGB", (10, 10), color="blue")
        results: list[tuple[Image.Image | None, str | None]] = [(img, "A blue square")]
        saved = save_images(results, tmp_path / "out")
        assert len(saved) == 1
        assert saved[0].exists()
        assert saved[0].suffix == ".png"

    def test_saves_multiple_images(self, tmp_path: Path):
        img1 = Image.new("RGB", (10, 10), color="red")
        img2 = Image.new("RGB", (10, 10), color="green")
        results: list[tuple[Image.Image | None, str | None]] = [(img1, None), (img2, None)]
        saved = save_images(results, tmp_path / "out")
        assert len(saved) == 2
        assert all(p.exists() for p in saved)

    def test_no_images_raises_output_error(self, tmp_path: Path):
        results: list[tuple[Image.Image | None, str | None]] = [(None, "Blocked by safety filter")]
        with pytest.raises(OutputError, match="No images were generated"):
            save_images(results, tmp_path / "out")

    def test_creates_output_dir(self, tmp_path: Path):
        img = Image.new("RGB", (10, 10))
        results: list[tuple[Image.Image | None, str | None]] = [(img, None)]
        out = tmp_path / "nested" / "output"
        save_images(results, out)
        assert out.exists()

    def test_filename_pattern(self, tmp_path: Path):
        img = Image.new("RGB", (10, 10))
        results: list[tuple[Image.Image | None, str | None]] = [(img, None)]
        saved = save_images(results, tmp_path / "out")
        assert saved[0].name.startswith("gemini_")
        assert saved[0].name.endswith("_1.png")


class TestGenerateImages:
    @patch("api.genai.Client")
    def test_text_to_image(self, mock_client_class: MagicMock):
        img = Image.new("RGB", (10, 10), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        mock_part_img = MagicMock()
        mock_part_img.text = None
        mock_part_img.inline_data = MagicMock()
        mock_part_img.inline_data.data = img_bytes

        mock_part_text = MagicMock()
        mock_part_text.text = "Here is your image"
        mock_part_text.inline_data = None

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part_text, mock_part_img]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        results = generate_images(
            client=mock_client,
            prompt="A red square",
            model=DEFAULT_MODEL,
        )

        assert len(results) == 1
        result_img, result_text = results[0]
        assert result_img is not None
        assert result_text == "Here is your image"
        mock_client.models.generate_content.assert_called_once()

    @patch("api.genai.Client")
    def test_passes_image_config(self, mock_client_class: MagicMock):
        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        generate_images(
            client=mock_client,
            prompt="test",
            model=DEFAULT_MODEL,
            aspect_ratio="16:9",
            image_size="2K",
            person_generation="ALLOW_ADULT",
            count=2,
        )

        call_kwargs = mock_client.models.generate_content.call_args
        config = call_kwargs.kwargs.get("config") or call_kwargs[1].get("config")
        assert config.candidate_count == 2
        assert config.image_config.aspect_ratio == "16:9"
        assert config.image_config.image_size == "2K"
        assert config.image_config.person_generation == "ALLOW_ADULT"

    @patch("api.genai.Client")
    def test_no_candidates(self, mock_client_class: MagicMock):
        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        results = generate_images(client=mock_client, prompt="blocked prompt", model=DEFAULT_MODEL)

        assert len(results) == 1
        img, text = results[0]
        assert img is None
        assert text is not None
        assert "blocked" in text.lower()

    @patch("api.genai.Client")
    def test_single_api_call_for_count(self, mock_client_class: MagicMock):
        """Verify count is passed via number_of_images, not multiple API calls."""
        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        generate_images(client=mock_client, prompt="test", model=DEFAULT_MODEL, count=3)

        assert mock_client.models.generate_content.call_count == 1
        config = mock_client.models.generate_content.call_args.kwargs.get(
            "config"
        ) or mock_client.models.generate_content.call_args[1].get("config")
        assert config.candidate_count == 3

    @patch("api.genai.Client")
    def test_api_failure_raises_api_error(self, mock_client_class: MagicMock):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("connection timeout")

        with pytest.raises(ApiError, match="API call failed"):
            generate_images(client=mock_client, prompt="test", model=DEFAULT_MODEL)
