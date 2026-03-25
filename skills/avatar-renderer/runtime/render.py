"""CLI entry point for avatar rendering."""

from __future__ import annotations

import argparse
import json
import os
import sys

from animation_renderer import AnimationRenderer
from face_renderer import FaceRenderer
from models import AvatarConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Render avatar images with emotional expressions.")
    parser.add_argument("--emotion", type=str, default="neutral", help="Emotion to render (default: neutral)")
    parser.add_argument("--intensity", type=float, default=0.8, help="Expression intensity 0.0-1.0 (default: 0.8)")
    parser.add_argument("--script", type=str, help="Path to animation script JSON file")
    parser.add_argument("--sprite-sheet", action="store_true", help="Generate sprite sheet of all emotions")
    parser.add_argument("--output", type=str, default="output/", help="Output path (file or directory)")
    parser.add_argument("--size", type=int, default=512, help="Canvas size in pixels (default: 512)")

    args = parser.parse_args()

    config = AvatarConfig(width=args.size, height=args.size)
    renderer = FaceRenderer(config)

    if args.script:
        # Render animation sequence from script
        if not os.path.isfile(args.script):
            print(f"Error: Script file not found: {args.script}", file=sys.stderr)
            sys.exit(1)

        with open(args.script) as f:
            script = json.load(f)

        anim = AnimationRenderer(renderer)
        output_dir = args.output if args.output != "output/" else "output/frames/"
        paths = anim.render_sequence(script, output_dir)
        print(f"Rendered {len(paths)} frames to {output_dir}")

    elif args.sprite_sheet:
        # Render sprite sheet
        anim = AnimationRenderer(renderer)
        sheet = anim.render_sprite_sheet()
        output_path = args.output if args.output.endswith(".png") else os.path.join(args.output, "sprite_sheet.png")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        sheet.save(output_path)
        print(f"Sprite sheet saved to {output_path}")

    else:
        # Render single emotion frame
        img = renderer.render_emotion(args.emotion, args.intensity)
        if args.output.endswith(".png"):
            output_path = args.output
        else:
            output_path = os.path.join(args.output, f"avatar_{args.emotion}.png")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        img.save(output_path)
        print(f"Avatar saved to {output_path}")


if __name__ == "__main__":
    main()
