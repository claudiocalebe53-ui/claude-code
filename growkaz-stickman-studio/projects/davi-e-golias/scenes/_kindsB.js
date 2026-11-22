// _kindsB.js — inserts, blueprints, glowing lines, lessons and modern-day scenes.
import { E, V, S, mood, layer, blurLayer, veil, ease, prog, key, clamp, lerp, shake, talkAmount, wordTime, seg, circle, ring, rr, poly, glow, alpha, shade, mix, linGrad, radGrad, text, measure, FONTS, rng, backdrop } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe, walkPose } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { valley, camp, pasture, house, tentIn, street, brook, GYv } from './_sets.js';
import { actor, face, sheep, lion, bear, stone, sling, shield, sword, spear, helmet, crown, loaf, cheese, coin, heartShape, eyeIcon, keyIcon, BRONZE, GOLD, IRON, LEATHER, WOOD } from './_props.js';
import { K, camAt } from './_kindsA.js';

const CX = () => E.W / 2;
const P = (n) => POSES[n];
const ui = () => S().ui;
const lbl = (g, str, x, y, o = {}) => text(g, str, x, y, { size: o.size || V(40, 46), color: o.color || ui().cream, font: FONTS.ui, weight: 900, spacing: 2, alpha: o.a ?? 1, align: o.align || 'center', glow: o.glow ?? 10, glowColor: alpha(o.color || ui().cream, 0.5) });
const big = (g, str, x, y, o = {}) => text(g, str, x, y, { size: o.size || V(84, 80), color: o.color || ui().gold, glow: 26, glowColor: alpha(o.color || ui().gold, 0.6), spacing: 3, alpha: o.a ?? 1 });
const pop = (t, a, b = a + 0.4) => ease.outBack(prog(t, a, b));
const fin = (t, a, b = a + 0.4) => ease.out(prog(t, a, b));

// big hand helpers (inserts)
function arm(g, x, y, s, sleeveC, fromX = E.W + 300, fromY = E.H + 200) {
  const ink = S().ink; seg(g, [[x, y], [fromX, fromY]], 70 * s, ink); seg(g, [[lerp(x, fromX, 0.35), lerp(y, fromY, 0.35)], [fromX, fromY]], 96 * s, sleeveC);
}
function fist(g, x, y, s, open = 0) { const ink = S().ink; circle(g, x, y, 46 * s, ink); for (let i = 0; i < 4; i++) { const a = -2.3 + i * 0.3; const L = lerp(28, 90, open); seg(g, [[x, y], [x + Math.cos(a) * L * s, y + Math.sin(a) * L * s]], 18 * s, ink); } seg(g, [[x - 6 * s, y + 10 * s], [x - 60 * s, y + lerp(20, 50, open) * s]], 18 * s, ink); }
const INS_BG = { valley: (g, t) => valley(g, t, { z: 1.8, x: -160, y: -180 }, { israel: false, phil: false }), pasture: (g, t) => pasture(g, t, { z: 1.7, x: 200, y: -160 }), camp: (g, t) => camp(g, t, { z: 1.7, x: 100, y: -140 }), tent: (g, t) => tentIn(g, t, { z: 1.6, x: -200, y: -160 }), street: (g, t) => street(g, t, { z: 1.6, x: 200, y: -180 }), brook: (g, t) => brook(g, t, { z: 1.7, x: 0, y: -120 }) };

