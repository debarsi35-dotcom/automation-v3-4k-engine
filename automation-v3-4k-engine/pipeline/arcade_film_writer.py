"""pipeline/arcade_film_writer.py — Dynamic film.js Generator for Arcade Motion Graphics.

Translates script.json and words.json into a seek-safe, deterministic film.js
driven by kit/arcade.js, GSAP timelines, pixel typography, and the arcade HUD.
"""
import sys, json
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def generate_film_js(project_dir: Path, story: dict):
    words_path = project_dir / "work/words.json"
    if not words_path.exists():
        raise FileNotFoundError(f"Missing {words_path}. Run align.py first.")

    words = json.load(open(words_path, encoding="utf-8"))
    title = story.get("title", "Arcade Story")
    hero_label = story.get("hero_label", "PLAYER 1")
    hero_color = story.get("hero_color", "#E2311D")

    # Group words by line
    line_words = {}
    for w in words:
        l = w["line"]
        line_words.setdefault(l, []).append(w)

    total_duration = words[-1]["end"] + 1.2 if words else 30.0

    js_code = f"""/* "{title}" — ARCADE MOTION GRAPHICS (9:16 vertical short).
 * Pure function of time FILM.render(ctx, t). Word cues from WORDS.
 */
(function () {{
  const {{ W, H, clamp, lerp, pr, E, rnd, stepT, snap }} = A;
  const w = (i) => WORDS[i] ? WORDS[i].s : 0, we = (i) => WORDS[i] ? WORDS[i].e : 0;
  const IMG = (window.IMG = {{}});
  const F = (window.FILM = {{ DUR: {total_duration:.2f} }});

  // ================================================================ Sprites & Palette
  const PAL = {{
    R: '{hero_color}', B: '#2D5BDA', S: '#FFBA8C', H: '#5A2A0E',
    K: '#16080A', Y: '#FFD23A', W: '#FFFFFF', G: '#1E5A3C'
  }};

  const CAP = ['.....RRRRR......', '....RRRRRRRRR...'];
  const HEAD = ['....HHHSSKS.....', '...HSHSSSKSSS...', '...HSHHSSSSSSSS.', '...HHSSSSSSSSS..', '.....SSSSSSSS...'];
  const BODY = ['.....RRBRRR.....', '....RRRBRRBRRR..', '...RRRRBBBBRRRR.', '...SSRBYBBYBRSS.', '...SSSBBBBBBSSS.', '...SSBBBBBBBBSS.'];
  const LEGS_A = ['.....BBB..BBB...', '....HHH....HHH..', '...HHHH....HHHH.'];
  const LEGS_B = ['......BBBBB.....', '......HHHHH.....', '.....HHHHHH.....'];
  const LEGS_J = ['..BBBB....BBB...', '.HHH.......HHH..', '.HH.........HHH.'];

  function buildHero(legs) {{
    const legRows = legs === 'j' ? LEGS_J : legs === 'b' ? LEGS_B : LEGS_A;
    return [...CAP, ...HEAD, ...BODY, ...legRows];
  }}

  A.defSprite('hero_idle', buildHero('a'), PAL);
  A.defSprite('hero_run', buildHero('b'), PAL);
  A.defSprite('hero_jump', buildHero('j'), PAL);

  A.defSprite('cab', [
    '..KKKKKKKKKK..', '.KMMMMMMMMMMK.', '.KMYMYMMYMYMK.', '.KMMMMMMMMMMK.', '.KKKKKKKKKKKK.', '.KRKKKKKKKKRK.',
    '.KRKSSSSSSKRK.', '.KRKSLSSSSKRK.', '.KRKSSSSLSKRK.', '.KRKSSSSSSKRK.', '.KRKSSLSSSKRK.', '.KRKKKKKKKKRK.',
    'KRRRRRRRRRRRRK', 'KRWRRRRYRRORRK', 'KKKKKKKKKKKKKK', '.KRRRRRRRRRRK.', '.KRRKKKKKKRRK.', '.KRRKYKKYKRRK.',
    '.KRRKKKKKKRRK.', '.KRRRRRRRRRRK.', '.KRRRRRRRRRRK.', '.KRRRRRRRRRRK.', '.KKKKKKKKKKKK.',
  ], {{ K: '#120A14', M: '#2B4FD8', Y: '#FFD23A', R: '{hero_color}', S: '#3B9BFF', L: '#B9E6FF', W: '#F2F2F2', O: '#3B9BFF' }});

  function coin(ctx, x, y, s, ph) {{
    const wds = [8, 6, 2, 6], wd = wds[Math.floor(ph * 4) % 4], h = 14;
    const X = Math.round(x - (wd * s) / 2), Y = Math.round(y - (h * s) / 2);
    ctx.fillStyle = '#3A2304'; ctx.fillRect(X - s, Y + s, (wd + 2) * s, (h - 2) * s); ctx.fillRect(X, Y, wd * s, h * s);
    ctx.fillStyle = '#FFC928'; ctx.fillRect(X + (wd > 2 ? s : 0), Y + s, Math.max(1, wd - (wd > 2 ? 2 : 0)) * s, (h - 2) * s);
    if (wd > 2) {{ ctx.fillStyle = '#FFF3A0'; ctx.fillRect(X + s, Y + 2 * s, s, (h - 4) * s); ctx.fillStyle = '#D9860E'; ctx.fillRect(X + (wd - 2) * s, Y + 2 * s, s, (h - 4) * s); }}
  }}

  // ================================================================ Cached Textures
  let L = null;
  function build() {{
    L = {{}};
    const sk = A.canvas(180, 100), x = sk.getContext('2d');
    for (let i = 0, px = -4; px < 184; i++) {{
      const bw = 8 + Math.floor(rnd(i * 3.1) * 16), bh = 26 + Math.floor(rnd(i * 7.3 + 2) * 70);
      x.fillStyle = '#40B4E1'; x.fillRect(px, 100 - bh, bw, bh);
      x.fillStyle = '#76D3F2';
      for (let yy = 100 - bh + 3; yy < 98; yy += 4) for (let xx = px + 2; xx < px + bw - 1; xx += 3) if (rnd(xx * 13 + yy * 7) > 0.5) x.fillRect(xx, yy, 1, 2);
      px += bw + Math.floor(rnd(i * 5.7) * 3);
    }}
    L.skyline = sk;
    L.clouds = [0, 1, 2, 3, 4, 5].map((i) => A.makeCloud(i * 13 + 5, 30 + Math.floor(rnd(i * 2.2) * 22), 15 + Math.floor(rnd(i * 4.4) * 6)));
    L.heat = A.halftone('#F06A1E', '#C2260E', 'rgba(255,214,120,0.22)', 18);
    L.graph = A.graph('#0F1433', '#18204C', 54);
    L.wood = A.stripes('#A65C28', '#7C3D17', 42);
  }}

  // ================================================================ Master HUD
  function drawHUD(ctx, t) {{
    const p = clamp(t / F.DUR, 0, 1);
    ctx.save();
    // Top HUD Bar Background
    ctx.fillStyle = 'rgba(0,0,0,0.75)';
    ctx.fillRect(36, 40, W - 72, 84);
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 4;
    ctx.strokeRect(36, 40, W - 72, 84);

    // Life / Health Bar (Story Progress)
    ctx.font = '22px "Press Start 2P", monospace';
    ctx.fillStyle = '#FFBA8C';
    ctx.fillText('HP', 56, 92);
    ctx.fillStyle = '#220808';
    ctx.fillRect(110, 64, 320, 36);
    const hpWidth = Math.round(312 * p);
    ctx.fillStyle = p > 0.85 ? '#FFD23A' : '{hero_color}';
    ctx.fillRect(114, 68, hpWidth, 28);

    // Level Indicator
    ctx.fillStyle = '#FFFFFF';
    const stage = t < 10 ? 'LVL 1' : t < 20 ? 'LVL 2' : 'BOSS';
    ctx.fillText(stage, 460, 92);

    // Coin / Score Counter
    coin(ctx, 680, 82, 3, t * 4);
    ctx.fillStyle = '#FFD23A';
    const scoreVal = Math.floor(p * 9990);
    ctx.fillText('x' + String(scoreVal).padStart(4, '0'), 710, 92);

    // Player Badge
    ctx.fillStyle = '#40B4E1';
    ctx.fillText('{hero_label}', 860, 92);
    ctx.restore();
  }}

  // ================================================================ Master Render Loop
  F.render = function (ctx, t) {{
    if (!L) build();
    ctx.clearRect(0, 0, W, H);

    // Background World
    if (t < 9.0) {{
      // World 1: The Origin Problem (Navy graph)
      ctx.drawImage(L.graph, 0, 0, W, H);
      // Skyline at bottom
      ctx.drawImage(L.skyline, 0, H - 400, W, 400);
    }} else if (t < 20.0) {{
      // World 2: The Struggle & Level Up (Warm Heat Halftone)
      ctx.drawImage(L.heat, 0, 0, W, H);
    }} else {{
      // World 3: The Climax & Win (Deep wood / arcade cabinet glow)
      ctx.drawImage(L.wood, 0, 0, W, H);
      A.drawSpr(ctx, 'cab', 320, 680, 24);
    }}

    // Animated Hero
    const heroFrame = Math.floor(t * 8) % 2 === 0 ? 'hero_idle' : 'hero_run';
    const heroY = snap(H - 480 + Math.sin(t * 6) * 12, 4);
    A.drawSpr(ctx, t > 21 ? 'hero_jump' : heroFrame, 440, heroY, 14);

    // Dynamic Word Pop Typography
    let activeWord = null;
    for (let i = 0; i < WORDS.length; i++) {{
      if (t >= WORDS[i].s && t <= WORDS[i].e + 0.15) {{
        activeWord = WORDS[i];
        break;
      }}
    }}

    if (activeWord) {{
      ctx.save();
      ctx.font = '48px "Bungee", "Press Start 2P", sans-serif';
      ctx.textAlign = 'center';
      const text = activeWord.t.toUpperCase();
      // Drop shadow
      ctx.fillStyle = '#000000';
      ctx.fillText(text, W / 2 + 6, 426);
      // Neon/Gold fill
      ctx.fillStyle = '#FFD23A';
      ctx.fillText(text, W / 2, 420);
      ctx.restore();
    }}

    // Dialog RPG Box at Bottom
    ctx.save();
    ctx.fillStyle = 'rgba(10, 10, 26, 0.92)';
    ctx.fillRect(48, H - 280, W - 96, 200);
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 6;
    ctx.strokeRect(48, H - 280, W - 96, 200);

    // Current Spoken Line in RPG Box
    let currentLineText = "";
    for (let i = 0; i < WORDS.length; i++) {{
      if (WORDS[i].s <= t) {{
        currentLineText += WORDS[i].t + " ";
        if (WORDS[i].t.endsWith('.') || WORDS[i].t.endsWith('?')) {{
          if (WORDS[i].e + 0.35 <= t) currentLineText = "";
        }}
      }}
    }}

    ctx.font = '28px "Pixelify Sans", "Press Start 2P", monospace';
    ctx.fillStyle = '#FFFFFF';
    A.wrapText(ctx, currentLineText.trim(), 80, H - 220, W - 160, 42);
    ctx.restore();

    // Top HUD (always alive across the entire film)
    drawHUD(ctx, t);

    // CRT glass scanlines & vignette
    A.crtGlass(ctx, 0.6);
  }};

  // Preloader required by HyperFrames index.html
  F.load = async () => {{
    const fonts = [
      ['Press Start 2P', 'assets/fonts/PressStart2P-Regular.ttf'],
      ['Pixelify Sans', 'assets/fonts/PixelifySans-VF.ttf'],
      ['Bungee', 'assets/fonts/Bungee-Regular.ttf']
    ];
    await Promise.all(fonts.map(async ([n, u]) => {{
      try {{
        const f = new FontFace(n, `url(${{u}})`);
        await f.load();
        document.fonts.add(f);
      }} catch (e) {{
        console.warn('Font load warning', n, e);
      }}
    }}));
    build();
  }};

  // Helper text wrapper
  A.wrapText = function(ctx, text, x, y, maxWidth, lineHeight) {{
    const words = text.split(' ');
    let line = '';
    for(let n = 0; n < words.length; n++) {{
      const testLine = line + words[n] + ' ';
      const metrics = ctx.measureText(testLine);
      if (metrics.width > maxWidth && n > 0) {{
        ctx.fillText(line, x, y);
        line = words[n] + ' ';
        y += lineHeight;
      }} else {{
        line = testLine;
      }}
    }}
    ctx.fillText(line, x, y);
  }};
}})();
"""

    out_path = project_dir / "assets/film.js"
    out_path.write_text(js_code, encoding="utf-8")
    print(f"Dynamic film.js written to {out_path} ({len(js_code)} bytes)")
    return out_path


if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "arcade-motiongraphics/_selftest"
    from arcade_researcher import select_topic_for_today
    story = select_topic_for_today()
    generate_film_js(p, story)
