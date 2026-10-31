"""studio/tools/generate_thumbnail_canvas.py — High-CTR 4K (3840x2160 / 2160x3840) Ifverse × TED-Ed Thumbnail Generator.

Renders:
  - 16:9 Main Video Thumbnail at 4K (`3840x2160` PNG + `<1.9MB` YouTube Data API JPEG).
  - 9:16 Vertical Shorts/Reels Cover Thumbnail at 4K (`2160x3840` PNG + JPEG).
"""
import argparse, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PALETTES = {
    "ted_ifverse": {"bg_top": (18, 14, 38), "bg_bot": (58, 28, 56), "rim": (255, 201, 130), "gold": (255, 212, 126), "accent": (255, 107, 87), "cyan": (136, 188, 242)},
    "dusk": {"bg_top": (30, 22, 52), "bg_bot": (98, 52, 78), "rim": (255, 198, 138), "gold": (255, 212, 126), "accent": (255, 111, 97), "cyan": (143, 184, 232)},
    "midnight": {"bg_top": (10, 16, 40), "bg_bot": (34, 48, 92), "rim": (184, 200, 255), "gold": (255, 198, 110), "accent": (255, 138, 92), "cyan": (127, 232, 255)},
    "emerald": {"bg_top": (8, 26, 20), "bg_bot": (24, 68, 56), "rim": (143, 255, 224), "gold": (255, 217, 125), "accent": (66, 245, 155), "cyan": (107, 240, 196)},
    "ember": {"bg_top": (28, 10, 12), "bg_bot": (92, 28, 24), "rim": (255, 158, 94), "gold": (255, 184, 77), "accent": (255, 77, 56), "cyan": (255, 210, 160)},
}

