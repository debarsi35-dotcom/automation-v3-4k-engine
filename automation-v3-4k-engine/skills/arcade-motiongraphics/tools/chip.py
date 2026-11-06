"""ARCADE MOTION GRAPHICS — chiptune bed + arcade SFX, synthesised locally (numpy + scipy).
usage: python chip.py <project>      reads work/music.json + work/sfx.json, writes assets/audio/music.wav + sfx.wav

Soft by design (the user's ears): band-limited pulse/triangle voices, low-passed, no hi-hats, no clicks or ticks,
every note has a few-ms attack, a short room reverb rounds everything off.

music.json: {"bpm":120, "offset":0.0, "key_root":"A", "sections":[{"t0":0.75,"t1":5.5,"chords":["Am","F","G","C"],
             "per":"bar"|"half", "parts":["bass","arp","lead","drums","kick"], "lead":"motifA", "transpose":0, "gain":1.0}],
             "lead_motifs": {"motifA": [[note, eighths], ...] per bar}}
sfx.json:   [[time, "name", gain, {params}], ...]  names: see SFX below
"""
import sys, json, math
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
NOTES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(n):
    """'A4' -> 440; also accepts midi ints."""
    if isinstance(n, (int, float)):
        return 440.0 * 2 ** ((n - 69) / 12)
    name, octv = (n[:-1], int(n[-1]))
    return 440.0 * 2 ** ((NOTES[name] + 12 * (octv + 1) - 69) / 12)


def midi(n):
    name, octv = (n[:-1], int(n[-1]))
    return NOTES[name] + 12 * (octv + 1)


def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2 - 100) / (SR / 2), 'low', output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f / (SR / 2), 'high', output='sos'), x)


def bp(x, f0, f1, order=2):
    return sosfilt(butter(order, [f0 / (SR / 2), min(f1, SR / 2 - 100) / (SR / 2)], 'band', output='sos'), x)


def env(n, a=0.006, d=0.08, s=0.6, r=0.06, dur=None):
    """ADSR over n samples; release happens inside n."""
    t = np.arange(n) / SR
    dur = dur if dur is not None else n / SR
    e = np.ones(n) * s
    ai = t < a
    e[ai] = t[ai] / max(a, 1e-4)
    di = (t >= a) & (t < a + d)
    e[di] = 1 - (1 - s) * (t[di] - a) / max(d, 1e-4)
    ri = t > dur - r
    e[ri] *= np.clip((dur - t[ri]) / max(r, 1e-4), 0, 1)
    return e


