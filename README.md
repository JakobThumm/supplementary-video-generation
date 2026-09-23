# supplementary-video-generation

A [Claude Code](https://claude.com/claude-code) skill for producing **narrated supplementary
videos for research papers** — conference submission videos, project-page explainers, demo reels
— built from a repository's own data and assembled by a reproducible script.

It was extracted from the production of a real 3-minute robotics conference submission video and
keeps the parts that generalise: the pipeline, the shot contract, and the bugs.

## What it gives you

* **A narration-first pipeline.** Synthesise the voice-over, measure it, and derive every shot's
  length from it. Renderers take `--duration` and lay their beats out as fractions of it, so
  editing a sentence never breaks a layout.
* **A shot contract** (`reference/shot-spec.md`) strict enough to hand to several agents at once
  and still get a film that looks like one system.
* **A working scaffold** (`scaffold/`): orchestrator, storyboard, style module, exact-duration
  frame writer, offline TTS, subtitle generation, contact sheets, and a re-timer that re-syncs
  subtitles after a human re-records the narration.
* **The gotchas** (`reference/gotchas.md`) — manim collapsing word spaces below font_size 40,
  libass rendering SRT at 288 p, VAD silently eating a sentence of speech, and a dozen others.

## Install

```bash
git clone https://github.com/JakobThumm/supplementary-video-generation \
          ~/.claude/skills/supplementary-video-generation
```

Then ask Claude Code for a paper video and the skill loads itself. Or invoke it directly with
`/supplementary-video-generation`.

## Use

```bash
cp -r ~/.claude/skills/supplementary-video-generation/scaffold video   # into your paper's repo
bash video/setup_env.sh                                                # conda env with manim + ffmpeg
export VIDEO_ENV=$(conda info --base)/envs/video

$VIDEO_ENV/bin/python video/build.py all
```

Edit `video/script.py` to change what is said; everything downstream follows.

```bash
python video/build.py narrate          # re-synthesise, re-check the time budget
python video/build.py shots            # re-render only what moved
python video/build.py assemble         # mux, subtitle, size-targeted encode
python video/build.py check            # verify the venue's constraints
```

If the narration is later re-recorded by hand:

```bash
python video/retime_subtitles.py --video video/out/final_dubbed.mp4
```

which transcribes the dub, force-aligns your written script to it, and re-emits the script table
plus YouTube-ready `.srt`, `.vtt` and a plain transcript.

## Requirements

Python ≥ 3.10, ffmpeg ≥ 6, and a conda-forge environment for manim (`scaffold/setup_env.sh`
builds it — manim cannot be pip-installed on a bare box because `pycairo`/`manimpango` need
system cairo and pango headers). `faster-whisper` is only needed for re-timing.

## Licence

MIT. See [LICENSE](LICENSE).
