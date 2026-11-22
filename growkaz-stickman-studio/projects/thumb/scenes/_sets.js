// _sets.js — reusable locations. Each set(g, t, cam, o) draws background layers and returns { GY, CX, M }.
import { E, V, mood, layer, backdrop, rr, seg, circle, poly, linGrad, radGrad, glow, alpha, shade, mix, rng, noise, clamp, lerp } from '/engine/core.js';
import { drawFigure, POSES, walkPose, breathe } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { tent, spear, crestBand, capIsr, CREST, STONE } from './_props.js';

export const GYv = () => E.H * 0.8;
const CXv = () => E.W / 2;
// valley profile: Israel hill on the left, Philistine hill on the right, brook in the middle
export function hillY(x) { const CX = CXv(), GY = GYv(); return GY - 330 * Math.exp(-(((x - (CX - 1080)) / 620) ** 2)) - 330 * Math.exp(-(((x - (CX + 1080)) / 620) ** 2)); }

function sky(g, M, t, o = {}) {
  backdrop(g, M.sky);
  if (o.stars) FX.stars(g, t, { count: 160, area: [-E.W, -E.H, E.W * 3, E.H * 1.4] });
  if (o.moon) FX.moon(g, o.moon[0], o.moon[1], 34, '#eef0ff');
  if (o.sun) FX.sun(g, o.sun[0], o.sun[1], o.sunR || 60, '#fff3dc', M.key, 5);
  if (o.clouds !== false) FX.clouds(g, { y: E.H * 0.12, h: 220, count: 7, color: o.cloudC || '#fff0dc', a: o.cloudA ?? 0.12, seed: o.seed || 3 });
}