def _load_font(size: int, bold: bool = True):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def render_thumbnail(out_path: str, text_hook: str, badge_text: str, aspect: str = "16:9", style: str = "ted_ifverse"):
    pal = PALETTES.get(style, PALETTES["ted_ifverse"])
    vertical = (aspect == "9:16")
    W, H = (2160, 3840) if vertical else (3840, 2160)

    # Create base gradient at 1/4 resolution and resize smoothly for ultra-fast 4K rendering
    gw, gh = W // 4, H // 4
    grad = Image.new("RGB", (gw, gh))
    gpx = grad.load()
    for y in range(gh):
        u = y / max(1, gh - 1)
        r = int(pal["bg_top"][0] * (1 - u) + pal["bg_bot"][0] * u)
        g = int(pal["bg_top"][1] * (1 - u) + pal["bg_bot"][1] * u)
        b = int(pal["bg_top"][2] * (1 - u) + pal["bg_bot"][2] * u)
        for x in range(gw):
            gpx[x, y] = (r, g, b)
    img = grad.resize((W, H), Image.Resampling.BICUBIC).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Blueprint grid overlay on right/top half
    grid_step = 120
    for x in range(0, W, grid_step):
        draw.line([(x, 0), (x, H)], fill=(136, 188, 242, 22), width=2)
    for y in range(0, H, grid_step):
        draw.line([(0, y), (W, y)], fill=(136, 188, 242, 22), width=2)

    # Volumetric radial glow behind subject & text
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow_layer, "RGBA")
    if vertical:
        gdraw.ellipse([W * 0.1, H * 0.32, W * 0.9, H * 0.78], fill=(*pal["accent"], 90))
        gdraw.ellipse([W * 0.15, H * 0.08, W * 0.85, H * 0.42], fill=(*pal["gold"], 75))
    else:
        gdraw.ellipse([W * 0.42, H * 0.12, W * 0.96, H * 0.88], fill=(*pal["accent"], 85))
        gdraw.ellipse([W * 0.02, H * 0.15, W * 0.52, H * 0.95], fill=(*pal["rim"], 70))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=90))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Draw giant Ifverse Stickman Hero Silhouette (`bigFace`) with 4.5px-scaled glowing rim crescent
    hx = int(W * (0.50 if vertical else 0.27))
    hy = int(H * (0.64 if vertical else 0.58))
    hr = int(min(W, H) * (0.31 if vertical else 0.34))

    # Red-orange signature hoodie shoulders
    draw.ellipse([hx - int(hr * 1.32), hy + int(hr * 0.72), hx + int(hr * 1.32), hy + int(hr * 2.35)], fill=(214, 74, 51, 255), outline=pal["rim"], width=14)
    # Rim light crescent around head
    draw.ellipse([hx - hr - 18, hy - hr - 14, hx + hr + 22, hy + hr + 14], fill=(*pal["rim"], 255))
    # Pitch-black silhouette head
    draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(11, 10, 16, 255))

    # Expressive wide awe/shocked eyes + mouth
    for side in (-1, 1):
        ex = hx + int(side * hr * 0.33) + (0 if vertical else int(hr * 0.12))
        ey = hy - int(hr * 0.10)
        er = int(hr * 0.21)
        draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(247, 242, 232, 255))
        pr = int(er * 0.42)
        draw.ellipse([ex - pr + 8, ey - pr - 4, ex + pr + 8, ey + pr - 4], fill=(11, 10, 16, 255))
        # Raised brow
        draw.arc([ex - er, ey - int(er * 1.65), ex + er, ey - int(er * 0.45)], start=200, end=340, fill=(247, 242, 232, 255), width=18)

    mx = hx + (0 if vertical else int(hr * 0.14))
    my = hy + int(hr * 0.38)
    draw.ellipse([mx - int(hr * 0.14), my - int(hr * 0.18), mx + int(hr * 0.14), my + int(hr * 0.18)], outline=(247, 242, 232, 255), width=20)

    # Concentric neural/time shockwave rings around head
    for k in range(1, 4):
        rr_rad = hr + k * int(hr * 0.22)
        draw.arc([hx - rr_rad, hy - rr_rad, hx + rr_rad, hy + rr_rad], start=290, end=70, fill=(*pal["cyan"], max(40, 190 - k * 45)), width=8)

    # High-CTR Hook Typography (2–4 Words)
    words = text_hook.strip().upper().split()
    if len(words) >= 3:
        mid = math.ceil(len(words) / 2)
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [text_hook.strip().upper()]

    font_main = _load_font(int(min(W, H) * (0.115 if vertical else 0.135)), bold=True)
    font_badge = _load_font(int(min(W, H) * 0.055), bold=True)

    tx = int(W * (0.50 if vertical else 0.67))
    ty_start = int(H * (0.20 if vertical else 0.36))
    line_gap = int(min(W, H) * (0.14 if vertical else 0.165))

    for idx, ln in enumerate(lines):
        y_pos = ty_start + idx * line_gap
        color = pal["gold"] if idx == len(lines) - 1 else (255, 248, 238, 255)
        bbox = draw.textbbox((0, 0), ln, font=font_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x_pos = tx - tw // 2
        # Heavy shadow & stroke for instant mobile readability
        for ox, oy in [(-10, 10), (10, 10), (-8, -8), (8, -8), (0, 14)]:
            draw.text((x_pos + ox, y_pos + oy), ln, font=font_main, fill=(0, 0, 0, 235))
        draw.text((x_pos, y_pos), ln, font=font_main, fill=color)

    # Top-Right / Top-Center High-Contrast Metric Badge Pill
    if badge_text:
        b_str = badge_text.strip().upper()
        bb = draw.textbbox((0, 0), b_str, font=font_badge)
        bw, bh = bb[2] - bb[0] + 110, bb[3] - bb[1] + 56
        bx0 = int(W - bw - 90) if not vertical else int((W - bw) / 2)
        by0 = 85 if not vertical else int(H * 0.07)
        draw.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=36, fill=(*pal["accent"], 245), outline=(255, 255, 255, 230), width=6)
        draw.text((bx0 + 55, by0 + 22), b_str, font=font_badge, fill=(255, 255, 255, 255))

    # Cinematic letterbox bars for 16:9
    if not vertical:
        bar_h = int(H * 0.045)
        draw.rectangle([0, 0, W, bar_h], fill=(0, 0, 0, 255))
        draw.rectangle([0, H - bar_h, W, H], fill=(0, 0, 0, 255))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    rgb_out = img.convert("RGB")
    rgb_out.save(out_path, format="PNG", optimize=True)

    # Also save a <1.9MB high-quality JPEG sibling for YouTube Data API v3 (which enforces a 2MB upload cap)
    jpg_path = os.path.splitext(out_path)[0] + ".jpg"
    rgb_out.save(jpg_path, format="JPEG", quality=92, optimize=True)
    print(f"[Thumbnail V3 4K] Rendered {W}x{H} ({aspect}) -> {out_path} & {jpg_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--text", default="1 SEC = 10 SEC")
    ap.add_argument("--badge", default="10x BRAIN")
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--style", default="ted_ifverse")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    render_thumbnail(a.out, a.text, a.badge, a.aspect, a.style)

if __name__ == "__main__":
    main()