// ======================= INSERTS =======================
K.insert = (g, t, info, p) => {
  const d = info.dur, o = p.obj, k = ease.inOut(t / d);
  const bgName = { slingStones: 'pasture', book: 'tent', armor: 'valley', spear: 'valley', bread: 'tent', cheese: 'tent', coins: 'camp', armorPieces: 'tent', pouch: 'brook', sling: 'valley', handStone: 'valley', whirl: 'valley', handGlow: 'pasture', modernStones: 'street' }[o] || 'valley';
  blurLayer(g, 16, (g) => INS_BG[bgName](g, t)); veil(g, '#0a0608', 0.4);
  const M = mood(bgName === 'street' ? 'night' : bgName === 'tent' ? 'interiorWarm' : 'golden');
  const z = 1 + 0.06 * k; g.save(); g.translate(E.W / 2, E.H / 2); g.scale(z, z); g.translate(-E.W / 2, -E.H / 2);
  const DAV = '#c8552e', s = V(1.4, 1.3);
  if (o === 'slingStones' || o === 'handGlow' || o === 'sling') {
    const hx = E.W * 0.42, hy = E.H * 0.38; arm(g, hx, hy, s, DAV, E.W + 200, E.H * 0.1); fist(g, hx, hy, s);
    sling(g, hx - 20, hy + 30, t, { len: 260, w: 7, swing: 1.5, stoneR: o === 'handGlow' ? 22 : 0 });
    if (o === 'slingStones') for (let i = 0; i < 5; i++) { const a = pop(t, 0.5 + i * 0.3); if (a <= 0) continue; g.save(); g.translate(E.W * 0.62 + i * 90, E.H * 0.74); g.scale(a, a); stone(g, 0, 0, 30, i); g.restore(); lbl(g, String(i + 1), E.W * 0.62 + i * 90, E.H * 0.62, { a: fin(t, 0.5 + i * 0.3), color: ui().gold }); }
    if (o === 'handGlow') { glow(g, hx, hy + 120, 420, '#fff3dc', 0.35 + 0.1 * Math.sin(t * 3)); FX.sparkle(g, hx + 40, hy + 280, 40, '#fff3dc', 0.8); }
  }
  if (o === 'book') {
    const bx = E.W / 2, by = E.H * 0.55, w = 520, h = 360, open = ease.inOut(prog(t, 0.2, 1.4));
    rr(g, bx - w - 10, by - h / 2 - 10, w * 2 + 20, h + 20, 14); g.fillStyle = '#6a2a2a'; g.fill();
    g.fillStyle = '#f2e6c8'; g.fillRect(bx - w, by - h / 2, w, h); g.fillRect(bx, by - h / 2, w, h); seg(g, [[bx, by - h / 2], [bx, by + h / 2]], 4, '#c8b088');
    const ink = '#3a2a1a'; g.save(); g.globalAlpha *= open; drawFigure(g, { x: bx - w * 0.6, y: by + h * 0.35, s: 0.8, facing: 1, pose: P('point'), expr: 'happy', outfit: { top: 'dress', color: '#c8552e', head: 'curly' }, rim: false });
    drawFigure(g, { x: bx + w * 0.45, y: by + h * 0.4, s: 1.4, facing: -1, pose: P('stand'), expr: 'angry', outfit: { top: 'suit', color: '#9a7a3c' }, rim: false });
    text(g, 'Era uma vez...', bx - w / 2, by - h / 2 + 50, { size: 36, color: ink, font: FONTS.serif, weight: 900, italic: true, glow: 0 }); g.restore();
    const turn = prog(t, 1.4, 2.2); if (turn > 0 && turn < 1) { g.fillStyle = '#e8dcbc'; const w2 = w * Math.cos(turn * Math.PI); g.fillRect(bx, by - h / 2, w2, h); }
  }
  if (o === 'armor') {
    const cx = E.W / 2, cy = E.H * 0.56, r = 250; g.save(); g.translate(cx, cy);
    for (let j = 0; j < 7; j++) for (let i = -6; i <= 6; i++) { const x = i * 46 + (j % 2) * 23, y = j * 34 + 40; g.fillStyle = shade(BRONZE, -0.1 - ((i + j) % 3) * 0.08); g.beginPath(); g.ellipse(x, y, 26, 34, 0, 0, Math.PI); g.fill(); }
    g.restore(); helmet(g, cx, cy - 120, r * 0.9, 1, null);
    const sh = (t * 0.6) % 1; FX.lensStreak(g, lerp(cx - 500, cx + 500, sh), cy - 220, 500, '#fff3dc', 0.6, 4); FX.sparkle(g, lerp(cx - 300, cx + 300, sh), cy - 260, 50, '#fff3dc', 0.9);
    UI.callout(g, t, { at: [cx - 60, cy - 300], to: [cx - 420, cy - 380], str: 'BRONZE', start: 0.4, color: ui().gold });
  }
  if (o === 'spear') {
    const a = -0.35; spear(g, -200, E.H * 0.85, E.W * 0.62, E.H * 0.38, 30, IRON); glow(g, E.W * 0.7, E.H * 0.33, 260, '#cfd8ff', 0.2);
    UI.readout(g, { label: 'PONTA DE FERRO', value: `≈ ${Math.round(lerp(0, 7, fin(t, 1.0, 2.2)))} kg`, x: E.W * 0.6, y: E.H * 0.72, a: fin(t, 0.8, 1.1) });
  }
  if (o === 'bread' || o === 'cheese') {
    const n = Math.min(10, Math.floor(clamp((t - 0.3) / (d * 0.7)) * 10.99));
    rr(g, E.W * 0.08, E.H * 0.72, E.W * 0.84, 40, 12); g.fillStyle = '#4a2e22'; g.fill();
    for (let i = 0; i < n; i++) { const x = E.W * 0.16 + (i % 5) * 300, y = E.H * (i < 5 ? 0.66 : 0.5); o === 'bread' ? loaf(g, x, y, 2.3) : cheese(g, x, y, 2.2); }
    if (o === 'bread') { rr(g, E.W * 0.82, E.H * 0.28, 200, 240, 60); g.fillStyle = '#b8a07a'; g.fill(); for (let i = 0; i < 20; i++) circle(g, E.W * 0.86 + (i % 5) * 26, E.H * 0.3 - 6 + Math.floor(i / 5) * 8, 7, '#d8b060'); }
    UI.readout(g, { value: `${n} ${o === 'bread' ? 'PÃES' : 'QUEIJOS'}`, x: E.W / 2, y: E.H * 0.2, align: 'center', size: V(60, 64) });
  }
  if (o === 'coins') {
    const cx = E.W / 2, cy = E.H * 0.7; glow(g, cx, cy - 80, 520, GOLD, 0.35);
    const r = rng(4); for (let i = 0; i < 140; i++) { const a = r() * Math.PI, d2 = r() ** 0.6 * 420; const x = cx + Math.cos(a) * d2 * (r() < 0.5 ? -1 : 1), y = cy - Math.sin(a) * d2 * 0.45 + 40 + (1 - fin(t, 0, 0.8)) * 400 * r(); coin(g, x, y, 22); }
    for (let i = 0; i < 6; i++) FX.sparkle(g, cx - 300 + i * 120, cy - 120 - (i % 3) * 60, 30, '#fff3dc', Math.abs(Math.sin(t * 3 + i)));
    UI.readout(g, { value: 'GRANDES RIQUEZAS', x: E.W / 2, y: E.H * 0.18, align: 'center', size: V(56, 60), a: fin(t, 0.5) });
  }
  if (o === 'armorPieces') {
    const items = [['CAPACETE', 0.2, (x, y) => helmet(g, x, y, 90, 1, null, { crest: false })], ['COURAÇA', 0.9, (x, y) => { rr(g, x - 90, y - 120, 180, 240, 30); g.fillStyle = BRONZE; g.fill(); g.strokeStyle = shade(BRONZE, -0.35); g.lineWidth = 6; g.stroke(); }], ['ESPADA', 1.6, (x, y) => sword(g, x - 20, y + 130, -1.45, 300, 16)]];
    items.forEach(([str, at, fn], i) => { const a = pop(t, at); if (a <= 0) return; const x = E.W * (0.22 + i * 0.28), y = E.H * 0.5; g.save(); g.translate(x, y); g.scale(a, a); g.translate(-x, -y); fn(x, y); g.restore(); lbl(g, str, x, E.H * 0.82, { a: fin(t, at + 0.2), color: ui().gold }); });
  }
  if (o === 'pouch') {
    const bx = E.W / 2, by = E.H * 0.62; rr(g, bx - 220, by - 120, 440, 300, 90); g.fillStyle = LEATHER; g.fill(); g.fillStyle = shade(LEATHER, -0.4); g.beginPath(); g.ellipse(bx, by - 110, 200, 46, 0, 0, 7); g.fill();
    for (let i = 0; i < 5; i++) { const t0 = 0.2 + i * 0.32, u = prog(t, t0, t0 + 0.45); if (u <= 0) continue; const y = lerp(-100, by - 110, ease.in(u)); if (u < 1) stone(g, bx - 80 + i * 40, y, 28, i); }
    lbl(g, 'ALFORJE DE PASTOR', bx, E.H * 0.16, { a: fin(t, 0.3), color: ui().gold });
  }
  if (o === 'handStone') { const u = ease.inOut(prog(t, 0.2, d - 0.2)); const bx = E.W * 0.5, by = E.H * 0.72; rr(g, bx - 260, by - 140, 520, 340, 100); g.fillStyle = LEATHER; g.fill();
    const hx = lerp(bx, bx + 120, u), hy = lerp(by - 60, by - 420, u); arm(g, hx, hy, s, DAV, E.W + 200, E.H * 1.2); fist(g, hx, hy, s, 0.2); stone(g, hx - 40, hy - 40, 26); }
  if (o === 'whirl') { const hx = E.W * 0.5, hy = E.H * 0.55; arm(g, hx, hy, s, DAV, E.W * 0.7, E.H + 300); fist(g, hx, hy, s);
    for (let i = 0; i < 5; i++) { const a = (t - i * 0.03) * 13; g.save(); g.globalAlpha *= 0.15 * (5 - i); const px = hx + Math.cos(a) * 320, py = hy - 60 + Math.sin(a) * 200; seg(g, [[hx, hy], [px, py]], 6, '#d8c09a'); if (i === 0) stone(g, px, py, 24); g.restore(); }
    FX.rings(g, hx, hy - 60, t, { count: 3, r0: 200, r1: 420, speed: 2.4, color: '#fff3e0', a: 0.3 }); }
  if (o === 'modernStones') { const hx = lerp(E.W * 0.7, E.W * 0.5, ease.out(prog(t, 0, 1))), hy = lerp(E.H * 0.4, E.H * 0.62, ease.inOut(prog(t, 0, 1.2))); for (let i = 0; i < 5; i++) stone(g, E.W * 0.3 + i * 110, E.H * 0.8, 30, i); arm(g, hx, hy, s, '#8a5ad6', E.W + 200, E.H * 0.1); fist(g, hx, hy, s, 1 - prog(t, 0.8, 1.2)); if (t > 1.2) stone(g, hx - 30, hy + 40, 28); }
  g.restore();
  FX.dust(g, t, { count: 30, color: M.key, a: 0.3 });
};