// ---------- the Valley of Elah ----------
// o: mood, israel/phil army state ('idle'|'scared'|'flee'|'charge'|'cheer'|'watch'|false), sunX, storm, rays
export function valley(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = GYv(), CX = CXv();
  const sunP = o.sunPos || [CX + 560, GY - 380];
  layer(g, cam, 0.1, (g) => {
    sky(g, M, t, { sun: o.storm ? null : sunP, stars: o.mood === 'night', cloudA: o.storm ? 0.3 : 0.12, cloudC: o.storm ? '#4a5580' : '#ffe7c7' });
    if (o.storm) { FX.clouds(g, { y: -40, h: 300, count: 10, color: '#0d1020', a: 0.5, seed: 11 }); }
    if (!o.storm) FX.godRays(g, sunP[0], sunP[1], { count: 9, angle: Math.PI * 0.75, spread: 1.4, len: 1700, color: M.key, a: 0.05, t });
  });
  layer(g, cam, 0.3, (g) => { FX.hills(g, { y: GY - 250, amp: 150, color: mix(M.sky[1], M.dark, 0.62), seed: 21, freq: 0.0025 }); FX.fog(g, GY - 260, 160, M.fog, 0.18); });
  layer(g, cam, 0.55, (g) => { FX.hills(g, { y: GY - 120, amp: 80, color: mix(M.wall, M.dark, 0.55), seed: 5, freq: 0.004 }); });
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 340, 0, GY + 260, [shade(M.floor, 0.06), M.floor, shade(M.dark, -0.2)]);
    g.beginPath(); g.moveTo(-E.W * 1.2, E.H * 2); for (let x = -E.W * 1.2; x <= E.W * 2.2; x += 24) g.lineTo(x, hillY(x)); g.lineTo(E.W * 2.2, E.H * 2); g.closePath(); g.fill();
    // hill rim light (sun behind the right hill)
    g.strokeStyle = alpha(M.rim, 0.35); g.lineWidth = 3; g.beginPath(); for (let x = CX + 300; x <= E.W * 2.2; x += 24) x === CX + 300 ? g.moveTo(x, hillY(x)) : g.lineTo(x, hillY(x)); g.stroke();
    // brook
    g.fillStyle = linGrad(g, CX - 700, 0, CX + 700, 0, [alpha(M.sky[M.sky.length - 1], 0), alpha(M.sky[M.sky.length - 1], 0.55), alpha(M.sky[M.sky.length - 1], 0)]);
    g.beginPath(); g.ellipse(CX + 40, GY + 26, 820, 9, -0.01, 0, 7); g.fill(); FX.pool(g, CX + 80, GY + 26, 300, 20, M.key, 0.12);
    const r = rng(17); for (let i = 0; i < 26; i++) { const x = CX - 1400 + r() * 2800, y = hillY(x) + 10 + r() * 40; g.fillStyle = shade(M.dark, -0.1); g.beginPath(); g.ellipse(x, y, 12 + r() * 26, 6 + r() * 9, 0, Math.PI, 0); g.fill(); }
    // tents on the hilltops
    for (const [x, c] of [[CX - 1500, '#6a5a48'], [CX - 1330, '#7a6a52'], [CX - 1180, '#5a4a3a'], [CX - 1420, '#4a3e32']]) tent(g, x, hillY(x) + 6, 150, 110, shade(c, -0.25), { lit: o.mood === 'night' ? 0.6 : 0.2 });
    for (const [x, c] of [[CX + 1200, '#7a3a2a'], [CX + 1360, '#6a2a22'], [CX + 1520, '#7a4a2a'], [CX + 1430, '#5a2a1a']]) tent(g, x, hillY(x) + 6, 160, 120, shade(c, -0.2), { lit: 0.25 });
    if (o.israel !== false) army(g, t, -1, o.israel || 'idle', M, o);
    if (o.phil !== false) army(g, t, 1, o.phil || 'idle', M, o);
  });
  return { GY, CX, M };
}
// an army of small soldiers on one hill. side -1 = Israel (left, faces right), +1 = Philistines
export function army(g, t, side, state, M, o = {}) {
  const CX = CXv(), r = rng(side < 0 ? 31 : 47), k = o.armyScale || 0.56, rim = { color: M.rim, dir: [side < 0 ? 0.6 : -0.3, -1], w: 3 };
  const rows = 3, n = 16;
  for (let j = rows - 1; j >= 0; j--) for (let i = 0; i < n; i++) {
    let x = CX + side * (560 + i * 58 + j * 24 + r() * 16); const ph = r() * 6.28, f = -side;
    let pose = breathe(POSES.stand, t, 1, ph), dx = 0, rot = 0;
    if (state === 'scared') { pose = i % 3 ? breathe(POSES.handsOnHead, t, 1, ph) : breathe(POSES.crossArms, t, 1, ph); dx = side * 26 * clamp(t / 1.5); }
    if (state === 'cheer') pose = POSES.cheer, dx = 0;
    if (state === 'flee') { pose = walkPose(t * 10 + ph, { run: true }); dx = side * t * 190; }
    if (state === 'charge') { pose = walkPose(t * 10 + ph, { run: true }); dx = -side * t * 170; }
    if (state === 'march') { pose = walkPose(t * 5.6 + i * 0.3, {}); dx = -side * t * 40; }
    x += dx; const y = hillY(x) - j * 16 + 4; const facing = state === 'flee' ? side : f;
    if (state === 'flee' || state === 'charge') { if (Math.abs(x - CX) < 120) continue; }
    const fo = { x, y, s: k * (1 - j * 0.06), facing, pose, rim, shadow: false };
    if (side > 0 || state !== 'cheer') { const hx = x + facing * 8 * k, hy = y - 100 * k; spear(g, hx - facing * 4, y + 6, hx + facing * 10 * k, y - 300 * k, 3.2 * k * 1.6); }
    drawFigure(g, fo);
    const hx = x + pose.head[0] * facing * fo.s, hy = y + pose.head[1] * fo.s, hr = 26 * fo.s;
    side > 0 ? crestBand(g, hx, hy, hr) : capIsr(g, hx, hy, hr);
  }
}

// ---------- Israelite camp (golden) ----------
export function camp(g, t, cam, o = {}) {
  const M = mood(o.mood || 'golden'), GY = GYv(), CX = CXv();
  layer(g, cam, 0.1, (g) => { sky(g, M, t, { sun: [CX - 620, GY - 520], seed: 5 }); FX.godRays(g, CX - 620, GY - 520, { angle: Math.PI * 0.35, spread: 1.2, color: M.key, a: 0.05, t }); });
  layer(g, cam, 0.3, (g) => { FX.hills(g, { y: GY - 230, amp: 130, color: mix(M.sky[1], M.dark, 0.6), seed: 9 }); FX.fog(g, GY - 240, 150, M.fog, 0.2); });
  layer(g, cam, 0.55, (g) => {
    FX.hills(g, { y: GY - 70, amp: 50, color: mix(M.wall, M.dark, 0.5), seed: 13 });
    const cs = ['#6a5a48', '#7a6a52', '#5a4a3a', '#8a7a5a'];
    for (let i = -4; i <= 4; i++) tent(g, CX + i * 330 + (i % 2) * 60, GY - 60 + (i % 2) * 12, 240 + (i % 3) * 40, 170 + (i % 2) * 30, shade(cs[(i + 8) % 4], -0.3), { lit: 0.3 });
  });
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 70, 0, GY + 300, [shade(M.floor, 0.05), M.floor, shade(M.dark, -0.25)]); g.fillRect(-E.W, GY - 30, E.W * 3, E.H * 2);
    FX.floorLines(g, GY, GY + 400, 'rgba(0,0,0,.18)', 0.1);
    const r = rng(23); for (let i = 0; i < 14; i++) { const x = -400 + r() * (E.W + 800), y = GY + 20 + r() * 160; g.fillStyle = shade(M.dark, 0.05); g.beginPath(); g.ellipse(x, y, 30 + r() * 50, 12 + r() * 16, 0, Math.PI, 0); g.fill(); }
    for (const x of [CX - 760, CX + 820]) { for (let k = 0; k < 4; k++) spear(g, x + k * 14, GY - 4, x + k * 14 + 30, GY - 230, 4); }
    FX.pool(g, CX, GY + 40, 700, 60, M.key, 0.12);
  });
  return { GY, CX, M };
}

