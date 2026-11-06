"""work/words.json (from align.py) -> assets/words.js (window.WORDS = [{i,t,s,e,l}]) for the film to read cue times.
usage: python3 words_js.py <project>"""
import sys, json
from pathlib import Path
P = Path(sys.argv[1])
w = json.load(open(P / 'work/words.json'))
out = [{'i': x['i'], 't': x['text'], 's': round(x['start'], 3), 'e': round(x['end'], 3), 'l': x['line']} for x in w]
(P / 'assets/words.js').write_text('// generated from work/words.json (wav2vec2 forced alignment of the narration)\nwindow.WORDS = ' + json.dumps(out) + ';\n')
for x in out: print(f"{x['i']:>3} L{x['l']:<2} {x['s']:6.2f} {x['t']}")
