from pathlib import Path
from unittest.mock import MagicMock, patch

from download_cover import DEFAULT_OUTPUT_DIR, download_cover


class TestDefaultOutputDir:
    def test_resolves_to_skill_output_folder(self):
        assert DEFAULT_OUTPUT_DIR.name == "output"
        assert DEFAULT_OUTPUT_DIR.parent.name == "tiktok-downloader"


class TestDownloadCover:
    def test_creates_output_directory(self, tmp_path: Path):
        output_dir = tmp_path / "new_dir"
        with patch("download_cover.get_video_info", side_effect=Exception("network error")):
            download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(output_dir))
        assert output_dir.exists()

    @patch("download_cover.urllib.request.urlretrieve")
    @patch("download_cover.get_video_info")
    def test_downloads_thumbnail_as_jpg(self, mock_info: MagicMock, mock_retrieve: MagicMock, tmp_path: Path):
        mock_info.return_value = {
            "title": "Test TikTok",
            "thumbnail": "https://p16-sign.tiktokcdn.com/obj/cover.jpg",
        }

        result = download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(tmp_path))

        assert result is True
        mock_retrieve.assert_called_once_with(
            "https://p16-sign.tiktokcdn.com/obj/cover.jpg",
            tmp_path / "7593159807394123063.jpg",
        )

    @patch("download_cover.urllib.request.urlretrieve")
    @patch("download_cover.get_video_info")
    def test_detects_webp_extension(self, mock_info: MagicMock, mock_retrieve: MagicMock, tmp_path: Path):
        mock_info.return_value = {
            "title": "Test TikTok",
            "thumbnail": "https://p16-sign.tiktokcdn.com/obj/cover.webp",
        }

        result = download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(tmp_path))

        assert result is True
        mock_retrieve.assert_called_once_with(
            "https://p16-sign.tiktokcdn.com/obj/cover.webp",
            tmp_path / "7593159807394123063.webp",
        )

    @patch("download_cover.urllib.request.urlretrieve")
    @patch("download_cover.get_video_info")
    def test_detects_png_extension(self, mock_info: MagicMock, mock_retrieve: MagicMock, tmp_path: Path):
        mock_info.return_value = {
            "title": "Test TikTok",
            "thumbnail": "https://example.com/thumb.png?v=1",
        }

        result = download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(tmp_path))

        assert result is True
        mock_retrieve.assert_called_once_with(
            "https://example.com/thumb.png?v=1",
            tmp_path / "7593159807394123063.png",
        )

    @patch("download_cover.urllib.request.urlretrieve")
    @patch("download_cover.get_video_info")
    def test_custom_filename(self, mock_info: MagicMock, mock_retrieve: MagicMock, tmp_path: Path):
        mock_info.return_value = {
            "title": "Test TikTok",
            "thumbnail": "https://p16-sign.tiktokcdn.com/obj/cover.jpg",
        }

        result = download_cover(
            "https://www.tiktok.com/@user/video/7593159807394123063",
            output_path=str(tmp_path),
            filename="my_cover",
        )

        assert result is True
        mock_retrieve.assert_called_once_with(
            "https://p16-sign.tiktokcdn.com/obj/cover.jpg",
            tmp_path / "my_cover.jpg",
        )

    @patch("download_cover.get_video_info")
    def test_returns_false_when_no_thumbnail(self, mock_info: MagicMock, tmp_path: Path):
        mock_info.return_value = {"title": "Test TikTok", "thumbnail": ""}

        result = download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(tmp_path))
        assert result is False

    @patch("download_cover.get_video_info")
    def test_returns_false_on_failure(self, mock_info: MagicMock, tmp_path: Path):
        mock_info.side_effect = Exception("network error")

        result = download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(tmp_path))
        assert result is False

    @patch("download_cover.urllib.request.urlretrieve")
    @patch("download_cover.get_video_info")
    def test_returns_true_on_success(self, mock_info: MagicMock, mock_retrieve: MagicMock, tmp_path: Path):
        mock_info.return_value = {
            "title": "Test TikTok",
            "thumbnail": "https://p16-sign.tiktokcdn.com/obj/cover.jpg",
        }

        result = download_cover("https://www.tiktok.com/@user/video/7593159807394123063", output_path=str(tmp_path))
        assert result is True
