// engine/sets.js — Complete 8-Set Multi-Layer Parallax Environment Library (16:9 Landscape & 9:16 Vertical Shorts).
// Sets: cafe, lab, street, bedroom, classroom, rooftop, hospital, park.
import { E, V, mood, layer, backdrop, rr, seg, circle, ring, poly, linGrad, glow, alpha, shade, mix, text, FONTS } from './core.js';
import * as FX from './fx2d.js';

export const groundY = () => E.H * V(0.80, 0.68);

export function drawSet(name, g, t, cam = { z: 1, x: 0, y: 0 }, o = {}) {
  const fn = SETS[name] || SETS.cafe;
  return fn(g, t, cam, o);
}

export function cafeSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'golden'), GY = groundY(), CX = E.W / 2;
  const wall = shade(M.wall, -0.3), wallDark = shade(M.wall, -0.6);
  layer(g, cam, 0.15, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX + V(580, 260), GY - V(540, 920), V(68, 80), '#fff3dc', M.key, 5);
    FX.clouds(g, { y: GY - V(820, 1300), h: 180, color: '#ffe7c7', a: 0.16, seed: 3 });
    FX.skyline(g, { x: -E.W, y: GY - V(380, 620), w: E.W * 3, minH: 80, maxH: V(250, 380), color: mix(M.sky[1], wallDark, 0.75), windowColor: alpha(M.practical, 0.5), lit: 0.18, seed: 8 });
  });
  layer(g, cam, 0.55, (g) => {
    const top = GY - V(540, 780), left = CX - 1400, w = 2800;
    g.fillStyle = linGrad(g, 0, top, 0, GY, [shade(wall, 0.06), wall, wallDark]);
    g.fillRect(left, top, w, GY - top + 4);
    const ay = GY - V(410, 520), ah = 54;
    for (const i of [-2, -1, 1, 2]) {
      const ww = 200, wh = V(240, 280), wx = CX + i * 280 - ww / 2, wy = ay + 42;
      FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 2, rows: 1, frame: wallDark, bar: 8 }, (g, x, y, w, h) => {
        g.fillStyle = linGrad(g, 0, y, 0, y + h, [M.practical, shade(M.practical, -0.45), shade(M.practical, -0.7)]);
        g.fillRect(x, y, w, h);
        circle(g, x + w * 0.5, y + 34, 9, '#fff3d6');
        glow(g, x + w * 0.5, y + 34, 70, '#fff3d6', 0.5);
      });
    }
    FX.door(g, { x: CX - 65, y: GY, w: 130, h: V(310, 350), color: wallDark, open: 0.25, light: M.practical });
    for (let x = left, k = 0; x < left + w; x += 56, k++) {
      g.fillStyle = k % 2 ? '#c9b8a4' : '#8f3328';
      g.fillRect(x, ay - ah, 56, ah);
      g.beginPath(); g.arc(x + 28, ay, 28, 0, Math.PI); g.fill();
    }
    rr(g, CX - 110, ay - ah - 62, 220, 48, 10); g.fillStyle = wallDark; g.fill();
    text(g, 'CAFÉ', CX, ay - ah - 38, { size: 28, color: M.practical, font: FONTS.title });
  });
  layer(g, cam, 0.9, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 500, [shade(M.floor, -0.1), shade(M.dark, -0.25)]);
    g.fillRect(-E.W, GY, E.W * 3, E.H);
    FX.floorLines(g, GY, GY + 500, 'rgba(0,0,0,.25)', 0.08);
    FX.pool(g, CX, GY + 24, 240, 40, M.practical, 0.24);
  });
  return { GY, CX, M };
}

