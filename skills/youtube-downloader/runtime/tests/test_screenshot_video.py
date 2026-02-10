import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from screenshot_video import (
    DEFAULT_OUTPUT_DIR,
    capture_screenshot,
    format_timestamp,
    parse_timestamps,
    screenshot_video,
)


class TestDefaultOutputDir:
    def test_resolves_to_skill_output_folder(self):
        assert DEFAULT_OUTPUT_DIR.name == "output"
        assert DEFAULT_OUTPUT_DIR.parent.name == "youtube-downloader"


class TestFormatTimestamp:
    def test_seconds_only(self):
        assert format_timestamp(45) == "0:45"

    def test_minutes_and_seconds(self):
        assert format_timestamp(125) == "2:05"

    def test_hours(self):
        assert format_timestamp(3661) == "1:01:01"

    def test_zero(self):
        assert format_timestamp(0) == "0:00"

    def test_float_truncates(self):
        assert format_timestamp(90.7) == "1:30"


class TestParseTimestamps:
    def test_seconds_only(self):
        assert parse_timestamps("30,60,90") == [30.0, 60.0, 90.0]

    def test_mm_ss_format(self):
        assert parse_timestamps("1:15,2:00") == [75.0, 120.0]

    def test_h_mm_ss_format(self):
        assert parse_timestamps("1:02:03") == [3723.0]

    def test_mixed_formats(self):
        assert parse_timestamps("30,1:15,1:00:00") == [30.0, 75.0, 3600.0]

    def test_spaces_stripped(self):
        assert parse_timestamps(" 30 , 60 ") == [30.0, 60.0]

    def test_single_value(self):
        assert parse_timestamps("42") == [42.0]


class TestCaptureScreenshot:
    @patch("screenshot_video.subprocess.run")
    def test_success(self, mock_run: MagicMock, tmp_path: Path):
        mock_run.return_value = MagicMock(returncode=0)

        result = capture_screenshot("http://stream.url", 30.0, tmp_path / "out.jpg")

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "ffmpeg" in cmd
        assert "-ss" in cmd
        assert "30.0" in cmd
        assert "-frames:v" in cmd
        assert "1" in cmd

    @patch("screenshot_video.subprocess.run")
    def test_failure(self, mock_run: MagicMock, tmp_path: Path):
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")

        result = capture_screenshot("http://stream.url", 30.0, tmp_path / "out.jpg")

        assert result is False

    @patch("screenshot_video.subprocess.run")
    def test_quality_param(self, mock_run: MagicMock, tmp_path: Path):
        mock_run.return_value = MagicMock(returncode=0)

        capture_screenshot("http://stream.url", 10.0, tmp_path / "out.jpg", quality=5)

        cmd = mock_run.call_args[0][0]
        assert "-q:v" in cmd
        assert cmd[cmd.index("-q:v") + 1] == "5"


class TestScreenshotVideo:
    @patch("screenshot_video.capture_screenshot")
    @patch("screenshot_video.get_stream_url")
    @patch("screenshot_video.get_video_info")
    def test_captures_multiple_frames(
        self, mock_info: MagicMock, mock_stream: MagicMock, mock_capture: MagicMock, tmp_path: Path
    ):
        mock_info.return_value = {"title": "Test Video", "duration": 300, "uploader": "Tester"}
        mock_stream.return_value = "http://stream.url/video.mp4"
        mock_capture.return_value = True

        results = screenshot_video(
            "https://youtube.com/watch?v=test123",
            timestamps=[30.0, 60.0, 120.0],
            output_path=str(tmp_path),
        )

        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert mock_capture.call_count == 3

    @patch("screenshot_video.capture_screenshot")
    @patch("screenshot_video.get_stream_url")
    @patch("screenshot_video.get_video_info")
    def test_creates_output_directory(
        self, mock_info: MagicMock, mock_stream: MagicMock, mock_capture: MagicMock, tmp_path: Path
    ):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_stream.return_value = "http://stream.url/video.mp4"
        mock_capture.return_value = True

        output_dir = tmp_path / "new_dir"
        screenshot_video("https://youtube.com/watch?v=test123", timestamps=[10.0], output_path=str(output_dir))

        assert output_dir.exists()

    @patch("screenshot_video.capture_screenshot")
    @patch("screenshot_video.get_stream_url")
    @patch("screenshot_video.get_video_info")
    def test_writes_manifest_json(
        self, mock_info: MagicMock, mock_stream: MagicMock, mock_capture: MagicMock, tmp_path: Path
    ):
        mock_info.return_value = {"title": "Test Video", "duration": 120, "uploader": "Tester"}
        mock_stream.return_value = "http://stream.url/video.mp4"
        mock_capture.return_value = True

        screenshot_video(
            "https://youtube.com/watch?v=test123",
            timestamps=[20.0, 50.0],
            output_path=str(tmp_path),
            prefix="section",
        )

        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["video_title"] == "Test Video"
        assert len(manifest["frames"]) == 2
        assert manifest["frames"][0]["file"] == "section_001.jpg"
        assert manifest["frames"][1]["file"] == "section_002.jpg"

    @patch("screenshot_video.capture_screenshot")
    @patch("screenshot_video.get_stream_url")
    @patch("screenshot_video.get_video_info")
    def test_partial_failure(
        self, mock_info: MagicMock, mock_stream: MagicMock, mock_capture: MagicMock, tmp_path: Path
    ):
        mock_info.return_value = {"title": "Test", "duration": 120, "uploader": "Tester"}
        mock_stream.return_value = "http://stream.url/video.mp4"
        mock_capture.side_effect = [True, False, True]

        results = screenshot_video(
            "https://youtube.com/watch?v=test123",
            timestamps=[10.0, 20.0, 30.0],
            output_path=str(tmp_path),
        )

        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[2]["success"] is True

    @patch("screenshot_video.get_video_info")
    def test_returns_empty_on_info_error(self, mock_info: MagicMock, tmp_path: Path):
        mock_info.side_effect = subprocess.CalledProcessError(1, "yt-dlp")

        results = screenshot_video("https://youtube.com/watch?v=test123", timestamps=[10.0], output_path=str(tmp_path))

        assert results == []

    @patch("screenshot_video.get_stream_url")
    @patch("screenshot_video.get_video_info")
    def test_returns_empty_on_stream_error(self, mock_info: MagicMock, mock_stream: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_stream.side_effect = subprocess.CalledProcessError(1, "yt-dlp")

        results = screenshot_video("https://youtube.com/watch?v=test123", timestamps=[10.0], output_path=str(tmp_path))

        assert results == []

    @patch("screenshot_video.capture_screenshot")
    @patch("screenshot_video.get_stream_url")
    @patch("screenshot_video.get_video_info")
    def test_custom_prefix(self, mock_info: MagicMock, mock_stream: MagicMock, mock_capture: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_stream.return_value = "http://stream.url/video.mp4"
        mock_capture.return_value = True

        results = screenshot_video(
            "https://youtube.com/watch?v=test123",
            timestamps=[15.0],
            output_path=str(tmp_path),
            prefix="thumb",
        )

        assert results[0]["file"] == "thumb_001.jpg"
