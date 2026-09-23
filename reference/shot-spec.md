# Shot spec

The binding contract for one shot. Hand this file **verbatim** to every agent that writes a
renderer, alongside a short per-shot brief. The film only holds together because every shot obeys
it.

## The contract

Each shot is one file `video/shots/<sid>_<name>.py`, invoked by `build.py` as

```bash
<PY> video/shots/<module>.py --out video/build/shots/<sid>.mp4 --duration <SECONDS>
```

always from the project root. It must:

1. produce **exactly** `--duration` seconds of silent H.264 at the film's canvas (default
   1920×1080, 30 fps, yuv420p, **progressive**). Use `common.py` (`shot_args`,
   `FrameWriter` / `write_frames`, `conform`) — it guarantees the frame count and the encode
   settings. **Never hardcode a duration**: the narration drives it and it *will* change. Lay
   beats out as fractions of `--duration`, or on an absolute clock that degrades gracefully.
2. be **deterministic** and re-runnable: no interactive windows, no GUI, no network.
3. keep the bottom **14 %** of the frame (y > 928 px at 1080p) free of essential content —
   burned-in subtitles live there. Same for the top 40 px.
4. import the palette and type from `style.py`. Do not invent colours.
5. use only **real data from the project** for anything presented as a result. No synthetic
   stand-ins, no invented numbers. If a number appears on screen it must be traceable to a file,
   or computed live by the shot. Cite the source in a comment, and `assert` it against the
   published table where one exists.
6. hold its final state for **≥ 0.6 s**, so the cut lands on a readable frame.

## Interpreters

| purpose | interpreter |
|---|---|
| manim, matplotlib, opencv, PIL, piper (`interp="video"`) | `$VIDEO_ENV/bin/python` |
| the project's own models and datasets (`interp="project"`) | `$PROJECT_PY` |

**Expensive work must be cached.** If a shot needs model inference, dataset decoding or a long
GPU job, do it in a `--prepare` step that writes a small `.npz`/`.png` into `video/media/`, and
have the render path load that cache. The render must then run offline, without a GPU, in well
under a minute. Put the prepare command in the module docstring and in
`video/shots/<sid>_notes.md`.

## Visual language

* Background `style.BG` everywhere; no white frames, no default matplotlib look.
* **Semantic colour** — one hue per role, fixed across the whole film, e.g. `C_OURS`,
  `C_BASELINE`, `C_TRUTH`, `C_PRED`, `C_DANGER`, `C_OOD`, `C_ROBOT`. Never per chart series.
* **One sans family** (`style.FONT`). Sizes and weights may vary; a second sans may not. Math set
  in LaTeX / Computer Modern is the single exception — and real subscripts (*N*<sub>req</sub>)
  always beat ASCII (`N_req`).
* Titles ≤ 62 px, body 32 px, captions 26 px. Left-aligned labels; no ALL CAPS except short
  chapter kickers.
* Every shot carries a small chapter label top-left in `FG_MUTED`, using the film's agreed
  scheme. Keep the scheme identical across shots — mixed numbering is the most common drift when
  shots are written in parallel.

### Motion discipline

Animation is for **graphics**, not for words.

* **Text, numbers, equations, labels, captions, legends: entry is opacity only.** No slide-in, no
  shift, no scale, no `Transform`/`ReplacementTransform`, no travelling. Fade up over ≤ 0.25 s,
  or simply appear. A moving word costs the viewer attention that belongs to the content.
* **No exit animations anywhere.** Elements stay until the shot cuts. Where a shot has several
  beats, swap between them with a hard cut or an instant clear — never a "move down and fade
  away".
* Graphics keep their motion: 3-D scenes, camera moves, sets growing over a horizon, counters
  ticking, a highlight travelling over a figure, live footage. That is where animation earns its
  cost.
* Ease whatever does move; nothing pops in linearly.

## Verifying your shot — not optional

```bash
<PY> video/shots/<module>.py --out /tmp/<sid>.mp4 --duration <D>
ffprobe -v error -show_entries format=duration \
        -show_entries stream=width,height,r_frame_rate,pix_fmt -of default=nw=1 /tmp/<sid>.mp4
ffmpeg -i /tmp/<sid>.mp4 -vf "fps=1/2,scale=900:-1,tile=2x3" -frames:v 1 /tmp/<sid>_sheet.png
```

Then **look at the frames**. Iterate until they are legible at 50 % scale, free of overlapping
text, and clear of the subtitle band. A shot that has not been visually inspected is not done.
Also re-render at an off-nominal duration (say ±15 %) to prove the layout survives a narration
edit.

## Working in parallel

* One agent owns a shot file. A **shared module** (a renderer, a data loader, a figure helper) is
  owned by exactly one agent per round; anyone who changes it must re-render every other shot
  that imports it and say so.
* Never edit `build.py`, `script.py`, `style.py`, `common.py` or the project README — those
  belong to the integrator. Record new dependencies and prepare commands in
  `video/shots/<sid>_notes.md` instead.
* Do not commit. The integrator reviews and commits.
* Report: what you changed, which frames you looked at, every number's source, and every caveat
  you found. Caveats are the most valuable part of the report — they are usually real problems in
  the paper.
