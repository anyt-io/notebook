import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from download_video import DEFAULT_OUTPUT_DIR, download_video, extract_video_id


class TestDefaultOutputDir:
    def test_resolves_to_skill_output_folder(self):
        assert DEFAULT_OUTPUT_DIR.name == "output"
        assert DEFAULT_OUTPUT_DIR.parent.name == "tiktok-downloader"


class TestExtractVideoId:
    def test_standard_url(self):
        url = "https://www.tiktok.com/@user/video/7593159807394123063"
        assert extract_video_id(url) == "7593159807394123063"

    def test_mobile_url(self):
        url = "https://m.tiktok.com/v/7593159807394123063"
        assert extract_video_id(url) == "7593159807394123063"

    def test_raw_id(self):
        assert extract_video_id("7593159807394123063") == "7593159807394123063"

    def test_url_with_query_params(self):
        url = "https://www.tiktok.com/@user/video/7593159807394123063?is_from_webapp=1"
        assert extract_video_id(url) == "7593159807394123063"

    def test_invalid_url_returns_none(self):
        assert extract_video_id("https://example.com/not-a-tiktok") is None

    def test_short_number_returns_none(self):
        assert extract_video_id("12345") is None


class TestDownloadVideo:
    def test_creates_output_directory(self, tmp_path: Path):
        output_dir = tmp_path / "new_dir"
        with patch("download_video.subprocess.run", side_effect=subprocess.CalledProcessError(1, "yt-dlp")):
            download_video("https://www.tiktok.com/@user/video/123", output_path=str(output_dir))
        assert output_dir.exists()

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_best_quality_format_string(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 30, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://www.tiktok.com/@user/video/123", output_path=str(tmp_path))

        cmd = mock_run.call_args[0][0]
        assert "-f" in cmd
        assert cmd[cmd.index("-f") + 1] == "bestvideo+bestaudio/best"

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_audio_only_flags(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 30, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://www.tiktok.com/@user/video/123", output_path=str(tmp_path), audio_only=True)

        cmd = mock_run.call_args[0][0]
        assert "-x" in cmd
        assert "--audio-format" in cmd
        assert "mp3" in cmd
        assert "-f" not in cmd

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_merge_output_format(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 30, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://www.tiktok.com/@user/video/123", output_path=str(tmp_path), format_type="mkv")

        cmd = mock_run.call_args[0][0]
        assert "--merge-output-format" in cmd
        assert cmd[cmd.index("--merge-output-format") + 1] == "mkv"

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_no_playlist_flag(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 30, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://www.tiktok.com/@user/video/123", output_path=str(tmp_path))

        cmd = mock_run.call_args[0][0]
        assert "--no-playlist" in cmd

    @patch("download_video.get_video_info")
    def test_returns_false_on_failure(self, mock_info: MagicMock, tmp_path: Path):
        mock_info.side_effect = subprocess.CalledProcessError(1, "yt-dlp")

        result = download_video("https://www.tiktok.com/@user/video/123", output_path=str(tmp_path))
        assert result is False

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_returns_true_on_success(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 30, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        result = download_video("https://www.tiktok.com/@user/video/123", output_path=str(tmp_path))
        assert result is True
