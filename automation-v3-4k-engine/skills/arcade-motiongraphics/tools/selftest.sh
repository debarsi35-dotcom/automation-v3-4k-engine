#!/bin/bash
# Proves the install works: builds the worked example ("How Mario was born", 30 s, 9:16) end to end on this computer:
# Kokoro voice → word timings → chiptune + effects → mix → HyperFrames render.  ~/arcade-motiongraphics/_selftest  (3–6 min)
set -e
export AMG="${AMG:-$(cd "$(dirname "$0")/.." && pwd)}"
source "$AMG/tools/env.sh" >/dev/null
P="$HOME/arcade-motiongraphics/_selftest"; [ -d "$P" ] && rm -rf "${P:?}"
bash "$AMG/tools/new_film.sh" "$P" "Selftest" >/dev/null
"$AMG_TTS" "$AMG/tools/vo.py" "$P"
"$AMG_ALIGN" "$AMG/tools/align.py" "$P"
python3 "$AMG/tools/words_js.py" "$P" >/dev/null
(cd "$P" && python3 work/make_cues.py)
"$AMG_AUDIO" "$AMG/tools/chip.py" "$P"
python3 "$AMG/tools/mix.py" "$P"
cd "$P" && npx --yes hyperframes@0.8.203 render . -o renders/selftest.mp4 -q delivery >/dev/null
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/selftest.mp4)
ffmpeg -loglevel error -y -i renders/selftest.mp4 -vf "fps=1,scale=216:-1,tile=10x3" -frames:v 1 work/selftest_sheet.jpg
awk -v d="$D" 'BEGIN{exit !(d>25)}' && echo "SELFTEST PASSED: $P/renders/selftest.mp4 (${D}s) · sheet $P/work/selftest_sheet.jpg" || { echo "SELFTEST FAILED"; exit 1; }
