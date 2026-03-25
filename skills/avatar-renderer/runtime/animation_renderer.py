"""Animation sequence and sprite sheet rendering."""

from __future__ import annotations

import os

from PIL import Image

from config import SUPPORTED_EMOTIONS
from expression_map import EXPRESSION_MAP
from face_renderer import FaceRenderer
from models import ExpressionParams


class AnimationRenderer:
    """Renders animation sequences and sprite sheets from avatar expressions."""

    def __init__(self, face_renderer: FaceRenderer) -> None:
        self.face_renderer = face_renderer

    def render_sequence(self, script: list[dict[str, object]], output_dir: str) -> list[str]:
        """Render all frames from an animation script.

        Each script entry should have:
            - emotion (str): The emotion name
            - intensity (float, optional): Expression intensity (default 0.8)
            - frames (int, optional): Number of frames to hold (default 1)

        Args:
            script: List of animation step dictionaries.
            output_dir: Directory to write frame PNGs.

        Returns:
            List of output file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        paths: list[str] = []
        frame_idx = 0

        for step in script:
            emotion = str(step.get("emotion", "neutral"))
            intensity = float(step.get("intensity", 0.8))  # type: ignore[arg-type]
            hold_frames = int(step.get("frames", 1))  # type: ignore[arg-type]

            img = self.face_renderer.render_emotion(emotion, intensity)

            for _ in range(hold_frames):
                path = os.path.join(output_dir, f"frame_{frame_idx:04d}.png")
                img.save(path)
                paths.append(path)
                frame_idx += 1

        return paths

    def render_sprite_sheet(self, emotions: list[str] | None = None, cols: int = 4) -> Image.Image:
        """Render a grid sprite sheet of all emotions.

        Args:
            emotions: List of emotions to include. Defaults to all supported.
            cols: Number of columns in the grid.

        Returns:
            A PIL Image containing the sprite sheet.
        """
        if emotions is None:
            emotions = SUPPORTED_EMOTIONS

        w = self.face_renderer.config.width
        h = self.face_renderer.config.height
        rows = (len(emotions) + cols - 1) // cols
        sheet = Image.new("RGBA", (w * cols, h * rows), self.face_renderer.config.bg_color)

        for i, emotion in enumerate(emotions):
            row = i // cols
            col = i % cols
            frame = self.face_renderer.render_emotion(emotion, 0.8)
            sheet.paste(frame, (col * w, row * h))

        return sheet

    def interpolate_frames(
        self,
        from_emotion: str,
        to_emotion: str,
        steps: int = 5,
    ) -> list[Image.Image]:
        """Generate transition frames between two emotions.

        Args:
            from_emotion: Starting emotion name.
            to_emotion: Ending emotion name.
            steps: Number of intermediate frames (including start and end).

        Returns:
            List of PIL Images for the transition.

        Raises:
            ValueError: If an emotion is not recognized.
        """
        if from_emotion not in EXPRESSION_MAP:
            raise ValueError(f"Unknown emotion '{from_emotion}'")
        if to_emotion not in EXPRESSION_MAP:
            raise ValueError(f"Unknown emotion '{to_emotion}'")

        from_params = EXPRESSION_MAP[from_emotion]
        to_params = EXPRESSION_MAP[to_emotion]

        frames: list[Image.Image] = []
        for i in range(steps):
            t = i / max(steps - 1, 1)
            blended = _blend_params(from_params, to_params, t)
            frame = self.face_renderer.render(blended)
            frames.append(frame)

        return frames


def _blend_params(a: ExpressionParams, b: ExpressionParams, t: float) -> ExpressionParams:
    """Linearly blend between two ExpressionParams."""
    from dataclasses import fields

    kwargs: dict[str, float] = {}
    for f in fields(ExpressionParams):
        va = getattr(a, f.name)
        vb = getattr(b, f.name)
        kwargs[f.name] = va + (vb - va) * t
    return ExpressionParams(**kwargs)
