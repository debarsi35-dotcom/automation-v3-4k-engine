// engine/styles.js — colour moods + 11 switchable visual styles (including flagship 'ted_ifverse').
// A MOOD is the lighting situation of a location (day, dusk, night, storm, interiors, void).
// A STYLE re-grades every mood (palette overrides + a lift/gamma/gain colour grade on the final frame + post settings).

export const BASE_MOODS = {
  day:          { sky: ['#8fb0d8', '#cfdcea', '#efe3d2'], ambient: '#6f7d96', key: '#fff3dc', rim: '#fff1d6', wall: '#8d8496', floor: '#5f5866', dark: '#2f2a36', practical: '#ffe2a8', grass: '#4f8a55', road: '#5d5a66', fog: '#dfe4f0' },
  golden:       { sky: ['#6b5a8e', '#e89a6a', '#f9d49c'], ambient: '#4a3a50', key: '#ffcf8f', rim: '#ffc68a', wall: '#5a3a34', floor: '#45302a', dark: '#2a1814', practical: '#ffe7b0', grass: '#4d6b3c', road: '#4a3c40', fog: '#f0c49a' },
  dusk:         { sky: ['#3d3360', '#8a5a86', '#e8956b', '#f7cf98'], ambient: '#3b2b3d', key: '#ffc68a', rim: '#ffc68a', wall: '#4a3646', floor: '#3d2c38', dark: '#231a27', practical: '#ffd59a', grass: '#3d5a48', road: '#3a3040', fog: '#c08a8a' },
  night:        { sky: ['#0b1028', '#1d2550', '#3a3570'], ambient: '#1e2444', key: '#c9d4ff', rim: '#a9b8ff', wall: '#262a46', floor: '#1b1e33', dark: '#0f1122', practical: '#ffb860', grass: '#22433a', road: '#24263a', fog: '#3a4270' },
  storm:        { sky: ['#141a33', '#2a3358', '#3d4670'], ambient: '#232a48', key: '#dfe6ff', rim: '#cfd9ff', wall: '#2b3150', floor: '#1c2238', dark: '#0d1020', practical: '#bcd0ff', grass: '#25483e', road: '#232838', fog: '#4a5580' },
  interiorWarm: { sky: ['#c98a74', '#f2b585', '#f7cf98'], ambient: '#4a3646', key: '#ffd59a', rim: '#ffcf8f', wall: '#4f3a40', floor: '#3a2a2e', dark: '#21171c', practical: '#ffd28a', grass: '#3d5a48', road: '#3a3040', fog: '#a87a70' },
  interiorCool: { sky: ['#2a3560', '#5a6aa0'], ambient: '#2a2c48', key: '#cbd6ff', rim: '#b8c6ff', wall: '#2e3150', floor: '#22243a', dark: '#121426', practical: '#9fe0ff', grass: '#22433a', road: '#24263a', fog: '#4a5080' },
  void:         { sky: ['#0a0e1a', '#121a2e'], ambient: '#151c30', key: '#ffffff', rim: '#8fb8e8', wall: '#121a2e', floor: '#0d1322', dark: '#070a12', practical: '#ffd47e', grass: '#1d3a33', road: '#151a28', fog: '#1d2740' },
};

const UI = { card: 'rgba(14,22,40,.95)', cardLine: 'rgba(140,185,245,.32)', text: '#a8c2e8', sub: '#758eb2', accent: '#ff6b57', gold: '#ffd47e', cream: '#fff3df', blueprint: '#88bcf2', bpBg: '#081121', good: '#5fd39a' };