// ---------- Bethlehem pasture ----------
export function pasture(g, t, cam, o = {}) {
  const M = mood(o.mood || 'golden'), GY = GYv(), CX = CXv(), night = o.mood === 'night';
  const sunP = o.sunPos || [CX + 520, GY - 330];
  layer(g, cam, 0.1, (g) => {
    sky(g, M, t, { sun: night ? null : sunP, stars: night, moon: night ? [CX + 560, E.H * 0.2] : null, seed: 8 });
    if (!night) FX.godRays(g, sunP[0], sunP[1], { angle: Math.PI * 0.7, spread: 1.4, color: M.key, a: 0.05, t });
  });
  layer(g, cam, 0.3, (g) => { FX.hills(g, { y: GY - 200, amp: 120, color: mix(M.sky[1], M.dark, 0.55), seed: 44 }); FX.fog(g, GY - 210, 140, M.fog, 0.2);
    if (!night) for (let i = 0; i < 5; i++) { const x = CX - 900 + i * 90, y = GY - 210 - (i % 2) * 12; g.fillStyle = shade(M.wall, -0.2); g.fillRect(x, y - 30, 50, 30); g.fillStyle = alpha(M.practical, 0.7); g.fillRect(x + 18, y - 22, 10, 10); } });
  layer(g, cam, 0.55, (g) => { FX.hills(g, { y: GY - 60, amp: 70, color: mix(M.grass, M.dark, 0.6), seed: 3 }); FX.tree(g, CX - 760, GY - 40, 1.6, shade(M.dark, -0.1)); FX.tree(g, CX + 900, GY - 50, 1.3, shade(M.dark, -0.1)); });
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 40, 0, GY + 300, [mix(M.grass, M.floor, 0.5), shade(M.floor, -0.1), shade(M.dark, -0.3)]); g.fillRect(-E.W, GY - 20, E.W * 3, E.H * 2);
    const r = rng(9); g.strokeStyle = alpha(mix(M.grass, M.key, 0.3), 0.35); g.lineWidth = 2; for (let i = 0; i < 160; i++) { const x = -E.W + r() * E.W * 3, y = GY + r() * 220, h = 8 + r() * 14, sw = Math.sin(t * 1.3 + i) * 3; g.beginPath(); g.moveTo(x, y); g.lineTo(x + sw, y - h); g.stroke(); }
    if (!night) FX.pool(g, sunP[0] - 300, GY + 40, 600, 50, M.key, 0.14); else FX.pool(g, CX + 300, GY + 40, 600, 50, '#a9b8ff', 0.08);
  });
  return { GY, CX, M };
}

