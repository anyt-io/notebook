"""Tests for api.py — argument builders, request submission, polling, and saving."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api import (
    build_motion_control_args,
    generate_motion_video,
    poll_for_result,
    save_video,
    submit_motion_request,
)
from config import ApiError, OutputError

# ---------------------------------------------------------------------------
# Argument builder
# ---------------------------------------------------------------------------


class TestBuildMotionControlArgs:
    def test_required_args_only(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="image",
        )
        assert args["image"] == "https://img.png"
        assert args["video"] == "https://vid.mp4"
        assert args["character_orientation"] == "image"
        assert args["keep_original_sound"] is True
        assert "prompt" not in args
        assert "negative_prompt" not in args

    def test_with_prompt(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="video",
            prompt="A dancing person",
        )
        assert args["prompt"] == "A dancing person"
        assert args["character_orientation"] == "video"

    def test_with_negative_prompt(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="image",
            negative_prompt="blurry, distorted",
        )
        assert args["negative_prompt"] == "blurry, distorted"

    def test_no_keep_audio(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="image",
            keep_original_sound=False,
        )
        assert args["keep_original_sound"] is False

    def test_all_options(self):
        args = build_motion_control_args(
            image_url="https://img.png",
            video_url="https://vid.mp4",
            character_orientation="video",
            prompt="Dancing robot",
            negative_prompt="low quality",
            keep_original_sound=False,
        )
        assert args["image"] == "https://img.png"
        assert args["video"] == "https://vid.mp4"
        assert args["character_orientation"] == "video"
        assert args["prompt"] == "Dancing robot"
        assert args["negative_prompt"] == "low quality"
        assert args["keep_original_sound"] is False


# ---------------------------------------------------------------------------
# Submit request
# ---------------------------------------------------------------------------


class TestSubmitMotionRequest:
    @patch("api.httpx.Client")
    def test_successful_submission(self, mock_client_class: MagicMock):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"id": "pred-123"}}
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        request_id = submit_motion_request(
            api_key="test-key",
            arguments={"image": "https://img.png", "video": "https://vid.mp4"},
        )

        assert request_id == "pred-123"
        mock_client.post.assert_called_once()

    @patch("api.httpx.Client")
    def test_submission_with_direct_id_response(self, mock_client_class: MagicMock):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "pred-456"}
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        request_id = submit_motion_request(
            api_key="test-key",
            arguments={"image": "https://img.png", "video": "https://vid.mp4"},
        )

        assert request_id == "pred-456"

    @patch("api.httpx.Client")
    def test_no_prediction_id_raises_error(self, mock_client_class: MagicMock):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(ApiError, match="No prediction ID"):
            submit_motion_request(
                api_key="test-key",
                arguments={"image": "https://img.png", "video": "https://vid.mp4"},
            )


# ---------------------------------------------------------------------------
# Poll for result
# ---------------------------------------------------------------------------


class TestPollForResult:
    @patch("api.time.sleep")
    @patch("api.httpx.Client")
    def test_immediate_completion(self, mock_client_class: MagicMock, mock_sleep: MagicMock):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "status": "completed",
                "outputs": ["https://result.mp4"],
            }
        }
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = poll_for_result(api_key="test-key", request_id="pred-123")

        assert result["status"] == "completed"
        assert result["outputs"] == ["https://result.mp4"]
        mock_sleep.assert_not_called()

    @patch("api.time.sleep")
    @patch("api.httpx.Client")
    def test_polls_until_completion(self, mock_client_class: MagicMock, mock_sleep: MagicMock):
        responses = [
            {"data": {"status": "processing"}},
            {"data": {"status": "processing"}},
            {"data": {"status": "completed", "outputs": ["https://result.mp4"]}},
        ]
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.side_effect = responses
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = poll_for_result(api_key="test-key", request_id="pred-123", poll_interval=0.1)

        assert result["status"] == "completed"
        assert mock_sleep.call_count == 2

    @patch("api.time.sleep")
    @patch("api.httpx.Client")
    def test_failed_status_raises_error(self, mock_client_class: MagicMock, mock_sleep: MagicMock):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"status": "failed", "error": "Content filtered"}}
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(ApiError, match="Generation failed"):
            poll_for_result(api_key="test-key", request_id="pred-123")

    @patch("api.time.sleep")
    @patch("api.httpx.Client")
    def test_timeout_raises_error(self, mock_client_class: MagicMock, mock_sleep: MagicMock):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"status": "processing"}}
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(ApiError, match="timed out"):
            poll_for_result(api_key="test-key", request_id="pred-123", max_attempts=3, poll_interval=0.01)


# ---------------------------------------------------------------------------
# Generate motion video (full flow)
# ---------------------------------------------------------------------------


class TestGenerateMotionVideo:
    @patch("api.poll_for_result")
    @patch("api.submit_motion_request")
    def test_submits_and_polls(self, mock_submit: MagicMock, mock_poll: MagicMock):
        mock_submit.return_value = "pred-123"
        mock_poll.return_value = {"status": "completed", "outputs": ["https://result.mp4"]}

        result = generate_motion_video(
            api_key="test-key",
            arguments={"image": "https://img.png", "video": "https://vid.mp4"},
        )

        mock_submit.assert_called_once_with("test-key", {"image": "https://img.png", "video": "https://vid.mp4"})
        mock_poll.assert_called_once_with("test-key", "pred-123")
        assert result["outputs"] == ["https://result.mp4"]


# ---------------------------------------------------------------------------
# Save video
# ---------------------------------------------------------------------------


class TestSaveVideo:
    @patch("api.urllib.request.urlretrieve")
    def test_saves_video(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"outputs": ["https://cdn.wavespeed.ai/video.mp4"]}
        out = tmp_path / "out"

        saved = save_video(result, out, "test.mp4")

        assert saved == out / "test.mp4"
        assert out.exists()
        mock_retrieve.assert_called_once_with("https://cdn.wavespeed.ai/video.mp4", str(out / "test.mp4"))

    def test_no_outputs_in_response(self, tmp_path: Path):
        result: dict[str, object] = {}
        with pytest.raises(OutputError, match="no outputs"):
            save_video(result, tmp_path / "out", "test.mp4")

    def test_empty_outputs_list(self, tmp_path: Path):
        result: dict[str, object] = {"outputs": []}
        with pytest.raises(OutputError, match="no outputs"):
            save_video(result, tmp_path / "out", "test.mp4")

    def test_outputs_not_list(self, tmp_path: Path):
        result: dict[str, object] = {"outputs": "not a list"}
        with pytest.raises(OutputError, match="no outputs"):
            save_video(result, tmp_path / "out", "test.mp4")

    @patch("api.urllib.request.urlretrieve")
    def test_creates_nested_output_dir(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"outputs": ["https://cdn.wavespeed.ai/v.mp4"]}
        out = tmp_path / "nested" / "deep" / "output"

        save_video(result, out, "test.mp4")
        assert out.exists()

    @patch("api.urllib.request.urlretrieve", side_effect=OSError("download failed"))
    def test_download_failure_raises_output_error(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"outputs": ["https://cdn.wavespeed.ai/video.mp4"]}
        with pytest.raises(OutputError, match="Failed to download"):
            save_video(result, tmp_path / "out", "test.mp4")