export const STYLES = {
  ted_ifverse: {
    name: 'Ifverse x TED-Ed Cinema (Flagship 4K)',
    desc: 'Pitch-black silhouette stick figures (#0b0a10), 4.5px glowing warm amber rim light (#ffc982), moody indigo-mauve parallax sets, and crisp TED-Ed navy scientific blueprints (#081121).',
    ink: '#0b0a10', inkFar: '#272235', feature: '#f7f2e8', rimWidth: 4.5, ui: UI,
    grade: { contrast: 1.05, sat: 1.08, lift: [0.01, 0.005, 0.025], gamma: [1.02, 1.0, 1.04], gain: [1.04, 1.01, 0.98], vignette: 0.52, grain: 0.045, bloom: 0.65 },
    moods: {
      dusk: { sky: ['#2d234a', '#7c4c7a', '#e38b62', '#f7cf98'], key: '#ffd090', rim: '#ffc982', wall: '#433042', floor: '#332432', dark: '#1c1422', practical: '#ffd89e' },
      golden: { sky: ['#5a487d', '#e49263', '#fae4b2'], key: '#ffd294', rim: '#ffc982' },
    },
  },
  dusk: {
    name: 'Cinematic Dusk', desc: 'Reference look: mauve-purple shadows, amber key light, cream rim light, soft grain, 2:1 letterbox.',
    ink: '#0e0b12', inkFar: '#2b2333', feature: '#f4efe6', rimWidth: 4, ui: UI,
    grade: { contrast: 1.0, sat: 1.0, lift: [0, 0, 0], gamma: [1, 1, 1], gain: [1, 1, 1], vignette: 0.55, grain: 0.055, bloom: 0.55 },
    moods: {},
  },
  midnight: {
    name: 'Midnight Blue', desc: 'Cold navy world, blue-white rim light, sodium-orange practical lights, rain-friendly, higher contrast.',
    ink: '#0a0c16', inkFar: '#232a40', feature: '#eef3ff', rimWidth: 4, ui: { ...UI, accent: '#ff8a5c', gold: '#ffc66e' },
    grade: { contrast: 1.06, sat: 0.8, lift: [0.0, 0.025, 0.09], gamma: [0.92, 0.98, 1.08], gain: [0.84, 0.95, 1.15], vignette: 0.65, grain: 0.06, bloom: 0.7 },
    moods: { dusk: { sky: ['#141a3a', '#2c3470', '#5a5aa0', '#c08aa0'], key: '#d8dcff', rim: '#b8c8ff', wall: '#2a2c4a', floor: '#1e2036' }, golden: { rim: '#ffd6a8' }, interiorWarm: { wall: '#3a3448', sky: ['#5a5a90', '#c09ab0'] } },
  },
  golden: {
    name: 'Golden Hour', desc: 'Warm orange-and-teal daylight, big sun glows, brighter mid-tones, warm cream rim light.',
    ink: '#120c0a', inkFar: '#3a2a26', feature: '#fff6e6', rimWidth: 4.5, ui: { ...UI, card: 'rgba(30,26,40,.92)', accent: '#ff7a4a' },
    grade: { contrast: 1.04, sat: 1.18, lift: [0.035, 0.015, 0.0], gamma: [1.1, 1.04, 0.94], gain: [1.12, 1.02, 0.8], vignette: 0.45, grain: 0.045, bloom: 0.75 },
    moods: { night: { sky: ['#14183a', '#2e2c5a', '#6a4a6a'], rim: '#ffcf9a' }, dusk: { sky: ['#4a3a6a', '#d0786a', '#f2a46a', '#fbd8a0'] } },
  },
  neon: {
    name: 'Neon Noir', desc: 'Deep blacks, magenta + teal two-tone rim lights, glowing signage, strong bloom, cool shadows.',
    ink: '#07060c', inkFar: '#1e1830', feature: '#f6f0ff', rimWidth: 4, ui: { ...UI, card: 'rgba(14,10,28,.94)', cardLine: 'rgba(200,120,255,.3)', text: '#c9a8ff', accent: '#ff4fa3', gold: '#5ff2e8', blueprint: '#7fe8ff' },
    grade: { contrast: 1.15, sat: 1.4, lift: [0.01, 0.0, 0.04], gamma: [1.0, 0.9, 1.06], gain: [1.12, 0.86, 1.18], vignette: 0.7, grain: 0.06, bloom: 0.9 },
    moods: { dusk: { sky: ['#120a2a', '#3a1a5a', '#a03a8a', '#ff7a9a'], rim: '#ff6ac8', key: '#ff8ad0', practical: '#5ff2e8' }, night: { sky: ['#06061a', '#140f3a', '#2a1a5a'], rim: '#5ff2e8', practical: '#ff4fa3' }, interiorWarm: { rim: '#ff7ab8', practical: '#5ff2e8', wall: '#2a1e3a' }, day: { rim: '#7ff0ff' } },
  },
  storybook: {
    name: 'Soft Storybook', desc: 'Lighter pastel palette, lower contrast, lavender shadows, gentle paper grain — friendlier, family tone.',
    ink: '#1a1622', inkFar: '#4a4258', feature: '#fffaf0', rimWidth: 5, ui: { ...UI, card: 'rgba(40,36,60,.9)', accent: '#ff8a7a', gold: '#ffd98a' },
    grade: { contrast: 0.92, sat: 0.92, lift: [0.07, 0.055, 0.085], gamma: [1.12, 1.1, 1.06], gain: [1.06, 1.03, 0.98], vignette: 0.3, grain: 0.07, bloom: 0.45 },
    moods: { night: { sky: ['#2a2f5a', '#4a4f80', '#6a6aa0'], wall: '#3e4266' }, dusk: { sky: ['#6a5a90', '#c08aa8', '#f2b0a0', '#fbe0b8'] } },
  },
  emerald: {
    name: 'Bio-Lab Emerald', desc: 'Deep forest-teal shadows with bioluminescent mint and gold rim lighting — ideal for biology & cellular explainers.',
    ink: '#07120e', inkFar: '#1b352c', feature: '#eefaf4', rimWidth: 4.5, ui: { ...UI, accent: '#42f59b', gold: '#ffd97d', blueprint: '#6bf0c4', bpBg: '#061a14' },
    grade: { contrast: 1.06, sat: 1.1, lift: [0.0, 0.03, 0.02], gamma: [0.96, 1.04, 1.0], gain: [0.94, 1.08, 1.0], vignette: 0.55, grain: 0.05, bloom: 0.65 },
    moods: { dusk: { sky: ['#0d2622', '#1f4e46', '#468c7a', '#b8f2d8'], rim: '#8fffe0', key: '#b8ffe8' } },
  },
  ember: {
    name: 'Survival Ember', desc: 'High-stakes volcanic crimson and molten amber rim lighting for extreme survival & crisis scenarios.',
    ink: '#120808', inkFar: '#381a1a', feature: '#fff2eb', rimWidth: 4.5, ui: { ...UI, accent: '#ff4d38', gold: '#ffb84d', bpBg: '#1c0b0b' },
    grade: { contrast: 1.1, sat: 1.15, lift: [0.04, 0.01, 0.0], gamma: [1.06, 0.98, 0.92], gain: [1.12, 0.96, 0.88], vignette: 0.6, grain: 0.05, bloom: 0.7 },
    moods: { dusk: { sky: ['#260d12', '#661f24', '#c94a38', '#ffad66'], rim: '#ff9e5e', key: '#ffb870' } },
  },
  arctic: {
    name: 'Arctic Neural', desc: 'Crisp glacier cyan and silver-white highlights for cognitive, sleep, and cryo-science topics.',
    ink: '#080e17', inkFar: '#1f2f46', feature: '#f2f8ff', rimWidth: 4.5, ui: { ...UI, accent: '#45d4ff', gold: '#aee8ff', blueprint: '#8ce0ff', bpBg: '#071324' },
    grade: { contrast: 1.05, sat: 0.92, lift: [0.0, 0.02, 0.06], gamma: [0.96, 1.02, 1.08], gain: [0.92, 1.02, 1.12], vignette: 0.5, grain: 0.045, bloom: 0.65 },
    moods: { dusk: { sky: ['#0c1c36', '#214478', '#5288c4', '#cce6ff'], rim: '#b8ecff', key: '#d9f4ff' } },
  },
  sakura: {
    name: 'Sakura Psychology', desc: 'Warm twilight rose, plum shadows, and soft champagne gold for human behavior & relationship paradoxes.',
    ink: '#120a14', inkFar: '#36203d', feature: '#fff5f8', rimWidth: 4.5, ui: { ...UI, accent: '#ff6b9d', gold: '#ffe099' },
    grade: { contrast: 1.02, sat: 1.08, lift: [0.03, 0.01, 0.03], gamma: [1.04, 0.98, 1.02], gain: [1.08, 0.98, 1.04], vignette: 0.48, grain: 0.05, bloom: 0.6 },
    moods: { dusk: { sky: ['#2a1836', '#6e3562', '#cf6e8f', '#ffd1c2'], rim: '#ffb8d1', key: '#ffd9e6' } },
  },
  retro: {
    name: 'Analog Science 1984', desc: 'Warm phosphor amber, muted teal shadows, and classic documentary film warmth.',
    ink: '#120f0c', inkFar: '#332c24', feature: '#f7eedc', rimWidth: 4.2, ui: { ...UI, accent: '#ff7733', gold: '#ffcc55', blueprint: '#66d9b8', bpBg: '#0d1a1a' },
    grade: { contrast: 1.04, sat: 0.95, lift: [0.03, 0.025, 0.01], gamma: [1.05, 1.02, 0.94], gain: [1.06, 1.02, 0.9], vignette: 0.58, grain: 0.065, bloom: 0.55 },
    moods: {},
  },
};
export const STYLE_IDS = Object.keys(STYLES);
