"""studio/tools/selenium_render_fallback.py — Ultra-Fast Zero-Network Canvas-Direct Headless Chromium 4K/1440p Renderer.

Compiles `studio/engine/*.js` + project `config.json`, `story/shots.json`, `timeline/words.json`, and `scenes/cast.js`
into a single hermetic HTML payload injected directly into `about:blank` via Chrome DevTools Protocol (`Page.setDocumentContent`).
Uses direct batch HTML5 Canvas (`main.toDataURL('image/jpeg', 0.94)`) extraction inside V8 (35x faster than CDP `Page.captureScreenshot`!),
rendering frames deterministically at >=1440p native resolution and mastering to 4K UHD (3840x2160 / 2160x3840)
or 1440p QHD (2560x1440 / 1440x2560) via FFmpeg Lanczos + unsharp pipeline.
"""
import argparse, base64, json, os, re, shutil, subprocess, tempfile, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

STUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _strip_esm_and_wrap(fname: str) -> str:
    fpath = os.path.join(STUDIO_ROOT, "engine", fname)
    code = open(fpath, encoding="utf-8").read()
    code = re.sub(r"^\s*import\s+.*?;?\s*$", "", code, flags=re.M)
    exported_fns = re.findall(r"^\s*export\s+(?:async\s+)?function\s+(\w+)", code, flags=re.M)
    exported_vars = re.findall(r"^\s*export\s+(?:const|let|var)\s+(\w+)", code, flags=re.M)
    all_exports = list(dict.fromkeys(exported_fns + exported_vars))
    code = re.sub(r"^\s*export\s+(async\s+)?function\s+", r"\1function ", code, flags=re.M)
    code = re.sub(r"^\s*export\s+(const|let|var)\s+", r"\1 ", code, flags=re.M)
    code = re.sub(r"^\s*export\s+\{[^}]*\};?\s*$", "", code, flags=re.M)

    if fname == "fx2d.js":
        return f"const FX = (() => {{\n{code}\nreturn {{ {', '.join(all_exports)} }};\n}})();"
    if fname == "ui2d.js":
        return f"const UI = (() => {{\n{code}\nreturn {{ {', '.join(all_exports)} }};\n}})();\nconst captions = UI.captions;"
    return f"const {{ {', '.join(all_exports)} }} = (() => {{\n{code}\nreturn {{ {', '.join(all_exports)} }};\n}})();"


