"""WaveSpeed API interaction: request submission, polling, and output saving."""

import time
import urllib.request
from pathlib import Path

import httpx

from config import (
    DEFAULT_POLL_INTERVAL,
    MAX_POLL_ATTEMPTS,
    ApiError,
    OutputError,
    get_motion_control_url,
    get_result_url,
)


def build_motion_control_args(
    image_url: str,
    video_url: str,
    character_orientation: str,
    prompt: str | None = None,
    negative_prompt: str | None = None,
    keep_original_sound: bool = True,
) -> dict[str, object]:
    """Build arguments for the motion control endpoint."""
    args: dict[str, object] = {
        "image": image_url,
        "video": video_url,
        "character_orientation": character_orientation,
        "keep_original_sound": keep_original_sound,
    }
    if prompt:
        args["prompt"] = prompt
    if negative_prompt:
        args["negative_prompt"] = negative_prompt
    return args


def submit_motion_request(
    api_key: str,
    arguments: dict[str, object],
) -> str:
    """Submit a motion control request and return the prediction ID.

    Raises ApiError if the API call fails.
    """
    url = get_motion_control_url()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=arguments)
            response.raise_for_status()
            data = response.json()

            # Handle both response formats
            prediction_id = data["data"].get("id") if "data" in data else data.get("id")

            if not prediction_id:
                raise ApiError(f"No prediction ID in response: {data}")

            return prediction_id
    except httpx.HTTPStatusError as e:
        raise ApiError(f"API request failed with status {e.response.status_code}: {e.response.text}") from e
    except Exception as e:
        raise ApiError(f"API call to {url} failed: {e}") from e


def poll_for_result(
    api_key: str,
    request_id: str,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    max_attempts: int = MAX_POLL_ATTEMPTS,
) -> dict[str, object]:
    """Poll the result endpoint until completion or failure.

    Raises ApiError if polling fails or times out.
    """
    url = get_result_url(request_id)
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    for attempt in range(max_attempts):
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Handle both response formats
                result = data.get("data", data)
                status = result.get("status", "").lower()

                if status == "completed":
                    print(f"  Completed after {attempt + 1} poll(s)")
                    return result
                elif status == "failed":
                    error_msg = result.get("error", "Unknown error")
                    raise ApiError(f"Generation failed: {error_msg}")
                elif status in ("created", "pending", "processing"):
                    print(f"  Status: {status} (attempt {attempt + 1}/{max_attempts})...")
                    time.sleep(poll_interval)
                else:
                    print(f"  Unknown status: {status} (attempt {attempt + 1}/{max_attempts})...")
                    time.sleep(poll_interval)

        except httpx.HTTPStatusError as e:
            raise ApiError(f"Polling failed with status {e.response.status_code}: {e.response.text}") from e
        except ApiError:
            raise
        except Exception as e:
            raise ApiError(f"Polling request failed: {e}") from e

    raise ApiError(f"Polling timed out after {max_attempts} attempts")


def generate_motion_video(
    api_key: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    """Submit a motion control request and wait for the result.

    Raises ApiError if the API call fails.
    """
    print("  Submitting request...")
    request_id = submit_motion_request(api_key, arguments)
    print(f"  Request ID: {request_id}")
    print("  Waiting for completion...")
    return poll_for_result(api_key, request_id)


def save_video(result: dict[str, object], output_dir: Path, filename: str) -> Path:
    """Download and save the generated video.

    Returns the saved path. Raises OutputError if no video in response.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = result.get("outputs")
    if not outputs or not isinstance(outputs, list) or len(outputs) == 0:
        raise OutputError("API response contains no outputs. The generation may have been filtered.")

    video_url = outputs[0]
    if not video_url or not isinstance(video_url, str):
        raise OutputError("API response contains no video URL. The generation may have been filtered.")

    out_path = output_dir / filename
    try:
        urllib.request.urlretrieve(video_url, str(out_path))
    except Exception as e:
        raise OutputError(f"Failed to download video from {video_url}: {e}") from e

    print(f"  Saved: {out_path}")
    return out_path
