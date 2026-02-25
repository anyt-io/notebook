"""fal.ai API interaction: argument builders, video generation, and output saving."""

import urllib.request
from pathlib import Path

import fal_client

from config import ApiError, OutputError

# ---------------------------------------------------------------------------
# Argument builders (one per mode)
# ---------------------------------------------------------------------------


def build_text_to_video_args(
    prompt: str | None = None,
    duration: str | None = None,
    aspect_ratio: str | None = None,
    generate_audio: bool = False,
    multi_prompt: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build arguments for text-to-video endpoint."""
    args: dict[str, object] = {}
    if multi_prompt:
        args["multi_prompt"] = multi_prompt
        args["shot_type"] = "customize"
    elif prompt:
        args["prompt"] = prompt
    if duration:
        args["duration"] = duration
    if aspect_ratio:
        args["aspect_ratio"] = aspect_ratio
    if generate_audio:
        args["generate_audio"] = True
    return args


def build_image_to_video_args(
    image_url: str,
    prompt: str | None = None,
    end_image_url: str | None = None,
    duration: str | None = None,
    generate_audio: bool = False,
    multi_prompt: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build arguments for image-to-video endpoint."""
    args: dict[str, object] = {"image_url": image_url}
    if multi_prompt:
        args["multi_prompt"] = multi_prompt
        args["shot_type"] = "customize"
    elif prompt:
        args["prompt"] = prompt
    if end_image_url:
        args["end_image_url"] = end_image_url
    if duration:
        args["duration"] = duration
    if generate_audio:
        args["generate_audio"] = True
    return args


def build_reference_to_video_args(
    prompt: str | None = None,
    elements: list[dict[str, object]] | None = None,
    ref_images: list[str] | None = None,
    start_image_url: str | None = None,
    end_image_url: str | None = None,
    duration: str | None = None,
    aspect_ratio: str | None = None,
    generate_audio: bool = False,
    multi_prompt: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    """Build arguments for reference-to-video endpoint."""
    args: dict[str, object] = {}
    if multi_prompt:
        args["multi_prompt"] = multi_prompt
        args["shot_type"] = "customize"
    elif prompt:
        args["prompt"] = prompt
    if elements:
        args["elements"] = elements
    if ref_images:
        args["image_urls"] = ref_images
    if start_image_url:
        args["start_image_url"] = start_image_url
    if end_image_url:
        args["end_image_url"] = end_image_url
    if duration:
        args["duration"] = duration
    if aspect_ratio:
        args["aspect_ratio"] = aspect_ratio
    if generate_audio:
        args["generate_audio"] = True
    return args


def build_edit_video_args(
    prompt: str,
    video_url: str,
    ref_images: list[str] | None = None,
    elements: list[dict[str, object]] | None = None,
    keep_audio: bool = True,
) -> dict[str, object]:
    """Build arguments for edit-video endpoint."""
    args: dict[str, object] = {"prompt": prompt, "video_url": video_url}
    if ref_images:
        args["image_urls"] = ref_images
    if elements:
        args["elements"] = elements
    args["keep_audio"] = keep_audio
    return args


# ---------------------------------------------------------------------------
# Generation & saving
# ---------------------------------------------------------------------------


def generate_video(
    endpoint: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    """Submit a video generation request and wait for the result.

    Raises ApiError if the API call fails.
    """

    def on_queue_update(update: object) -> None:
        if isinstance(update, fal_client.Queued):
            print(f"  Queued (position: {update.position})...")
        elif isinstance(update, fal_client.InProgress):
            if update.logs:
                for log in update.logs:
                    print(f"  {log['message']}")
            else:
                print("  In progress...")

    try:
        result: dict[str, object] = fal_client.subscribe(
            endpoint,
            arguments=arguments,
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        return result
    except Exception as e:
        raise ApiError(f"API call to {endpoint} failed: {e}") from e


def save_video(result: dict[str, object], output_dir: Path, filename: str) -> Path:
    """Download and save the generated video.

    Returns the saved path. Raises OutputError if no video in response.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    video = result.get("video")
    if not video or not isinstance(video, dict):
        raise OutputError("API response contains no video object. Try adjusting your prompt.")

    video_url = video.get("url")
    if not video_url or not isinstance(video_url, str):
        raise OutputError("API response contains no video URL. The generation may have been filtered.")

    out_path = output_dir / filename
    try:
        urllib.request.urlretrieve(video_url, str(out_path))
    except Exception as e:
        raise OutputError(f"Failed to download video from {video_url}: {e}") from e

    print(f"  Saved: {out_path}")
    return out_path
