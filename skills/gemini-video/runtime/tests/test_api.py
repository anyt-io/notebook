"""Tests for api.py — video generation and saving."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from google.genai import types
from PIL import Image

from api import generate_video, save_video
from config import ApiError, OutputError


def make_test_image(path: Path, size: tuple[int, int] = (10, 10), fmt: str = "PNG") -> Path:
    """Create a small test image file."""
    img = Image.new("RGB", size, color="red")
    img.save(path, format=fmt)
    return path


class TestGenerateVideo:
    @patch("api.time.sleep")
    def test_text_to_video_polls_until_done(self, mock_sleep: MagicMock):
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
            model="veo-3.1-generate-preview",
            poll_interval=1,
        )

        mock_client.models.generate_videos.assert_called_once()
        mock_client.operations.get.assert_called_once_with(mock_op_pending)
        assert result == mock_response

    @patch("api.time.sleep")
    def test_passes_config_params(self, mock_sleep: MagicMock):
        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="test",
            model="veo-3.1-generate-preview",
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

    @patch("api.time.sleep")
    def test_image_to_video(self, mock_sleep: MagicMock, tmp_path: Path):
        img_path = make_test_image(tmp_path / "start.png")

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="Animate this image",
            model="veo-3.1-generate-preview",
            input_image=img_path,
            poll_interval=1,
        )

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert call_kwargs.get("image") is not None

    @patch("api.time.sleep")
    def test_first_last_frame_interpolation(self, mock_sleep: MagicMock, tmp_path: Path):
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
            model="veo-3.1-generate-preview",
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

    @patch("api.time.sleep")
    def test_reference_images(self, mock_sleep: MagicMock, tmp_path: Path):
        refs = [make_test_image(tmp_path / f"ref{i}.png") for i in range(2)]

        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(
            client=mock_client,
            prompt="A robot in a city",
            model="veo-3.1-generate-preview",
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

    @patch("api.time.sleep")
    def test_no_config_when_no_params(self, mock_sleep: MagicMock):
        mock_op = MagicMock()
        mock_op.done = True
        mock_op.response = MagicMock()

        mock_client = MagicMock()
        mock_client.models.generate_videos.return_value = mock_op

        generate_video(client=mock_client, prompt="test", model="veo-3.1-generate-preview", poll_interval=1)

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert call_kwargs.get("config") is None

    @patch("api.time.sleep")
    def test_api_failure_raises_api_error(self, mock_sleep: MagicMock):
        mock_client = MagicMock()
        mock_client.models.generate_videos.side_effect = RuntimeError("connection timeout")

        with pytest.raises(ApiError, match="API call failed"):
            generate_video(client=mock_client, prompt="test", model="veo-3.1-generate-preview", poll_interval=1)


class TestSaveVideo:
    def test_saves_video(self, tmp_path: Path):
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

    def test_no_generated_videos_raises_output_error(self, tmp_path: Path):
        mock_response = MagicMock()
        mock_response.generated_videos = []

        mock_client = MagicMock()

        with pytest.raises(OutputError, match="No videos were generated"):
            save_video(mock_client, mock_response, tmp_path / "out", "test.mp4")

    def test_creates_output_dir(self, tmp_path: Path):
        mock_video_file = MagicMock()
        mock_generated_video = MagicMock()
        mock_generated_video.video = mock_video_file

        mock_response = MagicMock()
        mock_response.generated_videos = [mock_generated_video]

        mock_client = MagicMock()

        out = tmp_path / "nested" / "output"
        save_video(mock_client, mock_response, out, "test.mp4")
        assert out.exists()
