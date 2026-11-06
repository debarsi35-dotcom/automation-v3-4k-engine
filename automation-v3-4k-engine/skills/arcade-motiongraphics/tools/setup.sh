#!/bin/bash
# One-time setup (free, no sudo, ~1.5 GB with torch). Shared with the Motion Graphics V3 skill: both use ~/.cache/motion-graphics-v3,
# so if you already set that one up, this finishes in seconds.
set -e
V="$HOME/.cache/motion-graphics-v3"; mkdir -p "$V/kokoro"
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
[ -x "$V/venv/bin/python" ] || uv venv --python 3.11 "$V/venv"
uv pip install --python "$V/venv/bin/python" kokoro-onnx soundfile numpy scipy pillow playwright torch torchaudio librosa matplotlib faster-whisper
"$V/venv/bin/python" -m playwright install chromium
for f in kokoro-v1.0.onnx voices-v1.0.bin; do [ -f "$V/kokoro/$f" ] || curl -L -o "$V/kokoro/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"; done
ok=1
node -e 'process.exit(+process.versions.node.split(".")[0] >= 22 ? 0 : 1)' 2>/dev/null && echo "node $(node -v) ok" || { echo "need Node 22+ (nodejs.org or brew install node)"; ok=0; }
command -v ffmpeg >/dev/null && echo "ffmpeg ok" || { echo "need ffmpeg (brew install ffmpeg / winget install ffmpeg)"; ok=0; }
[ $ok = 1 ] && echo "All set. Next: source tools/env.sh" || { echo "fix the items above, then run setup.sh again"; exit 1; }
