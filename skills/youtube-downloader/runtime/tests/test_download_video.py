import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from download_video import DEFAULT_OUTPUT_DIR, download_video


class TestDefaultOutputDir:
    def test_resolves_to_skill_output_folder(self):
        assert DEFAULT_OUTPUT_DIR.name == "output"
        assert DEFAULT_OUTPUT_DIR.parent.name == "youtube-downloader"


class TestDownloadVideo:
    def test_creates_output_directory(self, tmp_path: Path):
        output_dir = tmp_path / "new_dir"
        with (
            patch("download_video.subprocess.run", side_effect=subprocess.CalledProcessError(1, "yt-dlp")),
        ):
            download_video("https://youtube.com/watch?v=test123", output_path=str(output_dir))
        assert output_dir.exists()

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_best_quality_format_string(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path), quality="best")

        cmd = mock_run.call_args[0][0]
        assert "-f" in cmd
        assert cmd[cmd.index("-f") + 1] == "bestvideo+bestaudio/best"

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_specific_quality_format_string(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path), quality="720p")

        cmd = mock_run.call_args[0][0]
        assert "-f" in cmd
        assert "720" in cmd[cmd.index("-f") + 1]

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_audio_only_flags(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path), audio_only=True)

        cmd = mock_run.call_args[0][0]
        assert "-x" in cmd
        assert "--audio-format" in cmd
        assert "mp3" in cmd
        assert "-f" not in cmd

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_merge_output_format(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path), format_type="mkv")

        cmd = mock_run.call_args[0][0]
        assert "--merge-output-format" in cmd
        assert cmd[cmd.index("--merge-output-format") + 1] == "mkv"

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_no_playlist_flag(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path))

        cmd = mock_run.call_args[0][0]
        assert "--no-playlist" in cmd

    @patch("download_video.get_video_info")
    def test_returns_false_on_failure(self, mock_info: MagicMock, tmp_path: Path):
        from subprocess import CalledProcessError

        mock_info.side_effect = CalledProcessError(1, "yt-dlp")

        result = download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path))
        assert result is False

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_returns_true_on_success(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        result = download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path))
        assert result is True

    @patch("download_video.subprocess.run")
    @patch("download_video.get_video_info")
    def test_worst_quality_format_string(self, mock_info: MagicMock, mock_run: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test", "duration": 60, "uploader": "Tester"}
        mock_run.return_value = MagicMock(returncode=0)

        download_video("https://youtube.com/watch?v=test123", output_path=str(tmp_path), quality="worst")

        cmd = mock_run.call_args[0][0]
        assert cmd[cmd.index("-f") + 1] == "worstvideo+worstaudio/worst"
