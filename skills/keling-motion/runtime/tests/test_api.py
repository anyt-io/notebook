"""Tests for api.py — argument builder, video generation, and saving."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api import build_motion_control_args, generate_video, save_video
from config import ApiError, OutputError

# ---------------------------------------------------------------------------
# Argument builder
# ---------------------------------------------------------------------------


class TestBuildMotionControlArgs:
    def test_basic_required_only(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
        )
        assert args["image_url"] == "https://img.png"
        assert args["video_url"] == "https://vid.mp4"
        assert args["character_orientation"] == "image"
        assert "prompt" not in args
        assert "keep_original_sound" not in args

    def test_with_prompt(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            prompt="A person dancing",
        )
        assert args["prompt"] == "A person dancing"

    def test_orientation_video(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="video",
        )
        assert args["character_orientation"] == "video"

    def test_keep_original_sound_false(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            keep_original_sound=False,
        )
        assert args["keep_original_sound"] is False

    def test_keep_original_sound_true_not_in_args(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            keep_original_sound=True,
        )
        assert "keep_original_sound" not in args

    def test_with_all_options(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="video",
            prompt="Dancing in rain",
            keep_original_sound=False,
        )
        assert args["image_url"] == "https://img.png"
        assert args["video_url"] == "https://vid.mp4"
        assert args["character_orientation"] == "video"
        assert args["prompt"] == "Dancing in rain"
        assert args["keep_original_sound"] is False


# ---------------------------------------------------------------------------
# Generate video (API call)
# ---------------------------------------------------------------------------


class TestGenerateVideo:
    @patch("api.fal_client.subscribe")
    def test_calls_subscribe_with_endpoint_and_args(self, mock_subscribe: MagicMock):
        mock_subscribe.return_value = {"video": {"url": "https://result.mp4"}}

        result = generate_video(
            endpoint="fal-ai/kling-video/v2.6/standard/motion-control",
            arguments={"image_url": "https://img.png", "video_url": "https://vid.mp4"},
        )

        mock_subscribe.assert_called_once()
        call_args = mock_subscribe.call_args
        assert call_args[0][0] == "fal-ai/kling-video/v2.6/standard/motion-control"
        assert call_args[1]["arguments"]["image_url"] == "https://img.png"
        assert call_args[1]["arguments"]["video_url"] == "https://vid.mp4"
        assert call_args[1]["with_logs"] is True
        assert result == {"video": {"url": "https://result.mp4"}}

    @patch("api.fal_client.subscribe")
    def test_passes_all_arguments(self, mock_subscribe: MagicMock):
        mock_subscribe.return_value = {"video": {"url": "https://result.mp4"}}

        arguments: dict[str, object] = {
            "image_url": "https://img.png",
            "video_url": "https://vid.mp4",
            "character_orientation": "video",
            "prompt": "Dancing",
            "keep_original_sound": False,
        }
        generate_video(
            endpoint="fal-ai/kling-video/v2.6/standard/motion-control",
            arguments=arguments,
        )

        call_args = mock_subscribe.call_args
        assert call_args[1]["arguments"] == arguments

    @patch("api.fal_client.subscribe", side_effect=RuntimeError("connection timeout"))
    def test_api_failure_raises_api_error(self, mock_subscribe: MagicMock):
        with pytest.raises(ApiError, match=r"API call to .+ failed"):
            generate_video(
                endpoint="fal-ai/kling-video/v2.6/standard/motion-control",
                arguments={"image_url": "https://img.png", "video_url": "https://vid.mp4"},
            )


# ---------------------------------------------------------------------------
# Save video
# ---------------------------------------------------------------------------


class TestSaveVideo:
    @patch("api.urllib.request.urlretrieve")
    def test_saves_video(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"video": {"url": "https://cdn.fal.ai/video.mp4"}}
        out = tmp_path / "out"

        saved = save_video(result, out, "test.mp4")

        assert saved == out / "test.mp4"
        assert out.exists()
        mock_retrieve.assert_called_once_with("https://cdn.fal.ai/video.mp4", str(out / "test.mp4"))

    def test_no_video_in_response(self, tmp_path: Path):
        result: dict[str, object] = {}
        with pytest.raises(OutputError, match="no video object"):
            save_video(result, tmp_path / "out", "test.mp4")

    def test_no_url_in_video(self, tmp_path: Path):
        result: dict[str, object] = {"video": {"file_name": "x.mp4"}}
        with pytest.raises(OutputError, match="no video URL"):
            save_video(result, tmp_path / "out", "test.mp4")

    def test_video_not_dict(self, tmp_path: Path):
        result: dict[str, object] = {"video": "not a dict"}
        with pytest.raises(OutputError, match="no video object"):
            save_video(result, tmp_path / "out", "test.mp4")

    @patch("api.urllib.request.urlretrieve")
    def test_creates_nested_output_dir(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"video": {"url": "https://cdn.fal.ai/v.mp4"}}
        out = tmp_path / "nested" / "deep" / "output"

        save_video(result, out, "test.mp4")
        assert out.exists()

    @patch("api.urllib.request.urlretrieve", side_effect=OSError("download failed"))
    def test_download_failure_raises_output_error(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"video": {"url": "https://cdn.fal.ai/video.mp4"}}
        with pytest.raises(OutputError, match="Failed to download"):
            save_video(result, tmp_path / "out", "test.mp4")
