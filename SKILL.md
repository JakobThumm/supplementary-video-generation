---
name: supplementary-video-generation
description: Produce a narrated supplementary/submission video for a research paper — an explainer built from the repository's own data, assembled by a reproducible script. Use when asked to make a paper video, conference submission video (ICRA, IROS, RA-L, CoRL, CVPR, SIGGRAPH), demo reel, project-page video, or a 3blue1brown-style explainer of a method; when asked to add narration, burned-in or sidecar subtitles to such a video; or when asked to re-time subtitles after a voice-over has been re-recorded.
---

# Supplementary video generation

A paper video is not a slide deck with a voice on top. It is a short film with a hard length
limit, an audience that will watch it once, and a reviewer who wants evidence. The pipeline in
`scaffold/` exists so the film is **reproducible from a script**, so every number on screen is
**traceable to a file**, and so the length is **derived from the narration** rather than guessed.

Read `reference/architecture.md` before changing the pipeline, `reference/shot-spec.md` before
writing any shot (it is also the brief you hand to parallel agents), `reference/gotchas.md` when
something renders wrong, and `reference/venue-constraints.md` before the first frame is rendered.

## The one rule that shapes everything

**Narration first, then durations, then pictures.** Synthesise (or record) the voice-over, measure
it, and let each shot's length be `max(planned, voice + padding)`. Every renderer takes
`--duration` and lays its beats out as *fractions* of it. Nothing hardcodes a length.

Get this backwards — animate first, then try to fit words — and every script edit costs a
re-render of everything.

## Workflow

**1. Find the constraints first.** Duration cap, file-size cap, container, minimum height and
frame rate, scan type. Put them in `build.py` and make `build.py check` enforce them. Discovering
a 20 MB limit after rendering is an expensive way to learn it. See `reference/venue-constraints.md`.

**2. Agree the structure before writing any code.** Storyboard in `script.py`: shot id, chapter,
planned seconds, narration. Then run `python script.py` and look at the words-per-second column —
above ~3.2 w/s a line will not fit. For a submission video, results should get roughly twice the
time of methodology; say so explicitly if the author's edits drift from it, because they will.

**3. Inventory the real data before promising a shot.** Walk the repo for the result files,
checkpoints, recordings and tables the film will draw on. A shot you cannot back with a file is a
shot you should not storyboard. List the sources in the spec you hand out.

**4. Scaffold, then prove the assembly path empty.** Copy `scaffold/` into `video/`, run
`build.py shots --placeholders && build.py assemble`, and confirm the deliverable passes
`build.py check` with stub shots. Now the risky part (mux, subtitles, size-targeted encode) is
already known to work, and every later failure is a shot-level failure.

**5. Fan out.** One agent per 2–4 related shots, each handed `reference/shot-spec.md` verbatim
plus its own brief. Give each agent: the exact durations, the data files, what the narration says
over it, and which shared modules it owns. Shared modules are the collision risk — assign each to
exactly one agent per round and require a re-render check of the other shots that import it.

**6. Look at every frame yourself.** Agents report success; frames tell the truth. Extract a tile
sheet per shot (`contactsheet.py --shot s09`) and read it. Send back anything that does not read
at 50 % scale. Review the whole film the same way after assembly — that is where inconsistent
chapter labels, drifting typography and duplicated claims show up.

**7. Assemble, check, and report the constraint table**, not just "done".

## What makes these videos good

* **One idea per shot.** If a shot needs two sentences of explanation, it is two shots.
* **Real data, or nothing.** Compute the number in the shot from the source file and `assert` it
  against the published table. When they disagree — and they will — surface it rather than
  picking the prettier one.
* **Show the honest failure.** A results section that admits its four dangerous cases, or its
  higher miss-rate, is more persuasive than one that does not. Reviewers notice.
* **Motion is for graphics, not for words.** Text appears (opacity only) and never leaves.
  Animated words cost the viewer attention that belongs to the content, and they eat runtime.
* **Semantic colour.** One hue per *role* (ours / baseline / ground truth / danger), fixed across
  the whole film, so the viewer learns the legend once.
* **One typeface.** Sizes and weights may vary; a second sans may not. Math in LaTeX is the
  single exception, and real subscripts always beat `N_req` in ASCII.
* **Silence is fine.** A 2-second hold on a finished frame is how a viewer reads it.

## Narration and subtitles

Offline neural TTS (`piper`) keeps the build deterministic and lets length drive the edit; the
same pipeline accepts hand-recorded wavs dropped into `build/audio/` under the same names.

Ship subtitles both ways: **burned-in** for the submission (reviewers often watch muted, and some
portals strip sidecars) and **sidecar `.srt`/`.vtt`** for YouTube and the project page.

If the author re-records the voice-over after the film is cut, the timings are stale. Do **not**
re-time by hand: `retime_subtitles.py` transcribes the dubbed audio with word-level timestamps and
force-aligns the *written* script to it, so the wording stays authoritative and only the timing
comes from the recogniser. It also detects script text that was never actually spoken (a run of
words with no time to fit in) and reports it rather than crushing it into a gap — that has caught
a genuinely missing sentence.

## Deliverables to hand back

The master, a subtitled variant, `.srt` + `.vtt`, a timecoded narration script, a short
`summary.txt`, and the constraint check output. Plus: every discrepancy you found between the
paper and the repository. Producing the video means reading every number in the paper against its
source, which makes it the best audit the manuscript will get.