export function labSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorWarm'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.35, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [M.dark, M.wall]);
    g.fillRect(-E.W, -E.H, E.W * 3, GY + E.H);
    const wx = CX - V(340, 280), wy = GY - V(540, 720), ww = V(680, 560), wh = V(320, 390);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 3, frame: shade(M.wall, -0.55), bar: 10, blinds: 5 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, 0, y, 0, y + h, M.sky); g.fillRect(x, y, w, h);
      FX.sun(g, x + w / 2, y + h * 0.58, 52, '#fff7e6', M.key, 4);
      FX.skyline(g, { x, y: y + h, w, maxH: h * 0.58, color: alpha(shade(M.wall, -0.25), 0.8), windowColor: alpha(M.practical, 0.7), seed: 4 });
    });
    const bx = CX - V(740, 420), by = GY - V(500, 960);
    rr(g, bx, by, 280, 130, 8); g.fillStyle = '#161424'; g.fill();
    [bx + 52, bx + 140, bx + 228].forEach((x) => ring(g, x, by + 65, 30, 3, '#9fb6d8'));
    FX.clock(g, CX + V(540, 310), GY - V(560, 1020), 34, 9 * 3600 + 41 * 60 + t, { face: '#e9e2ea' });
  });
  layer(g, cam, 0.72, (g) => {
    FX.counter(g, { x: CX - V(540, 460), y: GY - 36, w: V(1080, 920), h: 115, color: shade(M.wall, -0.45), top: shade(M.wall, -0.2), doors: 8 });
    FX.screen(g, { x: CX + V(300, 180), y: GY - 250, w: 145, h: 90, glowC: '#7fd0d6', a: 0.24 }, (g, x, y, w, h) => {
      g.strokeStyle = '#7fd0d6'; g.lineWidth = 2.4; g.beginPath();
      for (let i = 0; i < 22; i++) g.lineTo(x + 6 + i * 6.2, y + h / 2 - Math.sin(i * 0.9 + t * 3.4) * 15 * (i % 5 === 0 ? 1.9 : 1));
      g.stroke();
    });
    g.fillStyle = linGrad(g, 0, GY - 36, 0, GY + 520, [shade(M.floor, 0.08), M.dark]);
    g.fillRect(-E.W, GY - 36, E.W * 3, E.H);
    FX.floorLines(g, GY - 36, GY + 520, 'rgba(0,0,0,.22)', 0.07);
    FX.pool(g, CX, GY + 12, 420, 68, M.key, 0.22);
  });
  return { GY, CX, M };
}

export function streetSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'night'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.15, (g) => {
    backdrop(g, M.sky);
    FX.stars(g, t, { count: 110, area: [-200, 0, E.W + 400, GY * 0.65] });
    FX.moon(g, CX + V(520, 240), GY - V(580, 980), 48);
    FX.skyline(g, { x: -E.W, y: GY - 40, w: E.W * 3, minH: 140, maxH: V(440, 640), color: shade(M.wall, -0.45), windowColor: alpha(M.practical, 0.65), lit: 0.32, seed: 14 });
  });
  layer(g, cam, 0.55, (g) => {
    for (const i of [-2, -1, 0, 1, 2]) {
      FX.facade(g, { x: CX + i * 420 - 180, y: GY, w: 360, h: V(460, 620), color: shade(M.wall, -0.25), win: M.practical, dark: M.dark, cols: 4, rows: 4, lit: 0.45, seed: 20 + i });
    }
    for (const sx of [-1, 1]) FX.lampPost(g, CX + sx * V(440, 280), GY, V(340, 390), { light: M.practical, a: 0.24 });
  });
  layer(g, cam, 0.9, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 500, [M.road, M.dark]);
    g.fillRect(-E.W, GY, E.W * 3, E.H);
    FX.floorLines(g, GY, GY + 500, 'rgba(255,255,255,.08)', 0.08);
    for (const sx of [-1, 1]) FX.pool(g, CX + sx * V(440, 280) + 36, GY + 18, 220, 42, M.practical, 0.26);
  });
  return { GY, CX, M };
}

export function bedroomSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorCool'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.35, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [M.dark, M.wall]);
    g.fillRect(-E.W, -E.H, E.W * 3, GY + E.H);
    const wx = CX + V(140, -180), wy = GY - V(520, 760), ww = V(420, 380), wh = V(320, 380);
    FX.windowFrame(g, { x: wx, y: wy, w: ww, h: wh, cols: 2, rows: 2, frame: shade(M.wall, -0.55), bar: 9 }, (g, x, y, w, h) => {
      g.fillStyle = linGrad(g, 0, y, 0, y + h, M.sky); g.fillRect(x, y, w, h);
      FX.moon(g, x + w * 0.7, y + h * 0.3, 28);
      FX.rain(g, t, { count: 90, area: [x, y, w, h], a: 0.28 });
    });
    FX.lightCone(g, wx + ww / 2, wy + wh / 2, { angle: Math.PI * 0.62, spread: 0.55, len: 680, color: M.key, a: 0.14 });
    FX.clock(g, CX - V(480, 260), GY - V(460, 820), 30, 3 * 3600 + 14 * 60 + t);
  });
  layer(g, cam, 0.75, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 30, 0, GY + 500, [M.floor, M.dark]);
    g.fillRect(-E.W, GY - 30, E.W * 3, E.H);
    FX.bed(g, { x: CX - V(560, 380), y: GY - 10, w: V(440, 380), color: '#484a8a', frame: shade(M.wall, -0.5) });
  });
  return { GY, CX, M };
}

