// _props.js — props, creatures and character helpers for Davi e Golias (biblical setting).
import { E, S, V, clamp, lerp, ease, prog, seg, circle, ring, rr, poly, glow, alpha, shade, mix, linGrad, radGrad, rng, talkAmount } from '/engine/core.js';
import { drawFigure, POSES, headPos, bigFace } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { DAVID, GOLIAS, SAUL, SAMUEL, JESSE, ELIABE, BROTHER, YOU, SOLDIER, SCALE } from './cast.js';

export const BRONZE = '#b8893e', BRONZE_D = '#6e5528', GOLD = '#f2c24a', IRON = '#8a8f9a', WOOD = '#5a3a24', LEATHER = '#7a4a2a', STONE = '#9a948a', WOOL = '#e9e2d2', CREST = '#d8452e';

// ---------- small math ----------
export const handPos = (o, which = 'F') => { const p = o.pose || POSES.stand, s = (o.s ?? 1) * (o.outfit?.kid ? 0.72 : 1), f = o.facing ?? 1, h = p['h' + which]; return [o.x + h[0] * f * s, o.y + h[1] * s]; };

// ---------- weapons & gear ----------
export function spear(g, x1, y1, x2, y2, w = 5, head = IRON) {
  seg(g, [[x1, y1], [x2, y2]], w, WOOD);
  const a = Math.atan2(y2 - y1, x2 - x1), L = w * 6, W = w * 1.7;
  poly(g, [[x2 + Math.cos(a) * L, y2 + Math.sin(a) * L], [x2 + Math.cos(a + 1.57) * W, y2 + Math.sin(a + 1.57) * W], [x2 - Math.cos(a) * w, y2 - Math.sin(a) * w], [x2 + Math.cos(a - 1.57) * W, y2 + Math.sin(a - 1.57) * W]], head);
}
export function sword(g, x, y, ang, len = 120, w = 9) {
  const c = Math.cos(ang), s = Math.sin(ang);
  seg(g, [[x, y], [x + c * len, y + s * len]], w, '#c9ccd4');
  seg(g, [[x + c * len * 0.1, y + s * len * 0.1], [x + c * len, y + s * len]], w * 0.3, '#f2f4f8');
  seg(g, [[x - s * w * 2.2, y + c * w * 2.2], [x + s * w * 2.2, y - c * w * 2.2]], w * 0.9, BRONZE_D);
  seg(g, [[x, y], [x - c * len * 0.18, y - s * len * 0.18]], w * 0.9, LEATHER);
}
export function shield(g, x, y, r, rimC = null) {
  if (rimC) circle(g, x - 3, y - 3, r + 3, rimC);
  circle(g, x, y, r, BRONZE_D); circle(g, x, y, r * 0.86, BRONZE); ring(g, x, y, r * 0.6, r * 0.06, shade(BRONZE, -0.3)); circle(g, x, y, r * 0.16, shade(BRONZE, 0.3));
  g.save(); g.globalCompositeOperation = 'lighter'; g.fillStyle = 'rgba(255,230,170,.18)'; g.beginPath(); g.arc(x - r * 0.25, y - r * 0.3, r * 0.45, 0, 7); g.fill(); g.restore();
}
export function stone(g, x, y, r, rot = 0, lit = '#fff3dc') {
  g.save(); g.translate(x, y); g.rotate(rot); g.fillStyle = STONE; g.beginPath(); g.ellipse(0, 0, r * 1.15, r * 0.9, 0, 0, 7); g.fill();
  g.fillStyle = shade(STONE, -0.35); g.beginPath(); g.ellipse(r * 0.2, r * 0.25, r * 0.9, r * 0.6, 0, 0, 7); g.fill();
  g.fillStyle = alpha(lit, 0.55); g.beginPath(); g.ellipse(-r * 0.35, -r * 0.35, r * 0.35, r * 0.22, -0.5, 0, 7); g.fill(); g.restore();
}
// sling hanging from a hand (hx,hy); whirl>0 spins the pouch around the hand
export function sling(g, hx, hy, t, o = {}) {
  const { whirl = 0, len = 70, w = 3, stoneR = 0, swing = 1 } = o;
  let px, py;
  if (whirl > 0) { const a = t * whirl * Math.PI * 2; px = hx + Math.cos(a) * len; py = hy - len * 0.9 + Math.sin(a) * len * 0.35; }
  else { const a = Math.sin(t * 2.2) * 0.25 * swing; px = hx + Math.sin(a) * len; py = hy + Math.cos(a) * len; }
  g.strokeStyle = '#d8c09a'; g.lineWidth = w; g.lineCap = 'round';
  g.beginPath(); g.moveTo(hx, hy); g.quadraticCurveTo((hx + px) / 2 - 8, (hy + py) / 2, px - w * 2, py); g.stroke();
  g.beginPath(); g.moveTo(hx + 2, hy); g.quadraticCurveTo((hx + px) / 2 + 8, (hy + py) / 2, px + w * 2, py); g.stroke();
  g.fillStyle = LEATHER; g.beginPath(); g.ellipse(px, py, w * 3.2, w * 2.2, 0, 0, 7); g.fill();
  if (stoneR) stone(g, px, py - w, stoneR);
  return [px, py];
}
export function staff(g, hx, hy, GYl, s = 1) {
  seg(g, [[hx, GYl - 4], [hx, hy - 70 * s], [hx + 4 * s, hy - 96 * s]], 6 * s, WOOD);
  g.strokeStyle = WOOD; g.lineWidth = 6 * s; g.lineCap = 'round'; g.beginPath(); g.arc(hx + 18 * s, hy - 96 * s, 16 * s, Math.PI, Math.PI * 2.15); g.stroke();
}
export function bag(g, x, y, s = 1) { rr(g, x - 16 * s, y - 4 * s, 32 * s, 26 * s, 9 * s); g.fillStyle = LEATHER; g.fill(); seg(g, [[x - 14 * s, y], [x + 14 * s, y]], 3 * s, shade(LEATHER, -0.3)); }

