"""Storyboard + narration -- the single source of truth for what is said, when, and for how long.

`build.py` reads SHOTS, synthesises the narration, stretches each shot to fit its line, renders
every shot to exactly that length, and concatenates. Editing a line here changes the film.

Shot contract (every renderer in `shots/` must honour it -- see reference/shot-spec.md):

    <interp> shots/<module>.py --out OUT.mp4 --duration SECONDS [--fps 30] [--width 1920]
                               [--height 1080]

  * writes a silent H.264 mp4 of EXACTLY `duration` seconds at the film's canvas
  * deterministic: same inputs -> same frames
  * `interp` is "video" (the rendering env) or "project" (your project's env, for real inference)
  * keeps the bottom ~14 % of the frame free (burned-in subtitles live there)
"""
from __future__ import annotations

from dataclasses import dataclass, field

VENUE = "ICRA"            # only used in log output
FILM_NAME = "film"        # out/<FILM_NAME>.mp4 and out/<FILM_NAME>_subtitled.mp4

# External assets copied into video/media/ by `build.py fetch`, so the film builds from video/
# alone once fetched.  "name in media/" -> path in your project.
SOURCE_MEDIA: dict[str, str] = {
    # "deployment.mp4": "../recordings/lab_run_2026-01-12.mp4",
}


@dataclass
class Shot:
    sid: str                      # stable id, also the build filename
    module: str                   # shots/<module>.py
    duration: float               # planned seconds (build stretches it to fit the narration)
    narration: str                # spoken text; "" = silent shot
    interp: str = "video"         # "video" | "project"
    args: list = field(default_factory=list)   # extra argv for the renderer
    part: str = ""                # hook | method | results | outro -- used for the time budget
    subtitle: str = ""            # override subtitle text (default: narration)
    enabled: bool = True          # False = kept on disk, cut from the film


SHOTS: list[Shot] = [
    Shot(
        "s01", "s01_example", 8.0, part="hook",
        narration=(
            "Open on the result, not the method. Show the thing working, in the real world, "
            "before you explain how it works."
        ),
    ),
    Shot(
        "s02", "s02_method", 10.0, part="method",
        narration=(
            "Then one idea per shot. Every number on screen comes from a real file in the "
            "repository, never from a slide."
        ),
    ),
    Shot(
        "s03", "s03_results", 12.0, part="results",
        narration=(
            "Give the results twice the time you give the method. Reviewers came for the "
            "evidence."
        ),
    ),
]


def active() -> list[Shot]:
    """The shots that actually make the cut, in film order."""
    return [s for s in SHOTS if s.enabled]


def total_planned() -> float:
    return sum(s.duration for s in active())


if __name__ == "__main__":
    for s in active():
        words = len(s.narration.split())
        print(f"{s.sid}  {s.part:8s} {s.duration:5.1f}s  {words:3d} words  "
              f"({words / max(s.duration, 1e-9):.2f} w/s)  {s.module}")
    print(f"total planned: {total_planned():.1f} s")