// ---------- Jesse's house in Bethlehem (dusk / night) ----------
export function house(g, t, cam, o = {}) {
  const M = mood(o.mood || 'dusk'), GY = GYv(), CX = CXv(), night = o.mood === 'night';
  layer(g, cam, 0.1, (g) => sky(g, M, t, { stars: night, moon: night ? [CX - 600, E.H * 0.18] : null, sun: night ? null : [CX - 700, GY - 300], seed: 12 }));
  layer(g, cam, 0.35, (g) => { const r = rng(4); for (let i = -8; i < 10; i++) { const x = CX + i * 150 + r() * 40, h = 60 + r() * 60; g.fillStyle = mix(M.wall, M.dark, 0.6); g.fillRect(x, GY - 200 - h, 120, h + 40); if (r() < 0.6) { g.fillStyle = alpha(M.practical, 0.8); g.fillRect(x + 40, GY - 200 - h + 20, 14, 14); glow(g, x + 47, GY - 200 - h + 27, 40, M.practical, 0.3); } } });
  layer(g, cam, 0.6, (g) => {
    const x0 = CX - 520, w = 1040, top = GY - 470;
    g.fillStyle = linGrad(g, 0, top, 0, GY, [shade(M.wall, 0.05), shade(M.wall, -0.25)]); g.fillRect(x0, top, w, GY - top);
    const r = rng(6); g.strokeStyle = 'rgba(0,0,0,.18)'; g.lineWidth = 2; for (let y = top + 30; y < GY; y += 42) for (let x = x0 + ((y / 42) % 2) * 40; x < x0 + w; x += 90) g.strokeRect(x, y, 86 + r() * 6, 40);
    g.fillStyle = shade(M.wall, -0.45); g.fillRect(x0 - 30, top - 24, w + 60, 28);
    FX.door(g, { x: CX + 60, y: GY, w: 170, h: 290, color: shade(M.wall, -0.5), open: o.door ?? 0.7, light: M.practical }); glow(g, CX + 145, GY - 140, 260, M.practical, 0.35);
    FX.windowFrame ? FX.windowFrame(g, { x: CX - 380, y: top + 110, w: 160, h: 140, cols: 2, rows: 2, frame: shade(M.wall, -0.5), bar: 8 }, (g, x, y, w, h) => { g.fillStyle = M.practical; g.fillRect(x, y, w, h); }) : 0;
    glow(g, CX - 300, top + 180, 200, M.practical, 0.3);
  });
  layer(g, cam, 0.85, (g) => { g.fillStyle = linGrad(g, 0, GY, 0, GY + 300, [shade(M.floor, 0), shade(M.dark, -0.3)]); g.fillRect(-E.W, GY, E.W * 3, E.H * 2); FX.pool(g, CX + 145, GY + 30, 320, 40, M.practical, 0.3); FX.floorLines(g, GY, GY + 300, 'rgba(0,0,0,.2)', 0.1); });
  return { GY, CX, M };
}

// ---------- Saul's tent (interior) ----------
export function tentIn(g, t, cam, o = {}) {
  const M = mood('interiorWarm'), GY = GYv(), CX = CXv();
  layer(g, cam, 0.5, (g) => {
    g.fillStyle = linGrad(g, 0, 0, 0, GY, [shade('#5a2e2a', -0.35), shade('#6a3a2e', -0.2), shade('#4a2a24', -0.35)]); g.fillRect(-E.W, -E.H, E.W * 3, E.H * 2 + GY);
    for (let i = -14; i < 20; i++) { const x = CX + i * 120; g.fillStyle = alpha('#000', 0.12 + (i % 2) * 0.08); g.fillRect(x, -E.H, 60, E.H + GY); }
    // opening on the right showing the sky
    const ox = CX + 520, ow = 320; const S2 = mood(o.outside || 'dusk');
    g.fillStyle = linGrad(g, 0, GY - 560, 0, GY, S2.sky); g.beginPath(); g.moveTo(ox, GY); g.lineTo(ox + ow * 0.5, GY - 560); g.lineTo(ox + ow, GY); g.closePath(); g.fill();
    FX.hills(g, { y: GY - 60, amp: 50, color: mix(S2.wall, S2.dark, 0.6), seed: 2 }); glow(g, ox + ow * 0.5, GY - 200, 360, S2.key, 0.25);
    g.fillStyle = shade('#3a1e1a', -0.2); g.fillRect(CX - 20, -E.H, 40, E.H + GY);
  });
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY, 0, GY + 300, [shade(M.floor, 0.05), shade(M.dark, -0.3)]); g.fillRect(-E.W, GY, E.W * 3, E.H * 2);
    rr(g, CX - 520, GY + 10, 1040, 120, 20); g.fillStyle = alpha('#8a2a2a', 0.5); g.fill(); g.strokeStyle = alpha('#e0a040', 0.35); g.lineWidth = 4; g.stroke();
    // hanging lamp
    const lx = CX - 260, ly = GY - 520; seg(g, [[lx, -E.H], [lx, ly]], 3, '#2a1a14'); rr(g, lx - 22, ly, 44, 34, 8); g.fillStyle = '#c89a4a'; g.fill(); glow(g, lx, ly + 20, 420, M.practical, 0.55); FX.pool(g, lx, GY + 40, 460, 60, M.practical, 0.25);
  });
  return { GY, CX, M };
}

