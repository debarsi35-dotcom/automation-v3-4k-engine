"""Cut out a product shot on a pure-white background by flood-filling from the borders (keeps light-grey plastic that
AI mattes eat, e.g. the NES lid). usage: python3 matte_white.py in.jpg out.png [--thr 236] [--maxw 1920]"""
import sys, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('--thr', type=int, default=236); ap.add_argument('--maxw', type=int, default=1920)
a = ap.parse_args()
im = Image.open(a.src).convert('RGB')
if im.width > a.maxw: im = im.resize((a.maxw, round(im.height * a.maxw / im.width)), Image.LANCZOS)
arr = np.asarray(im).astype(int)
m = Image.new('L', im.size, 0); m.putdata(list(((arr.min(axis=2) > a.thr) * 255).astype('uint8').ravel()))
W, H = m.size
for (x, y) in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)]:
    if m.getpixel((x, y)) == 255: ImageDraw.floodfill(m, (x, y), 128)
bg = np.asarray(m) == 128
al = Image.new('L', im.size); al.putdata(list(np.where(bg, 0, 255).astype('uint8').ravel()))
al = al.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
out = im.convert('RGBA'); out.putalpha(al); out = out.crop(al.getbbox()); out.save(a.dst)
print(a.dst, out.size, f'background {bg.mean():.0%}')
