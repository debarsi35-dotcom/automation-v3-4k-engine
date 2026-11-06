/* "How Mario was born" — ARCADE MOTION GRAPHICS demo (30 s, 9:16).
 * Every scene is a function of global time t. Cue times come from WORDS (forced-aligned narration):
 * w(i) = onset of shown word i, we(i) = its end.
 */
(function () {
  const { W, H, clamp, lerp, pr, E, rnd, stepT, snap } = A;
  const w = (i) => WORDS[i].s, we = (i) => WORDS[i].e;
  const IMG = (window.IMG = {});
  const F = (window.FILM = { DUR: 30.0 });

  // ================================================================ sprites (original pixel art)
  const PAL = { R: '#E2311D', B: '#2D5BDA', S: '#FFBA8C', H: '#5A2A0E', K: '#16080A', Y: '#FFD23A', W: '#FFFFFF' };
  const CAP = ['.....RRRRR......', '....RRRRRRRRR...'];
  const HAIR = ['.....HHHHH......', '....HHHHHHHH....'];
  const HEAD = ['....HHHSSKS.....', '...HSHSSSKSSS...', '...HSHHSSSSSSSS.', '...HHSSSSSSSSS..', '.....SSSSSSSS...'];
  const BODY = ['.....RRBRRR.....', '....RRRBRRBRRR..', '...RRRRBBBBRRRR.', '...SSRBYBBYBRSS.', '...SSSBBBBBBSSS.', '...SSBBBBBBBBSS.'];
  const LEGS = {
    a: ['.....BBB..BBB...', '....HHH....HHH..', '...HHHH....HHHH.'],
    b: ['......BBBBB.....', '......HHHHH.....', '.....HHHHHH.....'],
    j: ['..BBBB....BBB...', '.HHH.......HHH..', '.HH.........HHH.'],
  };
  const set = (row, i, ch) => row.slice(0, i) + ch + row.slice(i + 1);
  // build the 16x16 hero: cap/hair, moustache, mouth, legs
  function hero(o = {}) {
    const rows = [];
    if (o.cap) rows.push(...CAP);
    else if (o.hair === 'glitch') {
      const s = o.seed || 0;
      for (let j = 0; j < 2; j++) { let r = '................'; for (let i = 3; i < 13; i++) if (rnd(s * 31 + j * 17 + i) > 0.45) r = set(r, i, 'H'); rows.push(r); }
    } else if (o.hair) rows.push(...HAIR);
    else rows.push('................', '................');
    const head = HEAD.slice();
    if (o.mst) { head[2] = set(head[2], 11, 'H'); head[3] = head[3].slice(0, 9) + 'HHHHH' + head[3].slice(14); }
    if (o.mouth != null && o.mouth >= 0) {
      const m = [[9, 10], [10, 11, 12], [10], [9, 11]][o.mouth % 4];
      for (const i of m) head[4] = set(head[4], i, 'K');
    }
    rows.push(...head);
    const body = BODY.slice();
    if (o.legs === 'j') { body[0] = '.....RRBRRR.SS..'; body[1] = '....RRRBRRBRRSS.'; body[3] = '..SSRBYBBYBR....'; body[4] = '..SSBBBBBBBB....'; body[5] = '...BBBBBBBBBB...'; }
    rows.push(...body, ...LEGS[o.legs || 'a']);
    return rows;
  }
  const heroSpr = (key, o) => A.spr[key] || A.defSprite(key, hero(o), PAL);
  const MARIO = () => heroSpr('mario_a', { cap: 1, mst: 1, legs: 'a' });

  A.defSprite('cab', [
    '..KKKKKKKKKK..', '.KMMMMMMMMMMK.', '.KMYMYMMYMYMK.', '.KMMMMMMMMMMK.', '.KKKKKKKKKKKK.', '.KRKKKKKKKKRK.',
    '.KRKSSSSSSKRK.', '.KRKSLSSSSKRK.', '.KRKSSSSLSKRK.', '.KRKSSSSSSKRK.', '.KRKSSLSSSKRK.', '.KRKKKKKKKKRK.',
    'KRRRRRRRRRRRRK', 'KRWRRRRYRRORRK', 'KKKKKKKKKKKKKK', '.KRRRRRRRRRRK.', '.KRRKKKKKKRRK.', '.KRRKYKKYKRRK.',
    '.KRRKKKKKKRRK.', '.KRRRRRRRRRRK.', '.KRRRRRRRRRRK.', '.KRRRRRRRRRRK.', '.KKKKKKKKKKKK.',
  ], { K: '#120A14', M: '#2B4FD8', Y: '#FFD23A', R: '#D62A20', S: '#3B9BFF', L: '#B9E6FF', W: '#F2F2F2', O: '#3B9BFF' });
  A.defSprite('barrel', ['..OOOOOOOO..', '.OODDDDDDOO.', 'OOOOOOOOOOOO', 'ODOOWWOOOODO', 'ODOOOOOOOODO', 'ODOOOOOOOODO', 'OOOOOOOOOOOO', '.OODDDDDDOO.', '..OOOOOOOO..'],
    { O: '#D07624', D: '#6E2E0A', W: '#FAD08A' });
  A.defSprite('girder', ['RRRRRRRR', 'R.R..R.R', '.R.RR.R.', '..R..R..', '.R.RR.R.', 'R.R..R.R', 'RRRRRRRR'], { R: '#E8376A' });
  A.defSprite('flame', [
    '......K.......', '.....KRK......', '....KRRK..K...', '...KRRRK.KRK..', '...KRRYRKRRK..', '..KRRYYRRRRK..', '..KRYYYRRYRK..', '.KRRYYYYRYYRK.',
    '.KRYYYYYYYYRK.', 'KRRYYYWWYYYRRK', 'KRYYYWWWWYYYRK', 'KRYYWWWWWWYYRK', 'KRYYWWWWWWYYRK', '.KRYYWWWWYYRK.', '.KRRYYYYYYRRK.',
    '..KRRYYYYRRK..', '...KKRRRRKK...', '.....KKKK.....',
  ], { K: '#1A0606', R: '#E8384A', Y: '#FFB23A', W: '#FFE7A0' });
  A.defSprite('car', [
    '.......KKKKKKKK.........', '......KRRRRRRRRK........', '.....KRCCKCCCCKRK.......', '....KRRCCKCCCCKRRKKKK...',
    '..KKRRRRRRRRRRRRRRRRRK..', '.KRRRRRRRRRRRRRRRRRRRRK.', '.KYRRRRRRRRRRRRRRRRRRWK.', '.KKKKGGGKKKKKKKKKGGGKKK.',
    '....GGWGG.......GGWGG...', '.....GGG.........GGG....',
  ], { K: '#1C0A0A', R: '#E23A2C', C: '#BFF3FF', Y: '#FFE27A', W: '#FFFFFF', G: '#2A2A30' });
  A.defSprite('pencil', ['KKKKKKKKKKKKKK....', 'KYYYYYYYYYYYYPWK..', 'KOOOOOOOOOOOOPWWKK', 'KYYYYYYYYYYYYPWK..', 'KKKKKKKKKKKKKK....'],
    { K: '#1A1010', Y: '#FFD23A', O: '#E39A16', P: '#F28FA0', W: '#F6E2C0' });

  function coin(ctx, x, y, s, ph) {      // spinning pixel coin, 4 frames
    const wds = [8, 6, 2, 6], wd = wds[Math.floor(ph * 4) % 4], h = 14;
    const X = Math.round(x - (wd * s) / 2), Y = Math.round(y - (h * s) / 2);
    ctx.fillStyle = '#3A2304'; ctx.fillRect(X - s, Y + s, (wd + 2) * s, (h - 2) * s); ctx.fillRect(X, Y, wd * s, h * s);
    ctx.fillStyle = '#FFC928'; ctx.fillRect(X + (wd > 2 ? s : 0), Y + s, Math.max(1, wd - (wd > 2 ? 2 : 0)) * s, (h - 2) * s);
    if (wd > 2) { ctx.fillStyle = '#FFF3A0'; ctx.fillRect(X + s, Y + 2 * s, s, (h - 4) * s); ctx.fillStyle = '#D9860E'; ctx.fillRect(X + (wd - 2) * s, Y + 2 * s, s, (h - 4) * s); }
  }

  // ================================================================ cached layers
  let L = null;
  function build() {
    L = {};
    // --- city (art px, P = 6)
    const sk = A.canvas(180, 100), x = sk.getContext('2d');
    for (let i = 0, px = -4; px < 184; i++) {
      const bw = 8 + Math.floor(rnd(i * 3.1) * 16), bh = 26 + Math.floor(rnd(i * 7.3 + 2) * 70);
      x.fillStyle = '#40B4E1'; x.fillRect(px, 100 - bh, bw, bh);
      x.fillStyle = '#76D3F2';
      for (let yy = 100 - bh + 3; yy < 98; yy += 4) for (let xx = px + 2; xx < px + bw - 1; xx += 3) if (rnd(xx * 13 + yy * 7) > 0.5) x.fillRect(xx, yy, 1, 2);
      px += bw + Math.floor(rnd(i * 5.7) * 3);
    }
    L.skyline = sk;
    const b = A.canvas(150, 72), y = b.getContext('2d');
    y.fillStyle = '#B4512A'; y.fillRect(0, 20, 150, 52);
    y.fillStyle = '#8F3A1B';
    for (let r = 0; r < 17; r++) { y.fillRect(0, 22 + r * 3, 150, 1); for (let c = (r % 2) * 3; c < 150; c += 6) y.fillRect(c, 22 + r * 3, 1, 3); }
    y.fillStyle = '#3A1C10'; y.fillRect(0, 18, 150, 3);
    y.fillStyle = '#5A2E1A'; y.fillRect(-1, 20, 152, 1);
    // windows
    for (const wx of [12, 30, 108, 126]) { y.fillStyle = '#2A1410'; y.fillRect(wx - 1, 31, 14, 12); y.fillStyle = '#9EEBFF'; y.fillRect(wx, 32, 12, 10); y.fillStyle = '#DDF8FF'; y.fillRect(wx + 1, 33, 3, 3); }
    // roll-up door
    y.fillStyle = '#2B2F3A'; y.fillRect(51, 38, 48, 34);
    for (let r = 0; r < 11; r++) { y.fillStyle = r % 2 ? '#7E8592' : '#9BA2AE'; y.fillRect(53, 40 + r * 3, 44, 3); }
    // sign board
    y.fillStyle = '#E9E3F5'; y.fillRect(32, 0, 86, 18); y.fillStyle = '#1E5A3C'; y.fillRect(34, 2, 82, 14);
    y.fillStyle = '#3A1C10'; y.fillRect(44, 18, 2, 2); y.fillRect(104, 18, 2, 2);
    L.building = b;
    L.clouds = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => A.makeCloud(i * 13 + 5, 30 + Math.floor(rnd(i * 2.2) * 22), 15 + Math.floor(rnd(i * 4.4) * 6)));
    L.nesClouds = [0, 1, 2].map((i) => A.makeCloud(i * 7 + 101, 34, 16));
    // --- pixelated NES for the scan conversion
    L.nesPix = A.pixelate(IMG.nes, 96, 4, 1.4);
    L.heat = A.halftone('#F06A1E', '#C2260E', 'rgba(255,214,120,0.22)', 18);
    L.red = A.halftone('#E2531A', '#AE1C0E', 'rgba(120,10,6,0.35)', 18);
    L.wine = A.halftone('#2A0B12', '#120509', 'rgba(110,26,38,0.55)', 20);
    L.wood = A.stripes('#A65C28', '#7C3D17', 42);
    L.graph = A.graph('#0F1433', '#18204C', 54);
    L.miyaSil = A.silhouette(IMG.miya, '#1A0E08');
    L.nesSil = A.silhouette(IMG.nes, '#1A0E08');
  }

  // ================================================================ helpers
  const scr = (ctx, fn) => { ctx.save(); fn(); ctx.restore(); };
  const smooth = (ctx, on = true) => { ctx.imageSmoothingEnabled = on; ctx.imageSmoothingQuality = 'high'; };
  function shake(t, t0, amp = 22, dur = 0.28, seed = 1) {
    const p = pr(t, t0, t0 + dur); if (p <= 0 || p >= 1) return [0, 0];
    const k = (1 - p) * amp, f = Math.floor(t * 30);
    return [snap((rnd(f * 3 + seed) - 0.5) * 2 * k, 6), snap((rnd(f * 7 + seed) - 0.5) * 2 * k, 6)];
  }
  function tag(ctx, str, x, y, cell = 5, alpha = 1) {      // dark label box with white pixel text
    const B = A.textBmp(str, 'plainWhite'); const tw = B.w * cell, th = B.h * cell;
    ctx.save(); ctx.globalAlpha *= alpha;
    ctx.fillStyle = '#100A1E'; ctx.fillRect(Math.round(x - tw / 2 - 24), Math.round(y - th / 2 - 18), tw + 48, th + 36);
    ctx.fillStyle = '#FFFFFF'; ctx.fillRect(Math.round(x - tw / 2 - 24), Math.round(y + th / 2 + 18), tw + 48, 6);
    ctx.restore();
    A.ptext(ctx, str, x, y, cell, 'plainWhite', { alpha });
  }
  function pop(ctx, t, t0, str, x, y, cell, style = 'fire', o = {}) {   // a super that pops in (stepped scale) and optionally out
    const c = A.popCell(t, t0, cell, o.k || 1.9, o.dur || 0.2);
    if (!c) return;
    const out = o.out ? pr(t, o.out, o.out + 0.12) : 0;
    if (out >= 1) return;
    A.ptext(ctx, str, x, y - out * 40, c, style, { alpha: 1 - out, reveal: o.reveal, align: o.align, rot: o.rot });
  }
  function sky(ctx, top, bot) { const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, top); g.addColorStop(1, bot); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }

  // ================================================================ SCENES
  const SC = {};

  // ---- 1A: 1981, a pixel city; tilt down from the sky, the warehouse rises (REF-A 0.4–2.4 s)
  SC.city = (ctx, t) => {
    const P = 6;
    const camY = lerp(-1300, 0, E.outC(pr(t, 0.1, 1.5)));
    const z = 1 + 0.9 * E.inC(pr(t, 1.95, 2.45));
    ctx.save();
    ctx.translate(540, 1415); ctx.scale(z, z); ctx.translate(-540, -1415);
    ctx.fillStyle = A.C.sky; ctx.fillRect(-W, -H, 3 * W, 3 * H);
    // stepped horizon bands
    [['#38CEF3', 760], ['#52D6F5', 900], ['#6CDDF7', 1010]].forEach(([c, y0]) => { ctx.fillStyle = c; ctx.fillRect(-W, y0 - camY, 3 * W, 1500); });
    // clouds (parallax)
    const cl = [[80, -1180, 0], [620, -980, 1], [300, -700, 2], [760, -420, 3], [40, -180, 4], [520, 120, 5], [880, 330, 6], [180, 520, 7]];
    cl.forEach(([x0, y0, i]) => {
      const c = L.clouds[i];
      const x = snap(((x0 - t * (22 + i * 6)) % 1300 + 1300) % 1300 - 180, P), y = snap(y0 - camY * 0.85, P);
      ctx.drawImage(c, x, y, c.width * P, c.height * P);
    });
    // skyline
    const sy = 1500 - 100 * P - camY * 0.95;
    ctx.drawImage(L.skyline, 0, snap(sy, P), 180 * P, 100 * P);
    // warehouse rising
    const rise = lerp(420, 0, E.outBack(pr(t, 0.42, 1.12), 1.4));
    const by = snap(1500 - 72 * P - camY + rise, P);
    ctx.drawImage(L.building, 15 * P, by, 150 * P, 72 * P);
    const lit = t >= w(1);
    A.ptext(ctx, 'NINTENDO', 540, by + 9 * P, 6, lit ? 'plainYellow' : 'plainWhite');
    if (lit && t < w(1) + 0.08) A.flash(ctx, 0.35);
    // street
    const gy = 1500 - camY;
    ctx.fillStyle = '#C9CBD6'; ctx.fillRect(-W, gy, 3 * W, 24);
    ctx.fillStyle = '#3A3A46'; ctx.fillRect(-W, gy + 24, 3 * W, 150);
    ctx.fillStyle = '#F2F2F2'; for (let x = -12 * 6; x < W; x += 30 * 6) ctx.fillRect(x + 6 * 6, gy + 24 + 72, 14 * 6, 6);
    ctx.fillStyle = '#2E8C3E'; ctx.fillRect(-W, gy + 174, 3 * W, 900);
    ctx.fillStyle = '#3DAA4A'; for (let x = 0; x < W; x += 12 * 6) ctx.fillRect(x, gy + 174, 6 * 6, 6);
    // car drives in and parks
    const cx = lerp(-260, 150, E.outC(pr(t, 0.85, 1.55)));
    A.drawSpr(ctx, 'car', snap(cx, P), gy + 24 + 6, P);
    ctx.restore();
    pop(ctx, t, w(0), '1981', 540, 560, 22, 'fire', { k: 2.4, dur: 0.22 });
    if (t > w(0)) A.sparks(ctx, 540, 560, 420, t, 14, 3, { squash: 0.35 });
    // shutter slams down as we reach the door
    const sp = E.inC(pr(t, 2.26, 2.45));
    if (sp > 0) shutter(ctx, H * sp);
  };
  function shutter(ctx, edge) {
    ctx.save();
    const slat = 48;
    for (let y = edge - slat; y > -slat; y -= slat) { ctx.fillStyle = Math.round((edge - y) / slat) % 2 ? '#7E8592' : '#9BA2AE'; ctx.fillRect(0, y, W, slat); ctx.fillStyle = '#5A606C'; ctx.fillRect(0, y + slat - 6, W, 6); }
    ctx.fillStyle = '#2B2F3A'; ctx.fillRect(0, edge - 30, W, 30);
    ctx.fillStyle = '#C9CED8'; ctx.fillRect(470, edge - 22, 140, 10);
    ctx.restore();
  }

  // ---- 1B: the warehouse fills with 2,000 unsold cabinets
  const CAB_ROWS = [[4, 880], [5, 1010], [6, 1170], [8, 1380], [10, 1640], [12, 1960]];
  let CABS = null;
  function cabs() {
    if (CABS) return CABS;
    CABS = [];
    CAB_ROWS.forEach(([s, base], r) => {
      const sp = s * 14 * 1.12, n = Math.ceil(W / sp) + 1, off = (r % 2 ? sp / 2 : 0) - sp * 0.3;
      // every row fills at once, left to right, rows a beat apart: the floor is never empty
      for (let i = 0; i < n; i++) CABS.push({ r, s, x: off + i * sp, base, t: 2.47 + r * 0.13 + (i / n) * 0.85 + rnd(r * 31 + i) * 0.12 });
    });
    return CABS;
  }
  SC.ware = (ctx, t) => {
    sky(ctx, '#140F2A', '#2C2250');
    ctx.fillStyle = '#251C44'; ctx.fillRect(0, 980, W, H);
    ctx.fillStyle = '#2F2556'; for (let y = 1000; y < H; y += 60) ctx.fillRect(0, y, W, 4);
    // ceiling lamps + cones
    [200, 540, 880].forEach((lx, i) => {
      ctx.fillStyle = 'rgba(255,214,120,0.09)';
      ctx.beginPath(); ctx.moveTo(lx - 30, 250); ctx.lineTo(lx + 30, 250); ctx.lineTo(lx + 260, 1100); ctx.lineTo(lx - 260, 1100); ctx.fill();
      ctx.fillStyle = '#3A3050'; ctx.fillRect(lx - 4, 0, 8, 236); ctx.fillStyle = '#FFD878'; ctx.fillRect(lx - 36, 236, 72, 18);
    });
    const z = 1 + 0.06 * pr(t, 2.45, 4.6);
    ctx.save(); ctx.translate(540, 1200); ctx.scale(z, z); ctx.translate(-540, -1200);
    for (const c of cabs()) {
      const p = pr(t, c.t, c.t + 0.1); if (p <= 0) continue;
      const dy = snap((1 - E.outBack(p, 2)) * -60, c.s);
      A.drawSpr(ctx, 'cab', snap(c.x, c.s), c.base - 23 * c.s + dy, c.s);
      // screen flicker
      if (rnd(c.x + Math.floor(t * 12)) > 0.7) { ctx.fillStyle = 'rgba(190,230,255,0.25)'; ctx.fillRect(snap(c.x, c.s) + 4 * c.s, c.base - 23 * c.s + 6 * c.s + dy, 6 * c.s, 5 * c.s); }
    }
    ctx.restore();
    A.vignette(ctx, 0.5);
    // the count
    const n = 2000 * E.outC(pr(t, w(5), we(6) + 0.05));
    if (t >= w(5)) A.ptext(ctx, A.fmt(n), 540, 470, A.popCell(t, w(5), 20, 1.6, 0.16), 'fire');
    pop(ctx, t, w(7), 'ARCADE MACHINES', 540, 620, 6, 'white', { k: 1.6 });
    // shutter rolls up to open the scene
    const op = E.inOutC(pr(t, 2.45, 2.72));
    if (op < 1) shutter(ctx, H * (1 - op));
  };

  // ---- 1C: the real 1981 Radar Scope trade ad + GAME OVER stamp
  function adXf(t) { return { s: 1 + 0.07 * pr(t, 4.5, 5.7), r: -0.1, cx: 540, cy: 930, size: 1000 }; }
  function adPoint(t, px, py) {      // ad-crop pixel (920 space) -> screen
    const a = adXf(t), k = (a.size / 920) * a.s, x = (px - 460) * k, y = (py - 460) * k;
    return [a.cx + x * Math.cos(a.r) - y * Math.sin(a.r), a.cy + x * Math.sin(a.r) + y * Math.cos(a.r)];
  }
  SC.ad = (ctx, t) => {
    const [sx, sy] = shake(t, w(10), 26, 0.3, 5);
    ctx.drawImage(L.wine, 0, 0);
    A.speedLines(ctx, 540, 930, t, 7, { color: 'rgba(255,120,120,0.12)', n: 36 });
    const a = adXf(t);
    ctx.save(); ctx.translate(a.cx + sx, a.cy + sy); ctx.rotate(a.r); ctx.scale(a.s, a.s);
    const S = a.size;
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(-S / 2 + 22, -S / 2 + 30, S, S);
    ctx.fillStyle = '#FFFFFF'; ctx.fillRect(-S / 2 - 12, -S / 2 - 12, S + 24, S + 24);
    smooth(ctx); ctx.drawImage(IMG.ad, -S / 2, -S / 2, S, S);
    ctx.restore();
    A.ptext(ctx, 'RADAR SCOPE - 1981 TRADE AD', 540, 300, 4, 'plainWhite', { alpha: Math.min(1, pr(t, 4.58, 4.7) * 2) });
    const [hx, hy] = adPoint(t, 596, 616);
    A.lockOn(ctx, hx + sx, hy + sy, 190, t, w(9), w(10) + 0.25);
    if (t >= w(10)) {
      const c = A.popCell(t, w(10), 13, 2.6, 0.14);
      A.ptext(ctx, 'GAME OVER', 540 + sx, hy + sy, c, 'red', { rot: -0.2 });
      A.puff(ctx, 540, hy, pr(t, w(10), w(10) + 0.45), { r: 420, n: 14, cell: 14, size: 4 });
    }
  };

  // ---- 2: Shigeru Miyamoto, real cut-out on the REF-A counter world, nameplate + RPG dialog
  const MIYA = { w: 860 };
  function miyaRect(t) {
    const s = MIYA.w / IMG.miya.width, h = IMG.miya.height * s;
    const rise = lerp(170, 0, E.outBack(pr(t, 5.45, 5.95), 1.5));
    const br = 1 + 0.006 * Math.sin(t * 2.2);
    return { x: 540 - (MIYA.w * br) / 2, y: 1600 - h * br + rise, w: MIYA.w * br, h: h * br, s: s * br };
  }
  SC.miya = (ctx, t) => {
    const pz = 1 + 0.06 * E.inOutC(pr(t, 5.5, 8.5));
    ctx.save(); ctx.translate(540, 1000); ctx.scale(pz, pz); ctx.translate(-540, -1000);
    ctx.drawImage(L.wood, -60, -60, W + 120, H + 120);
    // a pixel poster on the wall: the enemy ship from the real ad, as a hint of what came before
    const r = miyaRect(t);
    smooth(ctx);
    for (const [dx, dy] of [[-10, 0], [10, 0], [0, -10], [0, 10], [-7, -7], [7, 7], [7, -7], [-7, 7]]) ctx.drawImage(L.miyaSil, r.x + dx, r.y + dy, r.w, r.h);
    ctx.drawImage(IMG.miya, r.x, r.y, r.w, r.h);
    smooth(ctx, false);
    // desk
    ctx.fillStyle = '#4A3226'; ctx.fillRect(0, 1560, W, 14); ctx.fillStyle = '#2A1A14'; ctx.fillRect(0, 1574, W, 140); ctx.fillStyle = '#1A100C'; ctx.fillRect(0, 1714, W, H);
    // paper with the hero being drawn on it
    const px = 640, py = 1452;
    ctx.fillStyle = '#16101F'; ctx.fillRect(px - 6, py - 6, 252, 168); ctx.fillStyle = '#F7F3E8'; ctx.fillRect(px, py, 240, 156);
    ctx.fillStyle = '#C9D8F5'; for (let y = py + 18; y < py + 150; y += 18) ctx.fillRect(px + 6, y, 228, 3);
    const rows = hero({ cap: 1, mst: 1, legs: 'a' }), n = rows.join('').replace(/\./g, '').length;
    const k = Math.floor(n * pr(t, w(14), we(17)));
    let c = 0;
    A.drawCells(ctx, rows, { R: '#E2311D', B: '#2D5BDA', S: '#E9B48E', H: '#5A2A0E', K: '#16080A', Y: '#FFD23A' }, px + 72, py + 30, 6, () => c++ < k);
    if (k > 0 && k < n) A.drawSpr(ctx, 'pencil', px + 72 + ((k % 16) * 6), py + 30 + Math.floor(k / 11) * 6 - 20, 5);
    ctx.restore();
    // nameplate
    const np = pr(t, w(12) - 0.05, w(12) + 0.2);
    if (np > 0) {
      const nx = snap(lerp(-1000, 60, E.outC(np)), 30), ny = 1300;
      ctx.fillStyle = '#05030A'; ctx.fillRect(nx - 8, ny - 8, 976, 186);
      ctx.fillStyle = '#FFFFFF'; ctx.fillRect(nx - 2, ny - 2, 964, 174);
      ctx.fillStyle = '#141A40'; ctx.fillRect(nx + 6, ny + 6, 948, 158);
      A.ptext(ctx, 'PLAYER 1', nx + 40, ny + 48, 4, 'plainYellow', { align: 'l' });
      A.ptext(ctx, 'SHIGERU MIYAMOTO', nx + 40, ny + 112, 6, 'white', { align: 'l', reveal: Math.floor(16 * pr(t, w(12), w(13) + 0.3)) });
    }
    // dialog box, typed on "draws a new game"
    const dt = pr(t, 7.02, 7.22);
    const sq = E.inC(pr(t, 8.28, 8.42));
    if (dt > 0 && t < 8.42) {
      const l1 = A.type('Drawing a new game...', t, w(14), we(17) + 0.05);
      const l2 = t >= w(19) && Math.floor(t * 6) % 2 === 0 ? '   PRESS START' : '';
      A.dialog(ctx, 70, 200, 940, 230, [l1, l2], { t: dt, tail: [300, 1], squash: sq, size: 60, lh: 84 });
      if (l2) { ctx.fillStyle = A.C.dlgInk; const tx = 116, ty = 330; ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(tx + 34, ty + 22); ctx.lineTo(tx, ty + 44); ctx.fill(); }
    }
    if (t >= 8.42) {      // the bubble pops into white rings (REF-A 5.6–5.9 s)
      const p = pr(t, 8.42, 8.62);
      A.ring(ctx, 540, 315, lerp(60, 520, E.outC(p)), 16, '#FFFFFF', 1 - p);
      A.puff(ctx, 540, 315, p, { r: 520, n: 12, cell: 16, size: 4, squash: 0.5 });
      A.flash(ctx, (1 - p) * 0.5);
    }
  };

  // ---- 3+4: the 16x16 grid, the hero built pixel by pixel, then zoom to the face: cap + moustache
  const G = { x: 108, y: 594, c: 54 };
  const FOCUS = [621, 783], TGT = [540, 900];
  function cam16(t) {
    const e = E.inOutC(pr(t, 10.7, 11.12)), z = lerp(1, 1.45, e);
    return { z, tx: lerp(FOCUS[0], TGT[0], e), ty: lerp(FOCUS[1], TGT[1], e) };
  }
  const toScr = (cm, x, y) => [(x - FOCUS[0]) * cm.z + cm.tx, (y - FOCUS[1]) * cm.z + cm.ty];
  const cellScr = (cm, i, j) => toScr(cm, G.x + (i + 0.5) * G.c, G.y + (j + 0.5) * G.c);
  SC.pix16 = (ctx, t) => {
    const cm = cam16(t);
    // background: navy graph -> warm halftone (dither swap, REF-A colour-state change)
    const bp = pr(t, 10.95, 11.22);
    if (bp <= 0) ctx.drawImage(L.graph, 0, 0); else if (bp >= 1) ctx.drawImage(L.heat, 0, 0); else A.dither(ctx, L.graph, L.heat, bp, 18);
    if (t > 11.1) A.speedLines(ctx, 540, 900, t, 11, { color: 'rgba(255,240,200,0.28)', n: 40, r0: 520 });
    ctx.save(); ctx.translate(cm.tx, cm.ty); ctx.scale(cm.z, cm.z); ctx.translate(-FOCUS[0], -FOCUS[1]);
    // grid frame drawing on from the centre
    const ga = 1 - pr(t, 11.0, 11.3);
    if (ga > 0) {
      ctx.globalAlpha = ga;
      for (let k = 0; k <= 16; k++) {
        const p = E.outC(pr(t, 8.55 + k * 0.014, 8.9 + k * 0.014)); if (p <= 0) continue;
        const len = 864 * p, edge = k === 0 || k === 16;
        ctx.fillStyle = edge ? '#FFFFFF' : '#3550C8';
        const lw = edge ? 8 : 4;
        ctx.fillRect(G.x + k * G.c - lw / 2, G.y + 432 - len / 2, lw, len);
        ctx.fillRect(G.x + 432 - len / 2, G.y + k * G.c - lw / 2, len, lw);
      }
      ctx.globalAlpha = 1;
    }
    // the hero, cell by cell
    const capT = w(32), mstT = w(39);
    const glitch = t < capT;
    const rows = hero({ cap: 0, hair: glitch && t > 10.85 ? 'glitch' : 1, seed: Math.floor(t * 12), mst: 0, mouth: t >= 12.45 && t < mstT ? Math.floor(t * 10) : -1, legs: 'a' });
    const order = [];
    rows.forEach((r, j) => [...r].forEach((ch, i) => { if (ch !== '.') order.push(i + ',' + j); }));
    const fillT0 = 9.95, fillT1 = 10.6, nShown = Math.floor(order.length * pr(t, fillT0, fillT1));
    const shown = new Set(order.slice(0, t > fillT1 ? order.length : nShown));
    const fresh = new Set(order.slice(Math.max(0, nShown - 4), nShown));
    rows.forEach((r, j) => [...r].forEach((ch, i) => {
      const col = PAL[ch]; if (!col) return;
      if (j < 2 ? t < fillT1 && !shown.has(i + ',' + j) : !shown.has(i + ',' + j)) return;
      ctx.fillStyle = fresh.has(i + ',' + j) && t < fillT1 ? '#FFFFFF' : col;
      ctx.fillRect(G.x + i * G.c, G.y + j * G.c, G.c, G.c);
    }));
    // cap drops in
    if (t >= capT - 0.2) {
      const p = pr(t, capT - 0.2, capT), off = snap(lerp(-9, 0, E.inQ(p)), 1);
      const bounce = t > capT && t < capT + 0.06 ? 0.3 : 0;
      CAP.forEach((r, j) => [...r].forEach((ch, i) => { if (ch === '.') return; ctx.fillStyle = PAL.R; ctx.fillRect(G.x + i * G.c, G.y + (j + off + bounce) * G.c, G.c, G.c); }));
      if (p < 1) A.motionLines(ctx, G.x + 9.5 * G.c, G.y + (off - 0.4) * G.c, 300, 150, 1, 8);
    }
    // moustache slaps on
    if (t >= mstT - 0.08) {
      const p = E.outC(pr(t, mstT - 0.08, mstT)), dx = lerp(-7, 0, p);
      ctx.fillStyle = PAL.H;
      ctx.fillRect(G.x + (11 + dx) * G.c, G.y + 4 * G.c, G.c, G.c);
      ctx.fillRect(G.x + (9 + dx) * G.c, G.y + 5 * G.c, 5 * G.c, G.c);
    }
    ctx.restore();
    // rulers
    const ra = 1 - pr(t, 10.6, 10.8);
    if (ra > 0) for (let i = 1; i <= 16; i++) {
      if (t >= w(22) + i * 0.02) A.ptext(ctx, String(i), G.x + (i - 0.5) * G.c, G.y - 34, 3, 'plainCyan', { alpha: ra });
      if (t >= w(24) + i * 0.018) A.ptext(ctx, String(i), 58, G.y + (i - 0.5) * G.c, 3, 'plainCyan', { alpha: ra });
    }
    // supers: 16 x 16 ... PIXELS
    const so = 10.62;
    pop(ctx, t, w(22), '16', 300, 340, 18, 'fire', { out: so });
    pop(ctx, t, w(23), 'x', 540, 350, 11, 'white', { out: so });
    pop(ctx, t, w(24), '16', 780, 340, 18, 'fire', { out: so });
    pop(ctx, t, w(25), 'PIXELS', 540, 1570, 12, 'fire', { out: 10.72 });
    if (t > w(25) && t < 10.8) A.sparks(ctx, 540, 1000, 560, t, 16, 21);
    // face: hair problem -> cap
    const [hx, hy] = cellScr(cm, 8, 0.6);
    A.lockOn(ctx, hx, hy, 150, t, w(27), capT - 0.06);
    if (t >= w(28) && t < capT) tag(ctx, 'HAIR? TOO HARD', 540, 470, 5);
    if (t >= capT) {
      const [cx, cy] = cellScr(cm, 8.5, 1);
      A.puff(ctx, cx, cy, pr(t, capT, capT + 0.4), { r: 420, n: 12, cell: 14, size: 3, squash: 0.45 });
      pop(ctx, t, capT + 0.02, '+1 CAP', 540, 470, 10, 'fire', { out: 12.5 });
    }
    // mouth problem -> moustache
    const [mx, my] = cellScr(cm, 10.5, 5.6);
    A.lockOn(ctx, mx, my, 130, t, w(34), mstT - 0.04);
    if (t >= w(37) && t < mstT) tag(ctx, 'MOUTH? NO ROOM', 540, 1460, 5);
    if (t >= mstT) {
      A.puff(ctx, mx, my, pr(t, mstT, mstT + 0.4), { r: 380, n: 12, cell: 14, size: 3, squash: 0.5 });
      pop(ctx, t, mstT + 0.02, '+1 MOUSTACHE', 540, 1460, 9, 'fire');
      A.sparks(ctx, 540, 900, 520, t, 18, 33);
    }
  };

  // ---- 5: "Jumpman" — a girder level, jump the barrel
  const DKP = 7;
  const girderY = (base, slope, x) => base + slope * Math.floor(x / (8 * DKP));
  function girder(ctx, base, slope) {
    for (let x = 0; x < W + 56; x += 8 * DKP) A.drawSpr(ctx, 'girder', x, girderY(base, slope, x), DKP);
  }
  function ladder(ctx, x, y0, y1) {
    ctx.fillStyle = '#46E0F0';
    ctx.fillRect(x, y0, DKP, y1 - y0); ctx.fillRect(x + 6 * DKP, y0, DKP, y1 - y0);
    for (let y = y0 + 2 * DKP; y < y1; y += 4 * DKP) ctx.fillRect(x, y, 7 * DKP, DKP);
  }
  SC.dk = (ctx, t) => {
    ctx.fillStyle = '#050308'; ctx.fillRect(0, 0, W, H);
    girder(ctx, 560, -7); girder(ctx, 980, 7); girder(ctx, 1420, -7);
    ladder(ctx, 260, girderY(560, -7, 260) + 49, girderY(980, 7, 260));
    ladder(ctx, 840, girderY(980, 7, 840) + 49, girderY(1420, -7, 840));
    // oil drum + flame
    const oy = girderY(1420, -7, 60);
    ctx.fillStyle = '#2B4FD8'; ctx.fillRect(40, oy - 16 * DKP, 16 * DKP, 16 * DKP);
    ctx.fillStyle = '#9DB6FF'; ctx.fillRect(40, oy - 13 * DKP, 16 * DKP, DKP); ctx.fillRect(40, oy - 4 * DKP, 16 * DKP, DKP);
    A.ptext(ctx, 'OIL', 40 + 8 * DKP, oy - 8 * DKP, 4, 'plainWhite');
    A.drawSpr(ctx, 'flame', 40 + 8 * DKP, oy - 16 * DKP, 4, { anchor: 'bc', flip: Math.floor(t * 10) % 2 === 0 });
    // barrels
    const bx = 1180 - (t - 14.1) * 900;
    A.drawSpr(ctx, 'barrel', snap(bx, DKP), girderY(1420, -7, bx) - 9 * DKP, DKP, { flip: Math.floor(t * 16) % 2 === 0 });
    const bx2 = -100 + (t - 14.1) * 520;
    A.drawSpr(ctx, 'barrel', snap(bx2, DKP), girderY(980, 7, bx2) - 9 * DKP, DKP, { flip: Math.floor(t * 16) % 2 === 1 });
    // Jumpman
    const jx = 280 + (t - 14.1) * 300, jp = pr(t, 14.58, 15.0);
    const jy = girderY(1420, -7, jx + 56) - Math.sin(Math.PI * jp) * 230;
    const legs = jp > 0 && jp < 1 ? 'j' : Math.floor(t * 10) % 2 ? 'a' : 'b';
    A.drawSpr(ctx, heroSpr('mario_' + legs, { cap: 1, mst: 1, legs }), snap(jx, DKP), snap(jy - 16 * DKP, DKP), DKP);
    if (t > 14.86) A.ptext(ctx, '100', snap(jx + 60, 6), jy - 170 - (t - 14.86) * 120, 5, 'plainWhite', { alpha: 1 - pr(t, 15.1, 15.3) });
    pop(ctx, t, w(40), 'THEY CALL HIM', 540, 250, 5, 'plainCyan');
    pop(ctx, t, w(43), 'JUMPMAN', 540, 400, 14, 'fire', { k: 1.6 });
    if (t > w(43)) A.sparks(ctx, 540, 400, 480, t, 12, 41, { squash: 0.3 });
  };

  // ---- 6: arcade high-score name entry: JUMPMAN -> MARIO, after the landlord Mario Segale
  const KEYS = ['ABCDEF', 'GHIJKL', 'MNOPQR', 'STUVWX', 'YZ.-<#'];
  const keyPos = (r, c) => [165 + c * 150, 800 + r * 115];
  SC.name = (ctx, t) => {
    ctx.fillStyle = '#05040A'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(70,90,200,0.08)'; for (let y = 0; y < H; y += 6) ctx.fillRect(0, y, W, 2);
    A.ptext(ctx, 'ENTER YOUR NAME', 540, 420, 6, 'plainCyan');
    // name field
    const del0 = w(44), del1 = we(46);
    let name = 'JUMPMAN';
    const nd = Math.floor(7 * pr(t, del0, del1)); name = name.slice(0, 7 - nd);
    const typ = [17.78, 17.865, 17.95, 18.035, 18.12];
    const mario = 'MARIO'; let typed = 0; typ.forEach((tt) => { if (t >= tt) typed++; });
    if (typed) name = mario.slice(0, typed);
    const sx0 = 540 - 364;
    for (let i = 0; i < 7; i++) { ctx.fillStyle = '#3A3F6A'; ctx.fillRect(sx0 + i * 104 + 6, 640, 92, 8); }
    const flash = t > 18.24 && t < 19.0;
    const style = flash ? ['fire', 'cyan', 'gold', 'white'][Math.floor(t * 12) % 4] : 'white';
    [...name].forEach((ch, i) => {
      const born = typed ? typ[i] : 0, c = born ? A.popCell(t, born, 12, 1.7, 0.1) : 12;
      A.ptext(ctx, ch, sx0 + i * 104 + 52, 580, c, style);
    });
    if (Math.floor(t * 4) % 2 === 0 && name.length < 7 && !flash) { ctx.fillStyle = '#FFD21E'; ctx.fillRect(sx0 + name.length * 104 + 6, 628, 92, 14); }
    // keyboard
    KEYS.forEach((row, r) => [...row].forEach((k, c) => {
      const [x, y] = keyPos(r, c);
      A.ptext(ctx, k === '<' ? 'DEL' : k === '#' ? 'END' : k, x, y, k === '<' || k === '#' ? 3 : 6, 'plainWhite', { alpha: 0.9 });
    }));
    // selector
    let sel = [4, 4];
    if (t > del1 + 0.05) sel = [2, 0];
    const path = [[2, 0], [0, 0], [2, 5], [1, 2], [2, 2]];
    typ.forEach((tt, i) => { if (t >= tt - 0.04) sel = path[i]; });
    if (t > 18.3) sel = [4, 5];
    const [kx, ky] = keyPos(sel[0], sel[1]);
    const pulse = Math.floor(t * 8) % 2 ? 6 : 0;
    ctx.strokeStyle = '#05040A'; ctx.lineWidth = 16; ctx.strokeRect(kx - 62 - pulse / 2, ky - 58 - pulse / 2, 124 + pulse, 116 + pulse);
    ctx.strokeStyle = '#FFD21E'; ctx.lineWidth = 8; ctx.strokeRect(kx - 62 - pulse / 2, ky - 58 - pulse / 2, 124 + pulse, 116 + pulse);
    // captions
    pop(ctx, t, w(48), 'NAMED AFTER', 540, 1390, 5, 'plainWhite');
    pop(ctx, t, w(50), "NINTENDO'S LANDLORD", 540, 1460, 5, 'white');
    pop(ctx, t, w(52), 'MARIO SEGALE', 540, 1575, 9, 'fire', { k: 2.1 });
    if (t > w(52)) A.sparks(ctx, 540, 1575, 470, t, 12, 55, { squash: 0.25 });
    if (flash) A.sparks(ctx, 540, 580, 420, t, 14, 61, { squash: 0.3 });
  };

  // ---- 7A: 1985 — the real NES drops in, scan-converts to pixels, iris closes on it
  const NES = { w: 900 };
  function nesRect(t) {
    const s = NES.w / IMG.nes.width, h = IMG.nes.height * s;
    const p = pr(t, 19.1, 19.4), y = lerp(-900, 1060, E.outBack(p, 1.3));
    const fl = 6 * Math.sin((t - 19.4) * 3) * (t > 19.4 ? 1 : 0);
    return { x: 540 - NES.w / 2, y: y - h / 2 + fl, w: NES.w, h };
  }
  SC.nes = (ctx, t) => {
    ctx.drawImage(L.red, 0, 0);
    A.speedLines(ctx, 540, 1060, t, 71, { color: 'rgba(255,255,255,0.32)', n: 44, r0: 420 });
    const r = nesRect(t);
    if (t < 19.4) A.motionLines(ctx, 540, r.y - 20, 600, 220, 1, 10);
    const real = (c) => { smooth(c); for (const [dx, dy] of [[-10, 0], [10, 0], [0, -10], [0, 10]]) c.drawImage(L.nesSil, r.x + dx, r.y + dy, r.w, r.h); c.drawImage(IMG.nes, r.x, r.y, r.w, r.h); smooth(c, false); };
    const pix = (c) => { smooth(c, false); for (const [dx, dy] of [[-12, 0], [12, 0], [0, -12], [0, 12]]) c.drawImage(A.silhouette(L.nesPix, '#1A0E08'), r.x + dx, r.y + dy, r.w, r.h); c.drawImage(L.nesPix, r.x, r.y, r.w, r.h); };
    A.scanConvert(ctx, real, pix, [r.x, r.y, r.x + r.w, r.y + r.h], pr(t, 19.62, 20.12), 77);
    A.puff(ctx, 540, r.y + r.h - 40, pr(t, 19.4, 19.85), { r: 560, n: 14, cell: 14, size: 4, squash: 0.25 });
    pop(ctx, t, w(53), '1985', 540, 430, 22, 'fire', { k: 2.5, dur: 0.22 });
    if (t > w(53)) A.sparks(ctx, 540, 430, 470, t, 14, 79, { squash: 0.35 });
    pop(ctx, t, 19.5, 'NINTENDO ENTERTAINMENT SYSTEM', 540, 1450, 3, 'plainWhite');
    // first frames: white flash + starburst (REF-A 16.08 s)
    A.flash(ctx, 1 - pr(t, 19.08, 19.16));
    A.starburst(ctx, 540, 1000, pr(t, 19.1, 19.3), 9);
  };

  // ---- 7B: the overworld: title slam, ? block, coin fountain, 40,000,000
  const WP = 8, GROUND = 1420, TILE = 16 * WP;
  const scrollX = (t) => Math.max(0, t - 20.42) * 250;
  function groundTile(ctx, x, y) {
    ctx.fillStyle = '#C8541A'; ctx.fillRect(x, y, TILE, TILE);
    ctx.fillStyle = '#FFC49A'; ctx.fillRect(x, y, TILE, WP); ctx.fillRect(x, y, WP, TILE);
    ctx.fillStyle = '#3A1404'; ctx.fillRect(x, y + TILE - WP, TILE, WP); ctx.fillRect(x + TILE - WP, y, WP, TILE);
    ctx.fillRect(x + 8 * WP, y + WP, WP, 7 * WP); ctx.fillRect(x + WP, y + 8 * WP, TILE - 2 * WP, WP); ctx.fillRect(x + 4 * WP, y + 9 * WP, WP, 6 * WP);
  }
  function qBlock(ctx, x, y, used) {
    ctx.fillStyle = '#3A1A00'; ctx.fillRect(x, y, TILE, TILE);
    ctx.fillStyle = used ? '#9A5A22' : '#F8B800'; ctx.fillRect(x + WP, y + WP, TILE - 2 * WP, TILE - 2 * WP);
    ctx.fillStyle = used ? '#B87A3C' : '#FFE38A'; ctx.fillRect(x + WP, y + WP, TILE - 2 * WP, WP);
    ctx.fillStyle = '#3A1A00'; for (const [a, b] of [[2, 2], [13, 2], [2, 13], [13, 13]]) ctx.fillRect(x + a * WP, y + b * WP, WP, WP);
    if (!used) A.ptext(ctx, '?', x + TILE / 2, y + TILE / 2, 10, { fill: ['#C84C0C', '#8A2A04'], out: '#3A1A00', depth: 1, ext: '#3A1A00' });
  }
  function brick(ctx, x, y) {
    ctx.fillStyle = '#C8541A'; ctx.fillRect(x, y, TILE, TILE);
    ctx.fillStyle = '#3A1404';
    for (let r = 0; r < 4; r++) { ctx.fillRect(x, y + r * 4 * WP + 3 * WP, TILE, WP); ctx.fillRect(x + ((r % 2) * 8 + 4) * WP, y + r * 4 * WP, WP, 3 * WP); }
    ctx.fillStyle = '#FFA070'; ctx.fillRect(x, y, TILE, WP);
  }
  function pipe(ctx, x, y) {
    ctx.fillStyle = '#0B3A10'; ctx.fillRect(x - WP, y - WP, 32 * WP + 2 * WP, 15 * WP); ctx.fillRect(x + WP, y + 13 * WP, 28 * WP + 2 * WP, H);
    ctx.fillStyle = '#2DB82D'; ctx.fillRect(x, y, 32 * WP, 13 * WP); ctx.fillRect(x + 2 * WP, y + 13 * WP, 28 * WP, H);
    ctx.fillStyle = '#9BEA5A'; ctx.fillRect(x + 3 * WP, y + WP, 3 * WP, 11 * WP); ctx.fillRect(x + 5 * WP, y + 13 * WP, 3 * WP, H);
  }
  function hill(ctx, x, base, wdt, hgt) {
    ctx.fillStyle = '#0B5A12';
    for (let j = 0; j < hgt; j += WP) { const hw = Math.sqrt(Math.max(0, 1 - Math.pow(1 - j / hgt, 2))) * wdt / 2; ctx.fillRect(snap(x - hw, WP) - WP, base - hgt + j, snap(2 * hw, WP) + 2 * WP, WP); }
    ctx.fillStyle = '#3CBF3C';
    for (let j = WP; j < hgt; j += WP) { const hw = Math.sqrt(Math.max(0, 1 - Math.pow(1 - j / hgt, 2))) * wdt / 2; ctx.fillRect(snap(x - hw, WP), base - hgt + j, snap(2 * hw, WP), WP); }
    ctx.fillStyle = '#0B5A12'; ctx.fillRect(x - 3 * WP, base - hgt * 0.55, 2 * WP, 5 * WP); ctx.fillRect(x + 2 * WP, base - hgt * 0.35, 2 * WP, 5 * WP);
  }
  const BLOCKS = [[540, 'b'], [668, 'q'], [796, 'b'], [924, 'q'], [1052, 'b'], [1500, 'q']];
  const HIT = { x: 668, t: () => w(57) };
  const MX = 380;
  function marioWorldY(t) {   // jump to hit the block
    const t0 = HIT.t() - 0.26, t1 = HIT.t() + 0.32;
    if (t < t0 || t > t1) return GROUND;
    if (t <= HIT.t()) return GROUND - 384 * E.outQ(pr(t, t0, HIT.t()));
    return GROUND - 384 * (1 - E.inQ(pr(t, HIT.t(), t1)));
  }
  SC.world = (ctx, t) => {
    // keep the hit block above Mario at the hit time
    const sx = scrollX(t), sxHit = scrollX(HIT.t());
    const off = HIT.x + TILE / 2 - (MX + 64) - sxHit;
    sky(ctx, '#63A6FF', '#9CCBFF');
    L.nesClouds.forEach((c, i) => ctx.drawImage(c, snap(((200 + i * 420 - sx * 0.3) % 1400 + 1400) % 1400 - 200, WP), 640 + i * 70, c.width * WP, c.height * WP));
    hill(ctx, snap(300 - sx * 0.55, WP), GROUND, 640, 280); hill(ctx, snap(1250 - sx * 0.55, WP), GROUND, 420, 180);
    // bushes = green clouds
    for (let i = 0; i < 4; i++) { const c = L.nesClouds[i % 3]; const bx = snap(((i * 520 + 150 - sx) % 2000 + 2000) % 2000 - 300, WP); ctx.save(); ctx.drawImage(A.silhouette(c, '#2FB52F'), bx, GROUND - 13 * WP, c.width * WP, c.height * WP * 0.8); ctx.restore(); }
    pipe(ctx, snap(1400 + off - sx, WP), GROUND - 28 * WP);
    for (let x = -((sx % TILE) + TILE); x < W + TILE; x += TILE) { groundTile(ctx, snap(x, WP), GROUND); groundTile(ctx, snap(x, WP), GROUND + TILE); groundTile(ctx, snap(x, WP), GROUND + 2 * TILE); groundTile(ctx, snap(x, WP), GROUND + 3 * TILE); }
    const by0 = GROUND - 4.5 * TILE;
    BLOCKS.forEach(([bx, k]) => {
      const x = snap(bx + off - sx, WP);
      const isHit = bx === HIT.x;
      const bump = isHit ? -Math.sin(Math.PI * pr(t, HIT.t(), HIT.t() + 0.14)) * 28 : 0;
      if (k === 'q') qBlock(ctx, x, by0 + bump, isHit && t >= HIT.t()); else brick(ctx, x, by0);
    });
    // coin fountain (one coin, then the flood)
    const bxs = HIT.x + off - sx + TILE / 2;
    if (t >= HIT.t()) {
      const p = pr(t, HIT.t(), HIT.t() + 0.5);
      if (p < 1) coin(ctx, bxs, by0 - 80 - Math.sin(Math.PI * p) * 260, 8, (t * 8) % 1);
    }
    for (let i = 0; i < 46; i++) {
      const t0 = w(58) + i * 0.022; if (t < t0) continue;
      const dt = t - t0, vx = (rnd(i * 3.3) - 0.5) * 1100, vy = -(1300 + rnd(i * 5.1) * 900);
      const x = bxs + vx * dt, y = by0 - 40 + vy * dt + 0.5 * 3200 * dt * dt;
      if (y > GROUND + 60) continue;
      coin(ctx, x, y, 6, (t * 6 + rnd(i)) % 1);
    }
    // Mario
    const my = marioWorldY(t), air = my < GROUND - 1;
    const legs = air ? 'j' : Math.floor(t * 12) % 2 ? 'a' : 'b';
    A.drawSpr(ctx, heroSpr('mario_' + legs, { cap: 1, mst: 1, legs }), MX, snap(my - 16 * WP, WP), WP);
    // title slam: SUPER  MARIO  BROS.
    ctx.font = '112px "Bungee"';
    const wS = ctx.measureText('SUPER').width, wM = ctx.measureText('MARIO').width, gap = 40;
    const x0 = 540 - (wS + gap + wM) / 2;
    const words = [['SUPER', x0 + wS / 2, 270, w(54)], ['MARIO', x0 + wS + gap + wM / 2, 270, w(55)], ['BROS.', 540, 400, w(56)]];
    words.forEach(([s, x, y, t0]) => {
      const sl = A.slam(t, t0); if (!sl) return;
      if (sl.smear > 0.05) for (let k = 3; k >= 1; k--) A.title(ctx, s, x - k * 60 * sl.smear, y + k * 40 * sl.smear, 112, { rot: sl.rot, scale: sl.scale, alpha: 0.18 * sl.smear });
      A.title(ctx, s, x, y, 112, { rot: sl.rot, scale: sl.scale, alpha: sl.alpha });
    });
    if (t > w(56) + 0.35) A.sparks(ctx, 540, 330, 470, t, 10, 91, { squash: 0.25 });
    // sales counter
    pop(ctx, t, w(58), 'OVER', 540, 560, 5, 'plainWhite');
    if (t >= w(59)) {
      const n = 40000000 * E.outC(pr(t, w(59), w(61)));
      A.ptext(ctx, A.fmt(n), 540, 668, A.popCell(t, w(59), 11, 1.5, 0.14), 'fire');
    }
    pop(ctx, t, w(61), 'COPIES', 540, 790, 8, 'fire', { k: 2.2 });
    if (t > w(61)) A.sparks(ctx, 540, 700, 500, t, 16, 97, { squash: 0.3 });
    // iris opens on Mario (REF: the classic circle)
    const ip = pr(t, 20.42, 20.66);
    if (ip < 1) A.iris(ctx, MX + 64, GROUND - 64, lerp(0, 1500, E.inC(ip)), 12);
  };

  // ---- 8: today — power-up, BEST-SELLING / GAME SERIES / EVER
  SC.today = (ctx, t) => {
    const [sx, sy] = shake(t, w(69), 30, 0.32, 9);
    ctx.save(); ctx.translate(sx, sy);
    ctx.drawImage(L.heat, 0, 0);
    A.speedLines(ctx, 540, 1250, t, 101, { color: 'rgba(255,255,255,0.4)', n: 54, r0: 330, speed: 2.2 });
    // power-up flicker small -> big (classic grow)
    const g0 = w(63), g1 = g0 + 0.6;
    let s = 14;
    if (t >= g0 && t < g1) s = [14, 20, 14, 20, 24, 20, 24][Math.floor(pr(t, g0, g1) * 7)];
    else if (t >= g1) s = 24;
    A.drawSpr(ctx, MARIO(), 540, 1520, Math.round(s * 1.3), { anchor: 'bc', outline: '#FFFFFF', ow: 12 });
    A.sparks(ctx, 540, 1250, 500, t, 18, 103);
    pop(ctx, t, w(62), 'TODAY', 540, 290, 6, 'plainWhite');
    pop(ctx, t, w(66), 'BEST-SELLING', 540, 430, 10, 'fire', { k: 2.0 });
    if (t >= w(67)) A.ptext(ctx, 'GAME SERIES', 540, 560, A.popCell(t, w(67), 10, 2.0, 0.2), 'fire', { reveal: t >= w(68) ? 11 : 5 });
    pop(ctx, t, w(69), 'EVER', 540, 770, 26, 'fire', { k: 2.6, dur: 0.24 });
    if (t >= w(69)) {
      A.ring(ctx, 540, 770, lerp(120, 900, E.outC(pr(t, w(69), w(69) + 0.4))), 18, '#FFFFFF', 1 - pr(t, w(69), w(69) + 0.4));
      A.sparks(ctx, 540, 770, 520, t, 22, 107, { squash: 0.4 });
    }
    ctx.restore();
    A.flash(ctx, 1 - pr(t, 23.58, 23.66));
    A.starburst(ctx, 540, 1000, pr(t, 23.6, 23.82), 13);
  };

  // ---- 9: 256 pixels, then pull back into a real 1981 Donkey Kong cabinet
  const OPEN = { x0: 400, y0: 332, x1: 625, y1: 548 };   // screen opening in the cabinet photo
  function endContent(ctx, t) {
    ctx.fillStyle = '#05040A'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(70,90,200,0.07)'; for (let y = 0; y < H; y += 6) ctx.fillRect(0, y, W, 2);
    const c = 30, ox = 540 - 8 * c, oy = 900 - 8 * c;
    const rows = hero({ cap: 1, mst: 1, legs: 'a' });
    const cnt = Math.floor(256 * pr(t, w(73), w(73) + 0.7));
    for (let j = 0; j < 16; j++) for (let i = 0; i < 16; i++) {
      const k = j * 16 + i, col = PAL[rows[j][i]];
      if (col) { ctx.fillStyle = col; ctx.fillRect(ox + i * c, oy + j * c, c, c); }
      if (k < cnt && t < w(73) + 1.1) { ctx.strokeStyle = k > cnt - 18 ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.22)'; ctx.lineWidth = 2; ctx.strokeRect(ox + i * c + 1, oy + j * c + 1, c - 2, c - 2); }
    }
    pop(ctx, t, w(70), 'NOT BAD FOR', 540, 520, 5, 'plainWhite');
    if (t >= w(73)) A.ptext(ctx, String(cnt), 540, 1290, A.popCell(t, w(73), 18, 1.6, 0.14), 'fire');
    pop(ctx, t, w(74), 'PIXELS', 540, 1430, 8, 'white');
  }
  SC.end = (ctx, t) => {
    const T0 = 28.62, T1 = 29.42;
    if (t < T0) { endContent(ctx, t); A.crtGlass(ctx, pr(t, 28.2, 28.6) * 0.9); return; }
    const sb = A.buffer('_endc'); endContent(sb.getContext('2d'), t);
    const e = E.inOutC(pr(t, T0, T1));
    const ow = OPEN.x1 - OPEN.x0, oh = OPEN.y1 - OPEN.y0, ocx = (OPEN.x0 + OPEN.x1) / 2, ocy = (OPEN.y0 + OPEN.y1) / 2;
    const S0 = W / ow, S1 = 1.62;
    const S = Math.exp(lerp(Math.log(S0), Math.log(S1), e));
    const pcx = lerp(540, 593, e), pcy = lerp(960, 700, e);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalAlpha = clamp(e * 4);
    smooth(ctx); const top = 172; ctx.drawImage(IMG.cab, 0, top, IMG.cab.width, IMG.cab.height - top, pcx - ocx * S, pcy + (top - ocy) * S, IMG.cab.width * S, (IMG.cab.height - top) * S);
    const fg = ctx.createLinearGradient(0, pcy + (top - ocy) * S, 0, pcy + (top - ocy + 40) * S); fg.addColorStop(0, 'rgba(0,0,0,1)'); fg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = fg; ctx.fillRect(0, pcy + (top - ocy) * S, W, 40 * S);
    ctx.restore();
    // our film inside the cabinet's screen
    const sx0 = pcx - (ow / 2) * S, sy0 = pcy - (oh / 2) * S, sw = ow * S, sh = oh * S;
    ctx.save(); ctx.beginPath(); ctx.roundRect ? ctx.roundRect(sx0, sy0, sw, sh, 14 * S) : ctx.rect(sx0, sy0, sw, sh); ctx.clip();
    smooth(ctx, e > 0.02); ctx.drawImage(sb, 0, 420, 1080, 1080, sx0, sy0, sw, sh);
    const g = ctx.createRadialGradient(sx0 + sw / 2, sy0 + sh / 2, sw * 0.2, sx0 + sw / 2, sy0 + sh / 2, sw * 0.75);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.45)'); ctx.fillStyle = g; ctx.fillRect(sx0, sy0, sw, sh);
    ctx.fillStyle = 'rgba(0,0,0,0.16)'; for (let y = sy0; y < sy0 + sh; y += Math.max(3, S * 1.2)) ctx.fillRect(sx0, y, sw, Math.max(1, S * 0.4));
    ctx.restore();
    // screen glow spilling onto the room
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.18 * e;
    const gg = ctx.createRadialGradient(pcx, pcy, sw * 0.3, pcx, pcy, sw * 1.4); gg.addColorStop(0, 'rgba(120,150,255,0.6)'); gg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gg; ctx.fillRect(0, 0, W, H); ctx.restore();
    pop(ctx, t, 29.1, 'LEVEL COMPLETE', 540, 190, 8, 'fire', { k: 2.0 });
    if (t > 29.1) A.sparks(ctx, 540, 190, 470, t, 10, 113, { squash: 0.2 });
    if (t > 29.35 && Math.floor(t * 3) % 2 === 0) A.ptext(ctx, 'INSERT COIN', 540, 1730, 5, 'plainYellow');
    ctx.save(); ctx.globalAlpha = 0.6 * pr(t, 29.3, 29.6); ctx.fillStyle = '#E9E3F5'; ctx.font = '22px "Pixelify"'; ctx.textAlign = 'center';
    ctx.fillText('Photos: Wikimedia Commons (J. Driggs CC BY-SA 2.0, CC BY 4.0, public domain)', 540, 1875);
    ctx.restore();
  };

  // ================================================================ timeline of scenes + transitions
  const SPANS = [['city', 0, 2.45], ['ware', 2.45, 4.56], ['ad', 4.56, 5.62], ['miya', 5.62, 8.5], ['pix16', 8.5, 14.1], ['dk', 14.1, 15.3],
    ['name', 15.3, 19.1], ['nes', 19.1, 20.42], ['world', 20.42, 23.6], ['today', 23.6, 26.5], ['end', 26.5, 30.01]];
  const S = (id, t, buf) => { const c = A.buffer(buf); SC[id](c.getContext('2d'), t); return c; };
  const TR = [
    [0, 0.22, (ctx, t) => A.crtOn(ctx, S('city', t, 'b1'), pr(t, 0, 0.22))],
    [0.22, 0.8, (ctx, t) => A.knit(ctx, S('city', t, 'b1'), 1 - E.outC(pr(t, 0.22, 0.8)), t)],
    [4.5, 4.62, (ctx, t) => A.glitchV(ctx, S(t < 4.56 ? 'ware' : 'ad', t, 'b1'), 1 - Math.abs(pr(t, 4.5, 4.62) * 2 - 1), t, 3)],
    [5.4, 5.92, (ctx, t) => A.pinwheel(ctx, S('ad', t, 'b1'), S('miya', t, 'b2'), pr(t, 5.4, 5.92), 512, 815, 8)],
    [8.5, 8.68, (ctx, t) => { ctx.drawImage(S('pix16', t, 'b1'), 0, 0); A.flash(ctx, 1 - pr(t, 8.5, 8.56)); A.starburst(ctx, 540, 960, pr(t, 8.5, 8.68), 17); }],
    [14.02, 14.34, (ctx, t) => { const p = pr(t, 14.02, 14.34), o = { base: '#3A1A0A', tint: '#FFD9A8', stitch: 'rgba(255,236,210,0.85)', ta: 0.18 }; if (p < 0.5) A.knit(ctx, S('pix16', t, 'b1'), E.outC(p * 2), t, o); else A.knit(ctx, S('dk', t, 'b1'), 1 - E.outC((p - 0.5) * 2), t, o); }],
    [15.22, 15.42, (ctx, t) => A.glitchV(ctx, S(t < 15.3 ? 'dk' : 'name', t, 'b1'), 1 - Math.abs(pr(t, 15.22, 15.42) * 2 - 1), t, 5)],
    [20.18, 20.42, (ctx, t) => { ctx.drawImage(S('nes', t, 'b1'), 0, 0); A.iris(ctx, 540, 1060, lerp(1500, 0, E.inC(pr(t, 20.18, 20.42))), 12); }],
    [26.36, 26.62, (ctx, t) => A.dither(ctx, S('today', t, 'b1'), S('end', t, 'b2'), pr(t, 26.36, 26.62), 24)],
  ];

  F.render = (ctx, t) => {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.imageSmoothingEnabled = false;
    const tr = TR.find(([a, b]) => t >= a && t < b);
    if (tr) tr[2](ctx, t);
    else { const sp = SPANS.find(([, a, b]) => t >= a && t < b) || SPANS[SPANS.length - 1]; SC[sp[0]](ctx, t); }
    // game HUD over the story: health = story progress, coins = what the hero collects
    const ha = t < 0.75 ? 0 : t > 28.45 ? 1 - pr(t, 28.45, 28.6) : 1;
    if (ha > 0 && !(t >= 4.5 && t < 5.62)) {
      let coins = 0; if (t >= w(32)) coins = 1; if (t >= w(39)) coins = 2; if (t >= w(57)) coins = 3;
      if (t >= w(59)) { const n = 40000000 * E.outC(pr(t, w(59), w(61))); coins = n >= 1e6 ? 'x' + Math.floor(n / 1e6) + 'M' : n >= 1000 ? 'x' + Math.floor(n / 1000) + 'K' : 'x' + String(Math.max(3, Math.round(n))).padStart(3, '0'); }
      const hp = Math.floor(clamp((t - 0.75) / (w(69) - 0.75)) * 12) / 12;
      A.hud(ctx, { health: hp, coins, alpha: ha, label: t >= w(69) ? 'MAX' : null });
    }
  };

  F.load = async () => {
    const im = (src) => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
    const fonts = [['PS2P', 'assets/fonts/PressStart2P-Regular.ttf'], ['Pixelify', 'assets/fonts/PixelifySans-VF.ttf'], ['Bungee', 'assets/fonts/Bungee-Regular.ttf']];
    await Promise.all(fonts.map(async ([n, u]) => { const f = new FontFace(n, `url(${u})`); await f.load(); document.fonts.add(f); }));
    const [miya, nes, ad, cab] = await Promise.all(['assets/img/miyamoto_cut.png', 'assets/img/nes_cut.png', 'assets/img/ad_crop.jpg', 'assets/img/dk_cabinet.jpg'].map(im));
    Object.assign(IMG, { miya, nes, ad, cab });
    build();
  };
})();
