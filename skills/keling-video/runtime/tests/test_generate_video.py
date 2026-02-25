"""Tests for generate_video.py."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from generate_video import (
    DEFAULT_ASPECT_RATIO,
    DEFAULT_DURATION,
    DEFAULT_QUALITY,
    ENDPOINTS,
    MAX_ELEMENT_REFS,
    MAX_ELEMENTS,
    MAX_IMAGE_SIZE_MB,
    MAX_REF_IMAGES,
    MAX_VIDEO_SIZE_MB,
    SUPPORTED_ASPECT_RATIOS,
    SUPPORTED_DURATIONS,
    SUPPORTED_INPUT_EXTENSIONS,
    SUPPORTED_MODES,
    SUPPORTED_QUALITY,
    SUPPORTED_VIDEO_EXTENSIONS,
    build_edit_video_args,
    build_element,
    build_image_to_video_args,
    build_reference_to_video_args,
    build_text_to_video_args,
    detect_mode,
    get_api_key,
    get_endpoint,
    parse_elements_json,
    parse_multi_prompt,
    resolve_image_url,
    resolve_video_url,
    save_video,
    validate_input_image,
    validate_input_video,
)


def make_test_image(path: Path, size_bytes: int = 100) -> Path:
    """Create a small fake image file."""
    path.write_bytes(b"\x89PNG" + b"\x00" * max(0, size_bytes - 4))
    return path


def make_test_video(path: Path, size_bytes: int = 100) -> Path:
    """Create a small fake video file."""
    path.write_bytes(b"\x00\x00\x00\x1cftyp" + b"\x00" * max(0, size_bytes - 8))
    return path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_supported_modes(self):
        assert "text-to-video" in SUPPORTED_MODES
        assert "image-to-video" in SUPPORTED_MODES
        assert "reference-to-video" in SUPPORTED_MODES
        assert "edit-video" in SUPPORTED_MODES
        assert len(SUPPORTED_MODES) == 4

    def test_endpoints_all_modes_and_qualities(self):
        for mode in SUPPORTED_MODES:
            assert mode in ENDPOINTS
            for quality in SUPPORTED_QUALITY:
                assert quality in ENDPOINTS[mode]
                assert ENDPOINTS[mode][quality].startswith("fal-ai/kling-video/o3/")

    def test_default_quality(self):
        assert DEFAULT_QUALITY == "standard"
        assert DEFAULT_QUALITY in SUPPORTED_QUALITY

    def test_aspect_ratios(self):
        assert "16:9" in SUPPORTED_ASPECT_RATIOS
        assert "9:16" in SUPPORTED_ASPECT_RATIOS
        assert "1:1" in SUPPORTED_ASPECT_RATIOS

    def test_default_aspect_ratio(self):
        assert DEFAULT_ASPECT_RATIO == "16:9"

    def test_durations_range_3_to_15(self):
        assert [str(d) for d in range(3, 16)] == SUPPORTED_DURATIONS
        assert DEFAULT_DURATION == "5"

    def test_supported_image_extensions(self):
        assert ".png" in SUPPORTED_INPUT_EXTENSIONS
        assert ".jpg" in SUPPORTED_INPUT_EXTENSIONS
        assert ".jpeg" in SUPPORTED_INPUT_EXTENSIONS
        assert ".webp" in SUPPORTED_INPUT_EXTENSIONS
        assert ".gif" in SUPPORTED_INPUT_EXTENSIONS

    def test_supported_video_extensions(self):
        assert ".mp4" in SUPPORTED_VIDEO_EXTENSIONS
        assert ".mov" in SUPPORTED_VIDEO_EXTENSIONS

    def test_limits(self):
        assert MAX_IMAGE_SIZE_MB == 10
        assert MAX_VIDEO_SIZE_MB == 200
        assert MAX_ELEMENTS == 2
        assert MAX_ELEMENT_REFS == 3
        assert MAX_REF_IMAGES == 4


# ---------------------------------------------------------------------------
# API key
# ---------------------------------------------------------------------------


class TestGetApiKey:
    def test_returns_key_when_set(self):
        with patch.dict("os.environ", {"FAL_KEY": "test-key-123"}):
            assert get_api_key() == "test-key-123"

    def test_returns_none_when_not_set(self):
        with patch.dict("os.environ", {}, clear=True):
            assert get_api_key() is None


# ---------------------------------------------------------------------------
# Endpoint resolution
# ---------------------------------------------------------------------------


class TestGetEndpoint:
    def test_text_to_video_standard(self):
        assert get_endpoint("text-to-video", "standard") == "fal-ai/kling-video/o3/standard/text-to-video"

    def test_text_to_video_pro(self):
        assert get_endpoint("text-to-video", "pro") == "fal-ai/kling-video/o3/pro/text-to-video"

    def test_image_to_video_standard(self):
        assert get_endpoint("image-to-video", "standard") == "fal-ai/kling-video/o3/standard/image-to-video"

    def test_image_to_video_pro(self):
        assert get_endpoint("image-to-video", "pro") == "fal-ai/kling-video/o3/pro/image-to-video"

    def test_reference_to_video_standard(self):
        assert get_endpoint("reference-to-video", "standard") == "fal-ai/kling-video/o3/standard/reference-to-video"

    def test_reference_to_video_pro(self):
        assert get_endpoint("reference-to-video", "pro") == "fal-ai/kling-video/o3/pro/reference-to-video"

    def test_edit_video_standard(self):
        assert get_endpoint("edit-video", "standard") == "fal-ai/kling-video/o3/standard/video-to-video/edit"

    def test_edit_video_pro(self):
        assert get_endpoint("edit-video", "pro") == "fal-ai/kling-video/o3/pro/video-to-video/edit"


# ---------------------------------------------------------------------------
# Image validation
# ---------------------------------------------------------------------------


class TestValidateInputImage:
    def test_valid_png(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.png")
        assert validate_input_image(img) is None

    def test_valid_jpg(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.jpg")
        assert validate_input_image(img) is None

    def test_valid_webp(self, tmp_path: Path):
        img = make_test_image(tmp_path / "test.webp")
        assert validate_input_image(img) is None

    def test_file_not_found(self, tmp_path: Path):
        result = validate_input_image(tmp_path / "nonexistent.png")
        assert result is not None
        assert "not found" in result.lower()

    def test_not_a_file(self, tmp_path: Path):
        result = validate_input_image(tmp_path)
        assert result is not None
        assert "Not a file" in result

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.bmp"
        path.write_bytes(b"fake")
        result = validate_input_image(path)
        assert result is not None
        assert "Unsupported" in result

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.png"
        path.write_bytes(b"\x89PNG" + b"\x00" * (MAX_IMAGE_SIZE_MB * 1024 * 1024))
        result = validate_input_image(path)
        assert result is not None
        assert "too large" in result.lower()


# ---------------------------------------------------------------------------
# Video validation
# ---------------------------------------------------------------------------


class TestValidateInputVideo:
    def test_valid_mp4(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "test.mp4")
        assert validate_input_video(vid) is None

    def test_valid_mov(self, tmp_path: Path):
        vid = make_test_video(tmp_path / "test.mov")
        assert validate_input_video(vid) is None

    def test_file_not_found(self, tmp_path: Path):
        result = validate_input_video(tmp_path / "nonexistent.mp4")
        assert result is not None
        assert "not found" in result.lower()

    def test_not_a_file(self, tmp_path: Path):
        result = validate_input_video(tmp_path)
        assert result is not None
        assert "Not a file" in result

    def test_unsupported_extension(self, tmp_path: Path):
        path = tmp_path / "test.avi"
        path.write_bytes(b"fake")
        result = validate_input_video(path)
        assert result is not None
        assert "Unsupported" in result

    def test_file_too_large(self, tmp_path: Path):
        path = tmp_path / "huge.mp4"
        path.write_bytes(b"\x00" * (MAX_VIDEO_SIZE_MB * 1024 * 1024 + 1))
        result = validate_input_video(path)
        assert result is not None
        assert "too large" in result.lower()


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------


class TestResolveImageUrl:
    def test_http_url_passthrough(self):
        url = "https://example.com/img.png"
        assert resolve_image_url(url) == url

    def test_https_url_passthrough(self):
        url = "https://cdn.example.com/img.jpg"
        assert resolve_image_url(url) == url

    @patch("generate_video.fal_client.upload_file", return_value="https://fal.ai/uploaded/img.png")
    def test_local_file_upload(self, mock_upload: MagicMock, tmp_path: Path):
        img = make_test_image(tmp_path / "local.png")
        result = resolve_image_url(str(img))
        assert result == "https://fal.ai/uploaded/img.png"
        mock_upload.assert_called_once_with(img)

    def test_invalid_local_file_raises(self, tmp_path: Path):
        with pytest.raises(ValueError, match="not found"):
            resolve_image_url(str(tmp_path / "missing.png"))


class TestResolveVideoUrl:
    def test_url_passthrough(self):
        url = "https://example.com/vid.mp4"
        assert resolve_video_url(url) == url

    @patch("generate_video.fal_client.upload_file", return_value="https://fal.ai/uploaded/vid.mp4")
    def test_local_file_upload(self, mock_upload: MagicMock, tmp_path: Path):
        vid = make_test_video(tmp_path / "local.mp4")
        result = resolve_video_url(str(vid))
        assert result == "https://fal.ai/uploaded/vid.mp4"
        mock_upload.assert_called_once_with(vid)

    def test_invalid_local_file_raises(self, tmp_path: Path):
        with pytest.raises(ValueError, match="not found"):
            resolve_video_url(str(tmp_path / "missing.mp4"))


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------


class TestDetectMode:
    def _ns(self, **kwargs: object) -> MagicMock:
        ns = MagicMock()
        ns.image = kwargs.get("image")
        ns.video = kwargs.get("video")
        ns.element = kwargs.get("element")
        ns.elements_json = kwargs.get("elements_json")
        return ns

    def test_text_to_video(self):
        assert detect_mode(self._ns()) == "text-to-video"

    def test_image_to_video(self):
        assert detect_mode(self._ns(image="start.png")) == "image-to-video"

    def test_reference_with_element(self):
        assert detect_mode(self._ns(element=["char.png"])) == "reference-to-video"

    def test_reference_with_elements_json(self):
        assert detect_mode(self._ns(elements_json="[{}]")) == "reference-to-video"

    def test_edit_video(self):
        assert detect_mode(self._ns(video="input.mp4")) == "edit-video"

    def test_video_takes_priority_over_image(self):
        assert detect_mode(self._ns(video="input.mp4", image="start.png")) == "edit-video"

    def test_element_takes_priority_over_image(self):
        assert detect_mode(self._ns(element=["char.png"], image="start.png")) == "reference-to-video"


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
# Element building
# ---------------------------------------------------------------------------


class TestBuildElement:
    def test_frontal_only(self):
        elem = build_element("https://front.png")
        assert elem == {"frontal_image_url": "https://front.png"}

    def test_with_refs(self):
        elem = build_element("https://front.png", ref_urls=["https://side.png", "https://back.png"])
        assert elem["reference_image_urls"] == ["https://side.png", "https://back.png"]

    def test_with_video(self):
        elem = build_element("https://front.png", video_url="https://motion.mp4")
        assert elem["video_url"] == "https://motion.mp4"

    def test_with_all(self):
        elem = build_element(
            "https://front.png",
            ref_urls=["https://side.png"],
            video_url="https://motion.mp4",
        )
        assert elem["frontal_image_url"] == "https://front.png"
        assert elem["reference_image_urls"] == ["https://side.png"]
        assert elem["video_url"] == "https://motion.mp4"


# ---------------------------------------------------------------------------
# Multi-prompt parsing
# ---------------------------------------------------------------------------


class TestParseMultiPrompt:
    def test_json_string(self):
        data = parse_multi_prompt('[{"prompt":"Scene 1","duration":"5"},{"prompt":"Scene 2"}]')
        assert len(data) == 2
        assert data[0]["prompt"] == "Scene 1"
        assert data[0]["duration"] == "5"

    def test_json_file(self, tmp_path: Path):
        f = tmp_path / "prompts.json"
        f.write_text(json.dumps([{"prompt": "A"}, {"prompt": "B"}]))
        data = parse_multi_prompt(str(f))
        assert len(data) == 2

    def test_invalid_not_array(self):
        with pytest.raises(ValueError, match="JSON array"):
            parse_multi_prompt('{"prompt":"test"}')

    def test_invalid_missing_prompt(self):
        with pytest.raises(ValueError, match="prompt"):
            parse_multi_prompt('[{"duration":"5"}]')

    def test_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            parse_multi_prompt("not json")


class TestParseElementsJson:
    def test_json_string(self):
        data = parse_elements_json('[{"frontal_image_url":"https://x.png"}]')
        assert len(data) == 1

    def test_json_file(self, tmp_path: Path):
        f = tmp_path / "elements.json"
        f.write_text(json.dumps([{"frontal_image_url": "https://a.png"}, {"frontal_image_url": "https://b.png"}]))
        data = parse_elements_json(str(f))
        assert len(data) == 2

    def test_invalid_not_array(self):
        with pytest.raises(ValueError, match="JSON array"):
            parse_elements_json('{"frontal_image_url":"x"}')


# ---------------------------------------------------------------------------
# Generate video (API call)
# ---------------------------------------------------------------------------


class TestGenerateVideo:
    @patch("generate_video.fal_client.subscribe")
    def test_calls_subscribe_with_endpoint_and_args(self, mock_subscribe: MagicMock):
        from generate_video import generate_video

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

    @patch("generate_video.fal_client.subscribe")
    def test_passes_all_arguments(self, mock_subscribe: MagicMock):
        from generate_video import generate_video

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


# ---------------------------------------------------------------------------
# Save video
# ---------------------------------------------------------------------------


class TestSaveVideo:
    @patch("generate_video.urllib.request.urlretrieve")
    def test_saves_video(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"video": {"url": "https://cdn.fal.ai/video.mp4"}}
        out = tmp_path / "out"

        saved = save_video(result, out, "test.mp4")

        assert saved == out / "test.mp4"
        assert out.exists()
        mock_retrieve.assert_called_once_with("https://cdn.fal.ai/video.mp4", str(out / "test.mp4"))

    def test_no_video_in_response(self, tmp_path: Path):
        result: dict[str, object] = {}
        assert save_video(result, tmp_path / "out", "test.mp4") is None

    def test_no_url_in_video(self, tmp_path: Path):
        result: dict[str, object] = {"video": {"file_name": "x.mp4"}}
        assert save_video(result, tmp_path / "out", "test.mp4") is None

    def test_video_not_dict(self, tmp_path: Path):
        result: dict[str, object] = {"video": "not a dict"}
        assert save_video(result, tmp_path / "out", "test.mp4") is None

    @patch("generate_video.urllib.request.urlretrieve")
    def test_creates_nested_output_dir(self, mock_retrieve: MagicMock, tmp_path: Path):
        result: dict[str, object] = {"video": {"url": "https://cdn.fal.ai/v.mp4"}}
        out = tmp_path / "nested" / "deep" / "output"

        save_video(result, out, "test.mp4")
        assert out.exists()
