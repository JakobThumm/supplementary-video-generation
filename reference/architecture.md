# Architecture

```
video/
├── script.py       storyboard + narration -- the single source of truth
├── style.py        palette, type, canvas (imported by every renderer)
├── common.py       shot CLI, exact-duration frame writer, easing, clip conforming
├── tts.py          offline narration + SRT/VTT/ASS subtitle generation
├── build.py        orchestrator: fetch -> narrate -> shots -> assemble -> check
├── contactsheet.py tile sheet of the film (or one shot) for review
├── retime_subtitles.py   re-time against a hand-dubbed cut (ASR + forced alignment)
├── shots/          one renderer per shot, plus per-shot notes
├── media/          every external asset the film uses, copied in (self-contained)
├── build/          intermediates: per-shot mp4s, narration wavs, timeline.json
└── out/            the deliverables
```

## The dependency that defines the design

```
script.py (words)  ->  narration wavs  ->  timeline.json (durations)  ->  shots  ->  film
```

Durations are **derived**, never authored. `build.py narrate` synthesises each line, measures it,
and sets `duration = max(planned, voice + lead + tail)`. Renderers receive `--duration` and place
their beats as fractions of it. Consequences worth internalising:

* changing a sentence cannot break a layout;
* the time budget is checkable at any moment (`narrate` prints per-part totals, the
  method\:results ratio and the total against the cap) **before** anything is rendered;
* a shot can be re-rendered alone when only its line moved.

## Stages

| stage | what it does |
|---|---|
| `fetch` | copies `SOURCE_MEDIA` into `media/`, downloads the TTS voice |
| `narrate` | synthesises every line, fits durations, writes `build/timeline.json`, prints the budget |
| `shots [--only s06,s09] [--force] [--placeholders]` | runs each renderer to exactly its timeline duration |
| `assemble` | concatenates, mixes narration, burns subtitles, two-pass encodes to the size target |
| `check` | re-verifies the venue constraints on everything in `out/` |

`--placeholders` stubs every shot: it is how you prove the assembly path works before a single
real frame exists.

## Decisions worth keeping

**Re-encode at concat, don't stream-copy.** Shots come from different renderers (manim, a raw
frame writer, ffmpeg filter graphs); a stream copy inherits whatever SPS/PPS mismatch they happen
to have. The intermediate is near-lossless and the deliverable is re-encoded from it anyway.

**Fail soft on a broken shot.** One renderer crashing must not abort the other sixteen — stub it,
keep going, and list the failures at the end. A watchable cut with one stub is far more useful
than no cut.

**Two-pass, size-targeted encode.** Bitrate is computed from the byte cap and the real duration,
with ~8 % headroom. Read a "20 MB" limit the strict way (20 × 10⁶) so you are safe under either
convention.

**Subtitles as ASS, not SRT, for burn-in.** libass assumes a 288 px script height for SRT, so a
sensible `FontSize` renders enormous. Generating ASS with explicit `PlayResX/Y` fixes it. Ship
SRT/VTT as sidecars.

**Keep cut shots on disk.** `enabled=False` in the storyboard removes a shot from the film while
leaving the renderer and its notes intact. Authors change their minds; a one-line restore is
cheaper than rebuilding.

**One notes file per shot.** `shots/<sid>_notes.md` records what the shot reads, what it asserts,
which frames were inspected and every caveat. When work is split across parallel agents (or
sessions) this is the only durable channel between them.

## Parallel production

The shot contract exists so that *n* agents can write *n* shots at once without seeing each
other's code. What actually collides:

* **shared modules** — a 3-D rasteriser, a footage loader, a figure helper. Assign each to one
  agent per round; require a re-render check of every other shot that imports it.
* **the integrator's files** — `build.py`, `script.py`, `style.py`, `common.py`. Off limits to
  agents; they request changes in their report instead.
* **chapter labels and typography** — the drift you only see once the film is assembled. Budget a
  normalisation pass after the first full build, and do it yourself in one commit.

Expect agents to report success on shots that do not read well. Extract frames and judge them
yourself; that review loop is the difference between a competent film and a good one.
