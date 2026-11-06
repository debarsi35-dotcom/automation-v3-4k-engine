"""Narration with Kokoro-82M (local, Apache-2.0). Reads work/script.json, writes assets/audio/vo.wav and
work/vo_lines.json (each line's start/end in the file). usage: vo.py <project> [--voice am_michael] [--test "text"]"""
import sys, json, argparse
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
K = next((d for d in [Path.home() / x / 'kokoro' for x in ('.cache/motion-graphics-v3', '.engaging-carousel', '.faceless-videos', '.vox-style-video')]
          if (d / 'kokoro-v1.0.onnx').exists()), Path.home() / '.cache/motion-graphics-v3/kokoro')
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--voice'); ap.add_argument('--test'); ap.add_argument('--speed', type=float)
a = ap.parse_args(); P = Path(a.project)
cfg = json.load(open(P / 'work/script.json'))
voice = a.voice or cfg['voice']; speed = a.speed or cfg['speed']
k = Kokoro(str(K / 'kokoro-v1.0.onnx'), str(K / 'voices-v1.0.bin'))
lang = 'en-gb' if voice[0] == 'b' else 'en-us'
if a.test:
    au, sr = k.create(a.test, voice=voice, speed=speed, lang=lang); sf.write(P / 'work/test.wav', au, sr); print('work/test.wav'); sys.exit()
parts, meta, sr, t = [], [], 24000, 0.0
lead = np.zeros(int(cfg['lead'] * sr)); parts.append(lead); t += cfg['lead']
for shown, spoken in cfg['lines']:
    au, sr = k.create(spoken.replace("_", " "), voice=voice, speed=speed, lang=lang)
    # trim leading/trailing near-silence so gaps are ours
    idx = np.where(np.abs(au) > 0.01)[0]; au = au[max(0, idx[0] - 240): idx[-1] + 1200]
    meta.append({'text': shown, 'start': round(t, 3), 'end': round(t + len(au) / sr, 3)})
    parts.append(au); t += len(au) / sr
    g = cfg['gap'] + (0.12 if shown.rstrip().endswith('.') else 0)
    parts.append(np.zeros(int(g * sr))); t += g
out = np.concatenate(parts).astype(np.float32)
out = out / max(1e-6, np.abs(out).max()) * 0.89
sf.write(P / 'assets/audio/vo.wav', out, sr)
json.dump(meta, open(P / 'work/vo_lines.json', 'w'), indent=1)
print(f'{voice} x{speed}: {t:.2f}s, {len(meta)} lines')
