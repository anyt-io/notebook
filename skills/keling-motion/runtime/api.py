"""fal.ai API interaction: argument builder, video generation, and output saving."""

import urllib.request
from pathlib import Path

import fal_client

from config import ApiError, OutputError

# ---------------------------------------------------------------------------
# Argument builder
# ---------------------------------------------------------------------------


def build_motion_control_args(
    image_url: str,
    video_url: str,
    character_orientation: str = "image",
    prompt: str | None = None,
    keep_original_sound: bool = True,
) -> dict[str, object]:
    """Build arguments for the motion control endpoint."""
    args: dict[str, object] = {
        "image_url": image_url,
        "video_url": video_url,
        "character_orientation": character_orientation,
    }
    if prompt:
        args["prompt"] = prompt
    if not keep_original_sound:
        args["keep_original_sound"] = False
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
        raise OutputError("API response contains no video object. Try adjusting your inputs.")

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
