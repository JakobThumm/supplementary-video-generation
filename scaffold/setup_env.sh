#!/usr/bin/env bash
# Create the rendering environment. manim cannot be pip-installed on a bare box (pycairo and
# manimpango need system cairo/pango headers), so conda-forge does the heavy lifting.
set -euo pipefail

ENV_NAME="${ENV_NAME:-video}"

conda create -y -n "$ENV_NAME" -c conda-forge python=3.11 manim ffmpeg
CONDA_BASE="$(conda info --base)"
PY="$CONDA_BASE/envs/$ENV_NAME/bin/python"

"$PY" -m pip install \
    matplotlib scipy pandas \
    opencv-python-headless pillow \
    piper-tts \
    faster-whisper          # only needed if you re-time against a hand-dubbed cut

echo
echo "Add this to your shell (or pass it per command):"
echo "    export VIDEO_ENV=$CONDA_BASE/envs/$ENV_NAME"
echo
echo "Optional, for shots that run your project's own models:"
echo "    export PROJECT_PY=\$PWD/.venv/bin/python"