// ======================= BLUEPRINTS =======================
function lf(g, x, y, s, pose = 'stand', facing = 1, color = null, a = 1) { g.save(); g.globalAlpha *= a; UI.lineFigure(g, { x, y, s, pose: typeof pose === 'string' ? P(pose) : pose, color: color || ui().blueprint, facing }); g.restore(); }
function cross(g, x, y, r, a = 1, c = ui().accent) { if (a <= 0) return; seg(g, [[x - r, y - r], [lerp(x - r, x + r, a), lerp(y - r, y + r, a)]], 10, c); if (a > 0.5) seg(g, [[x + r, y - r], [lerp(x + r, x - r, (a - 0.5) * 2), lerp(y - r, y + r, (a - 0.5) * 2)]], 10, c); }
K.bp = (g, t, info, p) => {
  const d = info.dur, m = p.mode, k = ease.inOut(t / d), U = ui(), B = U.blueprint, G = U.gold, A = U.accent;
  UI.blueprint(g); const z = 1 + 0.04 * k; g.save(); g.translate(E.W / 2, E.H / 2); g.scale(z, z); g.translate(-E.W / 2, -E.H / 2);
  const gy = E.H * 0.8;
  if (m === 'year') { const off = lerp(600, 0, ease.out(prog(t, 0, 1.6))); seg(g, [[-100, E.H * 0.55], [E.W + 100, E.H * 0.55]], 3, B);
    for (let i = -6; i <= 6; i++) { const x = E.W / 2 + i * 260 + off, yr = 1000 - i * 500; seg(g, [[x, E.H * 0.55 - 16], [x, E.H * 0.55 + 16]], 3, B); lbl(g, yr > 0 && i !== 0 ? `${yr}` : '', x, E.H * 0.62, { size: 26, color: alpha(B, 0.6), glow: 0 }); }
    const a = fin(t, 1.2); big(g, '≈ 1000 a.C.', E.W / 2, E.H * 0.38, { a }); circle(g, E.W / 2, E.H * 0.55, 12 * a, G); glow(g, E.W / 2, E.H * 0.55, 80, G, 0.5 * a); }
  if (m === 'appearance' || m === 'height1' || m === 'height2') {
    const tall = m === 'appearance' ? 1.25 : 2.0, x1 = E.W * 0.36, x2 = E.W * 0.6;
    lf(g, x1, gy, 1.0, 'stand', 1, alpha(B, 0.7)); lf(g, x2, gy, tall, m === 'appearance' ? 'crossArms' : 'stand', -1, m === 'appearance' ? B : G);
    if (m !== 'appearance') helmet(g, x2 - 6 * tall, gy - 208 * tall, 22 * tall, -1, null);
    seg(g, [[E.W * 0.15, gy], [E.W * 0.85, gy]], 3, B);
    const top = gy - 230 * tall; UI.dimension(g, t, { x1: x2 + 180, y1: gy, x2: x2 + 180, y2: top, str: m === 'appearance' ? 'ALTURA' : m === 'height1' ? '6 CÔVADOS + 1 PALMO' : '≈ 2,9 m', start: 0.3, color: G });
    if (m === 'height1') lbl(g, 'SOLDADO ≈ 1,7 m', x1, gy + 50, { size: 30, a: fin(t, 0.8) });
    if (m === 'height2') { const a = fin(t, 0.2, 0.6); big(g, '≈ 2,9 m', E.W * 0.22, E.H * 0.3, { a, size: V(110, 100) }); }
    if (m === 'appearance') { cross(g, x2, gy - 140 * tall, 230, ease.inOut(prog(t, 1.4, 2.2))); lbl(g, 'APARÊNCIA', x2, E.H * 0.12, { a: fin(t, 0.3), color: A }); }
  }
  if (m === 'eyeHeart' || m === 'heart') {
    const x = E.W * 0.58; lf(g, x, gy, 2.2, 'stand', -1, alpha(B, 0.85));
    if (m === 'eyeHeart') { const a1 = fin(t, 0.2, 0.7), a2 = fin(t, 2.0, 2.6); g.save(); g.globalAlpha *= a1 * (1 - 0.6 * a2); eyeIcon(g, E.W * 0.2, E.H * 0.35, 90, B); for (let i = 0; i < 5; i++) seg(g, [[E.W * 0.27, E.H * 0.35], [x - 60 + i * 30, gy - 480 + i * 80]], 2, alpha(B, 0.4)); lbl(g, 'O HOMEM', E.W * 0.2, E.H * 0.5, { size: 36 }); g.restore();
      g.save(); g.globalAlpha *= a2; lbl(g, 'O SENHOR', E.W * 0.2, E.H * 0.62, { size: 36, color: G }); g.restore(); }
    const ha = m === 'heart' ? fin(t, 0.1, 0.6) : fin(t, 2.0, 2.6); const beat = 1 + 0.08 * Math.max(0, Math.sin(t * 7)); if (ha > 0) { glow(g, x - 10, gy - 330, 260 * ha, A, 0.5); heartShape(g, x - 10, gy - 330, 60 * beat * ha, A); }
  }
  if (m === 'map' || m === 'march') {
    g.fillStyle = alpha(B, 0.08); g.beginPath(); g.moveTo(E.W * 0.38, -50); g.bezierCurveTo(E.W * 0.32, E.H * 0.3, E.W * 0.3, E.H * 0.7, E.W * 0.22, E.H + 50); g.lineTo(-100, E.H + 50); g.lineTo(-100, -50); g.closePath(); g.fill();
    g.strokeStyle = B; g.lineWidth = 4; g.beginPath(); g.moveTo(E.W * 0.38, -50); g.bezierCurveTo(E.W * 0.32, E.H * 0.3, E.W * 0.3, E.H * 0.7, E.W * 0.22, E.H + 50); g.stroke(); lbl(g, 'MAR', E.W * 0.12, E.H * 0.5, { size: 34, color: alpha(B, 0.7) });
    const cities = [[0.33, 0.25, 'ECROM'], [0.31, 0.4, 'ASDODE'], [0.36, 0.48, 'GATE'], [0.29, 0.6, 'ASCALOM'], [0.25, 0.78, 'GAZA']];
    cities.forEach(([x, y, n], i) => { const a = m === 'map' ? pop(t, 0.3 + i * 0.25) : 1; if (a <= 0) return; const X = E.W * x, Y = E.H * y; g.save(); g.translate(X, Y); g.scale(a, a); rr(g, -18, -18, 36, 36, 4); g.strokeStyle = n === 'GATE' ? G : B; g.lineWidth = 4; g.stroke(); for (const dx of [-14, 0, 14]) g.fillRect(dx - 3, -26, 6, 8); g.restore(); lbl(g, n, X + 30, Y, { size: 26, align: 'left', color: n === 'GATE' ? G : B, glow: 0, a: Math.min(1, a) }); });
    if (m === 'map') { const a = pop(t, 1.6); if (a > 0) { g.save(); g.translate(E.W * 0.7, E.H * 0.45); g.scale(a, a); sword(g, -160, 120, -0.6, 340, 18); g.restore(); lbl(g, 'ARMAS DE FERRO', E.W * 0.7, E.H * 0.75, { color: G, a: fin(t, 1.8) }); } }
    if (m === 'march') { const u = ease.inOut(prog(t, 0.2, d - 0.4)); const pts = [[E.W * 0.36, E.H * 0.48], [E.W * 0.5, E.H * 0.42], [E.W * 0.63, E.H * 0.45]]; g.strokeStyle = A; g.lineWidth = 8; g.setLineDash([22, 14]); g.beginPath(); g.moveTo(...pts[0]); g.quadraticCurveTo(pts[1][0], pts[1][1] - 60, lerp(pts[0][0], pts[2][0], u), lerp(pts[0][1], pts[2][1], u)); g.stroke(); g.setLineDash([]);
      const ex = lerp(pts[0][0], pts[2][0], u), ey = lerp(pts[0][1], pts[2][1], u); poly(g, [[ex + 30, ey], [ex - 10, ey - 24], [ex - 10, ey + 24]], A);
      const va = fin(t, d - 1.2); ring(g, E.W * 0.66, E.H * 0.45, 70, 4, alpha(G, va)); lbl(g, 'VALE DE ELÁ', E.W * 0.66, E.H * 0.6, { color: G, a: va }); lbl(g, 'ISRAEL', E.W * 0.82, E.H * 0.3, { size: 32, color: alpha(B, 0.7) }); }
  }
  if (m === 'exposed') { const cx = E.W / 2, cy = E.H / 2; g.fillStyle = alpha(B, 0.1); g.fillRect(cx - 700, cy - 260, 380, 520); g.fillRect(cx + 320, cy - 260, 380, 520); lbl(g, 'ISRAEL', cx - 510, cy - 300, { size: 32 }); lbl(g, 'FILISTEUS', cx + 510, cy - 300, { size: 32 });
    for (let i = 0; i < 18; i++) { circle(g, cx - 600 + (i % 6) * 40, cy - 120 + Math.floor(i / 6) * 60, 9, B); circle(g, cx + 400 + (i % 6) * 40, cy - 120 + Math.floor(i / 6) * 60, 9, B); }
    seg(g, [[cx - 40, cy - 300], [cx + 40, cy + 300]], 6, alpha('#7fb8ff', 0.5)); const a = fin(t, 0.8); g.fillStyle = alpha(A, 0.25 * a + 0.08 * Math.sin(t * 6) * a); g.fillRect(cx - 300, cy - 260, 600, 520);
    g.setLineDash([16, 12]); seg(g, [[cx - 330, cy], [lerp(cx - 330, cx - 40, ease.inOut(prog(t, 0.2, 1.2))), cy]], 4, G); g.setLineDash([]); lbl(g, 'EXPOSTO', cx, cy + 320, { color: A, size: V(56, 60), a }); }
  if (m === 'kg57') { const cx = E.W * 0.36, cy = E.H * 0.58; seg(g, [[cx, cy - 260], [cx, cy + 160]], 8, B); const tilt = 0.25 * fin(t, 0.2, 1); seg(g, [[cx - 260 * Math.cos(tilt), cy - 260 - 260 * Math.sin(-tilt)], [cx + 260 * Math.cos(tilt), cy - 260 + 260 * Math.sin(tilt)]], 6, B);
    const lx = cx - 260 * Math.cos(tilt), ly = cy - 260 + 260 * Math.sin(tilt); rr(g, lx - 90, ly + 60, 180, 120, 20); g.fillStyle = BRONZE; g.fill(); seg(g, [[lx, ly], [lx, ly + 60]], 3, B); seg(g, [[cx + 260, cy - 260 - 60], [cx + 260, cy - 200]], 3, B); rr(g, cx - 120, cy + 160, 240, 30, 10); g.fillStyle = alpha(B, 0.4); g.fill();
    UI.readout(g, { label: 'ARMADURA', value: `≈ ${Math.round(lerp(0, 57, ease.inOut(prog(t, 0.3, d - 0.4))))} kg`, x: E.W * 0.58, y: E.H * 0.5, size: V(90, 90) }); }
  if (m === 'days') { const n = Math.round(lerp(1, 40, ease.inOut(prog(t, 0.1, d - 0.2)))); const a = t * 6; FX.sun(g, E.W / 2 + Math.cos(a) * 420, E.H * 0.55 - Math.sin(a) * 280, 34, '#fff3dc', G, 2.5); FX.moon(g, E.W / 2 - Math.cos(a) * 420, E.H * 0.55 + Math.sin(a) * 280, 26);
    big(g, `${n} DIAS`, E.W / 2, E.H * 0.55, { size: V(140, 120) }); }
  if (m === 'iconRing' || m === 'iconTax') {
    if (m === 'iconRing') { const a = pop(t, 0.2); g.save(); g.translate(E.W * 0.38, E.H * 0.5); g.scale(a * 3, a * 3); crown(g, 0, 0, 60); g.restore(); const b = pop(t, 0.7); ring(g, E.W * 0.62, E.H * 0.52, 90 * b, 18, GOLD); FX.sparkle(g, E.W * 0.62, E.H * 0.52 - 100 * b, 40, '#fff3dc', b * Math.abs(Math.sin(t * 3)));
      lbl(g, 'A FILHA DO REI', E.W / 2, E.H * 0.82, { color: G, a: fin(t, 0.6) }); }
    else { const a = pop(t, 0.2); g.save(); g.translate(E.W / 2, E.H * 0.48); g.scale(a, a); rr(g, -220, -260, 440, 520, 20); g.fillStyle = '#e8dcbc'; g.fill(); for (let i = 0; i < 7; i++) seg(g, [[-160, -180 + i * 50], [160 - (i % 3) * 40, -180 + i * 50]], 6, '#b8a888');
      const st = ease.outBack(prog(t, 0.9, 1.2)); if (st > 0) { g.save(); g.rotate(-0.25); g.scale(st, st); g.strokeStyle = A; g.lineWidth = 12; g.strokeRect(-200, 40, 400, 120); text(g, 'ISENTO', 0, 102, { size: 80, color: A, glow: 0 }); g.restore(); } g.restore();
      lbl(g, 'SEM IMPOSTOS', E.W / 2, E.H * 0.9, { color: G, a: fin(t, 1.2) }); } }
  if (m === 'compare') { lf(g, E.W * 0.25, gy, 1.0, 'stand', 1, B); lf(g, E.W * 0.25 + 160, gy, 1.75, 'crossArms', -1, A);
    UI.compareBars(g, t, { rows: [{ label: 'RAPAZ', v: 0.22, color: B }, { label: 'GUERREIRO', v: 0.95, color: A }], x: E.W * 0.45, y: E.H * 0.42, w: V(640, 700), start: 0.5 }); lbl(g, 'EXPERIÊNCIA DE GUERRA', E.W * 0.65, E.H * 0.3, { size: 34, a: fin(t, 0.3) }); }
  if (m === 'strength') { lf(g, E.W * 0.3, gy, 1.6, 'stand', 1, B); UI.meter(g, t, { x: E.W * 0.45, y: E.H * 0.5, w: E.W * 0.42, ticks: 30, label: 'FORÇA PRÓPRIA', color: G, start: 0.3, speed: 0.12 }); cross(g, E.W * 0.66, E.H * 0.5, 90, ease.inOut(prog(t, d - 1.2, d - 0.4))); }
  if (m === 'copy') { lf(g, E.W * 0.38, gy, 1.5, 'stand', 1, B); crown(g, E.W * 0.38 + 6, gy - 208 * 1.5, 30); lf(g, E.W * 0.62, gy, 1.5, 'stand', -1, alpha(B, 0.5)); g.save(); g.globalAlpha *= 0.5; crown(g, E.W * 0.62 - 6, gy - 208 * 1.5, 30); g.restore(); lbl(g, 'CÓPIA', E.W * 0.62, E.H * 0.16, { color: A, a: fin(t, 0.3) }); cross(g, E.W * 0.62, gy - 180, 220, ease.inOut(prog(t, 0.8, 1.6))); }
  if (m === 'slingWeapon') { const hx = E.W * 0.42, hy = E.H * 0.42; seg(g, [[hx, hy], [E.W * 0.3, E.H + 100]], 10, B); const a = t * 8; const px = hx + Math.cos(a) * 260, py = hy + Math.sin(a) * 110; seg(g, [[hx, hy], [px, py]], 4, G); circle(g, px, py, 16, G); g.strokeStyle = alpha(B, 0.4); g.lineWidth = 2; g.beginPath(); g.ellipse(hx, hy, 260, 110, 0, 0, 7); g.stroke();
    lbl(g, 'NÃO É BRINQUEDO', E.W * 0.72, E.H * 0.38, { color: A, a: fin(t, 0.3) }); lbl(g, 'É UMA ARMA', E.W * 0.72, E.H * 0.5, { color: G, a: fin(t, 0.9), size: V(56, 60) }); }
  if (m === 'slingers') { for (let i = 0; i < 7; i++) { const x = E.W * 0.12 + i * 240, ph = t * 7 + i; lf(g, x, gy, 1.05, { ...P('stand'), eF: [20, -200], hF: [26, -236] }, 1, B, fin(t, i * 0.12)); const px = x + 28 + Math.cos(ph) * 50, py = gy - 250 + Math.sin(ph) * 20; seg(g, [[x + 28, gy - 248], [px, py]], 2, G); circle(g, px, py, 6, G); } lbl(g, 'FUNDIBULÁRIOS', E.W / 2, E.H * 0.2, { color: G, a: fin(t, 0.4) }); }
  if (m === 'hair') { const tx = E.W * 0.75, ty = E.H * 0.42, u = ease.inOut(prog(t, 0.6, 3.4)); seg(g, [[tx, ty - 220], [tx, ty + 220]], 2, '#e8f0ff'); ring(g, tx, ty, 60, 3, alpha(A, 0.8)); ring(g, tx, ty, 120, 2, alpha(A, 0.4));
    lf(g, E.W * 0.15, gy, 1.3, { ...P('point'), eF: [34, -176], hF: [74, -170] }, 1, B); g.setLineDash([14, 12]); g.strokeStyle = G; g.lineWidth = 4; g.beginPath(); for (let i = 0; i <= 40; i++) { const v = (i / 40) * u, x = lerp(E.W * 0.22, tx, v), y = lerp(gy - 220, ty, v) - Math.sin(v * Math.PI) * 120; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); g.setLineDash([]);
    if (u >= 1) FX.rings(g, tx, ty, t - 3.4, { count: 2, r0: 10, r1: 160, color: G, a: 0.7 }); lbl(g, 'JUÍZES 20:16', E.W * 0.5, E.H * 0.14, { color: G, a: fin(t, 0.3) }); lbl(g, 'UM FIO DE CABELO', tx, ty + 280, { size: 30, a: fin(t, 1) }); }
  if (m === 'speed') { const hx = E.W * 0.28, hy = E.H * 0.45, u = prog(t, 2.6, d); const a = t * (6 + t * 3); if (u <= 0) { const px = hx + Math.cos(a) * 180, py = hy + Math.sin(a) * 70; seg(g, [[hx, hy], [px, py]], 4, G); circle(g, px, py, 14, G); } else { const x = lerp(hx + 180, E.W + 100, u); circle(g, x, hy, 14, G); FX.speedLines(g, t, { cx: x - 200, cy: hy, count: 30, a: 0.4, inner: 40 }); }
    const v = Math.round(lerp(0, 100, ease.in(prog(t, 0.2, 2.6)))); UI.readout(g, { value: `${v}${v >= 100 ? '+' : ''} km/h`, x: E.W * 0.6, y: E.H * 0.72, size: V(100, 96) }); }
  if (m === 'look1' || m === 'look2') {
    const gx = E.W * 0.75; lf(g, gx, gy, m === 'look1' ? 2.4 : 0.9, 'crossArms', -1, A); helmet(g, gx - 6 * (m === 'look1' ? 2.4 : 0.9), gy - 208 * (m === 'look1' ? 2.4 : 0.9), 22 * (m === 'look1' ? 2.4 : 0.9), -1, null);
    if (m === 'look1') { for (let i = 0; i < 4; i++) { const x = E.W * 0.12 + i * 120; lf(g, x, gy, 0.9, 'handsOnHead', 1, B); g.setLineDash([10, 10]); seg(g, [[x + 20, gy - 200], [lerp(x + 20, gx - 60, fin(t, 0.3 + i * 0.15, 1.2 + i * 0.15)), lerp(gy - 200, gy - 420, fin(t, 0.3 + i * 0.15, 1.2 + i * 0.15))]], 3, alpha(B, 0.7)); g.setLineDash([]); } lbl(g, 'O TAMANHO DE GOLIAS', E.W * 0.45, E.H * 0.14, { color: A, a: fin(t, 0.4) }); }
    else { const x = E.W * 0.3; lf(g, x, gy, 1.1, 'pointUp', 1, B); const a = fin(t, 0.3, 1.4); glow(g, E.W * 0.42, -200, 900 * a, '#fff3dc', 0.35); FX.godRays(g, E.W * 0.42, -300, { angle: Math.PI / 2, spread: 1.4, len: 1600, color: '#fff3dc', a: 0.12 * a, t }); g.setLineDash([10, 10]); seg(g, [[x + 20, gy - 230], [lerp(x + 20, E.W * 0.42, a), lerp(gy - 230, 40, a)]], 3, G); g.setLineDash([]); lbl(g, 'O TAMANHO DE DEUS', E.W * 0.55, E.H * 0.2, { color: G, a: fin(t, 0.8) }); }
  }
  if (m === 'fieldToValley') { const u = ease.inOut(prog(t, 0.3, d - 0.3)); rr(g, E.W * 0.08, E.H * 0.3, 520, 360, 20); g.strokeStyle = B; g.lineWidth = 4; g.stroke(); rr(g, E.W * 0.65, E.H * 0.3, 520, 360, 20); g.stroke();
    lion(g, E.W * 0.17, E.H * 0.6, 0.7, 1, t, { rimC: B }); bear(g, E.W * 0.3, E.H * 0.6, 0.55, -1, t, { rimC: B }); lbl(g, 'O CAMPO', E.W * 0.08 + 260, E.H * 0.25, { size: 34 });
    lf(g, E.W * 0.72, E.H * 0.6, 0.6, 'stand', 1, B); lf(g, E.W * 0.86, E.H * 0.6, 1.1, 'stand', -1, A); lbl(g, 'O VALE', E.W * 0.65 + 260, E.H * 0.25, { size: 34, color: G });
    g.strokeStyle = G; g.lineWidth = 8; g.beginPath(); g.moveTo(E.W * 0.38, E.H * 0.48); g.lineTo(lerp(E.W * 0.38, E.W * 0.62, u), E.H * 0.48); g.stroke(); if (u > 0.95) poly(g, [[E.W * 0.64, E.H * 0.48], [E.W * 0.61, E.H * 0.45], [E.W * 0.61, E.H * 0.51]], G); lbl(g, 'TREINO', E.W / 2, E.H * 0.42, { color: G, a: fin(t, 0.6), size: 32 }); }
  g.restore();
};

