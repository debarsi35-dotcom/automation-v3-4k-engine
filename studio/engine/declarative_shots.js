// engine/declarative_shots.js — Renders all 12 Ifverse x TED-Ed Declarative Shot Archetypes
// for both 16:9 Landscape (4K 3840x2160 / 1440p 2560x1440) and 9:16 Vertical Shorts (4K 2160x3840 / 1440p 1440x2560).
import { E, V, S, mood, layer, blurLayer, veil, backdrop, ease, prog, clamp, lerp, talkAmount, wordTime, seg, circle, ring, rr, poly, glow, alpha, text, FONTS } from './core.js';
import { drawFigure, POSES, posesAt, walkPose, breathe, bigFace } from './rig2d.js';
import * as FX from './fx2d.js';
import * as UI from './ui2d.js';
import { drawSet, groundY } from './sets.js';

const DEFAULT_CAST = {
  HERO: { top: 'hoodie', color: '#d64a33', head: 'none' },
  FRIEND: { top: 'tshirt', color: '#3a6ea5', head: 'cap', headColor: '#f2c21a' },
  SCIENTIST: { top: 'labcoat', face: 'glasses', head: 'none' },
};

function getCast(role = 'HERO') {
  const c = (typeof window !== 'undefined' && window.PROJECT_CAST) ? window.PROJECT_CAST : DEFAULT_CAST;
  return c[role] || c.HERO || DEFAULT_CAST.HERO;
}

// Icons for blueprint_pipeline
function drawBlueprintIcon(kind, g, x, y, r, c) {
  g.save();
  g.strokeStyle = c; g.fillStyle = c; g.lineWidth = 5; g.lineCap = 'round'; g.lineJoin = 'round';
  if (kind === 'eye') {
    g.beginPath(); g.ellipse(x, y, r, r * 0.56, 0, 0, Math.PI * 2); g.stroke();
    circle(g, x, y, r * 0.28, c);
  } else if (kind === 'brain') {
    for (const dx of [-0.32, 0.32]) { g.beginPath(); g.ellipse(x + dx * r, y, r * 0.42, r * 0.6, 0, 0, Math.PI * 2); g.stroke(); }
    seg(g, [[x - r * 0.48, y - r * 0.1], [x - r * 0.18, y + r * 0.15]], 4, c);
    seg(g, [[x + r * 0.48, y - r * 0.1], [x + r * 0.18, y + r * 0.15]], 4, c);
  } else if (kind === 'heart') {
    g.beginPath();
    g.moveTo(x, y + r * 0.55);
    g.bezierCurveTo(x - r * 0.9, y, x - r * 0.5, y - r * 0.75, x, y - r * 0.25);
    g.bezierCurveTo(x + r * 0.5, y - r * 0.75, x + r * 0.9, y, x, y + r * 0.55);
    g.stroke();
  } else if (kind === 'clock') {
    ring(g, x, y, r * 0.75, 5, c);
    seg(g, [[x, y], [x, y - r * 0.48]], 5, c);
    seg(g, [[x, y], [x + r * 0.36, y + r * 0.12]], 5, c);
  } else {
    // lightning / signal
    poly(g, [[x + r * 0.1, y - r * 0.75], [x - r * 0.45, y + r * 0.08], [x + r * 0.02, y + r * 0.08], [x - r * 0.15, y + r * 0.75], [x + r * 0.48, y - r * 0.08], [x + r * 0.02, y - r * 0.08]], c);
  }
  g.restore();
}