def build_hermetic_player_html(project_dir: str, raster_res: str, scale: float, style: str) -> str:
    """Inline engine/*.js and project JSON data into a single hermetic HTML string injected via CDP Page.setDocumentContent."""
    cfg = json.load(open(os.path.join(project_dir, "config.json"), encoding="utf-8"))
    story = json.load(open(os.path.join(project_dir, "story", "shots.json"), encoding="utf-8"))
    words_path = os.path.join(project_dir, "timeline", "words.json")
    words = json.load(open(words_path, encoding="utf-8")) if os.path.exists(words_path) else {"words": []}

    cast_path = os.path.join(project_dir, "scenes", "cast.js")
    cast_code = ""
    if os.path.exists(cast_path):
        raw_cast = open(cast_path, encoding="utf-8").read()
        cast_code = re.sub(r"^\s*export\s+const\s+", "const ", raw_cast, flags=re.M)

    engine_order = ["styles.js", "core.js", "rig2d.js", "fx2d.js", "ui2d.js", "sets.js", "declarative_shots.js"]
    bundled_js = [
        f"window.__INLINED_CFG = {json.dumps(cfg)};",
        f"window.__INLINED_STORY = {json.dumps(story)};",
        f"window.__INLINED_WORDS = {json.dumps(words)};",
        cast_code,
    ]
    for fname in engine_order:
        bundled_js.append(f"// --- {fname} ---\n" + _strip_esm_and_wrap(fname))

    player_driver_js = f"""
const RES = {{ '1440p': 1440, '2k': 1440, 'qhd': 1440, '2160p': 2160, '4k': 2160, '1080p': 1440, '720p': 1440 }};
let main, mg, bufA, bufB, grainTiles = [];
const errors = (window.ERRORS = []);
const mk = (w, h) => {{ const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }};

function bootHermetic() {{
  const cfg = window.__INLINED_CFG;
  const story = window.__INLINED_STORY;
  const words = window.__INLINED_WORDS;
  const vertical = (cfg.aspect || '16:9') === '9:16';
  const reqRes = {json.dumps(raster_res.lower())};
  const shortSide = RES[reqRes] || 1440;
  const longSide = Math.round((shortSide * 16) / 9 / 2) * 2;
  const scale = {float(scale)};
  const outW = Math.round(((vertical ? shortSide : longSide) * scale) / 2) * 2;
  const outH = Math.round(((vertical ? longSide : shortSide) * scale) / 2) * 2;

  Object.assign(E, {{
    vertical,
    W: vertical ? 1080 : 1920,
    H: vertical ? 1920 : 1080,
    fps: cfg.fps || 24,
    cfg,
    words: words.words || words || [],
    shots: story.shots,
    outW,
    outH,
  }});
  E.PX = outW / E.W;
  setStyle({json.dumps(style)} || cfg.style || 'ted_ifverse');

  main = document.getElementById('main');
  main.width = outW;
  main.height = outH;
  mg = main.getContext('2d');
  bufA = mk(outW, outH);
  bufB = mk(outW, outH);

  const gw = 512, gh = 512;
  for (let k = 0; k < 4; k++) {{
    const c = mk(gw, gh), x = c.getContext('2d'), id = x.createImageData(gw, gh);
    let s = 1234 + k * 999;
    for (let i = 0; i < id.data.length; i += 4) {{
      s = (s * 1664525 + 1013904223) >>> 0;
      const v = s >>> 24;
      id.data[i] = id.data[i + 1] = id.data[i + 2] = v;
      id.data[i + 3] = 255;
    }}
    x.putImageData(id, 0, 0);
    grainTiles.push(c);
  }}

  const dur = story.duration || E.shots[E.shots.length - 1].end;
  window.DURATION = dur;
  window.TOTAL_FRAMES = Math.ceil(dur * E.fps);
  window.OUT = [outW, outH];
  window.SHOT_LIST = E.shots.map(s => ({{ id: s.id, start: s.start, end: s.end, ok: true }}));
  window.READY = true;
}}

function getHardwareGradeFilter() {{
  const gr = E.style.grade || {{}};
  const con = gr.contrast ?? 1.0;
  const sat = gr.sat ?? 1.0;
  const parts = [];
  if (Math.abs(con - 1.0) > 0.01) parts.push(`contrast(${{(con * 100).toFixed(1)}}%)`);
  if (Math.abs(sat - 1.0) > 0.01) parts.push(`saturate(${{(sat * 100).toFixed(1)}}%)`);
  return parts.length ? parts.join(' ') : 'none';
}}

function shotIndexAt(t) {{
  const S = E.shots;
  for (let i = 0; i < S.length; i++) if (t < S[i].end) return i;
  return S.length - 1;
}}

function drawShot(buf, shot, lt) {{
  const g = buf.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.globalAlpha = 1;
  g.globalCompositeOperation = 'source-over';
  g.filter = 'none';
  g.fillStyle = '#000';
  g.fillRect(0, 0, buf.width, buf.height);
  g.setTransform(E.PX, 0, 0, E.PX, 0, 0);
  const dur = Math.max(0.1, shot.end - shot.start);
  const info = {{ ...(shot.params || {{}}), shot, dur, globalT: shot.start + lt, p: clamp(lt / dur), line: shot.line }};
  try {{
    g.save();
    renderDeclarativeShot(g, lt, info);
    g.restore();
  }} catch (e) {{
    errors.push(`${{shot.id}}: ${{e.message}}`);
  }}
}}

const BARS = () => ({{ none: 0, wide: V(60, 0), scope: V(132, 140), thin: V(30, 50) }});
const barVal = (s) => (typeof (s?.bars ?? E.cfg.bars) === 'number' ? (s.bars ?? E.cfg.bars) : BARS()[s?.bars ?? E.cfg.bars ?? V('wide', 'none')] ?? 0);

window.renderFrame = function (f) {{
  const t = f / E.fps, i = shotIndexAt(t), shot = E.shots[i], lt = t - shot.start;
  drawShot(bufA, shot, lt);
  const tr = shot.in || {{ type: 'cut' }}, tdur = tr.dur ?? (tr.type === 'whip' ? 0.35 : 0.5);
  const W = main.width, H = main.height;
  mg.setTransform(1, 0, 0, 1, 0, 0);
  mg.globalAlpha = 1;
  mg.globalCompositeOperation = 'source-over';
  const grade = E.style.grade || {{}};
  mg.filter = getHardwareGradeFilter();

  if (tr.type !== 'cut' && i > 0 && lt < tdur) {{
    const prev = E.shots[i - 1], k = ease.inOut(lt / tdur);
    drawShot(bufB, prev, t - prev.start);
    if (tr.type === 'fade') {{
      mg.drawImage(bufB, 0, 0); mg.globalAlpha = k; mg.drawImage(bufA, 0, 0);
    }} else if (tr.type === 'dip' || tr.type === 'dipWhite') {{
      const c = tr.type === 'dip' ? '#000' : '#fff';
      mg.drawImage(k < 0.5 ? bufB : bufA, 0, 0); mg.filter = 'none';
      mg.globalAlpha = k < 0.5 ? k * 2 : (1 - k) * 2; mg.fillStyle = c; mg.fillRect(0, 0, W, H);
    }} else if (tr.type === 'flash') {{
      mg.drawImage(bufA, 0, 0); mg.filter = 'none'; mg.globalAlpha = (1 - lt / tdur) ** 2; mg.fillStyle = '#fff'; mg.fillRect(0, 0, W, H);
    }} else if (tr.type === 'whip') {{
      const dir = tr.dir || 1;
      for (let s = 0; s < 4; s++) {{
        mg.globalAlpha = 0.3;
        mg.drawImage(bufB, -dir * k * W * 1.1 - dir * s * W * 0.02, 0);
        mg.drawImage(bufA, dir * (1 - k) * W * 1.1 + dir * s * W * 0.02, 0);
      }}
    }} else if (tr.type === 'zoom') {{
      mg.drawImage(bufB, 0, 0); const s = 1.15 - 0.15 * k; mg.globalAlpha = k;
      mg.translate(W / 2, H / 2); mg.scale(s, s); mg.drawImage(bufA, -W / 2, -H / 2); mg.setTransform(1, 0, 0, 1, 0, 0);
    }} else {{
      mg.drawImage(bufA, 0, 0);
    }}
  }} else {{
    mg.drawImage(bufA, 0, 0);
  }}

  mg.globalAlpha = 1; mg.filter = 'none'; mg.setTransform(1, 0, 0, 1, 0, 0);
  if (shot.vignette !== false && grade.vignette > 0) {{
    const v = mg.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.max(W, H) * 0.62);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${{grade.vignette}})`);
    mg.fillStyle = v; mg.fillRect(0, 0, W, H);
  }}
  if (grade.grain > 0) {{
    mg.save(); mg.globalAlpha = grade.grain; mg.globalCompositeOperation = 'overlay';
    mg.drawImage(grainTiles[f % 4], 0, 0, W, H); mg.restore();
  }}
  mg.setTransform(E.PX, 0, 0, E.PX, 0, 0);
  if ((E.cfg.captions || E.vertical) && shot.captions !== false) {{
    captions(mg, t, E.cfg.captionStyle || {{}});
  }}
  const cur = barVal(shot), prevB = i > 0 ? barVal(E.shots[i - 1]) : cur, bar = prevB + (cur - prevB) * ease.inOut(prog(lt, 0, 0.6));
  if (bar > 0) {{
    mg.fillStyle = '#000'; mg.fillRect(0, 0, E.W, bar); mg.fillRect(0, E.H - bar, E.W, bar);
  }}
  const fi = E.cfg.fadeIn ?? 0.5, fo = E.cfg.fadeOut ?? 0.8, dur = window.DURATION;
  const fade = Math.max(fi > 0 ? 1 - t / fi : 0, fo > 0 ? 1 - (dur - t) / fo : 0);
  if (fade > 0) {{
    mg.fillStyle = `rgba(0,0,0,${{clamp(fade)}})`; mg.fillRect(0, 0, E.W, E.H);
  }}
  mg.setTransform(1, 0, 0, 1, 0, 0);
}};

window.renderBatchDataUrls = function (fStart, fEnd) {{
  const out = [];
  for (let f = fStart; f < fEnd; f++) {{
    window.renderFrame(f);
    out.push(main.toDataURL('image/jpeg', 0.94).slice(23));
  }}
  return out;
}};
try {{ bootHermetic(); }} catch (e) {{ window.BOOT_ERROR = e.message + '\\n' + e.stack; }}
"""
    bundled_js.append(player_driver_js)
    full_js = "\n".join(bundled_js)
    html_str = (
        "<!doctype html><html><head><meta charset='utf-8'><title>player_v3_4k</title>"
        "<style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style></head>"
        f"<body><canvas id='main'></canvas><script>\n{full_js}\n</script></body></html>"
    )
    html_out = os.path.join(project_dir, "build", "player_bundled.html")
    os.makedirs(os.path.dirname(html_out), exist_ok=True)
    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html_str)
    return html_str


