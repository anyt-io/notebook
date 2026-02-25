"""Gemini Veo API interaction: video generation and saving."""

import time
from pathlib import Path

from google import genai
from google.genai import types

from config import DEFAULT_POLL_INTERVAL, ApiError, OutputError
from media import build_reference_images, load_image


def generate_video(
    client: genai.Client,
    prompt: str,
    model: str,
    input_image: Path | None = None,
    last_frame: Path | None = None,
    reference_images: list[Path] | None = None,
    aspect_ratio: str | None = None,
    resolution: str | None = None,
    duration_seconds: int | None = None,
    negative_prompt: str | None = None,
    person_generation: str | None = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
) -> types.GenerateVideosResponse:
    """Generate a video using the Gemini Veo API. Polls until complete.

    Raises ApiError if the API call fails.
    """
    config_kwargs: dict[str, object] = {}
    if aspect_ratio:
        config_kwargs["aspect_ratio"] = aspect_ratio
    if resolution:
        config_kwargs["resolution"] = resolution
    if duration_seconds:
        config_kwargs["duration_seconds"] = duration_seconds
    if negative_prompt:
        config_kwargs["negative_prompt"] = negative_prompt
    if person_generation:
        config_kwargs["person_generation"] = person_generation
    if last_frame:
        config_kwargs["last_frame"] = load_image(last_frame)
    if reference_images:
        config_kwargs["reference_images"] = build_reference_images(reference_images)

    config = types.GenerateVideosConfig(**config_kwargs) if config_kwargs else None  # type: ignore[arg-type]

    image = load_image(input_image) if input_image else None

    try:
        operation = client.models.generate_videos(
            model=model,
            prompt=prompt,
            image=image,
            config=config,
        )

        while not operation.done:
            print(f"  Waiting for video generation to complete (polling every {poll_interval}s)...")
            time.sleep(poll_interval)
            operation = client.operations.get(operation)

        return operation.response  # type: ignore[return-value]
    except ApiError:
        raise
    except Exception as e:
        raise ApiError(f"API call failed: {e}") from e


def save_video(
    client: genai.Client,
    response: types.GenerateVideosResponse,
    output_dir: Path,
    filename: str,
) -> Path:
    """Download and save the first generated video.

    Returns the saved path. Raises OutputError if no video was generated.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if not response.generated_videos:
        raise OutputError("No videos were generated. Try adjusting your prompt.")

    generated_video = response.generated_videos[0]
    video_file = generated_video.video  # type: ignore[union-attr]

    if video_file is None:
        raise OutputError("Video object is empty. The generation may have been filtered.")

    client.files.download(file=video_file)
    out_path = output_dir / filename
    video_file.save(str(out_path))
    print(f"  Saved: {out_path}")
    return out_path
