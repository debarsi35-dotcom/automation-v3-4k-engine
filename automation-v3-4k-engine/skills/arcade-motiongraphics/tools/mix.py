"""Mix narration + chiptune bed + SFX into assets/audio/mix.wav (local ffmpeg).
usage: python mix.py <project> [--bed -10] [--sfx -7]   (dB relative to the voice's loudness)
The bed ducks ~4 dB under the voice (sidechain), soft shelf above 7 kHz, limiter, loudnorm -15 LUFS / -1.2 dBTP.
"""
import sys, json, re, subprocess, argparse
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--bed', type=float, default=-10); ap.add_argument('--sfx', type=float, default=-7)
a = ap.parse_args(); P = Path(a.project); au = P / 'assets/audio'

def lufs(f):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(f), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])

lv, lm, ls = lufs(au / 'vo.wav'), lufs(au / 'music.wav'), lufs(au / 'sfx.wav')
gv = -16 - lv; gm = (-16 + a.bed) - lm; gs = (-16 + a.sfx) - ls
print(f'vo {lv:.1f}  music {lm:.1f}  sfx {ls:.1f} LUFS -> gains {gv:+.1f} {gm:+.1f} {gs:+.1f} dB')
fc = (f"[0:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume={gv:.2f}dB,asplit=2[v][vsc];"
      f"[1:a]volume={gm:.2f}dB[m];[m][vsc]sidechaincompress=threshold=0.03:ratio=3:attack=25:release=350:makeup=1[md];"
      f"[2:a]volume={gs:.2f}dB[s];"
      f"[v][md][s]amix=inputs=3:normalize=0,highshelf=f=7000:g=-2,alimiter=limit=0.89:level=false,"
      f"loudnorm=I=-15:TP=-1.2:LRA=9,aresample=48000[out]")
cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(au / 'vo.wav'), '-i', str(au / 'music.wav'), '-i', str(au / 'sfx.wav'),
       '-filter_complex', fc, '-map', '[out]', '-t', str(json.load(open(P / 'work/music.json')).get('duration', 30)), '-ar', '48000', str(au / 'mix.wav')]
subprocess.run(cmd, check=True)
print('mix', lufs(au / 'mix.wav'), 'LUFS')