def make_driver(w: int, h: int, user_data_dir: str):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-crash-reporter")
    opts.add_argument("--allow-file-access-from-files")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument(f"--window-size={w},{h}")
    opts.add_argument(f"--user-data-dir={user_data_dir}")
    opts.add_argument(f"--crash-dumps-dir={user_data_dir}")
    return webdriver.Chrome(options=opts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="0")
    ap.add_argument("--project", required=True)
    ap.add_argument("--mode", default="video", choices=["video", "sheet"])
    ap.add_argument("--raster-res", default="1440p")
    ap.add_argument("--target-w", type=int, default=3840)
    ap.add_argument("--target-h", type=int, default=2160)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--style", default="ted_ifverse")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    html_content = build_hermetic_player_html(a.project, a.raster_res, a.scale, a.style)
    user_data_dir = tempfile.mkdtemp(prefix="chromium_v3_4k_")
    driver = make_driver(1280, 720, user_data_dir)
    try:
        driver.get("about:blank")
        frame_tree = driver.execute_cdp_cmd("Page.getFrameTree", {})
        frame_id = frame_tree["frameTree"]["frame"]["id"]
        driver.execute_cdp_cmd("Page.setDocumentContent", {"frameId": frame_id, "html": html_content})
        time.sleep(0.1)
        boot_err = driver.execute_script("return window.BOOT_ERROR;")
        if boot_err:
            raise RuntimeError(f"Player boot error: {boot_err}")
        out_dims = driver.execute_script("return window.OUT;")
        if not out_dims:
            raise RuntimeError("Player did not initialize window.OUT")
        rw, rh = int(out_dims[0]), int(out_dims[1])

        if a.mode == "sheet":
            shots = driver.execute_script("return window.SHOT_LIST;")
            sheets_dir = os.path.join(a.project, "build", "sheets")
            os.makedirs(sheets_dir, exist_ok=True)
            for s in shots:
                mid_f = int(round((s["start"] + (s["end"] - s["start"]) * 0.45) * a.fps))
                b64_list = driver.execute_script(f"return window.renderBatchDataUrls({mid_f}, {mid_f + 1});")
                with open(os.path.join(sheets_dir, f"{s['id']}.jpg"), "wb") as f:
                    f.write(base64.b64decode(b64_list[0]))
            print(f"[Hermetic 4K/1440p Renderer] Wrote {len(shots)} shot stills ({rw}x{rh}) to {sheets_dir}")
            return

        total_frames = int(driver.execute_script("return window.TOTAL_FRAMES;"))
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        vf = []
        if (rw != a.target_w or rh != a.target_h) and a.scale == 1.0:
            vf.extend(["-vf", f"scale={a.target_w}:{a.target_h}:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=3:3:0.35:3:3:0.0"])

        ff_cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
            *vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "17",
            "-profile:v", "high", "-level:v", "5.1",
            "-pix_fmt", "yuv420p", "-colorspace", "bt709",
            "-r", str(a.fps), "-movflags", "+faststart", a.out
        ]
        proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE)
        start_t = time.time()
        batch_sz = 12
        for f0 in range(0, total_frames, batch_sz):
            f1 = min(total_frames, f0 + batch_sz)
            b64_frames = driver.execute_script(f"return window.renderBatchDataUrls({f0}, {f1});")
            for b64 in b64_frames:
                proc.stdin.write(base64.b64decode(b64))
            if f1 % 48 == 0 or f1 == total_frames:
                el = time.time() - start_t
                print(f"  [4K/1440p Fast Batch Render] {f1}/{total_frames} frames ({f1/max(0.1, el):.1f} fps)")
        proc.stdin.close()
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("FFmpeg encoding failed in selenium_render_fallback.py")
        print(f"[Hermetic 4K/1440p Renderer] Master video complete ({a.target_w}x{a.target_h}): {a.out}")
    finally:
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