def pulse(f, dur, duty=0.25, vib=0.0, glide=None, hmax=7000):
    """band-limited pulse by additive synthesis (no aliasing = no fizz)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = np.full(n, float(f))
    if glide is not None:
        fr = f * (glide / f) ** (t / dur)
    if vib:
        fr = fr * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.12) / 0.15, 0, 1))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    out = np.zeros(n)
    k = 1
    while k * f < hmax and k < 40:
        out += (2 / (k * np.pi)) * np.sin(np.pi * k * duty) * np.cos(k * ph)
        k += 1
    return out


def tri(f, dur, glide=None, hmax=5000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = np.full(n, float(f)) if glide is None else f * (glide / f) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    out = np.zeros(n)
    k = 1
    while k * f < hmax and k < 25:
        out += ((-1) ** ((k - 1) // 2)) * np.sin(k * ph) / (k * k)
        k += 2
    return out * (8 / np.pi ** 2)


def sine(f, dur, glide=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = np.full(n, float(f)) if glide is None else f * (glide / f) ** (t / dur)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR)


def noise(dur, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, int(dur * SR))


def add(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * g


def room(x, mix=0.16, length=0.9, seed=3):
    ir = noise(length, seed) * np.exp(-np.arange(int(length * SR)) / SR / (length / 5.5))
    ir = lp(ir, 5200)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 1.6


# ---------------------------------------------------------------- chords
QUAL = {'': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11], 'm7': [0, 3, 7, 10], 'sus4': [0, 5, 7], 'sus2': [0, 2, 7]}


def chord(name, tr=0):
    root = name[:2] if len(name) > 1 and name[1] in '#b' else name[:1]
    q = name[len(root):]
    r = NOTES[root] + tr
    return r, QUAL[q]


# ---------------------------------------------------------------- music
def render_music(cfg, dur):
    bpm = cfg.get('bpm', 120)
    beat = 60 / bpm
    e8 = beat / 2
    out = np.zeros(int(dur * SR) + SR)
    layers = {k: np.zeros_like(out) for k in ('bass', 'arp', 'lead', 'drums', 'pad')}
    motifs = cfg.get('lead_motifs', {})
    for sec in cfg['sections']:
        t0, t1, tr = sec['t0'], sec['t1'], sec.get('transpose', 0)
        g = sec.get('gain', 1.0)
        per = 4 * beat if sec.get('per', 'bar') == 'bar' else 2 * beat
        parts = sec['parts']
        chords = sec['chords']
        n_slots = int(math.ceil((t1 - t0) / per - 1e-6))
        for si in range(n_slots):
            cs = t0 + si * per
            ce = min(t1, cs + per)
            root, iv = chord(chords[si % len(chords)], tr)
            # bass: triangle 8ths root / octave / fifth
            if 'bass' in parts or 'bass_half' in parts:
                step = e8 if 'bass' in parts else beat
                pat = [0, 12, 0, 12, 7, 12, 0, 12] if 'bass' in parts else [0, 7, 12, 7]
                k = 0
                tt = cs
                while tt < ce - 1e-6:
                    m = 36 + root + pat[k % len(pat)]
                    d = min(step * 0.9, ce - tt)
                    x = tri(hz(m), d) * env(int(d * SR), 0.004, 0.06, 0.7, 0.03)
                    add(layers['bass'], x, tt, 0.55 * g)
                    tt += step
                    k += 1
            # arp: 16th chord tones, quiet pulse 12.5%
            if 'arp' in parts or 'arp_slow' in parts:
                step = e8 / 2 if 'arp' in parts else e8
                seq = [iv[i % len(iv)] + 12 * (i // len(iv)) for i in range(len(iv) * 2)]
                seq = seq + seq[-2:0:-1]
                k = 0
                tt = cs
                while tt < ce - 1e-6:
                    m = 60 + root + seq[k % len(seq)]
                    d = min(step * 0.85, ce - tt)
                    x = pulse(hz(m), d, 0.125, hmax=4500) * env(int(d * SR), 0.003, 0.04, 0.35, 0.02)
                    add(layers['arp'], x, tt, 0.16 * g)
                    tt += step
                    k += 1
            # pad: soft triangle chord, sustained (breakdowns)
            if 'pad' in parts:
                for i, v in enumerate(iv[:3]):
                    x = tri(hz(60 + root + v), ce - cs) * env(int((ce - cs) * SR), 0.25, 0.3, 0.8, 0.3)
                    add(layers['pad'], x, cs, 0.12 * g)
            # drums: soft kick on 1 & 3, soft snare on 2 & 4 (no hats)
            if 'drums' in parts or 'kick' in parts:
                nb = int(round((ce - cs) / beat))
                for b in range(nb):
                    bt = cs + b * beat
                    if b % 2 == 0:
                        k_ = sine(110, 0.2, glide=42) * np.exp(-np.arange(int(0.2 * SR)) / SR / 0.06)
                        k_ *= np.clip(np.arange(len(k_)) / (0.003 * SR), 0, 1)
                        add(layers['drums'], k_, bt, 0.62 * g)
                    elif 'drums' in parts:
                        sn = bp(noise(0.16, int(bt * 100)), 900, 3800) * np.exp(-np.arange(int(0.16 * SR)) / SR / 0.045)
                        sn += 0.35 * tri(190, 0.16) * np.exp(-np.arange(int(0.16 * SR)) / SR / 0.05)
                        sn *= np.clip(np.arange(len(sn)) / (0.002 * SR), 0, 1)
                        add(layers['drums'], sn, bt, 0.2 * g)
        # lead motif: one bar list per chord slot, 8ths
        if sec.get('lead') and 'lead' in parts:
            mot = motifs[sec['lead']]
            tt = t0
            bi = 0
            while tt < t1 - 1e-6:
                bar = mot[bi % len(mot)]
                bt = tt
                for note, n8 in bar:
                    d = n8 * e8
                    if note != '.' and bt < t1:
                        dd = min(d * 0.92, t1 - bt)
                        m = midi(note) + tr
                        x = pulse(hz(m), dd, 0.25, vib=0.012, hmax=6000) * env(int(dd * SR), 0.008, 0.1, 0.62, 0.06)
                        add(layers['lead'], x, bt, 0.24 * g)
                        if sec.get('double'):
                            add(layers['lead'], pulse(hz(m - 12), dd, 0.5, hmax=3000) * env(int(dd * SR), 0.008, 0.1, 0.5, 0.06), bt, 0.09 * g)
                    bt += d
                tt += 4 * beat
                bi += 1
    mixd = (lp(layers['bass'], 1600) + lp(layers['arp'], 5000) + lp(layers['lead'], 5600) + lp(layers['drums'], 7000) + lp(layers['pad'], 2800))
    mixd = hp(mixd, 35)
    mixd = room(mixd, 0.18)
    return mixd[: int(dur * SR)]


# ---------------------------------------------------------------- SFX library (all soft)
def s_thump(p):
    d = 0.32
    x = sine(p.get('f', 95), d, glide=p.get('to', 40)) * np.exp(-np.arange(int(d * SR)) / SR / 0.08)
    return x * np.clip(np.arange(len(x)) / (0.004 * SR), 0, 1)


def s_whoosh(p):
    d = p.get('d', 0.45)
    n = noise(d, p.get('seed', 1))
    t = np.arange(len(n)) / SR
    out = np.zeros_like(n)
    f0, f1 = p.get('f0', 300), p.get('f1', 2400)
    seg = 8
    for i in range(seg):
        a, b = int(i * len(n) / seg), int((i + 1) * len(n) / seg)
        fc = f0 * (f1 / f0) ** ((i + 0.5) / seg)
        out[a:b] = bp(n, fc * 0.6, fc * 1.4)[a:b]
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return lp(out * shape, 5000) * 1.4


def s_blip(p):
    d = p.get('d', 0.07)
    x = tri(p.get('f', 660), d) * env(int(d * SR), 0.004, 0.02, 0.6, 0.03)
    return lp(x, 3000)


def s_coin(p):
    a = pulse(hz(p.get('n1', 'A5')), 0.075, 0.5, hmax=5000) * env(int(0.075 * SR), 0.003, 0.02, 0.8, 0.01)
    b = pulse(hz(p.get('n2', 'E6')), 0.42, 0.5, hmax=5000) * np.exp(-np.arange(int(0.42 * SR)) / SR / 0.12)
    b *= np.clip(np.arange(len(b)) / (0.003 * SR), 0, 1)
    return lp(np.concatenate([a, b]), 5200) * 0.8


def s_jump(p):
    d = p.get('d', 0.2)
    x = pulse(p.get('f0', 260), d, 0.5, glide=p.get('f1', 820), hmax=4000) * env(int(d * SR), 0.004, 0.05, 0.7, 0.05)
    return lp(x, 3200) * 0.8


def s_drop(p):
    d = p.get('d', 0.22)
    x = tri(p.get('f0', 1300), d, glide=p.get('f1', 380)) * env(int(d * SR), 0.004, 0.05, 0.7, 0.05)
    return lp(x, 3000)


def s_arp(p):      # notes list played quickly (power-up / item get / fanfares)
    notes, step = p['notes'], p.get('step', 0.06)
    hold = p.get('hold', step * 0.9)
    total = step * (len(notes) - 1) + hold + 0.05
    out = np.zeros(int(total * SR))
    for i, n in enumerate(notes):
        x = pulse(hz(n), hold, p.get('duty', 0.25), vib=p.get('vib', 0), hmax=5000) * env(int(hold * SR), 0.004, 0.04, 0.6, 0.04)
        x = x + 0.5 * tri(hz(n) / 2, hold) * env(int(hold * SR), 0.004, 0.04, 0.6, 0.04)
        add(out, x, i * step)
    return lp(out, 5000) * 0.7


def s_pop(p):
    d = 0.09
    x = sine(p.get('f', 900), d, glide=p.get('to', 260)) * env(int(d * SR), 0.003, 0.03, 0.5, 0.04)
    return x


def s_rumble(p):   # shutter: low noise with slat ripple
    d = p.get('d', 0.3)
    n = lp(noise(d, p.get('seed', 4)), 500)
    t = np.arange(len(n)) / SR
    rip = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * p.get('rate', 26) * t))
    return lp(n * rip, 900) * np.sin(np.pi * np.clip(t / d, 0, 1)) * 2.4


def s_glitch(p):   # soft: low-passed noise + falling blip, no fizz
    d = p.get('d', 0.14)
    n = lp(noise(d, 9), 1800) * np.exp(-np.arange(int(d * SR)) / SR / 0.05)
    b = tri(700, d, glide=180) * env(int(d * SR), 0.003, 0.03, 0.5, 0.04)
    return n * 0.8 + b * 0.5


def s_sweep(p):    # rising counter sweep instead of ticks
    d = p.get('d', 0.6)
    x = tri(p.get('f0', 220), d, glide=p.get('f1', 880))
    t = np.arange(len(x)) / SR
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 14 * t)
    return lp(x * trem * env(len(x), 0.02, 0.1, 0.8, 0.12), 2800) * 0.8


def s_shimmer(p):
    notes = p.get('notes', ['C6', 'E6', 'G6', 'C7', 'E7'])
    return s_arp({'notes': notes, 'step': p.get('step', 0.05), 'hold': 0.18, 'duty': 0.125}) * 0.5


def s_gameover(p):
    return s_arp({'notes': p.get('notes', ['E5', 'C5', 'A4', 'E4']), 'step': 0.16, 'hold': 0.24, 'duty': 0.5, 'vib': 0.01})


def s_lock(p):
    return np.concatenate([s_blip({'f': 640, 'd': 0.06}), s_blip({'f': 960, 'd': 0.09})]) * 0.9


def s_hit(p):       # big super hit: thump + bright soft chord stab
    th = s_thump({'f': 120, 'to': 45})
    st = sum(pulse(hz(n), 0.3, 0.25, hmax=4000) for n in p.get('notes', ['C5', 'E5', 'G5'])) * np.exp(-np.arange(int(0.3 * SR)) / SR / 0.09)
    st = lp(st, 3200) * 0.22
    out = np.zeros(max(len(th), len(st)))
    out[: len(th)] += th
    out[: len(st)] += st
    return out


def s_crt(p):       # CRT power-on: soft rising hum + whoosh
    d = 0.5
    h = sine(55, d, glide=110) * env(int(d * SR), 0.01, 0.1, 0.6, 0.2) * 0.6
    w = s_whoosh({'d': 0.4, 'f0': 200, 'f1': 3000})
    out = np.zeros(int(d * SR))
    out += h
    out[: len(w)] += w * 0.5
    return out


SFX = {'thump': s_thump, 'whoosh': s_whoosh, 'blip': s_blip, 'coin': s_coin, 'jump': s_jump, 'drop': s_drop, 'arp': s_arp, 'pop': s_pop,
       'rumble': s_rumble, 'glitch': s_glitch, 'sweep': s_sweep, 'shimmer': s_shimmer, 'gameover': s_gameover, 'lock': s_lock, 'hit': s_hit, 'crt': s_crt}


def render_sfx(cues, dur):
    out = np.zeros(int(dur * SR) + 2 * SR)
    for c in cues:
        t, name, g = c[0], c[1], c[2]
        p = c[3] if len(c) > 3 else {}
        add(out, SFX[name](p), t, g)
    out = room(out, 0.12, 0.6, 7)
    return out[: int(dur * SR)]


def main():
    P = Path(sys.argv[1])
    dur = float(json.load(open(P / 'work/music.json')).get('duration', 30.0))
    music = render_music(json.load(open(P / 'work/music.json')), dur)
    sfx = render_sfx(json.load(open(P / 'work/sfx.json')), dur)
    for name, x in (('music', music), ('sfx', sfx)):
        x = x / (np.abs(x).max() + 1e-9) * 0.7
        sf.write(P / f'assets/audio/{name}.wav', np.stack([x, x], 1).astype(np.float32), SR)
        print(name, f'{len(x) / SR:.2f}s')


if __name__ == '__main__':
    main()