// ---------- headgear ----------
export function crown(g, x, y, r, a = 1) {
  g.save(); g.globalAlpha *= a; const w = r * 1.25, h = r * 0.55, y0 = y - r * 0.72;
  poly(g, [[x - w / 2, y0 + h * 0.2], [x - w / 2, y0 - h * 0.6], [x - w / 4, y0 - h * 0.05], [x, y0 - h * 0.8], [x + w / 4, y0 - h * 0.05], [x + w / 2, y0 - h * 0.6], [x + w / 2, y0 + h * 0.2]], GOLD);
  for (const dx of [-0.25, 0, 0.25]) circle(g, x + dx * w, y0 + h * 0.02, r * 0.05, '#e0443a');
  glow(g, x, y0 - h * 0.2, r * 1.2, GOLD, 0.25); g.restore();
}
// bronze helmet with a crest (Goliath) — for figures (r = head radius)
export function helmet(g, hx, hy, r, facing = 1, rimC = null, ho = {}) {
  const { crest = true, mono = null, crestK = 1 } = ho; const BR = mono || BRONZE;
  g.save(); g.translate(hx, hy - r * 0.4); g.scale(facing, 1);
  if (rimC) { g.fillStyle = rimC; g.beginPath(); g.arc(-2, -2, r * 1.1, Math.PI * 0.95, Math.PI * 2.05); g.fill(); }
  g.fillStyle = BR; g.beginPath(); g.arc(0, 0, r * 1.06, Math.PI * 0.95, Math.PI * 2.05); g.closePath(); g.fill();
  g.fillStyle = shade(BR, -0.35); g.fillRect(-r * 1.06, -r * 0.08, r * 2.12, r * 0.18);
  poly(g, [[r * 0.12, 0], [r * 0.2, r * 0.62], [r * 0.04, r * 0.62]], shade(BR, -0.15));
  if (crest) { g.fillStyle = mono || CREST; for (let i = 0; i < 9; i++) { const a = Math.PI * (1.12 + i * 0.095); g.beginPath(); g.ellipse(Math.cos(a) * r * (1.06 + 0.24 * crestK), Math.sin(a) * r * (1.06 + 0.24 * crestK), r * 0.1 * crestK, r * 0.34 * crestK, a + Math.PI / 2, 0, 7); g.fill(); } }
  if (!mono) g.fillStyle = 'rgba(255,235,190,.35)'; else g.fillStyle = 'rgba(0,0,0,0)'; g.beginPath(); g.ellipse(-r * 0.3, -r * 0.6, r * 0.3, r * 0.12, -0.4, 0, 7); g.fill();
  g.restore();
}
export function crestBand(g, hx, hy, r) { g.fillStyle = CREST; for (let i = 0; i < 5; i++) { const a = Math.PI * (1.25 + i * 0.12); g.beginPath(); g.ellipse(hx + Math.cos(a) * r * 1.25, hy + Math.sin(a) * r * 1.25, r * 0.12, r * 0.34, a + Math.PI / 2, 0, 7); g.fill(); } }
export function capIsr(g, hx, hy, r) { g.fillStyle = shade(BRONZE, -0.45); g.beginPath(); g.arc(hx, hy, r * 1.04, Math.PI, Math.PI * 2); g.fill(); }

