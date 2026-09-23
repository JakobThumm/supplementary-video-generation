# Venue constraints

**Find these before you render a frame.** They change per year and per track, so treat the table
below as a starting point and confirm against the current call for papers. Then encode them in
`build.py` (`MAX_SECONDS`, `MAX_BYTES`, `MIN_HEIGHT`, `MIN_FPS`) so `build.py check` enforces
them on every build.

| venue | typical limits |
|---|---|
| ICRA / IROS (IEEE RAS) | ≤ 180 s, ≤ 20 MB, mpeg/mp4/mpg, ≥ 480 p, ≥ 20 fps, progressive |
| RA-L | ≤ 180 s, ≤ 20 MB, same container rules |
| CoRL | commonly ≤ 3–5 min, size set by the submission portal |
| CVPR / ICCV / ECCV | supplementary bundle capped as a whole (often 100 MB); video usually mp4 |
| SIGGRAPH | longer, much larger caps; separate "representative image" requirements |

Independent of the venue: **1920×1080, 30 fps, H.264 High, yuv420p, progressive, faststart**
plays everywhere and satisfies every constraint above.

## Sizing the encode

Two-pass, with the bitrate derived from the cap and the real duration:

```
total_kbps = (target_bytes * 0.92 * 8 / 1000) / duration_seconds
video_kbps = total_kbps - audio_kbps          # 160 kbps AAC is plenty for narration
```

The 0.92 is container overhead plus headroom. At 180 s and a 20 MB cap that is ~660 kbps of
video, which is tight for live footage and generous for flat graphics — another reason to keep
the palette dark and the motion purposeful.

If the film will not fit: cut a shot before you lower the bitrate. A 170 s film that looks sharp
beats a 180 s film that blocks up on the one piece of real footage in it.

## The check

```
PASS  film.mp4: 174.7s, 17.6 MB, 1920x1080, 30 fps, h264, progressive
```

Report this table when you hand the film over — "done" is not a verifiable claim. `ffprobe`
reports `field_order`; treat anything other than `progressive` or `unknown` as a failure.

## Two traps

**A hand-dubbed or re-exported cut is not checked.** When the author replaces the master with
their own render, re-run the check on *their* file — it can easily come back at twice the size
limit.

**Sidecar subtitles may not survive the portal.** Ship a burned-in variant as well as the
`.srt`/`.vtt`, and assume reviewers watch muted.
