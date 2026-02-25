"""Tests for generate_video.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from google.genai import types
from PIL import Image

from generate_video import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_POLL_INTERVAL,
    MAX_INPUT_SIZE_MB,
    MAX_REFERENCE_IMAGES,
    MIME_TYPES,
    PERSON_GENERATION_OPTIONS,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_DURATIONS,
    SUPPORTED_INPUT_EXTENSIONS,
    SUPPORTED_RESOLUTIONS,
    build_reference_images,
    get_api_key,
    load_image,
    validate_input_image,
)


def make_test_image(path: Path, size: tuple[int, int] = (10, 10), fmt: str = "PNG") -> Path:
    """Create a small test image file."""
    img = Image.new("RGB", size, color="red")
    img.save(path, format=fmt)
    return path


class TestConstants:
    def test_default_model_is_veo_3_1(self):
        assert DEFAULT_MODEL == "veo-3.1-generate-preview"

    def test_default_model_in_available(self):
        assert DEFAULT_MODEL in AVAILABLE_MODELS

    def test_available_models_only_veo_3_1(self):
        assert "veo-3.1-generate-preview" in AVAILABLE_MODELS
        assert "veo-3.1-fast-generate-preview" in AVAILABLE_MODELS
        assert len(AVAILABLE_MODELS) == 2
        for model in AVAILABLE_MODELS:
            assert model.startswith("veo-3.1")

    def test_aspect_ratios(self):
        assert "16:9" in SUPPORTED_ASPECT_RATIOS
        assert "9:16" in SUPPORTED_ASPECT_RATIOS
        for ratio in SUPPORTED_ASPECT_RATIOS:
            parts = ratio.split(":")
            assert len(parts) == 2
            assert int(parts[0]) > 0
            assert int(parts[1]) > 0

    def test_resolutions(self):
        assert SUPPORTED_RESOLUTIONS == ["720p", "1080p", "4k"]

    def test_durations(self):
        assert SUPPORTED_DURATIONS == [4, 6, 8]

    def test_person_generation_options(self):
        assert "allow_all" in PERSON_GENERATION_OPTIONS
        assert "allow_adult" in PERSON_GENERATION_OPTIONS
        assert "dont_allow" in PERSON_GENERATION_OPTIONS

    def test_mime_types_cover_extensions(self):
        for ext in SUPPORTED_INPUT_EXTENSIONS:
            assert ext in MIME_TYPES

    def test_default_poll_interval(self):
        assert DEFAULT_POLL_INTERVAL == 10

    def test_max_reference_images(self):
        assert MAX_REFERENCE_IMAGES == 3


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


class TestLoadImage:
    def test_returns_image_with_data(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.png")
        image = load_image(img_path)
        assert image.image_bytes is not None
        assert image.mime_type == "image/png"

    def test_jpeg_mime_type(self, tmp_path: Path):
        img_path = make_test_image(tmp_path / "test.jpg", fmt="JPEG")
        image = load_image(img_path)
        assert image.mime_type == "image/jpeg"


class TestBuildReferenceImages:
    def test_builds_references(self, tmp_path: Path):
        paths = [make_test_image(tmp_path / f"ref{i}.png") for i in range(3)]
        refs = build_reference_images(paths)
        assert len(refs) == 3
        for ref in refs:
            assert ref.reference_type == types.VideoGenerationReferenceType.ASSET
            assert ref.image is not None
            assert ref.image.mime_type == "image/png"

    def test_single_reference(self, tmp_path: Path):
        path = make_test_image(tmp_path / "ref.png")
        refs = build_reference_images([path])
        assert len(refs) == 1
        assert refs[0].reference_type == types.VideoGenerationReferenceType.ASSET

    def test_empty_list(self):
        refs = build_reference_images([])
        assert refs == []


class TestGenerateVideo:
    @patch("generate_video.time.sleep")
    def test_text_to_video_polls_until_done(self, mock_sleep: MagicMock):
        from generate_video import generate_video

        mock_video = MagicMock()
        mock_generated_video = MagicMock()
        mock_generated_video.video = mock_video

        mock_response = MagicMock()
        mock_response.generated_videos = [mock_generated_video]

        mock_op_pending = MagicMock()
        mock_op_pending.done = False

        mock_op_done = MagicMock()
        mock_op_done.done = True
        mock_op_done.response = mock_response

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op_pending
        mock_client.operations.get.return_value = mock_op_done

        result = generate_video(
            client=mock_client,
            prompt="A test prompt",
            poll_interval=1,
        )

        mock_client.models.generate_videos.assert_called_once()
        mock_client.operations.get.assert_called_once_with(mock_op_pending)
        assert result == mock_response

    @patch("generate_video.time.sleep")
    def test_passes_config_params(self, mock_sleep: MagicMock):
        from generate_video import generate_video

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="test",
            aspect_ratio="9:16",
            resolution="1080p",
            duration_seconds=8,
            negative_prompt="cartoon",
            person_generation="allow_adult",
            poll_interval=1,
        )

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        config = call_kwargs.get("config")
        assert config is not None
        assert config.aspect_ratio == "9:16"
        assert config.resolution == "1080p"
        assert config.duration_seconds == 8
        assert config.negative_prompt == "cartoon"
        assert config.person_generation == "allow_adult"

    @patch("generate_video.time.sleep")
    def test_image_to_video(self, mock_sleep: MagicMock, tmp_path: Path):
        from generate_video import generate_video

        img_path = make_test_image(tmp_path / "start.png")

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="Animate this image",
            input_image=img_path,
            poll_interval=1,
        )

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert call_kwargs.get("image") is not None

    @patch("generate_video.time.sleep")
    def test_first_last_frame_interpolation(self, mock_sleep: MagicMock, tmp_path: Path):
        from generate_video import generate_video

        first = make_test_image(tmp_path / "first.png")
        last = make_test_image(tmp_path / "last.png")

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="Transition between frames",
            input_image=first,
            last_frame=last,
            poll_interval=1,
        )

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert call_kwargs.get("image") is not None
        config = call_kwargs.get("config")
        assert config is not None
        assert config.last_frame is not None
        assert config.last_frame.mime_type == "image/png"

    @patch("generate_video.time.sleep")
    def test_reference_images(self, mock_sleep: MagicMock, tmp_path: Path):
        from generate_video import generate_video

        refs = [make_test_image(tmp_path / f"ref{i}.png") for i in range(2)]

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="A robot in a city",
            reference_images=refs,
            poll_interval=1,
        )

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        config = call_kwargs.get("config")
        assert config is not None
        assert config.reference_images is not None
        assert len(config.reference_images) == 2
        for ref in config.reference_images:
            assert ref.reference_type == types.VideoGenerationReferenceType.ASSET

    @patch("generate_video.time.sleep")
    def test_no_config_when_no_params(self, mock_sleep: MagicMock):
        from generate_video import generate_video

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(client=mock_client, prompt="test", poll_interval=1)

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert call_kwargs.get("config") is None


class TestSaveVideo:
    def test_saves_video(self, tmp_path: Path):
        from generate_video import save_video

        mock_video_file = MagicMock()
        mock_generated_video = MagicMock()
        mock_generated_video.video = mock_video_file

        mock_response = MagicMock()
        mock_response.generated_videos = [mock_generated_video]

        mock_client = MagicMock()

        out = tmp_path / "out"
        result = save_video(mock_client, mock_response, out, "test.mp4")

        assert result == out / "test.mp4"
        mock_client.files.download.assert_called_once_with(file=mock_video_file)
        mock_video_file.save.assert_called_once_with(str(out / "test.mp4"))

    def test_no_generated_videos(self, tmp_path: Path):
        from generate_video import save_video

        mock_response = MagicMock()
        mock_response.generated_videos = []

        mock_client = MagicMock()

        result = save_video(mock_client, mock_response, tmp_path / "out", "test.mp4")
        assert result is None

    def test_creates_output_dir(self, tmp_path: Path):
        from generate_video import save_video

        mock_video_file = MagicMock()
        mock_generated_video = MagicMock()
        mock_generated_video.video = mock_video_file

        mock_response = MagicMock()
        mock_response.generated_videos = [mock_generated_video]

        mock_client = MagicMock()

        out = tmp_path / "nested" / "output"
        save_video(mock_client, mock_response, out, "test.mp4")
        assert out.exists()