// ---------- creatures ----------
export function sheep(g, x, y, s = 1, facing = 1, t = 0, seed = 1, o = {}) {
  const graze = o.graze ?? (Math.sin(t * 0.7 + seed * 2.3) > 0.2 ? 1 : 0), rimC = o.rim;
  g.save(); g.translate(x, y); g.scale(facing * s, s);
  g.fillStyle = 'rgba(0,0,0,.25)'; g.beginPath(); g.ellipse(0, 2, 48, 7, 0, 0, 7); g.fill();
  for (const lx of [-24, -12, 14, 26]) seg(g, [[lx, -22], [lx, 0]], 6, S().ink);
  const wool = o.lamb ? '#f4efe4' : WOOL, puffs = [[-26, -40, 20], [-8, -48, 22], [12, -46, 22], [28, -38, 18], [-16, -30, 20], [10, -30, 21]];
  if (rimC) for (const [px, py, r] of puffs) circle(g, px - 3, py - 3, r + 3, rimC);
  for (const [px, py, r] of puffs) circle(g, px, py, r, wool);
  g.fillStyle = shade(wool, -0.18); g.beginPath(); g.ellipse(0, -28, 40, 10, 0, 0, 7); g.fill();
  const hy = graze ? -22 : -54, hx = 46;
  g.fillStyle = S().ink; g.beginPath(); g.ellipse(hx, hy, 14, 11, graze ? 0.8 : 0.2, 0, 7); g.fill(); g.beginPath(); g.ellipse(hx - 8, hy - 6, 8, 4, -0.6, 0, 7); g.fill();
  circle(g, hx + 4, hy - 3, 2.4, '#ffffff');
  g.restore();
}
export function lion(g, x, y, s = 1, facing = 1, t = 0, o = {}) {
  const { rimC = null, lamb = false, leap = 0 } = o; const ink = S().ink;
  g.save(); g.translate(x, y - leap * 60 * s); g.scale(facing * s, s); g.rotate(-leap * 0.25);
  const body = (c) => { g.fillStyle = c; g.beginPath(); g.ellipse(0, -60, 78, 30, 0, 0, 7); g.fill(); for (const [lx, k] of [[-50, 0], [-36, 1], [40, 0], [54, 1]]) seg(g, [[lx, -50], [lx + (k ? 6 : -4) + Math.sin(t * 6 + lx) * 4 * leap, 0]], 13, c);
    g.strokeStyle = c; g.lineWidth = 7; g.beginPath(); g.moveTo(-76, -66); g.quadraticCurveTo(-120, -90 + Math.sin(t * 3) * 10, -112, -40); g.stroke(); circle(g, -112, -40, 9, c);
    circle(g, 84, -84, 46, c); circle(g, 98, -80, 28, c); };
  if (rimC) { g.save(); g.translate(-4, -4); body(rimC); g.restore(); }
  body(ink); circle(g, 84, -84, 46, shade('#8a5a2a', -0.45)); circle(g, 98, -80, 28, ink);
  circle(g, 108, -88, 4, '#ffd45a'); seg(g, [[106, -68], [122, -66]], 3, '#ffd45a');
  if (lamb) sheep(g, 128, -54, 0.5, 1, 0, 3, { lamb: true, graze: 0 });
  g.restore();
}
export function bear(g, x, y, s = 1, facing = 1, t = 0, o = {}) {
  const { rimC = null, rear = 0 } = o; const ink = S().ink;
  g.save(); g.translate(x, y); g.scale(facing * s, s);
  const shape = (c) => { g.save(); g.rotate(-rear * 1.1); g.fillStyle = c; g.beginPath(); g.ellipse(0, -70, 90, 52, 0, 0, 7); g.fill(); circle(g, 92, -96, 40, c); circle(g, 80, -132, 13, c); circle(g, 104, -134, 13, c);
    for (const lx of [-60, 50]) seg(g, [[lx, -50], [lx, 0]], 30, c); seg(g, [[60, -70], [rear ? 130 : 66, rear ? -60 : 0]], 26, c); g.restore(); };
  if (rimC) { g.save(); g.translate(-5, -5); shape(rimC); g.restore(); }
  shape(ink); g.save(); g.rotate(-rear * 1.1); circle(g, 108, -102, 4, '#ffd45a'); g.restore();
  g.restore();
}
export function vulture(g, x, y, s = 1, t = 0) {
  const f = Math.sin(t * 5) * 0.35; g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = S().ink;
  g.beginPath(); g.moveTo(0, 0); g.quadraticCurveTo(-40, -20 - f * 30, -80, -6 - f * 40); g.quadraticCurveTo(-40, 4, 0, 6); g.quadraticCurveTo(40, 4, 80, -6 - f * 40); g.quadraticCurveTo(40, -20 - f * 30, 0, 0); g.fill();
  circle(g, 0, 2, 7, S().ink); g.restore();
}

