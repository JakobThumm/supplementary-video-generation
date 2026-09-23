# Gotchas

Every one of these cost real debugging time on a shipped film.

## Typography

**manim collapses word spaces below `font_size ≈ 40.** `Text("conformal prediction sets for …",
font_size=16)` renders as `conformalprediction setsfor …`: Pango's advances get quantised onto
manim's own grid. It is invisible in a thumbnail and obvious on a projector. Render large and
scale down:

```python
RENDER_FS = 48.0
def big(cls, s, target_fs, **kw):
    k = max(1.0, RENDER_FS / target_fs)
    return cls(s, font_size=target_fs * k, **kw).scale(1.0 / k)
```

Route *all* manim prose through one helper so no shot can bypass it.

**libass renders SRT at 288 px script height.** Burning `subtitles=x.srt:force_style='FontSize=21'`
gives ~79 px glyphs at 1080p. Generate ASS with explicit `PlayResX: 1920 / PlayResY: 1080` and
size in real pixels.

**PIL has no tabular figures without libraqm.** Inter's proportional digits make a ticking counter
shimmer (a "1" is ⅔ the width of a "4"), and `features=["tnum"]` raises without Raqm. Draw the
number glyph-by-glyph on the widest-digit advance instead of switching to a monospace face — a
second typeface for one counter is not worth it.

**Real math in a PIL shot, without a LaTeX subprocess:** matplotlib's
`MathTextParser("agg")`. Match the cap height and baseline to the sans by measuring, not by eye:
render `$K$`, find its ink top and the baseline (`height - depth`), and scale to the sans's own
cap height from `font.getbbox("K")`.

**Check your font actually resolves.** A missing weight silently falls back and the film gains a
second typeface. Assert the `.otf` exists.

## Video and encoding

**`-vsync` is gone in ffmpeg 7+**; use `-fps_mode`.

**`tile=NxM` needs an explicit M.** `tile=6x0` errors out — compute the row count from the
duration.

**Pad to an exact frame count.** Floating-point duration × fps rounds inconsistently across
renderers; a shot one frame short desynchronises everything after it. Let the frame writer own
the count and pad with the last frame.

**Manim's own trim can land a frame short.** Render ~0.25 s of extra material and let the
conforming `-t` cut it exactly.

**A "20 MB" limit may mean 20 × 10⁶ or 20 × 2²⁰.** Target the strict one.

## Audio

**Loudness.** Normalise the mix (`loudnorm=I=-16:TP=-1.5:LRA=11`) or the voice-over will be
quiet relative to everything else the reviewer watches.

**Padding, not overlap.** A short lead-in and tail around each line stops sentences from colliding
across a cut.

**Ambience is usually wrong.** Lab-recording audio under narration sounds like a mistake unless
it is doing real work.

## Speech recognition, when re-timing a hand-dubbed cut

**VAD filters can swallow whole sentences.** faster-whisper's `vad_filter=True` dropped 22
consecutive words of clean speech. Use `vad_filter=False` for alignment work.

**Force-align, don't transcribe.** Take the wording from the written script and only the timing
from the recogniser (difflib over normalised tokens, interpolate the gaps). ASR mistakes then
cannot change a single subtitle word.

**Detect text that was never spoken.** If a run of unmatched script words has less time available
than ~0.12 s/word, it is not in the audio — report it instead of crushing it into the gap. This
is how a missing sentence gets caught rather than shipped as an unreadable 0.15 s caption.

**Make the re-timer idempotent.** It overwrites the same script file it reads, so the parser must
accept both the original and the re-timed column layout.

**Cache the transcript.** It is the slow step and depends only on the audio.

## Subtitle quality

* Two lines maximum, ≤ ~46 characters each, ≤ ~25 characters/second.
* Chunk a sentence into *balanced* pieces — greedy filling to the character limit strands a
  one-word stub ("instance.") on screen for 0.6 s.
* Prefer breaking after a comma; avoid orphaning a leading function word.
* Enforce priority in this order: **never overlap** > reach a minimum duration > lead-in. A
  minimum-duration floor applied *after* the overlap clamp silently reintroduces overlap.
* Absorb a caption too short to read into its predecessor. What limits it is the window until the
  next caption starts, not its own word span.

## Process

**Numbers drift between the paper and the repo.** Re-running an experiment changes a CSV while
the committed table stays put. Decide once whether the film follows the manuscript or the current
data — follow the manuscript so the two agree — and report every divergence.

**An abstract can disagree with its own results section.** Check both.

**Anonymity.** If the manuscript compiles anonymised, the video must match: no author names, no
project URL, no institution. Gate the URL behind a flag so the camera-ready is one switch.

**Footage shows faces.** Say so out loud; it is the author's call, not yours.
