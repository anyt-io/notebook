"""Configuration constants for avatar rendering."""

# Canvas defaults
DEFAULT_CANVAS_WIDTH = 512
DEFAULT_CANVAS_HEIGHT = 512

# Colors (RGBA)
DEFAULT_BG_COLOR = (240, 240, 245, 255)
DEFAULT_SKIN_COLOR = (255, 220, 185, 255)
DEFAULT_LINE_COLOR = (60, 60, 60, 255)
DEFAULT_EYE_WHITE_COLOR = (255, 255, 255, 255)
DEFAULT_PUPIL_COLOR = (40, 40, 40, 255)
DEFAULT_MOUTH_COLOR = (180, 80, 80, 255)
DEFAULT_EYEBROW_COLOR = (80, 60, 50, 255)

# Drawing defaults
DEFAULT_LINE_WIDTH = 3
DEFAULT_FACE_LINE_WIDTH = 4
DEFAULT_EYEBROW_WIDTH = 5
DEFAULT_MOUTH_WIDTH = 4

# Face proportions (relative to canvas size)
FACE_CENTER_X_RATIO = 0.5
FACE_CENTER_Y_RATIO = 0.48
FACE_WIDTH_RATIO = 0.55
FACE_HEIGHT_RATIO = 0.65

# Eye proportions
EYE_Y_RATIO = 0.42
EYE_SPACING_RATIO = 0.15
EYE_WIDTH_RATIO = 0.09
EYE_HEIGHT_RATIO = 0.055
PUPIL_SIZE_RATIO = 0.03

# Eyebrow proportions
EYEBROW_Y_OFFSET_RATIO = 0.07
EYEBROW_WIDTH_RATIO = 0.10

# Mouth proportions
MOUTH_Y_RATIO = 0.60
MOUTH_WIDTH_RATIO = 0.12

# Supported emotions
SUPPORTED_EMOTIONS = [
    "neutral",
    "attentive",
    "skeptical",
    "satisfied",
    "stern",
    "surprised",
    "concerned",
]

# Font size
DEFAULT_FONT_SIZE = 14
