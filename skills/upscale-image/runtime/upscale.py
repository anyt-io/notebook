#!/usr/bin/env python3
"""
Upscale images using Real-ESRGAN ncnn Vulkan.
Run with: uv run --project runtime runtime/upscale.py <image> [<image> ...]

Automatically downloads the ncnn binary and models on first run.
Supports macOS (arm64/x86_64), Linux, and Windows.
"""

import argparse
import platform
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import requests
from PIL import Image

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "output"
CACHE_DIR = Path.home() / ".cache" / "realesrgan-ncnn-vulkan"
BINARY_DIR = CACHE_DIR / "bin"
MODEL_DIR = CACHE_DIR / "models"

# Release URLs
NCNN_RELEASE_TAG = "v0.2.0"
NCNN_REPO = "xinntao/Real-ESRGAN-ncnn-vulkan"
# Models are distributed via the main Real-ESRGAN repo
MODELS_URL = (
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
)

PLATFORM_ASSETS = {
    "darwin": f"realesrgan-ncnn-vulkan-{NCNN_RELEASE_TAG}-macos.zip",
    "linux": f"realesrgan-ncnn-vulkan-{NCNN_RELEASE_TAG}-ubuntu.zip",
    "windows": f"realesrgan-ncnn-vulkan-{NCNN_RELEASE_TAG}-windows.zip",
}

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

AVAILABLE_MODELS = [
    "realesr-animevideov3",
    "realesrgan-x4plus",
    "realesrgan-x4plus-anime",
]


def get_platform_key() -> str:
    """Return platform key: darwin, linux, or windows."""
    system = platform.system().lower()
    if system == "darwin":
        return "darwin"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_binary_name() -> str:
    """Return the binary filename for the current platform."""
    if get_platform_key() == "windows":
        return "realesrgan-ncnn-vulkan.exe"
    return "realesrgan-ncnn-vulkan"


def get_binary_path() -> Path:
    """Return the expected path to the cached binary."""
    return BINARY_DIR / get_binary_name()


def download_file(url: str, dest: Path) -> None:
    """Download a file with progress indication."""
    print(f"Downloading: {url}")
    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                pct = downloaded * 100 // total
                print(f"\r  {pct}% ({downloaded // 1024 // 1024}MB / {total // 1024 // 1024}MB)", end="", flush=True)
    print()


def ensure_binary() -> Path:
    """Ensure the ncnn binary is available, downloading if needed. Return path to binary."""
    binary_path = get_binary_path()
    if binary_path.exists():
        return binary_path

    plat = get_platform_key()
    asset_name = PLATFORM_ASSETS[plat]
    asset_url = f"https://github.com/{NCNN_REPO}/releases/download/{NCNN_RELEASE_TAG}/{asset_name}"

    BINARY_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / asset_name
        download_file(asset_url, zip_path)

        with zipfile.ZipFile(zip_path) as zf:
            # Find the binary inside the zip
            bin_name = get_binary_name()
            for info in zf.infolist():
                if info.filename.endswith(bin_name):
                    data = zf.read(info.filename)
                    binary_path.write_bytes(data)
                    binary_path.chmod(0o755)
                    break
            else:
                raise RuntimeError(f"Binary '{bin_name}' not found in {asset_name}")

    print(f"Installed binary: {binary_path}")
    return binary_path


def ensure_models() -> Path:
    """Ensure ncnn model files are available, downloading if needed. Return model directory."""
    # Check if models already exist
    expected_model = MODEL_DIR / "realesr-animevideov3-x4.bin"
    if expected_model.exists():
        return MODEL_DIR

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "models.zip"
        download_file(MODELS_URL, zip_path)

        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                # Extract only model files (.param and .bin)
                if "/models/" in info.filename and (info.filename.endswith(".param") or info.filename.endswith(".bin")):
                    filename = Path(info.filename).name
                    dest = MODEL_DIR / filename
                    dest.write_bytes(zf.read(info.filename))

    print(f"Installed models: {MODEL_DIR}")
    return MODEL_DIR


def validate_input(path: Path) -> str | None:
    """Return an error message if the input path is invalid, else None."""
    if not path.exists():
        return f"File not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return f"Unsupported format '{path.suffix}': {path} (supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"
    return None


def get_image_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) of an image."""
    with Image.open(path) as img:
        return img.size


def upscale_image(
    input_path: Path,
    output_dir: Path,
    binary: Path,
    model_dir: Path,
    model_name: str,
    scale: int,
) -> Path:
    """Upscale a single image using realesrgan-ncnn-vulkan."""
    output_path = output_dir / f"{input_path.stem}_upscaled.png"

    cmd = [
        str(binary),
        "-i",
        str(input_path),
        "-o",
        str(output_path),
        "-m",
        str(model_dir),
        "-n",
        model_name,
        "-s",
        str(scale),
        "-f",
        "png",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"realesrgan-ncnn-vulkan failed (exit {result.returncode}): {result.stderr.strip()}")

    if not output_path.exists():
        raise RuntimeError("realesrgan-ncnn-vulkan produced no output")

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Upscale images using Real-ESRGAN ncnn Vulkan (GPU-accelerated)")
    parser.add_argument("images", nargs="+", help="Input image path(s)")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="realesr-animevideov3",
        choices=AVAILABLE_MODELS,
        help="Model to use (default: realesr-animevideov3, fastest)",
    )
    parser.add_argument(
        "-s",
        "--scale",
        type=int,
        default=4,
        choices=[2, 3, 4],
        help="Upscale factor (default: 4)",
    )
    args = parser.parse_args()

    # Ensure binary and models are available
    binary = ensure_binary()
    model_dir = ensure_models()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate all inputs before processing
    input_paths: list[Path] = []
    for img_str in args.images:
        p = Path(img_str)
        error = validate_input(p)
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        input_paths.append(p)

    print(f"Model: {args.model}")
    print(f"Scale: {args.scale}x")
    print(f"Output: {output_dir}")
    print(f"Images: {len(input_paths)}\n")

    for input_path in input_paths:
        w, h = get_image_dimensions(input_path)
        print(f"Processing: {input_path.name} ({w}x{h}) ... ", end="", flush=True)
        try:
            output_path = upscale_image(input_path, output_dir, binary, model_dir, args.model, args.scale)
            ow, oh = get_image_dimensions(output_path)
            print(f"-> {output_path.name} ({ow}x{oh})")
        except Exception as e:
            print(f"FAILED: {e}", file=sys.stderr)
            return 1

    print(f"\nDone! {len(input_paths)} image(s) upscaled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