export function classroomSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorWarm'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.35, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, [shade(M.wall, -0.25), M.wall]);
    g.fillRect(-E.W, -E.H, E.W * 3, GY + E.H);
    const bx = CX - V(460, 360), by = GY - V(500, 680), bw = V(920, 720), bh = V(280, 320);
    rr(g, bx - 10, by - 10, bw + 20, bh + 20, 10); g.fillStyle = '#3a2820'; g.fill();
    rr(g, bx, by, bw, bh, 6); g.fillStyle = '#18342b'; g.fill();
    seg(g, [[bx + 60, by + 90], [bx + bw * 0.45, by + 90]], 4, 'rgba(255,255,255,.45)');
    seg(g, [[bx + 60, by + 150], [bx + bw * 0.72, by + 150]], 4, 'rgba(255,220,140,.55)');
    ring(g, bx + bw * 0.78, by + 120, 48, 3.5, 'rgba(140,210,255,.65)');
  });
  layer(g, cam, 0.8, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 30, 0, GY + 500, [M.floor, M.dark]);
    g.fillRect(-E.W, GY - 30, E.W * 3, E.H);
    FX.floorLines(g, GY - 30, GY + 500, 'rgba(0,0,0,.22)', 0.07);
    FX.pool(g, CX, GY + 10, 440, 70, M.key, 0.2);
  });
  return { GY, CX, M };
}

export function rooftopSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.15, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX, GY - V(420, 740), V(88, 104), '#fff3dc', M.key, 5);
    FX.godRays(g, CX, GY - V(420, 740), { count: 12, angle: -Math.PI / 2, spread: Math.PI * 1.4, len: 1700, a: 0.08, t });
    FX.skyline(g, { x: -E.W, y: GY - 80, w: E.W * 3, minH: 100, maxH: V(380, 560), color: '#221930', windowColor: alpha(M.practical, 0.8), lit: 0.3, seed: 19 });
  });
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = '#161120'; g.fillRect(-E.W, GY - 24, E.W * 3, 26);
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 500, ['#251d33', '#120d1a']);
    g.fillRect(-E.W, GY, E.W * 3, E.H);
    for (let x = -E.W; x < E.W * 2; x += 90) seg(g, [[x, GY - 24], [x, GY - 86]], 4, '#2d233d');
    seg(g, [[-E.W, GY - 86], [E.W * 2, GY - 86]], 6, '#3b2e50');
  });
  return { GY, CX, M };
}

export function hospitalSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'interiorCool'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.35, (g) => {
    g.fillStyle = linGrad(g, 0, -E.H, 0, GY, ['#1c2838', '#2c3d54']);
    g.fillRect(-E.W, -E.H, E.W * 3, GY + E.H);
    FX.screen(g, { x: CX + V(280, 140), y: GY - V(420, 620), w: 190, h: 115, glowC: '#5fd39a', a: 0.32 }, (g, x, y, w, h) => {
      g.strokeStyle = '#5fd39a'; g.lineWidth = 3; g.beginPath();
      for (let i = 0; i < 28; i++) {
        const ph = (i + Math.floor(t * 14)) % 14;
        const dy = ph === 6 ? -32 : ph === 7 ? 24 : ph === 8 ? -10 : 0;
        g.lineTo(x + 6 + i * 6.4, y + h * 0.55 + dy);
      }
      g.stroke();
    });
  });
  layer(g, cam, 0.8, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 30, 0, GY + 500, ['#233042', '#131b26']);
    g.fillRect(-E.W, GY - 30, E.W * 3, E.H);
    FX.floorLines(g, GY - 30, GY + 500, 'rgba(255,255,255,.07)', 0.07);
    FX.pool(g, CX, GY + 12, 420, 65, '#9fe0ff', 0.2);
  });
  return { GY, CX, M };
}

export function parkSet(g, t, cam, o = {}) {
  const M = mood(o.mood || 'golden'), GY = groundY(), CX = E.W / 2;
  layer(g, cam, 0.15, (g) => {
    backdrop(g, M.sky);
    FX.sun(g, CX - V(480, 220), GY - V(520, 880), 74, '#fff5e0', M.key, 5);
    FX.hills(g, { y: GY - 110, amp: 95, color: shade(M.grass, -0.35), seed: 8 });
  });
  layer(g, cam, 0.55, (g) => {
    for (const dx of [-680, -320, 340, 720]) FX.tree(g, CX + dx, GY - 10, V(1.15, 1.3), shade(M.grass, -0.5));
  });
  layer(g, cam, 0.9, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 15, 0, GY + 500, [M.grass, shade(M.grass, -0.45)]);
    g.fillRect(-E.W, GY - 15, E.W * 3, E.H);
    g.fillStyle = shade(M.floor, 0.08);
    g.fillRect(-E.W, GY + 10, E.W * 3, 75);
  });
  return { GY, CX, M };
}

export const SETS = {
  cafe: cafeSet,
  lab: labSet,
  street: streetSet,
  bedroom: bedroomSet,
  classroom: classroomSet,
  rooftop: rooftopSet,
  hospital: hospitalSet,
  park: parkSet,
};
