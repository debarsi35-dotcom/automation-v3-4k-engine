/* ARCADE MOTION GRAPHICS — kit (arcade.js)
 * One 1080x1920 canvas, drawn by a pure function of time t (seconds), so every frame is seek-safe.
 * Learned frame by frame from REF-A (McDonald's "Spicy McNuggets Side Mission": 8-bit world + real food +
 * pixel HUD) and REF-B (pixel girl walking in a beige CRT). Devices are documented in reference/devices.md.
 */
(function () {
  const W = 1080, H = 1920;
  const A = (window.A = { W, H });

  // ---------------------------------------------------------------- math
  const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
  const lerp = (a, b, t) => a + (b - a) * t;
  const pr = (t, a, b) => clamp((t - a) / (b - a));
  const E = {
    lin: (t) => t,
    inQ: (t) => t * t,
    outQ: (t) => 1 - (1 - t) * (1 - t),
    inC: (t) => t * t * t,
    outC: (t) => 1 - Math.pow(1 - t, 3),
    inOutC: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    outQuint: (t) => 1 - Math.pow(1 - t, 5),
    outExpo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
    inExpo: (t) => (t <= 0 ? 0 : Math.pow(2, 10 * t - 10)),
    outBack: (t, s = 1.9) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
    outElastic: (t) => (t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -9 * t) * Math.sin((t * 9 - 0.75) * ((2 * Math.PI) / 3)) + 1),
  };
  const rnd = (n) => { const x = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };
  const stepT = (t, fps) => Math.floor(t * fps + 1e-6) / fps;      // stepped (sprite-rate) time
  const snap = (v, g) => Math.round(v / g) * g;                    // snap to the art-pixel grid
  Object.assign(A, { clamp, lerp, pr, E, rnd, stepT, snap });

  // ---------------------------------------------------------------- canvases
  A.canvas = (w, h) => {
    const c = document.createElement('canvas');
    c.width = Math.max(1, Math.ceil(w)); c.height = Math.max(1, Math.ceil(h));
    c.getContext('2d').imageSmoothingEnabled = false;
    return c;
  };
  A.buf = {};                                   // named full-frame scratch buffers
  A.buffer = (name) => {
    if (!A.buf[name]) A.buf[name] = A.canvas(W, H);
    const c = A.buf[name], x = c.getContext('2d');
    x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over';
    x.imageSmoothingEnabled = false; x.clearRect(0, 0, W, H);
    return c;
  };

  // ---------------------------------------------------------------- colour (REF-A / REF-B measured)
  A.C = {
    sky: '#1FC6F1', skyHi: '#5CD9F6', skyLo: '#14B3E6', cloud: '#FFFFFF', cloudSh: '#C5EEFB',
    ink: '#16101F', night: '#141029', navy: '#101536',
    fire: ['#FFF7A8', '#FFD43A', '#FF8F1F', '#E9361B'], fireOut: '#2E0904', fireExt: '#7E1A0A',
    gold: ['#FFF3A0', '#FFC928', '#E08A10'], goldOut: '#3A2304',
    white: ['#FFFFFF', '#FFFFFF', '#E6E2D6'], whiteOut: '#16101F',
    red: ['#FF6B5A', '#E8291C', '#A8120C'],
    cyan: ['#C8FBFF', '#45E3F5', '#1590C8'],
    dlg: '#F7B81F', dlgHi: '#FFD54D', dlgSh: '#B66A08', dlgInk: '#2A1A05',
    heat1: '#D8430F', heat2: '#B5200C',
    hudRed: ['#FF5A3C', '#F2A12C'], hudBlue: '#3BA3F2', hudSlate: '#2B3248',
  };
  A.hex = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const mix = (h1, h2, t) => { const a = A.hex(h1), b = A.hex(h2); return `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], t))).join(',')})`; };
  const ramp = (stops, t) => { t = clamp(t); const n = stops.length - 1, i = Math.min(n - 1, Math.floor(t * n)); return mix(stops[i], stops[i + 1], t * n - i); };
  A.mix = mix; A.ramp = ramp;

  // ---------------------------------------------------------------- sprites from strings
  A.spr = {};
  A.defSprite = (name, rows, pal) => {
    const h = rows.length, w = Math.max(...rows.map((r) => r.length));
    const c = A.canvas(w, h), x = c.getContext('2d');
    rows.forEach((r, j) => [...r].forEach((ch, i) => { const col = pal[ch]; if (col) { x.fillStyle = col; x.fillRect(i, j, 1, 1); } }));
    return (A.spr[name] = { c, w, h, rows, pal });
  };
  // silhouette (for chunky pixel outlines around sprites / cut-outs)
  const silCache = new Map();
  A.silhouette = (src, color) => {
    const key = src; let m = silCache.get(key);
    if (!m) { m = {}; silCache.set(key, m); }
    if (!m[color]) {
      const c = A.canvas(src.width, src.height), x = c.getContext('2d');
      x.drawImage(src, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = color; x.fillRect(0, 0, c.width, c.height);
      m[color] = c;
    }
    return m[color];
  };
  // draw sprite: s = screen px per art px; anchor 'tl' | 'c' | 'bc'
  A.drawSpr = (ctx, name, x, y, s, o = {}) => {
    const S = typeof name === 'string' ? A.spr[name] : name;
    const w = S.w * s, h = S.h * s;
    let X = x, Y = y;
    if (o.anchor === 'c') { X = x - w / 2; Y = y - h / 2; } else if (o.anchor === 'bc') { X = x - w / 2; Y = y - h; }
    X = Math.round(X); Y = Math.round(Y);
    ctx.save(); ctx.imageSmoothingEnabled = false;
    if (o.alpha != null) ctx.globalAlpha *= o.alpha;
    if (o.flip) { ctx.translate(X + w, Y); ctx.scale(-1, 1); X = 0; Y = 0; }
    if (o.outline) {
      const sil = A.silhouette(S.c, o.outline), d = Math.max(1, Math.round(o.ow || s));
      for (const [dx, dy] of [[-d, 0], [d, 0], [0, -d], [0, d], [-d, -d], [d, d], [-d, d], [d, -d]]) ctx.drawImage(sil, X + dx, Y + dy, w, h);
    }
    ctx.drawImage(S.c, X, Y, w, h);
    ctx.restore();
    return { x: X, y: Y, w, h };
  };
  // draw a sprite cell by cell from rows (lets callers reveal pixels one at a time)
  A.drawCells = (ctx, rows, pal, x, y, s, keep = () => true) => {
    rows.forEach((r, j) => [...r].forEach((ch, i) => {
      const col = pal[ch]; if (!col || !keep(i, j, ch)) return;
      ctx.fillStyle = col; ctx.fillRect(Math.round(x + i * s), Math.round(y + j * s), Math.ceil(s), Math.ceil(s));
    }));
  };

  // procedural pixel cloud (REF-A sky): union of circles, shaded underside
  A.makeCloud = (seed, w, h) => {
    const c = A.canvas(w, h), x = c.getContext('2d');
    const blobs = [];
    const n = 4 + Math.floor(rnd(seed) * 3);
    for (let i = 0; i < n; i++) {
      const bx = w * (0.18 + 0.64 * (i / (n - 1))) + (rnd(seed + i * 3.1) - 0.5) * w * 0.08;
      const r = h * (0.26 + 0.2 * rnd(seed + i * 7.7)) * (i === 1 || i === n - 2 ? 1.25 : 1);
      blobs.push([bx, h - r - h * 0.08, r]);
    }
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
      let inside = false, low = 0;
      for (const [bx, by, r] of blobs) { const d = Math.hypot(i + 0.5 - bx, j + 0.5 - by); if (d < r) { inside = true; low = Math.max(low, (j + 0.5 - by) / r); } }
      if (j > h * 0.9) inside = inside && i > w * 0.12 && i < w * 0.88;
      if (!inside) continue;
      x.fillStyle = low > 0.55 ? A.C.cloudSh : A.C.cloud; x.fillRect(i, j, 1, 1);
    }
    return c;
  };

  // ---------------------------------------------------------------- pixel type (Press Start 2P mask -> styled bitmap)
  // The font is drawn at 8px so one font pixel = one cell, then rebuilt as blocks: gradient fill by row,
  // 3D extrusion down-right, dark outline around everything (the REF-A "MAXIMUM FLAVOUR" / "HEAT MODE: ON" look).
  const maskCache = new Map(), bmpCache = new Map();
  A.font8 = '"PS2P"';
  A.textMask = (str) => {
    if (maskCache.has(str)) return maskCache.get(str);
    const w = str.length * 8 + 16, h = 16;
    const c = A.canvas(w, h), x = c.getContext('2d');
    x.font = `8px ${A.font8}`; x.textBaseline = 'top'; x.fillStyle = '#fff'; x.fillText(str, 4, 4);
    const d = x.getImageData(0, 0, w, h).data;
    let x0 = w, x1 = -1, y0 = h, y1 = -1;
    const on = new Uint8Array(w * h);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (d[(j * w + i) * 4 + 3] > 100) { on[j * w + i] = 1; x0 = Math.min(x0, i); x1 = Math.max(x1, i); y0 = Math.min(y0, j); y1 = Math.max(y1, j); }
    // keep the full advance width so monospaced prefixes line up
    const mw = str.length * 8, mh = 8, ox = 4, oy = Math.min(y0, 4);
    const m = new Uint8Array(mw * mh);
    for (let j = 0; j < mh; j++) for (let i = 0; i < mw; i++) m[j * mw + i] = on[(j + oy) * w + (i + ox)] || 0;
    const r = { w: mw, h: mh, m };
    maskCache.set(str, r); return r;
  };
  A.STYLE = {
    fire: { fill: A.C.fire, out: A.C.fireOut, ext: A.C.fireExt, depth: 1 },
    gold: { fill: A.C.gold, out: A.C.goldOut, ext: '#8A4A06', depth: 1 },
    white: { fill: A.C.white, out: A.C.whiteOut, ext: '#5A5470', depth: 1 },
    whiteFlat: { fill: A.C.white, out: A.C.whiteOut, depth: 0 },
    red: { fill: A.C.red, out: '#240503', ext: '#5A0A06', depth: 1 },
    cyan: { fill: A.C.cyan, out: '#04202E', ext: '#0B4F70', depth: 1 },
    ink: { fill: ['#2A1A05', '#2A1A05'], depth: 0 },
    plainWhite: { fill: ['#FFFFFF', '#FFFFFF'], depth: 0 },
    plainYellow: { fill: ['#FFE14A', '#FFC21A'], depth: 0 },
    plainCyan: { fill: ['#7EF2FF', '#3CD0F0'], depth: 0 },
    plainRed: { fill: ['#FF5A4A', '#E3261A'], depth: 0 },
  };
  A.textBmp = (str, styleName) => {
    const key = str + '|' + (typeof styleName === 'string' ? styleName : JSON.stringify(styleName));
    if (bmpCache.has(key)) return bmpCache.get(key);
    const st = typeof styleName === 'string' ? A.STYLE[styleName] : styleName;
    const M = A.textMask(str), d = st.depth || 0, o = st.out ? 1 : 0;
    const w = M.w + d + 2 * o, h = M.h + d + 2 * o;
    const c = A.canvas(w, h), x = c.getContext('2d');
    const at = (i, j) => i >= 0 && j >= 0 && i < M.w && j < M.h && M.m[j * M.w + i];
    const body = (i, j) => { for (let k = 0; k <= d; k++) if (at(i - k, j - k)) return true; return false; };
    for (let j = -o; j < M.h + d + o; j++) for (let i = -o; i < M.w + d + o; i++) {
      let col = null;
      if (at(i, j)) col = ramp(st.fill, M.h > 1 ? j / (M.h - 1) : 0);
      else if (body(i, j)) col = st.ext || st.fill[st.fill.length - 1];
      else if (o) { for (const [a, b] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [1, -1], [-1, 1]]) if (body(i + a, j + b)) { col = st.out; break; } }
      if (col) { x.fillStyle = col; x.fillRect(i + o, j + o, 1, 1); }
    }
    const r = { c, w, h, pad: o };
    bmpCache.set(key, r); return r;
  };
  // draw pixel text; cell = screen px per font px; align 'c' | 'l' | 'r'; reveal = chars shown (prefix)
  A.ptext = (ctx, str, x, y, cell, style = 'fire', o = {}) => {
    const B = A.textBmp(str, style);
    cell = Math.max(1, Math.round(cell));
    const w = B.w * cell, h = B.h * cell;
    let X = o.align === 'l' ? x : o.align === 'r' ? x - w : x - w / 2;
    let Y = o.valign === 't' ? y : y - h / 2;
    X = Math.round(X); Y = Math.round(Y);
    ctx.save(); ctx.imageSmoothingEnabled = false;
    if (o.alpha != null) ctx.globalAlpha *= o.alpha;
    if (o.rot) { ctx.translate(X + w / 2, Y + h / 2); ctx.rotate(o.rot); ctx.translate(-(X + w / 2), -(Y + h / 2)); }
    if (o.reveal != null && o.reveal < str.length) {
      const st = typeof style === 'string' ? A.STYLE[style] : style;
      const cw = Math.min(B.w, 2 * B.pad + o.reveal * 8 + (st.depth || 0));
      if (o.reveal > 0) ctx.drawImage(B.c, 0, 0, cw, B.h, X, Y, cw * cell, h);
    } else ctx.drawImage(B.c, X, Y, w, h);
    ctx.restore();
    return { x: X, y: Y, w, h };
  };
  // pop-in scale for a super: integer cell steps from big to target (stepped growth reads as pixel)
  A.popCell = (t, t0, cell, k = 1.9, dur = 0.2) => {
    const p = pr(t, t0, t0 + dur);
    if (p <= 0) return 0;
    return Math.max(1, Math.round(cell * lerp(k, 1, E.outBack(p, 2.4))));
  };

  // ---------------------------------------------------------------- backgrounds
  const bgCache = new Map();
  A.halftone = (c1, c2, dot, cell = 18, grow = 1) => {
    const key = [c1, c2, dot, cell, grow].join();
    if (bgCache.has(key)) return bgCache.get(key);
    const c = A.canvas(W, H), x = c.getContext('2d');
    const g = x.createLinearGradient(0, 0, 0, H); g.addColorStop(0, c1); g.addColorStop(1, c2);
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    x.fillStyle = dot;
    for (let j = 0; j < H / cell + 1; j++) for (let i = 0; i < W / cell + 1; i++) {
      const v = (j * cell) / H;
      const r = cell * 0.5 * (0.18 + 0.5 * Math.pow(v, 1.2) * grow);
      const px = i * cell + (j % 2 ? cell / 2 : 0), py = j * cell;
      x.fillRect(Math.round(px - r), Math.round(py - r), Math.round(2 * r), Math.round(2 * r)); // square dots = pixel halftone
    }
    bgCache.set(key, c); return c;
  };
  A.stripes = (c1, c2, band, key2 = '') => {   // REF-A wood-panel wall behind the counter
    const key = ['stripes', c1, c2, band, key2].join();
    if (bgCache.has(key)) return bgCache.get(key);
    const c = A.canvas(W, H), x = c.getContext('2d');
    for (let y = 0; y < H; y += band) { x.fillStyle = (y / band) % 2 ? c2 : c1; x.fillRect(0, y, W, band); }
    x.fillStyle = 'rgba(0,0,0,0.18)';
    for (let y = band - 6; y < H; y += band) x.fillRect(0, y, W, 6);
    bgCache.set(key, c); return c;
  };
  A.bands = (top, bottom, n) => {               // REF-A end card: stepped (posterised) gradient bands
    const key = ['bands', top, bottom, n].join();
    if (bgCache.has(key)) return bgCache.get(key);
    const c = A.canvas(W, H), x = c.getContext('2d');
    for (let i = 0; i < n; i++) { x.fillStyle = mix(top, bottom, i / (n - 1)); x.fillRect(0, Math.floor((i * H) / n), W, Math.ceil(H / n) + 1); }
    bgCache.set(key, c); return c;
  };
  A.graph = (bg, line, cell) => {
    const key = ['graph', bg, line, cell].join();
    if (bgCache.has(key)) return bgCache.get(key);
    const c = A.canvas(W, H), x = c.getContext('2d');
    x.fillStyle = bg; x.fillRect(0, 0, W, H); x.fillStyle = line;
    for (let i = 0; i < W; i += cell) x.fillRect(i, 0, 2, H);
    for (let j = 0; j < H; j += cell) x.fillRect(0, j, W, 2);
    bgCache.set(key, c); return c;
  };
  A.vignette = (ctx, k = 0.45, r0 = 0.55) => {
    const g = ctx.createRadialGradient(W / 2, H * 0.45, W * r0 * 0.5, W / 2, H * 0.45, H * 0.75);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${k})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  };

  // ---------------------------------------------------------------- real image -> pixel art
  A.pixelate = (img, cellsW, levels = 5, sat = 1.15) => {
    const ar = img.height / img.width, w = cellsW, h = Math.round(cellsW * ar);
    const c = A.canvas(w, h), x = c.getContext('2d');
    x.imageSmoothingEnabled = true; x.drawImage(img, 0, 0, w, h);
    const id = x.getImageData(0, 0, w, h), d = id.data;
    const q = (v) => Math.round(Math.round((v / 255) * (levels - 1)) * (255 / (levels - 1)));
    for (let i = 0; i < d.length; i += 4) {
      const l = (d[i] + d[i + 1] + d[i + 2]) / 3, ch = Math.max(d[i], d[i + 1], d[i + 2]) - Math.min(d[i], d[i + 1], d[i + 2]);
      if (ch < 28) { const g = q(l); d[i] = d[i + 1] = d[i + 2] = g; }      // keep greys grey (no posterise speckle)
      else for (let k = 0; k < 3; k++) d[i + k] = q(clamp(l + (d[i + k] - l) * sat, 0, 255));
      d[i + 3] = d[i + 3] > 110 ? 255 : 0;
    }
    x.putImageData(id, 0, 0);
    return c;
  };

  // ---------------------------------------------------------------- HUD (REF-B: heart + segmented bar, coin + counter)
  A.defSprite('heart', [
    '.KK...KK.', 'KRRK.KRRK', 'KRWRKRRRK', 'KRRRRRRRK', '.KRRRRRK.', '..KRRRK..', '...KRK...', '....K....',
  ], { K: '#1A0E10', R: '#F0412F', W: '#FFD0C8' });
  A.defSprite('coinIcon', [
    '..KKKK..', '.KYYYYK.', 'KYWYYOYK', 'KYWYYOYK', 'KYWYYOYK', 'KYYYYOYK', '.KYOOOK.', '..KKKK..',
  ], { K: '#3A2304', Y: '#FFC928', W: '#FFF3A0', O: '#D9860E' });
  A.fmt = (n) => Math.round(n).toLocaleString('en-US');
  A.hud = (ctx, o) => {
    const s = 6, x = o.x ?? 48, y = o.y ?? 110, a = o.alpha ?? 1;
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a;
    // heart in a dark frame
    ctx.fillStyle = 'rgba(16,12,30,0.78)'; ctx.fillRect(x, y, 14 * s, 13 * s);
    ctx.fillStyle = '#E9E3F5'; ctx.fillRect(x, y, 14 * s, s); ctx.fillRect(x, y + 12 * s, 14 * s, s); ctx.fillRect(x, y, s, 13 * s); ctx.fillRect(x + 13 * s, y, s, 13 * s);
    A.drawSpr(ctx, 'heart', x + 2.5 * s, y + 2.5 * s, s);
    // segmented bar
    const n = o.segs ?? 12, bx = x + 15 * s, bw = n * 4 * s + 2 * s, bh = 9 * s, by = y + 2 * s;
    ctx.fillStyle = '#E9E3F5'; ctx.fillRect(bx, by, bw, bh);
    ctx.fillStyle = '#120E1E'; ctx.fillRect(bx + s, by + s, bw - 2 * s, bh - 2 * s);
    const lit = o.health * n;
    for (let i = 0; i < n; i++) {
      const f = clamp(lit - i);
      ctx.fillStyle = f > 0 ? mix(A.C.hudRed[0], A.C.hudRed[1], i / (n - 1)) : A.C.hudSlate;
      ctx.fillRect(bx + 2 * s + i * 4 * s, by + 2 * s, 3 * s, bh - 4 * s);
      if (f > 0 && f < 1) { ctx.fillStyle = 'rgba(255,255,255,0.5)'; ctx.fillRect(bx + 2 * s + i * 4 * s, by + 2 * s, 3 * s, s); }
    }
    if (o.label) A.ptext(ctx, o.label, bx + bw / 2, by + bh / 2, 4, 'plainWhite');
    // coin counter, top right
    const cs = o.coins ?? 0;
    const txt = typeof cs === 'string' ? cs : 'x' + String(Math.round(cs)).padStart(3, '0');
    const r = W - x;
    const tb = A.textBmp(txt, 'whiteFlat');
    const tw = tb.w * 6;
    A.drawSpr(ctx, 'coinIcon', r - tw - 12 * s, y + 2.5 * s, s);
    A.ptext(ctx, txt, r, y + 6.5 * s, 6, 'whiteFlat', { align: 'r' });
    ctx.restore();
  };

  // ---------------------------------------------------------------- garnish
  A.crosshair = (ctx, x, y, r, t, o = {}) => {        // REF-A yellow reticle that locks onto the hero object
    const a = o.alpha ?? 1; if (a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.rotate(o.rot ?? t * 1.2);
    const col = o.color || '#FFD21E';
    for (const [lw, c] of [[r * 0.2, '#2A1604'], [r * 0.1, col]]) {
      ctx.strokeStyle = c; ctx.lineWidth = lw;
      ctx.beginPath(); ctx.arc(0, 0, r, 0.25, Math.PI / 2 - 0.25); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, r, Math.PI / 2 + 0.25, Math.PI - 0.25); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, r, Math.PI + 0.25, 1.5 * Math.PI - 0.25); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, r, 1.5 * Math.PI + 0.25, 2 * Math.PI - 0.25); ctx.stroke();
      ctx.beginPath();
      for (let k = 0; k < 4; k++) { const an = (k * Math.PI) / 2; ctx.moveTo(Math.cos(an) * r * 0.55, Math.sin(an) * r * 0.55); ctx.lineTo(Math.cos(an) * r * 1.35, Math.sin(an) * r * 1.35); }
      ctx.stroke();
    }
    ctx.fillStyle = col; const q = r * 0.16; ctx.fillRect(-q / 2, -q / 2, q, q);
    ctx.restore();
  };
  A.lockOn = (ctx, x, y, r, t, t0, t1 = 1e9) => {     // reticle flies in big + spinning, settles, then leaves
    const p = pr(t, t0, t0 + 0.28), q = pr(t, t1, t1 + 0.16);
    if (p <= 0 || q >= 1) return;
    A.crosshair(ctx, x, y, r * lerp(2.6, 1, E.outBack(p, 1.6)) * (1 + q * 0.6), t, { rot: lerp(2.4, 0, E.outC(p)) + t * 0.8, alpha: (1 - q) * Math.min(1, p * 3) });
  };
  A.sparks = (ctx, cx, cy, rad, t, n, seed, o = {}) => { // white pixel plus-shapes twinkling (REF-A 9.8 s)
    const s = o.cell || 8;
    for (let i = 0; i < n; i++) {
      const life = 0.7 + rnd(seed + i) * 0.8, ph = (t / life + rnd(seed + i * 2.3)) % 1;
      const k = Math.sin(ph * Math.PI);
      if (k < 0.15) continue;
      const an = rnd(seed + i * 5.1) * Math.PI * 2, rr = rad * (0.35 + 0.65 * rnd(seed + i * 9.7));
      const x = snap(cx + Math.cos(an) * rr, s), y = snap(cy + Math.sin(an) * rr * (o.squash || 1) - ph * (o.rise || 0), s);
      ctx.fillStyle = o.color || '#FFFFFF';
      ctx.globalAlpha = o.alpha ?? 1;
      if (k > 0.6 && (i % 3)) { ctx.fillRect(x - s, y, 3 * s, s); ctx.fillRect(x, y - s, s, 3 * s); } else ctx.fillRect(x, y, s, s);
      ctx.globalAlpha = 1;
    }
  };
  A.speedLines = (ctx, cx, cy, t, seed, o = {}) => {    // manga radial lines (REF-A 8.2 s, 16.2 s)
    const n = o.n || 46;
    ctx.save(); ctx.fillStyle = o.color || 'rgba(255,255,255,0.9)';
    for (let i = 0; i < n; i++) {
      const an = rnd(seed + i * 1.7) * Math.PI * 2, sp = 0.6 + rnd(seed + i * 3.3);
      const ph = (t * sp * (o.speed || 1.6) + rnd(seed + i * 4.1)) % 1;
      const r0 = lerp(o.r0 || 380, o.r1 || 1400, ph), len = (o.len || 260) * (0.5 + rnd(seed + i * 6.2));
      const wid = (o.w || 10) * (0.4 + rnd(seed + i * 8.8));
      const ca = Math.cos(an), sa = Math.sin(an), nx = -sa, ny = ca;
      ctx.beginPath();
      ctx.moveTo(cx + ca * r0, cy + sa * r0);
      ctx.lineTo(cx + ca * (r0 + len) + nx * wid, cy + sa * (r0 + len) + ny * wid);
      ctx.lineTo(cx + ca * (r0 + len) - nx * wid, cy + sa * (r0 + len) - ny * wid);
      ctx.closePath(); ctx.fill();
    }
    ctx.restore();
  };
  A.puff = (ctx, x, y, p, o = {}) => {                    // 8-bit smoke ring: chunky blobs flying out, shrinking
    if (p <= 0 || p >= 1) return;
    const s = o.cell || 12, n = o.n || 10, R = (o.r || 140) * E.outC(p);
    ctx.save(); ctx.fillStyle = o.color || '#FFFFFF'; ctx.globalAlpha = 1 - Math.pow(p, 2);
    for (let i = 0; i < n; i++) {
      const an = (i / n) * Math.PI * 2 + (o.rot || 0), b = Math.max(1, Math.round((1 - p) * (o.size || 3)));
      const bx = snap(x + Math.cos(an) * R, s), by = snap(y + Math.sin(an) * R * (o.squash || 0.7), s);
      ctx.fillRect(bx - (b * s) / 2, by - (b * s) / 2, b * s, b * s);
    }
    ctx.restore();
  };
  A.ring = (ctx, x, y, r, s, color, alpha = 1) => {   // pixel-stepped ring outline (REF-A 26.2 s impact rings)
    ctx.save(); ctx.globalAlpha *= alpha; ctx.fillStyle = color;
    const seen = new Set(), n = Math.max(16, Math.round((2 * Math.PI * r) / s));
    for (let i = 0; i < n; i++) { const an = (i / n) * Math.PI * 2; const px = snap(x + Math.cos(an) * r, s), py = snap(y + Math.sin(an) * r, s); const k = px + ',' + py; if (seen.has(k)) continue; seen.add(k); ctx.fillRect(px - s / 2, py - s / 2, s, s); }
    ctx.restore();
  };
  A.motionLines = (ctx, x, y, w, len, alpha = 1, s = 6) => { // REF-A 25.0 s: short vertical lines above a falling thing
    ctx.save(); ctx.globalAlpha *= alpha; ctx.fillStyle = '#FFFFFF';
    [[-0.3, 0.8], [0, 1], [0.3, 0.7]].forEach(([dx, k]) => ctx.fillRect(Math.round(x + dx * w), Math.round(y - len * k), s, Math.round(len * k)));
    ctx.restore();
  };

  // ---------------------------------------------------------------- dialog box (REF-A 2.9–5.6 s)
  A.dialog = (ctx, x, y, w, h, lines, o = {}) => {
    const s = 8, t = o.t ?? 1;
    const sq = o.squash || 0;            // anticipation before it pops
    const sx = 1 + sq * 0.06, sy = 1 - sq * 0.05;
    const p = E.outBack(clamp(t), 1.8);
    if (t <= 0) return;
    ctx.save();
    ctx.translate(x + w / 2, y + h / 2); ctx.scale(sx * lerp(0.2, 1, p), sy * lerp(0.2, 1, p)); ctx.translate(-(x + w / 2), -(y + h / 2));
    const box = (dx, dy, c) => {
      ctx.fillStyle = c;
      ctx.fillRect(x + dx + s, y + dy, w - 2 * s, h); ctx.fillRect(x + dx, y + dy + s, w, h - 2 * s);
    };
    box(14, 14, A.C.dlgSh);                                  // drop shadow
    box(-s, -s, A.C.dlgInk); box(s, s, A.C.dlgInk); box(-s, s, A.C.dlgInk); box(s, -s, A.C.dlgInk);
    box(0, 0, A.C.dlg);
    ctx.fillStyle = A.C.dlgHi; ctx.fillRect(x + s, y + s, w - 2 * s, s * 2);
    ctx.fillStyle = 'rgba(0,0,0,0.12)'; ctx.fillRect(x + s, y + h - 3 * s, w - 2 * s, s * 2);
    // stepped tail
    if (o.tail) {
      const [tx, dir] = o.tail; const ty = y + h;
      for (let k = 0; k < 6; k++) {
        const ww = (6 - k) * s;
        ctx.fillStyle = A.C.dlgInk; ctx.fillRect(x + tx + dir * k * s - s, ty + k * s - s, ww + 2 * s, s * 2);
      }
      for (let k = 0; k < 5; k++) { const ww = (5 - k) * s; ctx.fillStyle = A.C.dlg; ctx.fillRect(x + tx + dir * k * s, ty + k * s - s, ww, s); }
    }
    ctx.fillStyle = A.C.dlgInk; ctx.textBaseline = 'top';
    ctx.font = `600 ${o.size || 52}px "Pixelify"`;
    lines.forEach((ln, i) => ctx.fillText(ln, x + 44, y + 40 + i * (o.lh || 70)));
    ctx.restore();
  };
  A.type = (str, t, t0, t1) => str.slice(0, Math.round(str.length * pr(t, t0, t1)));

  // ---------------------------------------------------------------- transitions (each composites two drawn frames)
  // knit / stitch dissolve (REF-A 0.0–0.4 s and 7.9–8.1 s): columns wobble like a knitted jumper, V-stitches on top
  A.knit = (ctx, src, k, t, o = {}) => {
    if (k <= 0.001) { ctx.drawImage(src, 0, 0); return; }
    const cw = o.cw || 54, rh = o.rh || 40, amp = k * (o.amp || 46);
    ctx.fillStyle = o.base || '#D9F4FB'; ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < W; i += cw) for (let j = 0; j < H; j += rh) {
      const dy = Math.sin(i * 0.11 + j * 0.006 + t * 7) * amp, dx = Math.sin(j * 0.02 + i * 0.3) * amp * 0.2;
      ctx.drawImage(src, i, clamp(j + dy, 0, H - rh), cw, rh, i + dx, j, cw, rh);
    }
    ctx.save(); ctx.globalAlpha = k * (o.ta ?? 0.3);
    ctx.fillStyle = o.tint || '#F2FBFF'; ctx.fillRect(0, 0, W, H);
    // knitted V-stitches: two leaning loops per cell, lit on top, shaded below, dark seam between columns
    ctx.lineCap = 'round';
    for (let i = 0; i < W; i += cw) for (let j = -rh; j < H; j += rh) {
      const dy = Math.sin(i * 0.11 + j * 0.006 + t * 7) * amp * 0.3;
      for (const [lw, col, oy, al] of [[cw * 0.26, 'rgba(0,0,0,0.5)', 5, 0.45], [cw * 0.2, o.stitch || 'rgba(255,255,255,0.9)', 0, 0.6]]) {
        ctx.globalAlpha = k * al; ctx.strokeStyle = col; ctx.lineWidth = lw;
        ctx.beginPath(); ctx.moveTo(i + cw * 0.18, j + dy + oy); ctx.lineTo(i + cw * 0.46, j + dy + rh * 0.95 + oy); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(i + cw * 0.82, j + dy + oy); ctx.lineTo(i + cw * 0.54, j + dy + rh * 0.95 + oy); ctx.stroke();
      }
    }
    ctx.globalAlpha = k * 0.5; ctx.fillStyle = 'rgba(0,20,40,0.7)';
    for (let i = 0; i < W; i += cw) ctx.fillRect(i - 2, 0, 4, H);
    ctx.restore();
  };
  // pinwheel wedge wipe (REF-A 2.44–3.04 s): wedges of the next shot grow + rotate around a point
  A.pinwheel = (ctx, from, to, p, cx, cy, n = 8) => {
    ctx.drawImage(from, 0, 0);
    if (p <= 0) return;
    if (p >= 1) { ctx.drawImage(to, 0, 0); return; }
    const R = 2600, half = (Math.PI / n) * E.inOutC(p), rot = E.outC(p) * Math.PI * 0.5;
    ctx.save(); ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const a = rot + (i / n) * Math.PI * 2;
      ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(a - half) * R, cy + Math.sin(a - half) * R); ctx.lineTo(cx + Math.cos(a + half) * R, cy + Math.sin(a + half) * R); ctx.closePath();
    }
    ctx.clip(); ctx.drawImage(to, 0, 0); ctx.restore();
  };
  // white manga starburst flash (REF-A 8.12 s, 16.08 s, 18.04 s)
  A.starburst = (ctx, cx, cy, p, seed, o = {}) => {
    if (p <= 0 || p >= 1) return;
    const n = o.n || 26, rIn = lerp(o.r0 || 60, o.r1 || 1500, E.outC(p));
    ctx.save(); ctx.fillStyle = o.color || '#FFFFFF';
    ctx.globalAlpha = 1 - Math.pow(p, 3);
    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + rnd(seed + i) * 0.2, w = (Math.PI / n) * (0.5 + rnd(seed + i * 2) * 0.6);
      const ri = rIn * (0.6 + rnd(seed + i * 3) * 0.5);
      ctx.moveTo(cx + Math.cos(a) * ri, cy + Math.sin(a) * ri);
      ctx.lineTo(cx + Math.cos(a - w) * 2600, cy + Math.sin(a - w) * 2600);
      ctx.lineTo(cx + Math.cos(a + w) * 2600, cy + Math.sin(a + w) * 2600);
      ctx.closePath();
    }
    ctx.fill(); ctx.restore();
  };
  A.flash = (ctx, k, color = '#FFFFFF') => { if (k <= 0) return; ctx.save(); ctx.globalAlpha = clamp(k); ctx.fillStyle = color; ctx.fillRect(0, 0, W, H); ctx.restore(); };
  // white scan-stripes that turn a real photo into pixel art (REF-A 17.48 s / 18.2 s)
  A.scanConvert = (ctx, drawA, drawB, box, p, seed) => {
    const [x0, y0, x1, y1] = box, band = 150;
    const yb = lerp(y0 - band, y1 + band, E.inOutC(clamp(p)));
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, yb); ctx.clip(); drawB(ctx); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.rect(0, yb, W, H - yb); ctx.clip(); drawA(ctx); ctx.restore();
    if (p <= 0 || p >= 1) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 9; i++) {
      const yy = snap(yb - band / 2 + i * (band / 9), 6);
      const l = (x1 - x0) * (0.45 + 0.55 * rnd(seed + i * 3.7 + Math.floor(p * 20)));
      const xs = snap(x0 + (x1 - x0 - l) * rnd(seed + i * 1.9), 6);
      ctx.shadowColor = 'rgba(255,240,220,0.9)'; ctx.shadowBlur = 24;
      ctx.fillStyle = 'rgba(255,255,255,0.95)'; ctx.fillRect(xs, yy, l, 9);
    }
    ctx.restore();
  };
  // Bayer-dither dissolve: the pixel-native crossfade
  const bayer = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
  const patCache = new Map();
  A.dither = (ctx, from, to, p, cell = 12) => {
    ctx.drawImage(from, 0, 0);
    if (p <= 0) return; if (p >= 1) { ctx.drawImage(to, 0, 0); return; }
    const lvl = Math.round(p * 16), key = lvl + '_' + cell;
    let pat = patCache.get(key);
    if (!pat) {
      const c = A.canvas(4 * cell, 4 * cell), x = c.getContext('2d'); x.fillStyle = '#000';
      for (let k = 0; k < 16; k++) if (bayer[k] < lvl) x.fillRect((k % 4) * cell, Math.floor(k / 4) * cell, cell, cell);
      pat = c; patCache.set(key, c);
    }
    const b = A.buffer('_dither'), x = b.getContext('2d');
    x.drawImage(to, 0, 0); x.globalCompositeOperation = 'destination-in'; x.fillStyle = x.createPattern(pat, 'repeat'); x.fillRect(0, 0, W, H);
    ctx.drawImage(b, 0, 0);
  };
  // classic circle iris (close to black on a point, open on the next shot)
  A.iris = (ctx, cx, cy, r, s = 12) => {
    r = Math.max(0, snap(r, s));
    ctx.save(); ctx.fillStyle = '#000'; ctx.beginPath(); ctx.rect(0, 0, W, H);
    for (let y = -r; y <= r; y += s) { const hw = snap(Math.sqrt(Math.max(0, r * r - y * y)), s); ctx.rect(cx + hw, cy + y, -2 * hw, s); }
    ctx.fill('evenodd'); ctx.restore();
  };
  // CRT vertical-line glitch (REF-A 9.44–9.6 s): vertical scan texture + RGB-ish offset + torn slices
  let vlines = null;
  A.glitchV = (ctx, src, k, t, seed = 1) => {
    ctx.drawImage(src, 0, 0);
    if (k <= 0) return;
    for (let i = 0; i < 7; i++) {
      if (rnd(seed + i + Math.floor(t * 30)) > k) continue;
      const y = Math.floor(rnd(seed * 3 + i * 7 + Math.floor(t * 30)) * H), h = 30 + rnd(i + t) * 180, dx = (rnd(i * 9 + Math.floor(t * 30)) - 0.5) * 160 * k;
      ctx.drawImage(src, 0, y, W, h, dx, y, W, h);
    }
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.45 * k;
    ctx.drawImage(src, 18 * k, 0); ctx.restore();
    if (!vlines) { vlines = A.canvas(W, H); const x = vlines.getContext('2d'); for (let i = 0; i < W; i += 6) { x.fillStyle = i % 12 ? 'rgba(255,255,255,0.22)' : 'rgba(0,0,0,0.35)'; x.fillRect(i, 0, 3, H); } }
    ctx.save(); ctx.globalAlpha = k; ctx.drawImage(vlines, 0, 0); ctx.restore();
  };
  // CRT power-on: frame squashed into a bright line that opens up
  A.crtOn = (ctx, src, p) => {
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    if (p <= 0) return;
    const sy = Math.max(0.004, E.outExpo(p)), sx = lerp(0.3, 1, E.outC(clamp(p * 3)));
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sx, sy); ctx.drawImage(src, -W / 2, -H / 2); ctx.restore();
    A.flash(ctx, (1 - p) * 0.9);
  };
  // CRT glass (REF-B): scanlines + soft vignette + diagonal window reflection
  let glass = null;
  A.crtGlass = (ctx, k = 1) => {
    if (k <= 0) return;
    if (!glass) {
      glass = A.canvas(W, H); const x = glass.getContext('2d');
      for (let j = 0; j < H; j += 6) { x.fillStyle = 'rgba(0,0,0,0.10)'; x.fillRect(0, j, W, 2); }
      const g = x.createRadialGradient(W / 2, H / 2, W * 0.3, W / 2, H / 2, H * 0.68); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.45)');
      x.fillStyle = g; x.fillRect(0, 0, W, H);
      x.save(); x.translate(W * 0.78, H * 0.18); x.rotate(0.5); x.fillStyle = 'rgba(255,255,255,0.07)'; x.fillRect(-60, -500, 70, 1000); x.fillRect(40, -500, 26, 1000); x.restore();
    }
    ctx.save(); ctx.globalAlpha = k; ctx.drawImage(glass, 0, 0); ctx.restore();
  };

  // ---------------------------------------------------------------- display title slam (REF-A "SPICY McNUGGETS SIDE MISSION")
  // heavy rounded display face, cream-to-white face, deep extrusion, flies in rotated with a smear, settles with overshoot
  A.title = (ctx, str, x, y, size, o = {}) => {
    ctx.save();
    ctx.translate(x, y); if (o.rot) ctx.rotate(o.rot); if (o.scale) ctx.scale(o.scale, o.scale);
    if (o.alpha != null) ctx.globalAlpha *= o.alpha;
    ctx.font = `${size}px "Bungee"`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const d = Math.round(size * 0.12);
    ctx.lineJoin = 'round';
    for (let k = d; k >= 1; k -= 2) { ctx.fillStyle = k > d * 0.5 ? '#14080A' : '#2A0E0C'; ctx.fillText(str, k * 0.55, k); }
    ctx.lineWidth = size * 0.14; ctx.strokeStyle = o.stroke || '#C7180F'; ctx.strokeText(str, 0, 0);
    const g = ctx.createLinearGradient(0, -size / 2, 0, size / 2);
    (o.face || ['#FFFFFF', '#FFF2D6', '#F5C88A']).forEach((c, i, a) => g.addColorStop(i / (a.length - 1), c));
    ctx.fillStyle = g; ctx.fillText(str, 0, 0);
    ctx.restore();
  };
  A.slam = (t, t0, dur = 0.34) => {   // returns {p, scale, rot, alpha, smear} for a title slam
    const p = pr(t, t0, t0 + dur);
    if (p <= 0) return null;
    const e = E.outBack(p, 2.2);
    return { p, scale: lerp(2.6, 1, e), rot: lerp(-0.42, 0, E.outElastic(p)), alpha: Math.min(1, p * 4), smear: 1 - E.outC(clamp(p * 1.6)) };
  };
})();
