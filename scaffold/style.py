"""The film's visual language: one palette, one typeface, one canvas.

Every shot -- manim, matplotlib, OpenCV or ffmpeg -- imports from here, so the whole film reads
as one system.  Dark, high-contrast, explainer-style: near-black background, one accent hue per
semantic *role* (not per chart series), generous whitespace, no chart junk.

Retheme by editing this file only; nothing else hardcodes a colour.
"""
from __future__ import annotations

# --------------------------------------------------------------------------- canvas
WIDTH, HEIGHT, FPS = 1920, 1080, 30

# --------------------------------------------------------------------------- palette
BG          = "#0E1117"   # canvas
BG_PANEL    = "#161A22"   # inset panels / cards
FG          = "#ECEFF4"   # primary text
FG_MUTED    = "#8C94A6"   # captions, axes, secondary text
GRID        = "#232937"   # grid lines, faint geometry

BLUE        = "#4C9BE8"   # OUR conformal sets / our method
TEAL        = "#2DD4BF"   # predicted mean pose / model output
YELLOW      = "#F5C542"   # math highlight, calibration, "look here"
ORANGE      = "#F08A3C"   # ISO 13855 baseline
RED         = "#E4572E"   # failure, contact, danger
GREEN       = "#5BD99B"   # safe, verified, ground truth
PURPLE      = "#A87BE0"   # OOD / monitor
WHITE       = "#FFFFFF"

# semantic aliases (use these, not the raw hues)
C_OURS      = BLUE
C_ISO       = ORANGE
C_TRUTH     = GREEN
C_PRED      = TEAL
C_DANGER    = RED
C_OOD       = PURPLE
C_ROBOT     = "#C8CEDA"

# --------------------------------------------------------------------------- type
# ONE sans family for the whole film. Sizes and weights may vary; a second sans may not.
# Math (LaTeX / Computer Modern) is the single permitted exception.
FONT        = "Inter"
FONT_DIR    = "/usr/share/fonts/opentype/inter"    # where the .otf weights live
FONT_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TITLE_SIZE  = 62      # px at 1080p
H1_SIZE     = 46
BODY_SIZE   = 32
CAPTION_SIZE = 26

# lower-third safe area: the burned-in subtitles live below y = 0.86 * HEIGHT.
SUBTITLE_TOP_PX = int(0.855 * HEIGHT)


def font_path(weight: str = "Regular") -> str:
    """Path to a weight of the film's typeface, with a fallback so a fresh box still renders."""
    from pathlib import Path
    p = Path(FONT_DIR) / f"{FONT}-{weight}.otf"
    return str(p) if p.exists() else FONT_FALLBACK


def mpl_rc() -> dict:
    """matplotlib rcParams matching the film's look."""
    return {
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "text.color": FG,
        "axes.labelcolor": FG,
        "axes.edgecolor": GRID,
        "xtick.color": FG_MUTED,
        "ytick.color": FG_MUTED,
        "grid.color": GRID,
        "font.family": "sans-serif",
        "font.sans-serif": [FONT, "DejaVu Sans"],
        "font.size": 16,
        "axes.titlesize": 22,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 100,
        "lines.antialiased": True,
    }


def manim_config(config, quality_fps: int = FPS) -> None:
    """Apply the film's canvas + background to a manim `config` object."""
    config.pixel_width = WIDTH
    config.pixel_height = HEIGHT
    config.frame_rate = quality_fps
    config.background_color = BG
