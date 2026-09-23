"""s03 -- a minimal shot renderer, showing the contract and the house style.

Copy this as the starting point for a new shot. What matters:

  * the length comes from ``--duration``; every beat below is a *fraction* of it, so the shot
    still works when the narration changes and the build stretches it;
  * text enters on opacity only and never leaves (see reference/shot-spec.md, "Motion
    discipline"); graphics may move;
  * nothing essential below y = 928 px -- burned-in subtitles live there.

Render::

    python shots/s01_example.py --out build/shots/s01.mp4 --duration 8.0
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

VIDEO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VIDEO_DIR))

import common  # noqa: E402
import style  # noqa: E402

_FONTS: dict = {}


def font(px: int, weight: str = "Regular"):
    key = (px, weight)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(style.font_path(weight), px)
    return _FONTS[key]


def text(d, xy, s, px, colour, weight="Regular", a=1.0):
    """Opacity-only text. `a` is the fade; the position never moves."""
    if not s or a <= 0.01:
        return
    d.text(xy, s, font=font(px, weight), fill=common.hex2rgb(colour) + (int(255 * min(a, 1)),))


def main() -> None:
    a = common.shot_args(__doc__)
    D = a.duration

    def frame(t: float) -> np.ndarray:
        img = Image.new("RGB", (a.width, a.height), common.hex2rgb(style.BG))
        d = ImageDraw.Draw(img, "RGBA")

        # --- type: appears, holds, never exits
        text(d, (96, 52), "Chapter name", style.CAPTION_SIZE, style.FG_MUTED,
             a=common.seg(t, 0.02 * D, 0.02 * D + 0.25))
        text(d, (96, 100), "One idea, stated plainly", 46, style.FG, "Medium",
             a=common.seg(t, 0.10 * D, 0.10 * D + 0.25))
        text(d, (96, 168), "and the number that backs it", 30, style.C_OURS, "Medium",
             a=common.seg(t, 0.35 * D, 0.35 * D + 0.25))

        # --- graphics: motion is allowed, and earns its cost
        grow = common.seg(t, 0.30 * D, 0.80 * D, "smoother")
        cx, cy, r = 1340, 540, 40 + 250 * grow
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=common.hex2rgb(style.C_OURS) + (220,), width=3)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=common.hex2rgb(style.C_TRUTH) + (255,))
        return np.asarray(img)

    common.write_frames(a, (frame(i / a.fps) for i in range(a.n_frames)))


if __name__ == "__main__":
    main()
