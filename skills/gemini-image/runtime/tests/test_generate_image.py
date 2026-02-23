"""Tests for generate_image.py."""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from generate_image import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    MAX_INPUT_SIZE_MB,
    MIME_TYPES,
    PERSON_GENERATION_OPTIONS,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_IMAGE_SIZES,
    SUPPORTED_INPUT_EXTENSIONS,
    get_api_key,
    load_image_as_part,
    save_images,
    validate_input_image,
)


def make_test_image(path: Path, size: tuple[int, int] = (10, 10), fmt: str = "PNG") -> Path:
    """Create a small test image file."""
    img = Image.new("RGB", size, color="red")
    img.save(path, format=fmt)
    return path


class TestConstants:
    def test_default_model_is_nano_banana(self):
        assert DEFAULT_MODEL == "gemini-2.5-flash-image"

    def test_default_model_in_available(self):
        assert DEFAULT_MODEL in AVAILABLE_MODELS

    def test_available_models_are_current(self):
        assert "gemini-2.5-flash-image" in AVAILABLE_MODELS
        assert "gemini-3-pro-image-preview" in AVAILABLE_MODELS
        # Ensure no deprecated models
        for model in AVAILABLE_MODELS:
            assert not model.startswith("gemini-2.0-")
            assert not model.startswith("gemini-1.5-")

    def test_aspect_ratios_format(self):
        for ratio in SUPPORTED_ASPECT_RATIOS:
            parts = ratio.split(":")
            assert len(parts) == 2
            assert int(parts[0]) > 0
            assert int(parts[1]) > 0

    def test_image_sizes(self):
        assert SUPPORTED_IMAGE_SIZES == ["1K", "2K", "4K"]

    def test_person_generation_options(self):
        assert "DONT_ALLOW" in PERSON_GENERATION_OPTIONS
        assert "ALLOW_ADULT" in PERSON_GENERATION_OPTIONS
        assert "ALLOW_ALL" in PERSON_GENERATION_OPTIONS

    def test_mime_types_cover_extensions(self):
        for ext in SUPPORTED_INPUT_EXTENSIONS:
            assert ext in MIME_TYPES


class TestGetApiKey:
    def test_returns_key_when_set(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-123"}):
            assert get_api_key() == "test-key-123"

    def test_returns_none_when_not_set(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_api_key() is None


class TestValidateInputImage:
    def test_valid_png(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.png")
        assert validate_input_image(img_path) is None

    def test_valid_jpeg(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.jpg", fmt="JPEG")
        assert validate_input_image(img_path) is None

    def test_valid_webp(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.webp", fmt="WEBP")
        assert validate_input_image(img_path) is None

    def test_file_not_found(self, tmp_path: Path):
        result = validate_input_image(tmp_path / "nonexistent.png")
        assert result is not None
        assert "not found" in result.lower()

    def test_not_a_file(self, tmp_path: Path):
        result = validate_input_image(tmp_path)
        assert result is not None
        assert "Not a file" in result

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.bmp"
        path.write_bytes(b"fake")
        result = validate_input_image(path)
        assert result is not None
        assert "Unsupported format" in result

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.png"
        path.write_bytes(b"\x00" * (MAX_INPUT_SIZE_MB * 1024 * 1024 + 1))
        result = validate_input_image(path)
        assert result is not None
        assert "too large" in result.lower()


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

    def test_handles_none_image(self, tmp_path: Path):
        results: list[tuple[Image.Image | None, str | None]] = [(None, "Blocked by safety filter")]
        saved = save_images(results, tmp_path / "out")
        assert len(saved) == 0

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
    @patch("generate_image.genai.Client")
    def test_text_to_image(self, mock_client_class: MagicMock):
        from generate_image import generate_images

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

    @patch("generate_image.genai.Client")
    def test_passes_image_config(self, mock_client_class: MagicMock):
        from generate_image import generate_images

        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        generate_images(
            client=mock_client,
            prompt="test",
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

    @patch("generate_image.genai.Client")
    def test_no_candidates(self, mock_client_class: MagicMock):
        from generate_image import generate_images

        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        results = generate_images(client=mock_client, prompt="blocked prompt")

        assert len(results) == 1
        img, text = results[0]
        assert img is None
        assert text is not None
        assert "blocked" in text.lower()

    @patch("generate_image.genai.Client")
    def test_single_api_call_for_count(self, mock_client_class: MagicMock):
        """Verify count is passed via number_of_images, not multiple API calls."""
        from generate_image import generate_images

        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        generate_images(client=mock_client, prompt="test", count=3)

        # Should be a single API call, not 3
        assert mock_client.models.generate_content.call_count == 1
        config = mock_client.models.generate_content.call_args.kwargs.get(
            "config"
        ) or mock_client.models.generate_content.call_args[1].get("config")
        assert config.candidate_count == 3
