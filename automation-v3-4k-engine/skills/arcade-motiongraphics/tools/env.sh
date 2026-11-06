# ARCADE MOTION GRAPHICS environment: `source ~/.claude/skills/arcade-motiongraphics/tools/env.sh`
export AMG="${AMG:-$HOME/.claude/skills/arcade-motiongraphics}"
pick() { for p in "$@"; do [ -x "$p" ] && { echo "$p"; return; }; done; echo "$HOME/.cache/arcade-motiongraphics/venv/bin/python"; }
export AMG_TTS=$(pick "$HOME/.cache/arcade-motiongraphics/venv/bin/python" "$HOME/.cache/motion-graphics-v3/venv/bin/python" "$HOME/.engaging-carousel/venv/bin/python" "$HOME/.faceless-videos/venv/bin/python")   # kokoro_onnx + soundfile
export AMG_ALIGN=$(pick "$HOME/.cache/arcade-motiongraphics/venv/bin/python" "$HOME/.cache/motion-graphics-v3/venv/bin/python" "$HOME/wx-env/bin/python")                                               # torch + torchaudio + scipy
export AMG_AUDIO=$(pick "$HOME/.cache/arcade-motiongraphics/venv/bin/python" "$HOME/.cache/motion-graphics-v3/venv/bin/python" "$HOME/.one-prompt-mv/venv/bin/python")                                 # numpy + scipy + soundfile (+ librosa/demucs for reference study)
export AMG_STT=$(pick "$HOME/.cache/arcade-motiongraphics/venv/bin/python" "$HOME/.faceless-videos/venv/bin/python")                                                                                    # faster_whisper (checks only)
echo "AMG=$AMG"; echo "tts=$AMG_TTS align=$AMG_ALIGN audio=$AMG_AUDIO stt=$AMG_STT"