// ======================= GLOWING LINES =======================
K.line = (g, t, info, p) => {
  const d = info.dur, M = mood(p.icon === 'sunrise' ? 'golden' : 'dusk');
  if (p.icon === 'david' || p.icon === 'sunrise') {
    const cam = camAt(1.4 + 0.05 * t, E.W / 2, GYv(), 0.9);
    valley(g, t, cam, { israel: false, phil: false, sunPos: [E.W / 2 + 40, GYv() - 260 + (p.icon === 'sunrise' ? -60 * t / d : 0)] });
    layer(g, cam, 1, (g) => actor(g, { who: 'david', x: E.W / 2 - 160, y: GYv() + 12, s: 0.95, facing: 1, pose: breathe(P('stand'), t), expr: 'determined', rim: { color: M.rim, dir: [1, -0.3], w: 6 }, gear: { sling: true, bag: true }, t }));
    veil(g, '#0a0604', 0.35); glow(g, E.W / 2 + 40, GYv() - 260, 700, M.key, 0.25);
  } else { backdrop(g, [shade(M.sky[0], -0.4), shade(M.sky[1], -0.5), shade(M.dark, -0.2)]); FX.stars(g, t, { count: 80 }); FX.dust(g, t, { count: 40, color: M.key, a: 0.35 }); }
  const cy = E.H * (p.icon === 'none' ? 0.5 : 0.62), a = clamp(Math.min(t / 0.4, (d - t) / 0.4));
  if (p.icon === 'key') { g.save(); g.globalAlpha *= a; keyIcon(g, E.W / 2, E.H * 0.36, 90 * pop(t, 0.1), ui().gold, 12); glow(g, E.W / 2, E.H * 0.36, 260, ui().gold, 0.25); g.restore(); }
  if (p.icon === 'eye') { g.save(); g.globalAlpha *= a; eyeIcon(g, E.W / 2, E.H * 0.36, 130 * pop(t, 0.1), ui().cream, 10); g.restore(); }
  if (p.icon === 'heart') { g.save(); g.globalAlpha *= a; const b = 1 + 0.1 * Math.max(0, Math.sin(t * 7)); glow(g, E.W / 2, E.H * 0.36, 300, ui().accent, 0.4); heartShape(g, E.W / 2, E.H * 0.36, 80 * b * pop(t, 0.05), ui().accent); g.restore(); }
  const sz = p.icon === 'david' || p.icon === 'sunrise' ? V(92, 80) : V(80, 74);
  UI.bigLine(g, t, { str: p.str, dur: d, y: p.icon === 'david' || p.icon === 'sunrise' ? E.H * 0.24 : cy, size: sz, color: p.icon === 'heart' ? ui().accent : ui().gold });
};