// ---------- modern street at night ----------
export function street(g, t, cam, o = {}) {
  const M = mood('night'), GY = GYv(), CX = CXv(), dawn = o.dawn || 0;
  layer(g, cam, 0.1, (g) => { backdrop(g, M.sky); if (dawn) { g.fillStyle = linGrad(g, 0, 0, 0, E.H, [alpha('#ffd59a', 0), alpha('#ffb070', dawn * 0.7)]); g.fillRect(-E.W, -E.H, E.W * 3, E.H * 3); } FX.stars(g, t, { count: 90 }); });
  layer(g, cam, 0.3, (g) => FX.skyline(g, { x: -E.W, y: GY - 240, w: E.W * 3, minH: 120, maxH: 460, color: mix(M.sky[1], M.dark, 0.6), windowColor: alpha(M.practical, 0.6), lit: 0.18, seed: 8 }));
  layer(g, cam, 0.6, (g) => {
    const top = GY - 640; g.fillStyle = linGrad(g, 0, top, 0, GY, [shade(M.wall, -0.1), shade(M.wall, -0.4)]); g.fillRect(-E.W, top, E.W * 3, GY - top);
    g.strokeStyle = 'rgba(0,0,0,.22)'; g.lineWidth = 2; for (let y = top + 20; y < GY; y += 36) { g.beginPath(); g.moveTo(-E.W, y); g.lineTo(E.W * 2, y); g.stroke(); for (let x = -E.W + ((y / 36) % 2) * 50; x < E.W * 2; x += 100) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 36); g.stroke(); } }
    FX.lampPost(g, CX + 640, GY, 420, { light: M.practical, a: 0.2 });
    glow(g, CX + 675, GY - 420, 500, M.practical, 0.25);
  });
  layer(g, cam, 0.85, (g) => { g.fillStyle = linGrad(g, 0, GY, 0, GY + 300, [shade(M.road, 0.05), shade(M.dark, -0.3)]); g.fillRect(-E.W, GY, E.W * 3, E.H * 2); FX.pool(g, CX + 700, GY + 30, 420, 50, M.practical, 0.3); FX.floorLines(g, GY, GY + 300, 'rgba(0,0,0,.2)', 0.1); });
  return { GY, CX, M };
}

// ---------- brook (daylight, stones) ----------
export function brook(g, t, cam, o = {}) {
  const M = mood('golden'), GY = GYv(), CX = CXv();
  layer(g, cam, 0.1, (g) => { sky(g, M, t, { sun: [CX + 600, GY - 420] }); });
  layer(g, cam, 0.35, (g) => { FX.hills(g, { y: GY - 180, amp: 120, color: mix(M.sky[1], M.dark, 0.6), seed: 7 }); FX.fog(g, GY - 190, 150, M.fog, 0.2); });
  layer(g, cam, 0.85, (g) => {
    g.fillStyle = linGrad(g, 0, GY - 30, 0, GY + 300, [mix(M.grass, M.floor, 0.5), shade(M.dark, -0.3)]); g.fillRect(-E.W, GY - 30, E.W * 3, E.H * 2);
    // water band
    const wy = GY + 70; g.fillStyle = linGrad(g, 0, wy - 40, 0, wy + 60, [alpha(M.sky[2], 0.65), alpha(shade(M.sky[1], -0.3), 0.8)]); g.fillRect(-E.W, wy - 40, E.W * 3, 100);
    g.strokeStyle = alpha('#fff3dc', 0.4); g.lineWidth = 2; for (let i = 0; i < 30; i++) { const x = ((i * 137 + t * 80) % (E.W + 400)) - 200, y = wy - 30 + (i * 29) % 80; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 40, y); g.stroke(); }
    const r = rng(3); for (let i = 0; i < 40; i++) { const x = -200 + r() * (E.W + 400), y = wy - 40 + r() * 110, rr2 = 8 + r() * 18; g.fillStyle = shade(STONE, -0.2 - r() * 0.3); g.beginPath(); g.ellipse(x, y, rr2 * 1.3, rr2 * 0.8, 0, 0, 7); g.fill(); g.fillStyle = alpha('#fff3dc', 0.25); g.beginPath(); g.ellipse(x - rr2 * 0.3, y - rr2 * 0.3, rr2 * 0.4, rr2 * 0.2, 0, 0, 7); g.fill(); }
    for (let i = 0; i < 18; i++) { const x = -100 + i * 120 + (i % 3) * 20; seg(g, [[x, GY - 10], [x + Math.sin(t + i) * 6, GY - 90 - (i % 4) * 20]], 3, shade(M.grass, -0.3)); }
  });
  return { GY, CX, M };
}
