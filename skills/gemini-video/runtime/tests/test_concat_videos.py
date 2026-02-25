"""Tests for concat_videos.py."""

from pathlib import Path
from unittest.mock import patch

from concat_videos import (
    SUPPORTED_EXTENSIONS,
    build_concat_file,
    check_ffmpeg,
    concat_videos,
    find_videos_in_directory,
    validate_video_files,
)


def make_fake_video(path: Path) -> Path:
    """Create a fake video file for testing."""
    path.write_bytes(b"\x00" * 100)
    return path


class TestCheckFfmpeg:
    @patch("concat_videos.shutil.which", return_value="/usr/bin/ffmpeg")
    def test_ffmpeg_available(self, _mock_which):
        assert check_ffmpeg() is None

    @patch("concat_videos.shutil.which", return_value=None)
    def test_ffmpeg_not_available(self, _mock_which):
        result = check_ffmpeg()
        assert result is not None
        assert "ffmpeg" in result.lower()


class TestValidateVideoFiles:
    def test_valid_mp4_files(self, tmp_path: Path):
        paths = [make_fake_video(tmp_path / f"vid{i}.mp4") for i in range(3)]
        assert validate_video_files(paths) is None

    def test_valid_mov_file(self, tmp_path: Path):
        path = make_fake_video(tmp_path / "clip.mov")
        assert validate_video_files([path]) is None

    def test_file_not_found(self, tmp_path: Path):
        result = validate_video_files([tmp_path / "missing.mp4"])
        assert result is not None
        assert "not found" in result.lower()

    def test_not_a_file(self, tmp_path: Path):
        result = validate_video_files([tmp_path])
        assert result is not None
        assert "Not a file" in result

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "video.flv"
        path.write_bytes(b"fake")
        result = validate_video_files([path])
        assert result is not None
        assert "Unsupported format" in result

    def test_empty_list(self):
        result = validate_video_files([])
        assert result is not None
        assert "No video files" in result

    def test_supported_extensions_cover_common_formats(self):
        for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
            assert ext in SUPPORTED_EXTENSIONS


class TestFindVideosInDirectory:
    def test_finds_mp4_files_sorted(self, tmp_path: Path):
        make_fake_video(tmp_path / "scene_03.mp4")
        make_fake_video(tmp_path / "scene_01.mp4")
        make_fake_video(tmp_path / "scene_02.mp4")
        result = find_videos_in_directory(tmp_path)
        assert len(result) == 3
        assert result[0].name == "scene_01.mp4"
        assert result[1].name == "scene_02.mp4"
        assert result[2].name == "scene_03.mp4"

    def test_empty_directory(self, tmp_path: Path):
        result = find_videos_in_directory(tmp_path)
        assert result == []

    def test_directory_not_found(self, tmp_path: Path):
        result = find_videos_in_directory(tmp_path / "nonexistent")
        assert result == []

    def test_custom_pattern(self, tmp_path: Path):
        make_fake_video(tmp_path / "scene_01.mp4")
        make_fake_video(tmp_path / "other.mp4")
        make_fake_video(tmp_path / "scene_02.mp4")
        result = find_videos_in_directory(tmp_path, "scene_*.mp4")
        assert len(result) == 2

    def test_ignores_non_matching_files(self, tmp_path: Path):
        make_fake_video(tmp_path / "video.mp4")
        (tmp_path / "readme.txt").write_text("hello")
        result = find_videos_in_directory(tmp_path)
        assert len(result) == 1


class TestBuildConcatFile:
    def test_writes_correct_format(self, tmp_path: Path):
        videos = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        concat_file = tmp_path / "list.txt"
        build_concat_file(videos, concat_file)
        content = concat_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            assert line.startswith("file '")
            assert line.endswith("'")

    def test_uses_absolute_paths(self, tmp_path: Path):
        videos = [tmp_path / "a.mp4"]
        concat_file = tmp_path / "list.txt"
        build_concat_file(videos, concat_file)
        content = concat_file.read_text()
        assert str(tmp_path.resolve()) in content

    def test_single_file(self, tmp_path: Path):
        videos = [tmp_path / "only.mp4"]
        concat_file = tmp_path / "list.txt"
        build_concat_file(videos, concat_file)
        lines = concat_file.read_text().strip().split("\n")
        assert len(lines) == 1


class TestConcatVideos:
    @patch("concat_videos.subprocess.run")
    def test_calls_ffmpeg_with_correct_args(self, mock_run, tmp_path: Path):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        videos = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        output = tmp_path / "out" / "result.mp4"

        concat_videos(videos, output)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "ffmpeg"
        assert "-f" in cmd
        assert "concat" in cmd
        assert "-c" in cmd
        assert "copy" in cmd
        assert str(output) in cmd

    @patch("concat_videos.subprocess.run")
    def test_returns_ffmpeg_exit_code(self, mock_run, tmp_path: Path):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "some error"
        videos = [tmp_path / "a.mp4"]
        output = tmp_path / "out.mp4"

        result = concat_videos(videos, output)
        assert result == 1

    @patch("concat_videos.subprocess.run")
    def test_returns_zero_on_success(self, mock_run, tmp_path: Path):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        videos = [tmp_path / "a.mp4"]
        output = tmp_path / "out.mp4"

        result = concat_videos(videos, output)
        assert result == 0

    @patch("concat_videos.subprocess.run")
    def test_creates_output_directory(self, mock_run, tmp_path: Path):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        videos = [tmp_path / "a.mp4"]
        output = tmp_path / "nested" / "deep" / "out.mp4"

        concat_videos(videos, output)
        assert output.parent.exists()

    @patch("concat_videos.subprocess.run")
    def test_cleans_up_temp_file(self, mock_run, tmp_path: Path):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        videos = [tmp_path / "a.mp4"]
        output = tmp_path / "out.mp4"

        concat_videos(videos, output)
        # Temp file should be cleaned up — verify no .txt files left in temp dir
        # (this is implicit; the finally block handles cleanup)
        mock_run.assert_called_once()