// ======================= LESSONS =======================
K.lesson = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode;
  if (m === 'giant') { blurLayer(g, 4, (g) => valley(g, t, camAt(1.5, E.W / 2 + 250, GYv(), 0.9), { israel: false, phil: false })); veil(g, '#0a0604', 0.3);
    const cam = camAt(1.5, E.W / 2 + 250, GYv(), 0.9); layer(g, cam, 1, (g) => actor(g, { who: 'goliath', x: E.W / 2 + 350, y: GYv() + 12, s: 0.95, facing: -1, pose: breathe(P('crossArms'), t), expr: 'smirk', rim: { color: mood('dusk').rim, dir: [0.6, -0.8], w: 5 }, t })); lbl(g, 'O GIGANTE NÃO MUDOU', E.W * 0.3, E.H * 0.3, { color: ui().cream, a: fin(t, 0.4), size: V(46, 46) }); }
  if (m === 'hidden') { pasture(g, t, camAt(1.1 + 0.05 * k, E.W / 2, GYv(), 0.86), { mood: 'night' }); const cam = camAt(1.1 + 0.05 * k, E.W / 2, GYv(), 0.86); layer(g, cam, 1, (g) => { actor(g, { who: 'david', x: E.W / 2 - 200, y: GYv() + 30, s: 1, facing: 1, pose: posesAt(t % 1.6, [[0, { ...P('stand'), eF: [20, -200], hF: [26, -236] }], [1.0, { ...P('point'), eF: [36, -176], hF: [74, -170] }]]), expr: 'determined', rim: { color: mood('night').rim, dir: [0.6, -0.8] }, gear: { sling: true, whirl: 1.6 }, t }); for (let i = 0; i < 3; i++) sheep(g, E.W / 2 + 200 + i * 170, GYv() + 30, 1, -1, t, i, { rim: mood('night').rim }); }); lbl(g, 'NO LUGAR ESCONDIDO', E.W / 2, E.H * 0.16, { color: ui().gold, a: fin(t, 0.4) }); }
  if (m === 'armor') { const cam = camAt(1.4 + 0.06 * k, E.W / 2, GYv(), 0.8); tentIn(g, t, cam); layer(g, cam, 1, (g) => { const y = GYv() + 30; helmet(g, E.W / 2 - 120, y - 40, 44, 1, null, { crest: false }); rr(g, E.W / 2 - 20, y - 36, 120, 40, 10); g.fillStyle = BRONZE; g.fill(); sword(g, E.W / 2 + 140, y - 6, -0.05, 200, 10); FX.pool(g, E.W / 2, y, 300, 30, '#ffd59a', 0.3); });
    if (p.n) lbl(g, 'NÃO É A SUA ARMADURA', E.W / 2, E.H * 0.18, { color: ui().cream, a: fin(t, 0.4) }); }
  if (m === 'people') { const cam = camAt(1.15, E.W / 2 - 300, GYv(), 0.86); valley(g, t, cam, { israel: 'cheer', phil: false }); lbl(g, 'UM POVO INTEIRO', E.W / 2, E.H * 0.16, { color: ui().gold, a: fin(t, 0.4) }); }
  if (p.n) { const a = pop(t, 0.1); g.save(); g.translate(V(150, 140), V(150, 200)); g.scale(a, a); circle(g, 0, 0, 70, alpha(ui().card, 0.9)); ring(g, 0, 0, 70, 4, ui().gold); text(g, String(p.n), 0, 4, { size: 80, color: ui().gold, glow: 20, glowColor: alpha(ui().gold, 0.6) }); g.restore(); }
  FX.dust(g, t, { count: 30, color: '#ffe2bd', a: 0.3 });
};