export const TEMPLATES = {
  establishing_wide(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'cafe';
    const dur = Math.max(0.5, info.dur || 3.0);
    const cam = { z: 1.0 + 0.09 * ease.inOut(t / dur), x: lerp(-35, 25, ease.inOut(t / dur)), y: 0 };
    const { GY, CX, M } = drawSet(setName, g, t, cam, { mood: info.mood });
    const figScale = V(1.5, 1.75);
    const rim = { color: M.rim, dir: [-0.8, -0.5], w: 4.5 };
    layer(g, cam, 1.0, (g) => {
      const isWalk = info.walk !== false;
      const xPos = isWalk ? lerp(CX - V(180, 90), CX + V(90, 60), ease.inOut(t / dur)) : CX;
      const p = isWalk ? walkPose(t * 5.2) : breathe(POSES[info.pose || 'stand'] || POSES.stand, t);
      drawFigure(g, {
        x: xPos, y: GY, s: figScale, facing: 1,
        outfit: getCast(info.actor || 'HERO'),
        pose: p,
        expr: info.expr || 'determined',
        talk: talkAmount(info.globalT),
        blink: (t % 3.1) > 2.98,
        rim,
      });
    });
    FX.godRays(g, CX + V(300, 120), 0, { count: 7, angle: Math.PI * 0.58, spread: 0.75, len: 1500, color: M.key, a: 0.09, t });
    FX.dust(g, t, { count: 42, color: M.practical, a: 0.4 });
  },

  medium_two_shot(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'cafe';
    const dur = Math.max(0.5, info.dur || 3.0);
    const cam = { z: 1.12 + 0.05 * ease.inOut(t / dur), x: 0, y: -30 };
    const { GY, CX, M } = drawSet(setName, g, t, cam, { mood: info.mood });
    const s = V(1.65, 1.78);
    const rim = { color: M.rim, dir: [0, -1], w: 4.5 };
    const span = V(230, 175);
    const talk = talkAmount(info.globalT);
    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: CX - span, y: GY, s, facing: 1,
        outfit: getCast('HERO'),
        pose: breathe(posesAt(t, [[0, 'stand'], [0.4, 'talk'], [1.8, 'explain']]), t),
        expr: 'determined',
        talk: talk * 0.85,
        blink: (t % 3.4) > 3.28,
        rim,
      });
      drawFigure(g, {
        x: CX + span, y: GY, s, facing: -1,
        outfit: getCast(setName === 'lab' || setName === 'hospital' ? 'SCIENTIST' : 'FRIEND'),
        pose: breathe(posesAt(t, [[0, 'relaxed'], [0.8, 'think']]), t, 1, 2),
        expr: t > dur * 0.5 ? 'surprised' : 'neutral',
        talk: talk * 0.35,
        blink: ((t + 1.1) % 3.2) > 3.08,
        rim,
      });
    });
    FX.dust(g, t, { count: 35, color: M.practical, a: 0.35 });
  },

  over_the_shoulder(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'lab';
    const dur = Math.max(0.5, info.dur || 3.0);
    const cam = { z: 1.22 + 0.06 * ease.inOut(t / dur), x: V(60, 20), y: -50 };
    const { GY, CX, M } = drawSet(setName, g, t, cam, { mood: info.mood });
    const s = V(1.75, 1.9);
    const rim = { color: M.rim, dir: [-0.8, -0.5], w: 4.5 };
    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: CX + V(140, 65), y: GY, s, facing: -1,
        outfit: getCast('SCIENTIST'),
        pose: breathe(posesAt(t, [[0, 'explain'], [1.1, 'point']]), t),
        expr: 'determined',
        talk: talkAmount(info.globalT),
        prop: { type: 'tablet' },
        rim,
      });
    });
    // Blurred foreground shoulder silhouette for cinematic depth of field
    blurLayer(g, 10, (g) => {
      drawFigure(g, {
        x: CX - V(340, 210), y: GY + 160, s: s * 1.45, facing: 1,
        outfit: getCast('HERO'),
        pose: POSES.stand,
        dim: true,
        rim: { color: M.rim, dir: [0.8, -0.4], w: 3 },
      });
    }, cam, 1.55);
  },

  big_face_reaction(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'cafe';
    const dur = Math.max(0.5, info.dur || 3.0);
    blurLayer(g, 14, (g) => drawSet(setName, g, t, { z: 1.55, x: -120, y: -110 }, { mood: info.mood }));
    veil(g, '#0d0914', 0.38);
    const M = mood(info.mood || 'dusk');
    const r = V(295, 315) * (1 + 0.045 * ease.inOut(t / dur));
    const talk = talkAmount(info.globalT);
    const cx = E.W / 2, cy = E.H * V(0.58, 0.50);
    bigFace(g, cx, cy, r, {
      outfit: getCast(info.actor || 'HERO'),
      expr: info.expr || (t > dur * 0.45 ? 'shocked' : 'awe'),
      talk,
      look: [Math.sin(t * 1.8) * 0.25, -0.1],
      rimColor: M.rim,
      rimSide: -1,
      blink: (t % 2.8) > 2.68,
    });
    if (talk > 0.1) {
      FX.rings(g, cx, cy, t, { count: 3, r0: r * 1.08, r1: r * 1.52, color: M.rim, a: 0.32 });
    }
    FX.dust(g, t, { count: 30, color: M.practical, a: 0.4 });
  },

  time_freeze(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'cafe';
    const dur = Math.max(0.5, info.dur || 3.0);
    const cam = { z: 1.12 + 0.06 * (t / dur), r: -0.025 + 0.01 * (t / dur), x: 0, y: -25 };
    blurLayer(g, 11, (g) => drawSet(setName, g, 0, { z: 1.6, x: -80, y: -140 }, { mood: 'night' }));
    veil(g, '#091024', 0.42);
    const GY = groundY(), CX = E.W / 2;
    layer(g, cam, 1.0, (g) => {
      FX.drops(g, t, { count: 65, color: '#cfe4ff', rMin: 3.5, rMax: 13, drift: 2.5 });
      FX.rings(g, CX, E.H * 0.46, t, { count: 4, r0: 90, r1: 540, speed: 0.4, color: '#bce0ff', a: 0.38 });
      drawFigure(g, {
        x: CX, y: GY, s: V(1.65, 1.8), facing: 1,
        outfit: getCast(info.actor || 'HERO'),
        pose: POSES[info.pose || 'ready'] || POSES.ready,
        expr: info.expr || 'awe',
        rim: { color: '#9fe8ff', dir: [-0.9, -0.5], w: 5 },
        trail: { count: 3, dx: -32, dy: 0, a: 0.24 },
      });
    });
    g.save();
    g.globalCompositeOperation = 'soft-light';
    g.fillStyle = 'rgba(70,130,255,.32)';
    g.fillRect(0, 0, E.W, E.H);
    g.restore();
    UI.badge(g, { str: info.badge || '0.025s FREEZE', a: ease.out(prog(t, 0.15, 0.6)) });
  },

  blueprint_pipeline(g, t, info) {
    UI.blueprint(g);
    const c = UI.bpStroke(), gold = S().ui.gold;
    const nodes = info.nodes || [
      { icon: 'eye', label: 'SENSORY INPUT' },
      { icon: 'brain', label: 'NEURAL CORTEX' },
      { icon: 'lightning', label: 'MOTOR OUTPUT' },
    ];
    const dur = Math.max(0.8, info.dur || 3.0);
    const T = [0.15, dur * 0.36, dur * 0.66];
    const pts = E.vertical
      ? [[E.W * 0.34, E.H * 0.23], [E.W * 0.34, E.H * 0.42], [E.W * 0.34, E.H * 0.61]]
      : [[E.W * 0.22, E.H * 0.46], [E.W * 0.50, E.H * 0.46], [E.W * 0.78, E.H * 0.46]];
    const R = V(88, 96);

    for (let i = 0; i < 2; i++) {
      const k = ease.inOut(prog(t, T[i] + 0.1, T[i + 1]));
      const [ax, ay] = pts[i], [bx, by] = pts[i + 1];
      g.setLineDash([10, 12]);
      seg(g, [[ax + (bx - ax) * 0.2, ay + (by - ay) * 0.2], [bx - (bx - ax) * 0.2, by - (by - ay) * 0.2]], 3.5, alpha(c, 0.38));
      g.setLineDash([]);
      if (k > 0 && k < 1) {
        const px = lerp(ax, bx, 0.2 + 0.6 * k), py = lerp(ay, by, 0.2 + 0.6 * k);
        glow(g, px, py, 54, gold, 0.92);
        circle(g, px, py, 10, '#fff8e0');
      }
    }
    pts.forEach(([x, y], i) => {
      const nd = nodes[i] || nodes[0];
      const on = ease.outBack(prog(t, T[i] - 0.08, T[i] + 0.28));
      const active = t >= T[i];
      const col = active ? gold : alpha(c, 0.55);
      g.save();
      g.translate(x, y);
      g.scale(0.65 + 0.35 * on, 0.65 + 0.35 * on);
      ring(g, 0, 0, R, 4.5, col);
      if (active) glow(g, 0, 0, R * 1.55, gold, 0.26);
      drawBlueprintIcon(nd.icon || 'brain', g, 0, 0, R * 0.54, col);
      g.restore();
      text(g, nd.label || `STAGE ${i + 1}`, x + (E.vertical ? R + 36 : 0), y + (E.vertical ? 0 : R + 58), {
        size: V(36, 38), color: col, font: FONTS.ui, weight: 900, spacing: 2,
        align: E.vertical ? 'left' : 'center', alpha: clamp(on),
      });
    });
    UI.readout(g, {
      label: info.readoutLabel || 'BIOLOGICAL PATHWAY:',
      value: info.readoutValue || '10.0x ACTIVE',
      x: E.W / 2, y: E.H * V(0.84, 0.72), align: 'center',
      a: ease.out(prog(t, 0.15, 0.55)),
    });
  },

  blueprint_compare(g, t, info) {
    UI.blueprint(g);
    const ui = S().ui, bpc = UI.bpStroke();
    const r1 = info.row1 || { label: 'HUMAN BASELINE', value: '1.0x', frac: 0.28 };
    const r2 = info.row2 || { label: 'YOUR THRESHOLD', value: '10.0x', frac: 0.92 };
    const x0 = V(460, 110), x1 = E.W - V(220, 110);
    const rowY = [E.H * V(0.38, 0.32), E.H * V(0.66, 0.54)];
    const drawRow = (y, rowObj, p, color, who) => {
      if (!E.vertical) {
        UI.lineFigure(g, { x: 260, y: y + 95, s: 0.95, pose: who === 'you' ? POSES.ready : POSES.stand, color: alpha(color, 0.9) });
      }
      text(g, rowObj.label, x0, y - 54, { size: V(38, 40), color, font: FONTS.ui, weight: 900, align: 'left', spacing: 2 });
      rr(g, x0, y - 24, x1 - x0, 48, 24); g.fillStyle = alpha(color, 0.12); g.fill();
      const w = Math.max(48, (x1 - x0) * clamp(rowObj.frac * p, 0.04, 1));
      rr(g, x0, y - 24, w, 48, 24); g.fillStyle = color; g.fill();
      glow(g, x0 + w, y, 56, color, 0.5);
      text(g, rowObj.value, Math.min(E.W - 80, x0 + w + 26), y + 2, {
        size: V(50, 52), color, font: FONTS.ui, weight: 900, align: 'left', glow: 14, glowColor: alpha(color, 0.55),
      });
    };
    drawRow(rowY[0], r1, ease.out(prog(t, 0.1, 0.9)), bpc, 'normal');
    drawRow(rowY[1], r2, ease.out(prog(t, 0.45, 1.45)), ui.gold, 'you');
    if (info.badge) {
      UI.badge(g, { str: info.badge, a: ease.out(prog(t, 0.7, 1.2)), size: V(40, 46) });
    }
  },

  data_card_counter(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'lab';
    blurLayer(g, 12, (g) => drawSet(setName, g, t, { z: 1.35, x: 0, y: -40 }, { mood: 'night' }));
    veil(g, '#080c18', 0.45);
    UI.dataCard(g, t, {
      title: info.title || 'NEURAL TELEMETRY',
      subtitle: info.subtitle || 'MEASURED THRESHOLD',
      from: info.from ?? 1,
      to: info.to ?? 100,
      decimals: info.decimals ?? 0,
      unit: info.unit ?? 'x',
      start: 0.15,
      dur: Math.max(0.8, (info.dur || 2.8) * 0.68),
      total: info.dur || 3.0,
    });
  },

  timeline_progression(g, t, info) {
    const shot = info.shot || {};
    const setName = shot.set || 'street';
    const dur = Math.max(0.5, info.dur || 3.0);
    const cam = { z: 1.05 + 0.06 * (t / dur), x: lerp(-40, 40, t / dur), y: 0 };
    const { GY, CX, M } = drawSet(setName, g, t, cam, { mood: info.mood });
    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: CX, y: GY, s: V(1.55, 1.75), facing: 1,
        outfit: getCast('HERO'),
        pose: walkPose(t * 5.6, { run: t > dur * 0.55 }),
        expr: t > dur * 0.55 ? 'worried' : 'determined',
        talk: talkAmount(info.globalT),
        rim: { color: M.rim, dir: [-0.8, -0.5], w: 4.5 },
      });
    });
    UI.meter(g, t, {
      x: V(200, 90), y: V(170, 250), w: E.W - V(400, 180),
      label: info.meterLabel || 'BIOLOGICAL ESCALATION TIMELINE',
      speed: 1 / Math.max(1, dur * 0.85),
    });
  },

  orbit_3d(g, t, info) {
    // High-framerate 2.5D volumetric parallax orbit (works everywhere without WebGL stalls)
    const shot = info.shot || {};
    const setName = shot.set || 'cafe';
    const dur = Math.max(0.5, info.dur || 3.0);
    const k = ease.inOut(t / dur);
    const cam = { z: 1.18 + 0.12 * Math.sin(k * Math.PI), x: lerp(-160, 160, k), y: -35 };
    const { GY, CX, M } = drawSet(setName, g, t, cam, { mood: 'golden' });
    layer(g, cam, 1.0, (g) => {
      drawFigure(g, {
        x: CX - 130, y: GY, s: V(1.65, 1.8), facing: 1,
        outfit: getCast('HERO'),
        pose: breathe(POSES.ready, t),
        expr: 'determined',
        rim: { color: M.rim, dir: [-0.8, -0.5], w: 4.5 },
      });
      drawFigure(g, {
        x: CX + 130, y: GY, s: V(1.65, 1.8), facing: -1,
        outfit: getCast('FRIEND'),
        pose: breathe(POSES.shocked || POSES.handsOnHead, t),
        expr: 'shocked',
        rim: { color: M.rim, dir: [0.8, -0.5], w: 4.5 },
      });
    });
    FX.godRays(g, CX, 0, { count: 10, angle: Math.PI / 2, spread: 1.1, len: 1600, color: M.key, a: 0.11, t });
  },

  title_card(g, t, info) {
    const shot = info.shot || {};
    const dur = Math.max(0.8, info.dur || 3.2);
    const M = mood(info.mood || 'dusk');
    const cam = { z: 1.06 - 0.05 * ease.inOut(t / dur), y: -15 * (t / dur) };
    layer(g, cam, 0.2, (g) => {
      backdrop(g, M.sky);
      FX.sun(g, E.W / 2, E.H * V(0.62, 0.52), V(92, 108), '#fff3dc', M.key, 5);
      FX.godRays(g, E.W / 2, E.H * V(0.62, 0.52), { count: 14, angle: -Math.PI / 2, spread: Math.PI * 1.5, len: 1800, a: 0.07, t });
    });
    layer(g, cam, 0.55, (g) => {
      FX.skyline(g, { x: -200, y: E.H * V(0.75, 0.65), w: E.W + 400, maxH: V(310, 480), color: '#241a33', windowColor: alpha(M.practical, 0.8), seed: 21 });
    });
    layer(g, cam, 0.85, (g) => {
      g.fillStyle = '#120d1a'; g.fillRect(-E.W, E.H * V(0.75, 0.65), E.W * 3, E.H);
    });
    FX.dust(g, t, { count: 35, color: '#ffd9b0', a: 0.42 });
    const rawTitle = (info.title || shot.scene || E.cfg?.title || 'WHAT IF?').replace(/^Title Card:\s*/i, '').toUpperCase();
    const words = rawTitle.split(/\s+/);
    const mid = Math.ceil(words.length / 2);
    const lines = words.length > 4 ? [words.slice(0, mid).join(' '), words.slice(mid).join(' ')] : [rawTitle];
    UI.titleCard(g, t, { lines, sub: info.sub || E.cfg?.thumbnailBadge || null, dur, y: E.H * V(0.42, 0.36) });
  },

  end_screen(g, t, info) {
    const castList = [getCast('HERO'), getCast('FRIEND'), getCast('SCIENTIST')];
    UI.endScreen(g, t, {
      question: info.question || 'What would YOU choose? Tell us below!',
      cast: castList,
    });
    if (E.vertical && E.cfg?.bridgeText) {
      const a = ease.out(prog(t, 0.25, 0.75));
      g.save();
      g.globalAlpha *= a;
      rr(g, E.W * 0.08, E.H * 0.14, E.W * 0.84, 86, 22);
      g.fillStyle = 'rgba(12,20,38,0.92)'; g.fill();
      g.strokeStyle = S().ui.gold; g.lineWidth = 3; g.stroke();
      text(g, E.cfg.bridgeText, E.W / 2, E.H * 0.14 + 43, {
        size: 32, color: S().ui.gold, font: FONTS.ui, weight: 900,
      });
      g.restore();
    }
  },
};

export function renderDeclarativeShot(g, t, info) {
  const tpl = info.shot?.template || 'establishing_wide';
  const fn = TEMPLATES[tpl] || TEMPLATES.establishing_wide;
  fn(g, t, info);
}
