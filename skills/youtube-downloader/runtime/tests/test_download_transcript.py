from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from download_transcript import DEFAULT_OUTPUT_DIR, extract_video_id


class TestDefaultOutputDir:
    def test_resolves_to_skill_output_folder(self):
        assert DEFAULT_OUTPUT_DIR.name == "output"
        assert DEFAULT_OUTPUT_DIR.parent.name == "youtube-downloader"


class TestExtractVideoId:
    def test_standard_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/v/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_with_params(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42") == "dQw4w9WgXcQ"

    def test_bare_video_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_video_id_with_hyphens_underscores(self):
        assert extract_video_id("abc-_DEF123") == "abc-_DEF123"

    def test_invalid_url_exits(self):
        with pytest.raises(SystemExit):
            extract_video_id("not-a-valid-url-or-id")

    def test_empty_string_exits(self):
        with pytest.raises(SystemExit):
            extract_video_id("")


class TestDownloadTranscript:
    @patch("download_transcript.YouTubeTranscriptApi")
    def test_creates_output_directory(self, mock_api_class: MagicMock, tmp_path: Path):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_api.fetch.side_effect = Exception("no network")

        output_dir = tmp_path / "new_dir"
        download_transcript("dQw4w9WgXcQ", output_path=output_dir)
        assert output_dir.exists()

    @patch("download_transcript.YouTubeTranscriptApi")
    def test_saves_text_file(self, mock_api_class: MagicMock, tmp_path: Path):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_transcript = MagicMock()
        mock_transcript.language = "English"
        mock_transcript.language_code = "en"
        mock_transcript.snippets = []
        mock_api.fetch.return_value = mock_transcript

        with patch("download_transcript.FORMATTERS") as mock_formatters:
            mock_formatters.__getitem__ = MagicMock(return_value=MagicMock())
            mock_formatters["text"].format_transcript.return_value = "Hello world"

            result = download_transcript("dQw4w9WgXcQ", output_path=tmp_path, fmt="text")

        assert result is True
        output_file = tmp_path / "dQw4w9WgXcQ.txt"
        assert output_file.exists()
        assert output_file.read_text() == "Hello world"

    @patch("download_transcript.YouTubeTranscriptApi")
    def test_saves_json_file(self, mock_api_class: MagicMock, tmp_path: Path):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_transcript = MagicMock()
        mock_transcript.language = "English"
        mock_transcript.language_code = "en"
        mock_transcript.snippets = []
        mock_api.fetch.return_value = mock_transcript

        with patch("download_transcript.FORMATTERS") as mock_formatters:
            mock_formatters.__getitem__ = MagicMock(return_value=MagicMock())
            mock_formatters["json"].format_transcript.return_value = '[{"text": "hi"}]'

            result = download_transcript("dQw4w9WgXcQ", output_path=tmp_path, fmt="json")

        assert result is True
        assert (tmp_path / "dQw4w9WgXcQ.json").exists()

    @patch("download_transcript.YouTubeTranscriptApi")
    def test_saves_srt_file(self, mock_api_class: MagicMock, tmp_path: Path):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_transcript = MagicMock()
        mock_transcript.language = "English"
        mock_transcript.language_code = "en"
        mock_transcript.snippets = []
        mock_api.fetch.return_value = mock_transcript

        with patch("download_transcript.FORMATTERS") as mock_formatters:
            mock_formatters.__getitem__ = MagicMock(return_value=MagicMock())
            mock_formatters["srt"].format_transcript.return_value = "1\n00:00:00,000 --> 00:00:01,000\nhi\n"

            result = download_transcript("dQw4w9WgXcQ", output_path=tmp_path, fmt="srt")

        assert result is True
        assert (tmp_path / "dQw4w9WgXcQ.srt").exists()

    @patch("download_transcript.YouTubeTranscriptApi")
    def test_returns_false_on_fetch_error(self, mock_api_class: MagicMock, tmp_path: Path):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_api.fetch.side_effect = Exception("No transcript")
        mock_api.list.side_effect = Exception("No list")

        result = download_transcript("dQw4w9WgXcQ", output_path=tmp_path)
        assert result is False

    @patch("download_transcript.YouTubeTranscriptApi")
    def test_lists_available_languages_on_error(self, mock_api_class: MagicMock, tmp_path: Path, capsys):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_api.fetch.side_effect = Exception("No English")

        mock_t1 = MagicMock()
        mock_t1.language_code = "ja"
        mock_t2 = MagicMock()
        mock_t2.language_code = "ko"
        mock_api.list.return_value = [mock_t1, mock_t2]

        result = download_transcript("dQw4w9WgXcQ", output_path=tmp_path, lang="en")

        assert result is False
        captured = capsys.readouterr()
        assert "ja" in captured.err
        assert "ko" in captured.err

    @patch("download_transcript.YouTubeTranscriptApi")
    def test_passes_language_to_fetch(self, mock_api_class: MagicMock, tmp_path: Path):
        from download_transcript import download_transcript

        mock_api = mock_api_class.return_value
        mock_transcript = MagicMock()
        mock_transcript.language = "Japanese"
        mock_transcript.language_code = "ja"
        mock_transcript.snippets = []
        mock_api.fetch.return_value = mock_transcript

        with patch("download_transcript.FORMATTERS") as mock_formatters:
            mock_formatters.__getitem__ = MagicMock(return_value=MagicMock())
            mock_formatters["text"].format_transcript.return_value = "test"

            download_transcript("dQw4w9WgXcQ", output_path=tmp_path, lang="ja")

        mock_api.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["ja"])