// ======================= MODERN (the viewer's giant) =======================
function shadowGiant(g, x, y, s, t, o = {}) { const ink = '#02030a'; g.save(); g.globalAlpha *= o.a ?? 0.85; drawFigure(g, { x, y, s, facing: -1, pose: o.pose || breathe(P('crossArms'), t), outfit: { top: 'none' }, rim: false, ink, inkFar: ink, expr: 'angry', shadow: false }); helmet(g, x - 3 * s, y - 208 * s, 26 * s, -1, null, { mono: ink }); g.restore(); }
K.modern = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode;
  const dawn = m === 'dawn' ? ease.inOut(prog(t, 0.3, d)) : 0;
  const cam = m === 'home' ? camAt(lerp(1.4, 1.48, k), E.W / 2, GYv(), 0.9) : camAt(lerp(1.0, 1.05, k), E.W / 2 + lerp(-20, 20, k), GYv(), 0.95);
  const { GY, M } = street(g, t, cam, { dawn });
  const rim = { color: M.practical, dir: [1, -0.4], w: 4.5 }, y = GY + 30;
  layer(g, cam, 1, (g) => {
    if (m === 'home') { const top = GY - 460; g.fillStyle = shade(M.wall, -0.5); g.fillRect(E.W / 2 + 120, top, 360, GY - top + 30); g.fillStyle = M.practical; g.fillRect(E.W / 2 + 160, top + 40, 280, GY - top - 10); glow(g, E.W / 2 + 300, GY - 200, 400, M.practical, 0.35);
      drawFigure(g, { x: E.W / 2 + 300, y, s: 1.1, facing: -1, pose: breathe(posesAt(t, [[0, 'crossArms'], [1.6, 'point']]), t), outfit: { top: 'none' }, rim: false, expr: 'angry' });
      actor(g, { who: 'you', x: E.W / 2 - 260, y, s: 1, facing: 1, pose: breathe(P('sad'), t), expr: 'sad', rim, t }); bag2(g, E.W / 2 - 290, y - 150); }
    const sg = m === 'dawn' ? lerp(3.1, 1.2, dawn) : m === 'small' ? 3.4 : 3.1, gx = E.W / 2 + 420;
    if (['shadow', 'giant', 'words', 'shout', 'small', 'approach', 'dawn', 'others'].includes(m)) {
      shadowGiant(g, gx, y, sg, t, { a: m === 'dawn' ? lerp(0.85, 0.25, dawn) : 0.85, pose: m === 'shout' ? posesAt(t, [[0, 'crossArms'], [0.3, 'point']]) : undefined });
      if (m === 'shout') { FX.rings(g, gx - 60, y - 208 * sg, t, { count: 4, r0: 80, r1: 420, color: '#8a90c0', a: 0.4 }); const [sx] = shake(t, 4); g.translate(sx, 0); UI.badge(g, { str: '40 DIAS', a: fin(t, 0.4) }); }
      const yx = m === 'approach' || m === 'dawn' ? lerp(E.W / 2 - 520, E.W / 2 - 160, k) : m === 'others' ? E.W / 2 - 160 : E.W / 2 - 300;
      const walking = m === 'approach' || m === 'dawn';
      actor(g, { who: 'you', x: yx, y, s: 1, facing: 1, pose: walking ? walkPose(t * 5.6) : breathe(P(m === 'small' ? 'relaxed' : 'stand'), t), expr: m === 'small' ? 'smile' : m === 'shout' ? 'scared' : walking ? 'determined' : 'worried', look: [0.4, -0.8], rim: { color: dawn ? '#ffd59a' : rim.color, dir: [1, -0.4], w: 4.5 }, t });
      if (m === 'others') for (let i = 0; i < 4; i++) { const st = prog(t, 0.6 + i * 0.6, 1.0 + i * 0.6); drawFigure(g, { x: E.W / 2 - 480 - i * 170, y, s: 0.92, facing: 1, pose: st > 0 ? posesAt(st, [[0, 'sit'], [0.5, 'stand']]) : P('sit'), outfit: { top: ['tshirt', 'hoodie', 'dress', 'tshirt'][i], color: ['#3a6ea5', '#f29ac0', '#3fb950', '#f2c21a'][i] }, rim: { color: rim.color, dir: [1, -0.4] }, expr: st > 0.5 ? 'determined' : 'worried' }); }
      if (m === 'words') { const ws = ['MEDO', 'DOENÇA', 'DÍVIDA', 'ANSIEDADE', 'VÍCIO']; ws.forEach((w, i) => { const wt = wordTime(w.slice(0, 4), info.globalT - 0.5); const at = wt != null ? wt - info.shot.start : i * 0.7; const a = ease.outBack(prog(t, at - 0.05, at + 0.3)); if (a <= 0) return; text(g, w, gx - 40 + (i % 2 ? 140 : -160), y - 200 * sg + 40 + i * 92, { size: 64 * a, color: ui().accent, glow: 20, glowColor: alpha(ui().accent, 0.6), font: FONTS.title, spacing: 2 }); }); }
    }
  });
  if (m === 'dawn') { glow(g, E.W * 0.75, E.H * 0.4, 900, '#ffd59a', 0.35 * dawn); FX.godRays(g, E.W * 0.85, E.H * 0.3, { angle: Math.PI * 0.85, spread: 0.9, color: '#ffd59a', a: 0.12 * dawn, t }); }
  FX.dust(g, t, { count: 30, color: M.practical, a: 0.3 });
};
function bag2(g, x, y) { rr(g, x - 40, y, 70, 90, 16); g.fillStyle = '#3a3a48'; g.fill(); }