// ---------- objects ----------
export function tent(g, x, GYl, w, h, color, o = {}) {
  const { lit = 0, light = '#ffd59a', open = 0.35, dark = shade(color, -0.45) } = o;
  poly(g, [[x - w / 2, GYl], [x, GYl - h], [x + w / 2, GYl]], color);
  poly(g, [[x, GYl - h], [x + w / 2, GYl], [x + w * 0.18, GYl]], shade(color, -0.25));
  const dw = w * 0.22 * open + 6; poly(g, [[x - dw, GYl], [x, GYl - h * 0.55], [x + dw, GYl]], lit ? light : dark);
  if (lit) glow(g, x, GYl - h * 0.2, w * 0.5, light, 0.35 * lit);
  seg(g, [[x, GYl - h], [x, GYl - h - 18]], 3, dark);
}
export function oilHorn(g, x, y, ang, s = 1) { g.save(); g.translate(x, y); g.rotate(ang); g.scale(s, s); g.fillStyle = '#e8dcc0'; g.beginPath(); g.moveTo(0, -8); g.quadraticCurveTo(40, -24, 70, -6); g.lineTo(70, 6); g.quadraticCurveTo(40, 0, 0, 8); g.closePath(); g.fill(); g.fillStyle = '#b8a888'; g.fillRect(56, -8, 6, 16); g.restore(); }
export function loaf(g, x, y, s = 1) { g.fillStyle = '#c88a4a'; g.beginPath(); g.ellipse(x, y, 34 * s, 20 * s, 0, Math.PI, 0); g.lineTo(x + 34 * s, y + 4 * s); g.lineTo(x - 34 * s, y + 4 * s); g.fill(); g.strokeStyle = '#8a5a2a'; g.lineWidth = 2.5 * s; for (const dx of [-12, 0, 12]) { g.beginPath(); g.moveTo(x + dx * s - 5 * s, y - 14 * s); g.lineTo(x + dx * s + 5 * s, y - 4 * s); g.stroke(); } }
export function cheese(g, x, y, s = 1) { g.fillStyle = '#e8c86a'; g.beginPath(); g.ellipse(x, y, 30 * s, 12 * s, 0, 0, 7); g.fill(); g.fillRect(x - 30 * s, y - 14 * s, 60 * s, 14 * s); g.fillStyle = '#f4dc8a'; g.beginPath(); g.ellipse(x, y - 14 * s, 30 * s, 12 * s, 0, 0, 7); g.fill(); }
export function coin(g, x, y, r) { circle(g, x, y, r, '#e8b84a'); ring(g, x, y, r * 0.7, r * 0.12, '#b8862a'); }
export function heartShape(g, x, y, s, color) { g.fillStyle = color; g.beginPath(); g.moveTo(x, y + s * 0.9); g.bezierCurveTo(x - s * 1.4, y - s * 0.1, x - s * 0.7, y - s * 1.1, x, y - s * 0.45); g.bezierCurveTo(x + s * 0.7, y - s * 1.1, x + s * 1.4, y - s * 0.1, x, y + s * 0.9); g.fill(); }
export function eyeIcon(g, x, y, s, color, w = 6) { g.strokeStyle = color; g.lineWidth = w; g.beginPath(); g.moveTo(x - s, y); g.quadraticCurveTo(x, y - s * 0.75, x + s, y); g.quadraticCurveTo(x, y + s * 0.75, x - s, y); g.stroke(); circle(g, x, y, s * 0.3, color); }
export function keyIcon(g, x, y, s, color, w = 8) { ring(g, x - s * 0.6, y, s * 0.35, w, color); seg(g, [[x - s * 0.25, y], [x + s, y], [x + s, y + s * 0.3]], w, color); seg(g, [[x + s * 0.65, y], [x + s * 0.65, y + s * 0.25]], w, color); }

