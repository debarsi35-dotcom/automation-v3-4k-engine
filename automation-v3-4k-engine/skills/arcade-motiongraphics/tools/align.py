"""Exact word timings for the narration: wav2vec2 forced alignment of the KNOWN script, line by line (local).
usage: ~/wx-env/bin/python align.py <project>
Needs work/script.json (shown/spoken pairs; '_' joins spoken words that make one shown word) and work/vo_lines.json
(the line windows vo.py wrote). Writes work/words.json: [{i, text, line, start, end}] in SHOWN words.
"""
import sys, json, re
from pathlib import Path
import torch, torchaudio, numpy as np
from scipy.io import wavfile

P = Path(sys.argv[1])
cfg = json.load(open(P / 'work/script.json'))
lines = json.load(open(P / 'work/vo_lines.json'))
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model().eval()
labels = bundle.get_labels()            # ('-', '|', 'E', 'T', ...)
idx = {c: i for i, c in enumerate(labels)}
sr, wav = wavfile.read(P / 'assets/audio/vo.wav'); wav = wav.astype('float32')
if wav.ndim > 1: wav = wav.mean(1)
wav = torchaudio.functional.resample(torch.from_numpy(wav), sr, bundle.sample_rate).numpy(); sr = bundle.sample_rate

DIG = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'}
def letters(w):
    w = re.sub(r'\d', lambda m: DIG[m.group()], w.upper().replace('-', ' '))
    return [c for c in re.sub(r'[^A-Z\' ]', '', w).replace(' ', "") if c in idx]

out, n = [], 0
for li, ((shown, spoken), L) in enumerate(zip(cfg['lines'], lines)):
    a0 = max(0, L['start'] - 0.08); a1 = L['end'] + 0.08
    chunk = torch.from_numpy(wav[int(a0 * sr): int(a1 * sr)]).unsqueeze(0)
    with torch.inference_mode():
        em, _ = model(chunk)
        em = torch.log_softmax(em, dim=-1)
    groups = spoken.split()
    words = []          # flat spoken words with their group index
    for gi, g in enumerate(groups):
        for p in g.split('_'):
            L_ = letters(p)
            if L_: words.append((gi, L_))
    seq = []
    for k, (gi, L_) in enumerate(words):
        seq += [idx[c] for c in L_]
        if k < len(words) - 1: seq.append(idx['|'])
    targets = torch.tensor([seq], dtype=torch.int32)
    ali, scores = torchaudio.functional.forced_align(em, targets, blank=0)
    ali = ali[0].tolist()
    fps = em.shape[1] / ((a1 - a0))
    toks = torchaudio.functional.merge_tokens(torch.tensor(ali), torch.zeros(len(ali)))
    # toks are in target order
    wstart, wend, k, tk = [], [], 0, 0
    for (gi, L_) in words:
        first = toks[tk]; last = toks[tk + len(L_) - 1]
        wstart.append(first.start / fps + a0); wend.append(last.end / fps + a0)
        tk += len(L_)
        if tk < len(toks) and labels[toks[tk].token] == '|': tk += 1
    for gi, sw in enumerate(shown.split()):
        ks = [k for k, (g, _) in enumerate(words) if g == gi]
        s = wstart[ks[0]] if ks else (out[-1]['end'] if out else L['start'])
        e = wend[ks[-1]] if ks else s + 0.15
        out.append({'i': n, 'text': sw, 'line': li, 'start': round(s, 3), 'end': round(e, 3)}); n += 1
json.dump(out, open(P / 'work/words.json', 'w'), indent=0)
for li in range(len(cfg['lines'])):
    print(li, ' '.join(f"{w['i']}:{w['text']}@{w['start']:.2f}" for w in out if w['line'] == li))
