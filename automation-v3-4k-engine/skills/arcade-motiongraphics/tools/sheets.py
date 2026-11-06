"""Contact sheets + per-frame diff for a reference.
usage: python sheets.py <frames_dir> <fps> <out_prefix> [cols] [rows]
Writes <out_prefix>_NN.jpg sheets (every frame, labelled #frame / t) and <out_prefix>_diff.tsv.
"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

d, fps, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 10
rows = int(sys.argv[5]) if len(sys.argv) > 5 else 3
files = sorted(glob.glob(os.path.join(d, "f_*.jpg")))
tw, th = 216, 384
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
except Exception:
    font = ImageFont.load_default()

prev = None
rows_out = []
per = cols * rows
for s in range(0, len(files), per):
    sheet = Image.new("RGB", (cols * tw, rows * th), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    for i, f in enumerate(files[s:s + per]):
        n = s + i + 1
        im = Image.open(f).convert("RGB")
        a = np.asarray(im.resize((90, 160))).astype(np.float32)
        diff = 0.0 if prev is None else float(np.abs(a - prev).mean())
        prev = a
        hsv = np.asarray(im.convert("HSV").resize((90, 160))).astype(np.float32)
        rows_out.append((n, (n - 1) / fps, diff, a.mean(), hsv[..., 1].mean()))
        t = im.resize((tw, th))
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(t, (x, y))
        lab = f"{n} {(n-1)/fps:.2f}s"
        col = (255, 60, 60) if diff > 28 else (255, 255, 0)
        dr.rectangle([x, y, x + 150, y + 26], fill=(0, 0, 0))
        dr.text((x + 3, y + 2), lab, fill=col, font=font)
    sheet.save(f"{out}_{s // per + 1:02d}.jpg", quality=80)

with open(f"{out}_diff.tsv", "w") as fh:
    fh.write("frame\tt\tdiff\tluma\tsat\n")
    for r in rows_out:
        fh.write("%d\t%.3f\t%.1f\t%.1f\t%.1f\n" % r)
print(len(files), "frames,", (len(files) + per - 1) // per, "sheets")
