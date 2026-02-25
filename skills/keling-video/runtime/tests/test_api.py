"""Tests for api.py — argument builders, video generation, and saving."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api import (
    build_edit_video_args,
    build_image_to_video_args,
    build_reference_to_video_args,
    build_text_to_video_args,
    generate_video,
    save_video,
)
from config import ApiError, OutputError

# ---------------------------------------------------------------------------
# Argument builders
# ---------------------------------------------------------------------------


class TestBuildTextToVideoArgs:
    def test_basic_prompt(self):
        args = build_text_to_video_args(prompt="A lion")
        assert args == {"prompt": "A lion"}

    def test_with_all_options(self):
        args = build_text_to_video_args(
            prompt="A lion",
            duration="10",
            aspect_ratio="9:16",
            generate_audio=True,
        )
        assert args["prompt"] == "A lion"
        assert args["duration"] == "10"
        assert args["aspect_ratio"] == "9:16"
        assert args["generate_audio"] is True

    def test_multi_prompt_overrides_prompt(self):
        mp = [{"prompt": "Scene 1"}, {"prompt": "Scene 2"}]
        args = build_text_to_video_args(prompt="ignored", multi_prompt=mp)
        assert "prompt" not in args
        assert args["multi_prompt"] == mp
        assert args["shot_type"] == "customize"


class TestBuildImageToVideoArgs:
    def test_basic(self):
        args = build_image_to_video_args(image_url="https://img.png", prompt="Animate")
        assert args["image_url"] == "https://img.png"
        assert args["prompt"] == "Animate"

    def test_with_end_image(self):
        args = build_image_to_video_args(
            image_url="https://first.png",
            prompt="Bloom",
            end_image_url="https://last.png",
        )
        assert args["end_image_url"] == "https://last.png"

    def test_with_duration_and_audio(self):
        args = build_image_to_video_args(
            image_url="https://img.png",
            prompt="test",
            duration="8",
            generate_audio=True,
        )
        assert args["duration"] == "8"
        assert args["generate_audio"] is True


class TestBuildReferenceToVideoArgs:
    def test_basic_with_elements(self):
        elems: list[dict[str, object]] = [{"frontal_image_url": "https://char.png"}]
        args = build_reference_to_video_args(prompt="@Element1 walks", elements=elems)
        assert args["prompt"] == "@Element1 walks"
        assert args["elements"] == elems

    def test_with_ref_images(self):
        args = build_reference_to_video_args(
            prompt="test",
            ref_images=["https://style.png"],
        )
        assert args["image_urls"] == ["https://style.png"]

    def test_with_start_and_end_images(self):
        args = build_reference_to_video_args(
            prompt="test",
            start_image_url="https://start.png",
            end_image_url="https://end.png",
        )
        assert args["start_image_url"] == "https://start.png"
        assert args["end_image_url"] == "https://end.png"

    def test_with_all_options(self):
        args = build_reference_to_video_args(
            prompt="test",
            elements=[{"frontal_image_url": "https://x.png"}],
            ref_images=["https://s.png"],
            start_image_url="https://start.png",
            duration="8",
            aspect_ratio="9:16",
            generate_audio=True,
        )
        assert "elements" in args
        assert "image_urls" in args
        assert args["duration"] == "8"
        assert args["aspect_ratio"] == "9:16"
        assert args["generate_audio"] is True


class TestBuildEditVideoArgs:
    def test_basic(self):
        args = build_edit_video_args(prompt="Change bg @Video1", video_url="https://vid.mp4")
        assert args["prompt"] == "Change bg @Video1"
        assert args["video_url"] == "https://vid.mp4"
        assert args["keep_audio"] is True

    def test_with_ref_images_and_elements(self):
        args = build_edit_video_args(
            prompt="Replace @Image1 @Video1",
            video_url="https://vid.mp4",
            ref_images=["https://ref.png"],
            elements=[{"frontal_image_url": "https://char.png"}],
        )
        assert args["image_urls"] == ["https://ref.png"]
        assert args["elements"] == [{"frontal_image_url": "https://char.png"}]

    def test_no_keep_audio(self):
        args = build_edit_video_args(prompt="test", video_url="https://vid.mp4", keep_audio=False)
        assert args["keep_audio"] is False


# ---------------------------------------------------------------------------
# Generate video (API call)
# ---------------------------------------------------------------------------


class TestGenerateVideo:
    @patch("api.fal_client.subscribe")
    def test_calls_subscribe_with_endpoint_and_args(self, mock_subscribe: MagicMock):
        mock_subscribe.return_value = {"video": {"url": "https://result.mp4"}}

        result = generate_video(
            endpoint="fal-ai/kling-video/o3/standard/text-to-video",
            arguments={"prompt": "A lion"},
        )

        mock_subscribe.assert_called_once()
        call_args = mock_subscribe.call_args
        assert call_args[0][0] == "fal-ai/kling-video/o3/standard/text-to-video"
        assert call_args[1]["arguments"] == {"prompt": "A lion"}
        assert call_args[1]["with_logs"] is True
        assert result == {"video": {"url": "https://result.mp4"}}

    @patch("api.fal_client.subscribe")
    def test_passes_all_arguments(self, mock_subscribe: MagicMock):
        mock_subscribe.return_value = {"video": {"url": "https://result.mp4"}}

        arguments = {
            "image_url": "https://img.png",
            "prompt": "Animate",
            "duration": "10",
            "generate_audio": True,
        }
        generate_video(
            endpoint="fal-ai/kling-video/o3/pro/image-to-video",
            arguments=arguments,
        )

        call_args = mock_subscribe.call_args
        assert call_args[1]["arguments"] == arguments

    @patch("api.fal_client.subscribe", side_effect=RuntimeError("connection timeout"))
    def test_api_failure_raises_api_error(self, mock_subscribe: MagicMock):
        with pytest.raises(ApiError, match=r"API call to .+ failed"):
            generate_video(
                endpoint="fal-ai/kling-video/o3/standard/text-to-video",
                arguments={"prompt": "test"},
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