// ---------- characters ----------
const WHO = {
  david: { outfit: DAVID, k: SCALE.david }, goliath: { outfit: GOLIAS, k: SCALE.goliath }, saul: { outfit: SAUL, k: 1.05 }, samuel: { outfit: SAMUEL, k: 1 },
  jesse: { outfit: JESSE, k: 0.98 }, eliabe: { outfit: ELIABE, k: SCALE.eliabe }, brother: { outfit: BROTHER, k: 1.02 }, you: { outfit: YOU, k: 1 },
  soldier: { outfit: SOLDIER, k: 1 }, phil: { outfit: SOLDIER, k: 1 },
};
export const whoOutfit = (w) => WHO[w].outfit;
// actor(g, {who, x, y, s, facing, pose, expr, talk, rim, gear:{spear, sling, staff, shield, sword, bag}, ...}) — draws figure + gear
export function actor(g, o) {
  const W = WHO[o.who] || WHO.soldier, s = (o.s ?? 1) * W.k, f = o.facing ?? 1;
  const fo = { ...o, s, facing: f, outfit: W.outfit, pose: o.pose || POSES.stand };
  const gear = o.gear || {}, rimC = o.rim?.color;
  if (gear.spear || o.who === 'goliath' && gear.spear !== false) { const [hx, hy] = handPos(fo, 'B'); const up = gear.spearUp ?? 1; spear(g, hx - f * 6 * s, hy + 60 * s * up, hx + f * 18 * s, hy - 190 * s * up, 6 * s); }
  if (gear.staff) { const [hx, hy] = handPos(fo, 'B'); staff(g, hx, hy, o.y, s); }
  drawFigure(g, fo);
  const [hx, hy, hr] = headPos(fo);
  if (o.who === 'goliath') helmet(g, hx, hy, hr, f, rimC);
  if (o.who === 'saul' && o.crown !== false) crown(g, hx, hy, hr);
  if (o.who === 'soldier' && o.cap !== false) capIsr(g, hx, hy, hr);
  if (o.who === 'phil') crestBand(g, hx, hy, hr);
  if (o.who === 'goliath' && gear.shield !== false) { const [bx, by] = handPos(fo, 'F'); shield(g, bx + f * 8 * s, by - 10 * s, 34 * s, rimC); }
  if (gear.sling) { const [ax, ay] = handPos(fo, gear.slingHand || 'F'); sling(g, ax, ay, o.t || 0, { len: 46 * s, w: 2.4 * s, whirl: gear.whirl || 0, stoneR: gear.stone ? 7 * s : 0 }); }
  if (gear.sword) { const [ax, ay] = handPos(fo, 'F'); sword(g, ax, ay, gear.swordAng ?? -1.4, 120 * s * (gear.swordK || 1), 9 * s); }
  if (gear.bag) bag(g, o.x - f * 14 * s, o.y - 96 * s, s);
  if (gear.sack) { const [ax, ay] = handPos(fo, 'B'); rr(g, ax - 30 * s, ay - 60 * s, 52 * s, 48 * s, 16 * s); g.fillStyle = '#b8a07a'; g.fill(); }
  if (o.talk) FX.rings(g, hx + f * hr * 0.6, hy, o.t || 0, { count: 2, r0: hr * 1.3, r1: hr * 2.6, color: rimC || '#fff1e6', a: 0.3 * Math.min(1, o.talk * 3) });
  return { hx, hy, hr };
}
// giant close-up with per-character extras
export function face(g, who, cx, cy, r, o = {}) {
  const W = WHO[who];
  bigFace(g, cx, cy, r, { outfit: W.outfit, expr: o.expr, talk: o.talk, blink: o.blink, look: o.look, rimColor: o.rimColor, rimSide: o.rimSide, tilt: o.tilt });
  if (who === 'saul') crown(g, cx, cy - r * 0.15, r, 1);
  if (who === 'goliath') helmet(g, cx, cy - r * 0.12, r * 0.92, 1, null, { crestK: 0.5 });
  if (who === 'david' && o.helmet) { g.save(); g.translate(cx, cy + r * 0.1 * o.helmet); helmet(g, 0, -r * 0.05, r * 1.08, 1, null, { crest: false }); g.restore(); }
}
