// _kindsA.js — character shot kinds: valley, goliath, face, camp, pasture, house, tent, brook, freeze, title, end.
import { E, V, S, mood, layer, blurLayer, veil, ease, prog, key, clamp, lerp, shake, talkAmount, seg, circle, ring, rr, poly, glow, alpha, shade, mix, linGrad, radGrad, text, FONTS, rng } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe, walkPose, bigFace } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { valley, camp, pasture, house, tentIn, street, brook, hillY, GYv, army } from './_sets.js';
import { actor, face, sheep, lion, bear, vulture, stone, sling, shield, sword, spear, helmet, crown, oilHorn, tent, BRONZE, GOLD, handPos } from './_props.js';
import { DAVID, GOLIAS, SAUL, SAMUEL, JESSE, ELIABE, YOU, CAST } from './cast.js';

export const K = {};
const CX = () => E.W / 2;
// camera that keeps the ground line at a given screen height while zooming on focusX
export const camAt = (z, fx, GY = GYv(), gs = 0.9, extra = {}) => ({ z, x: fx - E.W / 2, y: GY - E.H / 2 - (E.H * gs - E.H / 2) / z, ...extra });
const tk = (info, p) => (p.talk ? talkAmount(info.globalT, info.shot.start, info.shot.end) : 0);
const P = (n) => POSES[n];
const custom = {
  chest: { ...POSES.talk, eF: [20, -140], hF: [10, -160] },
  fist: { ...POSES.stand, eF: [24, -206], hF: [30, -250], eB: [-10, -140], hB: [-16, -104] },
  sling: { ...POSES.stand, eF: [20, -200], hF: [26, -236], eB: [24, -150], hB: [40, -160] },
  throw: { ...POSES.point, eF: [36, -176], hF: [74, -170], eB: [-22, -150], hB: [-40, -130], kF: [18, -50], fF: [30, 0] },
  pour: { ...POSES.stand, eF: [26, -196], hF: [52, -218], eB: [20, -150], hB: [40, -150] },
  swordUp: { ...POSES.cheer, eF: [10, -214], hF: [6, -258], eB: [-6, -214], hB: [0, -258] },
  sitRock: POSES.sit,
};

// ======================= VALLEY =======================
K.valley = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode || '';
  const pan = p.pan || [0, 0], zz = p.z || [1.02, 1.08];
  let cam = { x: lerp(pan[0], pan[1], k), z: lerp(zz[0], zz[1], k), y: 0, r: p.roll ? 0.018 * Math.sin(t * 0.9) : 0 };
  let israel = 'idle', phil = 'idle', moodN = p.mood || 'dusk';
  if (m === 'march') { israel = false; phil = 'march'; }
  if (m === 'empty' || m === 'golden') { israel = false; phil = false; }
  if (m === 'rush') israel = 'charge';
  if (m === 'philFlee') { phil = 'flee'; israel = 'cheer'; }
  if (m === 'charge') { israel = 'charge'; phil = 'flee'; }
  if (['watch', 'weapons', 'davidUp', 'faceoff', 'approach'].includes(m)) { israel = 'idle'; phil = 'idle'; }
  if (p.focus === 'israel') cam = { x: -1000 + lerp(-50, 50, k), y: -40, z: lerp(1.45, 1.55, k) };
  if (p.focus === 'phil') cam = { x: 1000 + lerp(-50, 50, k), y: -40, z: lerp(1.45, 1.55, k) };
  if (m === 'march') cam = { x: 1000 + lerp(-80, 0, k), y: -60, z: lerp(2.0, 2.1, k) };
  const near = ['faceoff', 'weapons', 'davidUp', 'davidRun', 'sword'].includes(m);
  if (near) cam = camAt(lerp(1.75, 1.85, k), CX() + (m === 'davidRun' ? -150 + t * 60 : 0), GYv(), 0.9, { r: 0 });
  if (m === 'closing') cam = camAt(lerp(1.25, 1.3, k), CX(), GYv(), 0.86);
  if (m === 'approach' || m === 'watch') cam = camAt(lerp(1.08, 1.15, k), CX(), GYv(), 0.82);
  if (m === 'sword') cam = camAt(lerp(1.9, 2.05, k), CX() + 120, GYv(), 0.86);
  const { GY, M } = valley(g, t, cam, { mood: moodN, israel, phil, storm: m === 'march', sunPos: m === 'sword' ? [CX() + 140, GYv() - 200] : null });
  const rim = { color: M.rim, dir: [0.7, -0.6], w: 4.5 };
  const y = GY + 12, s = near ? 0.95 : m === 'closing' ? 0.75 : 0.62;
  layer(g, cam, 1, (g) => {
    const dX = CX() - 220, gX = CX() + 250;
    if (m === 'approach') { const x = lerp(CX() - 620, CX() - 330, k); actor(g, { who: 'david', x, y, s, facing: 1, pose: walkPose(t * 6), rim, gear: { staff: true, bag: true }, t });
      actor(g, { who: 'goliath', x: CX() + 330, y, s, facing: -1, pose: breathe(P('stand'), t), rim, t, expr: 'smirk' }); }
    if (['faceoff', 'weapons', 'davidUp', 'watch'].includes(m)) {
      const dp = m === 'davidUp' ? posesAt(t, [[0, 'talk'], [0.7, 'pointUp']]) : m === 'weapons' ? posesAt(t, [[0, 'talk'], [1.4, 'explain']]) : P('stand');
      actor(g, { who: 'david', x: dX, y, s, facing: 1, pose: breathe(dp, t), expr: m === 'faceoff' ? 'determined' : 'determined', look: [0.4, -0.9], talk: tk(info, p), rim, gear: { sling: true, bag: true }, t });
      actor(g, { who: 'goliath', x: gX, y, s, facing: -1, pose: breathe(P(m === 'faceoff' ? 'crossArms' : 'stand'), t), expr: m === 'faceoff' ? 'smirk' : 'angry', look: [-0.3, 0.6], rim, t });
      if (m === 'weapons') { const hy = y - 240 * s * 1.75; [['ESPADA', 0.15], ['LANÇA', 0.45], ['ESCUDO', 0.75]].forEach(([str, at], i) => UI.callout(g, t, { at: [gX + [-30, 30, -60][i], hy + [180, -40, 120][i]], to: [gX + 210, hy - 40 + i * 70], str, start: at * d, color: S().ui.cream })); }
      if (m === 'davidUp') { g.save(); FX.godRays(g, dX, -400, { angle: Math.PI / 2, spread: 0.5, len: 1400, color: M.key, a: 0.12 * ease.inOut(prog(t, 0.6, 1.6)), t }); g.restore(); }
    }
    if (m === 'davidRun') { const x = dX - 120 + t * 260; actor(g, { who: 'david', x, y, s, facing: 1, pose: walkPose(t * 11, { run: true }), expr: 'determined', rim, gear: { sling: true }, t, trail: null }); FX.speedLines(g, t, { cx: x + 300, cy: y - 200, count: 40, a: 0.25 }); }
    if (m === 'closing') { const x = lerp(CX() - 520, CX() - 120, k); actor(g, { who: 'david', x, y, s, facing: 1, pose: walkPose(t * 11, { run: true }), expr: 'determined', rim, gear: { sling: true }, t });
      actor(g, { who: 'goliath', x: lerp(CX() + 420, CX() + 260, k), y, s, facing: -1, pose: walkPose(t * 4), expr: 'angry', rim, t }); }
    if (m === 'golden') actor(g, { who: 'david', x: CX() - 140, y, s: 0.7, facing: 1, pose: breathe(P('relaxed'), t), expr: 'smile', look: [0.5, -0.6], rim, gear: { staff: true, sling: true, bag: true }, t });
    if (m === 'sword') { const up = ease.out(prog(t, 0.3, 1.6));
      actor(g, { who: 'goliath', x: CX() + 330, y: y - 20, s, facing: -1, pose: P('lie'), rot: -Math.PI / 2, rim: false, t, gear: { spear: false, shield: false }, shadow: false });
      actor(g, { who: 'david', x: CX() + 40, y, s, facing: 1, pose: posesAt(t, [[0, 'stand'], [0.4, custom.swordUp]], 0.8), expr: 'determined', rim: { color: M.rim, dir: [0.9, -0.3], w: 5 }, gear: { sword: true, swordAng: lerp(0.4, -1.55, up), swordK: 1.3 }, t }); }
  });
  if (m === 'sword') veil(g, '#1a0a06', 0.18, 'multiply');
  FX.dust(g, t, { count: 30, color: M.key, a: 0.3 });
};

// ======================= GOLIATH (low angle) =======================
K.goliath = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode;
  const storm = m === 'curse', moodN = storm ? 'storm' : 'dusk';
  const timelapse = m === 'timelapse';
  const sunP = timelapse ? [lerp(-100, E.W + 100, t / d), E.H * 0.3 - Math.sin(Math.PI * t / d) * 200] : null;
  blurLayer(g, 10, (g) => valley(g, t, { z: 1.6, x: 380, y: -120 }, { mood: moodN, storm, israel: false, phil: m === 'emerge' ? 'idle' : 'idle', sunPos: sunP }));
  veil(g, '#0a0604', 0.25);
  if (timelapse) { veil(g, mix('#ffcf8f', '#4a2a6a', t / d), 0.2, 'soft-light'); }
  const M = mood(moodN), GY = E.H * 0.97, rim = { color: M.rim, dir: [0.6, -0.8], w: 5 };
  if (storm && t > 0.95 && t < 1.25) { FX.lightning(g, { x1: E.W * 0.25, y1: 0, x2: E.W * 0.32, y2: E.H * 0.45, seed: 4 }); veil(g, '#dfe6ff', 0.25 * (1 - prog(t, 0.95, 1.25)), 'lighter'); }
  let [sx, sy] = [0, 0];
  g.fillStyle = linGrad(g, 0, GY - 30, 0, E.H, [shade(M.floor, -0.1), shade(M.dark, -0.3)]); g.fillRect(0, GY - 20, E.W, E.H);
  let gx = E.W * 0.6, gy = E.H * 1.02, s = 1.75, pose = breathe(P('stand'), t), expr = 'angry', gear = {}, rot = 0, facing = -1, dy = 0;
  const talk = tk(info, p);
  if (m === 'reveal') { dy = lerp(560, 0, ease.out(prog(t, 0, d * 0.75))); expr = 'smirk'; }
  if (m === 'emerge' || m === 'advance') { const step = t * (m === 'advance' ? 4.2 : 3.6); gx = m === 'emerge' ? lerp(E.W + 260, E.W * 0.6, ease.out(prog(t, 0, d))) : lerp(E.W * 0.7, E.W * 0.45, k); pose = walkPose(step); const st = Math.abs(Math.sin(step / 2)); [sx, sy] = shake(t, 6 * (st < 0.12 ? 1 : 0.15), 4); }
  if (m === 'bearer') { gear = { shield: false, spearUp: lerp(1, 1.25, ease.out(prog(t, d * 0.6, d))) }; pose = posesAt(t, [[0, breathe(P('stand'), t)], [d * 0.62, custom.fist]]); }
  if (m === 'talkSelf') { pose = breathe(posesAt(t, [[0, 'talk'], [0.5, custom.chest]]), t); expr = 'smirk'; }
  if (m === 'talkPoint') { pose = breathe(posesAt(t, [[0, 'talk'], [0.4, 'point']]), t); s = 1.9; gx = E.W * 0.68; }
  if (m === 'rock') { gy = GY - 110; s = 1.45; pose = breathe(posesAt(t, [[0, 'stand'], [0.5, 'point'], [1.6, custom.fist]]), t); }
  if (timelapse) { pose = posesAt(t % 1.6, [[0, 'point'], [0.8, custom.fist]]); }
  if (m === 'otsDavid') { s = 2.6; gx = E.W * 0.12; }
  if (m === 'curse') { pose = breathe(custom.fist, t); expr = 'angry'; }
  if (m === 'vultures') { pose = breathe(posesAt(t, [[0, 'stand'], [0.4, 'point']]), t); }
  if (m === 'fall') { rot = -ease.in(prog(t, 0.2, 1.7)) * 1.55; pose = posesAt(t, [[0, 'stand'], [0.3, 'fall']]); expr = 'shocked'; gear = { spear: false, shield: false }; }
  if (m === 'fall' && t > 1.7) [sx, sy] = shake(t, 22 * (1 - prog(t, 1.7, 2.6)), 9);
  g.save(); g.translate(sx, sy + dy);
  if (m === 'rock') { poly(g, [[gx - 260, GY + 10], [gx - 200, gy - 10], [gx + 180, gy - 20], [gx + 280, GY + 10]], shade(M.dark, 0.05)); }
  if (m === 'bearer') { const bx = lerp(E.W * 0.2, E.W * 0.36, k); actor(g, { who: 'phil', x: bx, y: GY, s: 1.25, facing: -1, pose: walkPose(t * 5), rim, t }); shield(g, bx - 60, GY - 190, 120, M.rim); }
  const drawG = (g2) => actor(g2, { who: 'goliath', x: gx, y: gy, s, facing, pose, expr, talk, rim, gear, rot, t, look: m === 'otsDavid' ? [1, 0.7] : [-0.3, 0.2] });
  if (m === 'otsDavid') {
    const dx = E.W * 0.62; actor(g, { who: 'david', x: dx, y: GY - 120, s: 0.75, facing: -1, pose: breathe(P('stand'), t), expr: 'determined', look: [-0.2, -1], rim, gear: { sling: true, staff: true, bag: true }, t });
    UI.callout(g, t, { at: [dx - 6, GY - 120 - 200 * 0.75 * 0.88 - 10], to: [dx + 200, GY - 470], str: 'RUIVO', start: 0.6 });
    blurLayer(g, 12, drawG); veil(g, '#000', 0.12);
  } else drawG(g);
  g.restore();
  if (m === 'reveal') UI.dimension(g, t, { x1: gx + 300, y1: GY - 6, x2: gx + 300, y2: GY - 240 * s * 1.75 - 20, str: '≈ 2,9 m', start: d * 0.55 });
  if (m === 'fall' && t > 1.6) { const a = 1 - prog(t, 1.7, 3); for (let i = 0; i < 18; i++) { const px = gx - 520 + i * 40, r = 40 + (i % 5) * 24 + (t - 1.6) * 90; g.fillStyle = alpha(mix(M.floor, M.key, 0.3), 0.25 * a); g.beginPath(); g.arc(px, GY - 20 - (i % 3) * 30, r, 0, 7); g.fill(); } }
  if (m === 'vultures') for (let i = 0; i < 4; i++) { const a = t * 0.5 + i * 1.6; vulture(g, E.W * 0.3 + Math.cos(a) * 300, 160 + Math.sin(a) * 60 + i * 20, 0.8 - i * 0.1, t + i); }
  if (talk > 0 || timelapse || m === 'rock' || m === 'curse') { const hx = gx + (facing * 10) * s * 1.75, hy = gy - 210 * s * 1.75 + dy; FX.rings(g, hx - 80, hy, t, { count: 3, r0: 60, r1: 260, color: M.rim, a: 0.35 }); }
  FX.dust(g, t, { count: 30, color: M.key, a: 0.3 });
};

// ======================= FACE (giant close-up) =======================
const BG = {
  valley: (g, t) => valley(g, t, { z: 1.7, x: 120, y: -140 }, { israel: false, phil: false }),
  camp: (g, t) => camp(g, t, { z: 1.6, x: -200, y: -120 }),
  tent: (g, t) => tentIn(g, t, { z: 1.5, x: 200, y: -160 }),
  house: (g, t) => house(g, t, { z: 1.5, x: 140, y: -120 }, { mood: 'dusk' }),
  pasture: (g, t) => pasture(g, t, { z: 1.5, x: 200, y: -140 }),
  modern: (g, t) => street(g, t, { z: 1.5, x: 300, y: -160 }),
};
const BGM = { valley: 'dusk', camp: 'golden', tent: 'interiorWarm', house: 'dusk', pasture: 'golden', modern: 'night' };
K.face = (g, t, info, p) => {
  const d = info.dur, M = mood(BGM[p.bg] || 'dusk');
  blurLayer(g, 14, (g) => BG[p.bg || 'valley'](g, t)); veil(g, '#0a0608', 0.38);
  if (p.fade) veil(g, '#0a1030', 0.45 * ease.inOut(prog(t, 0.4, d)), 'multiply');
  const talk = tk(info, p); let [sx, sy] = p.shake ? [Math.sin(t * 9) * 14 * (1 - prog(t, 0, d)), 0] : [0, 0];
  if (p.roar) [sx, sy] = shake(t, 10, 6);
  if (p.hit && t > 0.15) [sx, sy] = shake(t, 26 * (1 - prog(t, 0.15, 1.2)), 10);
  const r = V(300, 330) * (1 + 0.05 * t / d) * (p.who === 'goliath' ? 1.05 : 1), cx = E.W / 2 + (p.who === 'goliath' ? V(160, 0) : V(-120, 0)), cy = E.H * V(0.62, 0.55);
  const side = p.who === 'goliath' ? 1 : -1;
  g.save(); g.translate(sx, sy);
  if (p.memories) { const items = [['lion', -1], ['bear', 1], ['sheep', -0.2]]; items.forEach(([w, sd], i) => { const a = clamp((t - i * 0.4) / 0.6) * 0.75, x = cx + sd * 520, y = cy - 260 + i * 120 + Math.sin(t + i) * 10; g.save(); g.globalAlpha *= a; ring(g, x, y, 110, 3, alpha(M.rim, 0.6)); if (w === 'lion') lion(g, x - 50, y + 40, 0.5, 1, t, { rimC: M.rim }); if (w === 'bear') bear(g, x - 50, y + 45, 0.45, 1, t, { rimC: M.rim }); if (w === 'sheep') sheep(g, x - 10, y + 40, 0.9, 1, t, 2, { rim: M.rim }); g.restore(); }); }
  face(g, p.who, cx, cy, r, { expr: p.hit && t > 0.15 ? 'shocked' : p.expr, talk: p.roar ? 0.9 : talk, look: p.look, rimColor: M.rim, rimSide: side, blink: (t % 3.3) > 3.2 && p.expr !== 'sleepy', helmet: p.helmet ? lerp(0, 1.6, ease.inOut(prog(t, 0, d))) : 0 });
  g.restore();
  if (talk > 0 || p.roar) FX.rings(g, cx, cy, t, { count: 3, r0: r * 1.1, r1: r * 1.7, color: M.rim, a: 0.35 });
  if (p.roar) FX.speedLines(g, t, { cx, cy, count: 50, a: 0.3, inner: r * 1.3 });
  if (p.hit && t > 0.15) { const a = 1 - prog(t, 0.15, 0.6); veil(g, '#ffffff', 0.7 * a, 'lighter'); FX.rings(g, cx, cy - r * 0.55, t - 0.15, { count: 3, r0: 20, r1: 520, speed: 1.6, color: '#fff3e0', a: 0.7 * (1 - prog(t, 0.15, 1.4)) }); stone(g, cx + 6, cy - r * 0.55, 22); }
  if (p.rays) { const a = ease.inOut(prog(t, p.rays, p.rays + 0.8)); FX.godRays(g, cx - 200, -200, { angle: Math.PI * 0.45, spread: 0.7, len: 1600, color: '#fff3dc', a: 0.16 * a, t }); }
  if (p.label) UI.callout(g, t, { at: [cx + r * 0.75, cy - r * 0.55], to: [cx + r * 1.35, cy - r * 0.95], str: p.label, start: 0.3, color: S().ui.gold, size: V(40, 44) });
  FX.dust(g, t, { count: 24, color: M.key, a: 0.3 });
};

// ======================= CAMP =======================
K.camp = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode || '';
  const wide = ['arrive', 'run', 'flee'].includes(m), zz = wide ? [1.15, 1.2] : p.z ? [p.z[0] + 0.4, p.z[1] + 0.4] : [1.55, 1.65];
  const fx = { saulLead: CX() - 120, saulListen: CX() - 100, eliabe: CX(), ots: CX(), eliabeCross: CX(), davidShrug: CX(), whisper: CX() - 40, davidAsks: CX() - 100 }[m] ?? CX();
  const cam = camAt(lerp(zz[0], zz[1], k), fx + lerp(-30, 30, k), GYv(), 0.88);
  const { GY, M } = camp(g, t, cam);
  const rim = { color: M.rim, dir: [-0.8, -0.5], w: 4.5 }, talk = tk(info, p), y = GY + 30, s = 1.0;
  const soldier = (x, o = {}) => actor(g, { who: 'soldier', x, y: o.y ?? y, s: o.s ?? s * 0.95, facing: o.facing ?? 1, pose: o.pose || breathe(P('stand'), t, 1, x), expr: o.expr || 'neutral', rim, gear: { spear: o.spear ?? true }, t, look: o.look });
  layer(g, cam, 1, (g) => {
    // background soldiers
    if (!['run', 'arrive'].includes(m)) for (let i = 0; i < 5; i++) { const x = CX() - 900 + i * 420 + (i % 2) * 60; if (m === 'flee') continue; actor(g, { who: 'soldier', x, y: GY - 40, s: 0.62, facing: i % 2 ? -1 : 1, pose: breathe(P(p.soldiers === 'scared' ? 'handsOnHead' : 'stand'), t, 1, i), rim, gear: { spear: true }, t, expr: p.soldiers === 'scared' ? 'scared' : 'neutral' }); }
    if (m === '' && p.soldiers === 'scared') { const back = 30 * k; [-360, -150, 80, 300].forEach((dx, i) => soldier(CX() + dx - back * (i % 2 ? 1 : 0.6), { facing: 1, pose: breathe(P(i % 2 ? 'handsOnHead' : 'crossArms'), t, 1, i), expr: i % 2 ? 'scared' : 'worried', look: [1, 0], spear: i % 2 === 0 })); }
    if (m === 'saulLead') { actor(g, { who: 'saul', x: CX() - 380, y, s: 1.08, facing: 1, pose: breathe(posesAt(t, [[0, 'stand'], [0.6, 'point']]), t), expr: 'determined', rim, t });
      [0, 200, 400, 600].forEach((dx, i) => soldier(CX() - 60 + dx, { facing: -1, pose: posesAt(t + i * 0.2, [[0, 'stand'], [1 + i * 0.2, 'cheer']]), expr: 'happy' })); }
    if (m === 'saulListen') { actor(g, { who: 'saul', x: CX() - 120, y, s: 1.08, facing: 1, pose: breathe(P('crossArms'), t), expr: 'worried', look: [1, -0.1], rim, t });
      [-500, -320, 200, 420].forEach((dx, i) => soldier(CX() + dx, { facing: 1, expr: 'worried', look: [1, 0] })); }
    if (m === 'brothers') { const xs = [CX() - 360, CX(), CX() + 360]; const who = ['eliabe', 'brother', 'brother'];
      xs.forEach((x, i) => actor(g, { who: who[i], x, y, s: 1, facing: 1, pose: breathe(P('stand'), t, 1, i), expr: 'neutral', rim, gear: { spear: true }, t }));
      ['ELIABE', 'ABINADABE', 'SAMÁ'].forEach((str, i) => UI.callout(g, t, { at: [xs[i] + 4, y - 260 * (i ? 1.02 : 1.12)], to: [xs[i] + 90, y - 380], str, start: 0.3 + i * 0.4, color: i ? S().ui.cream : S().ui.gold })); }
    if (m === 'arrive') { const x = lerp(CX() - 900, CX() - 200, ease.out(k)); actor(g, { who: 'david', x, y, s, facing: 1, pose: walkPose(t * 6), expr: 'smile', rim, gear: { sack: true, sling: true }, t });
      soldier(CX() + 350, { facing: -1 }); soldier(CX() + 600, { facing: -1, expr: 'surprised' }); }
    if (m === 'run') { const x = lerp(CX() - 900, CX() + 300, k); actor(g, { who: 'david', x, y, s, facing: 1, pose: walkPose(t * 11, { run: true }), expr: 'happy', rim, t });
      actor(g, { who: 'eliabe', x: CX() + 620, y, s, facing: -1, pose: breathe(P('stand'), t), expr: 'surprised', rim, gear: { spear: true }, t }); }
    if (m === 'flee') { actor(g, { who: 'david', x: CX() + 120, y, s, facing: 1, pose: breathe(P('stand'), t), expr: 'surprised', look: [1, -0.2], rim, gear: { sling: true }, t });
      [0, 1, 2, 3].forEach(i => { const x = CX() + 900 - (t * 520 + i * 260) % 1900; soldier(x, { facing: -1, pose: walkPose(t * 11 + i, { run: true }), expr: 'scared', y: y + (i % 2) * 30 }); }); }
    if (m === 'whisper') { soldier(CX() - 330, { facing: 1, pose: breathe({ ...P('talk'), head: [12, -204] }, t), expr: 'smirk' }); soldier(CX() - 150, { facing: -1, pose: breathe({ ...P('stand'), head: [10, -204] }, t), expr: 'surprised' });
      actor(g, { who: 'david', x: CX() + 260, y, s, facing: -1, pose: breathe(P('think'), t), expr: 'thinking', rim, gear: { sling: true }, t }); UI.bubble(g, CX() - 240, y - 330, { w: 110, h: 60 }); }
    if (m === 'davidAsks') { actor(g, { who: 'david', x: CX() - 140, y, s, facing: 1, pose: breathe(posesAt(t, [[0, 'talk'], [1.2, 'point']]), t), expr: 'determined', talk, rim, gear: { sling: true }, t });
      soldier(CX() - 560, { facing: 1, expr: 'surprised' }); soldier(CX() + 380, { facing: -1, expr: 'worried' }); }
    if (['eliabe', 'ots', 'eliabeCross', 'davidShrug'].includes(m)) {
      const eT = m === 'davidShrug' ? 0 : talk, dT = m === 'davidShrug' ? talk : 0;
      const eP = m === 'eliabe' ? posesAt(t, [[0, 'talk'], [0.3, 'point']]) : m === 'eliabeCross' || m === 'davidShrug' ? P('crossArms') : P('talk');
      const dP = m === 'davidShrug' ? posesAt(t, [[0, 'stand'], [0.5, 'shrug']]) : P('stand');
      const drawE = (g2) => actor(g2, { who: 'eliabe', x: m === 'ots' ? CX() - 600 : CX() - 260, y: m === 'ots' ? y + 160 : y, s: m === 'ots' ? 1.9 : s, facing: 1, pose: breathe(eP, t), expr: 'angry', talk: eT, rim, gear: { spear: true }, t });
      if (m !== 'ots') drawE(g);
      actor(g, { who: 'david', x: CX() + (m === 'ots' ? 260 : 240), y, s, facing: -1, pose: breathe(dP, t, 1, 2), expr: m === 'davidShrug' ? 'confused' : 'sad', talk: dT, rim, gear: { sling: true }, t });
      if (m === 'ots') { blurLayer(g, 12, drawE, cam, 1); }
    }
  });
  if (p.counter) { const n = Math.round(lerp(p.counter[0], p.counter[1], ease.inOut(prog(t, 0.3, d - 0.3)))); UI.badge(g, { str: `DIA ${n}`, a: ease.out(prog(t, 0.2, 0.5)) }); }
  FX.dust(g, t, { count: 40, color: M.key, a: 0.3 });
};

// ======================= PASTURE =======================
K.pasture = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode;
  const night = ['lion', 'rescue', 'bear', 'night'].includes(m), moodN = night ? 'night' : ['ridgeWalk', 'alone', 'few', 'noAudience'].includes(m) ? 'dusk' : 'golden';
  const pz = { shepherd: [1.4, 1.5, CX() - 220], alone: [1.5, 1.6, CX() - 60], night: [1.45, 1.55, CX() - 60], bear: [1.3, 1.35, CX()], rescue: [1.25, 1.3, CX()], lion: [1.2, 1.25, CX() + 100], practice: [1.15, 1.2, CX()] }[m] || [1.05, 1.12, CX()];
  let cam = camAt(lerp(pz[0], pz[1], k), pz[2] + lerp(-40, 40, k), GYv(), 0.88);
  if (m === 'far') cam = { z: lerp(0.95, 1.0, k), x: 0, y: 0 };
  if (m === 'ridgeWalk') cam = { z: 1.04, x: lerp(-60, 60, k), y: 60 };
  let sunPos = null; if (m === 'montage') { const a = (t / d) * Math.PI * 2 * 2.5; sunPos = [CX() + Math.cos(a) * 700, GYv() - 200 - Math.abs(Math.sin(a)) * 450]; }
  const { GY, M } = pasture(g, t, cam, { mood: moodN, sunPos });
  const rim = { color: M.rim, dir: night ? [0.6, -0.8] : [0.8, -0.5], w: 4.5 }, y = GY + 30, s = 1.0;
  layer(g, cam, 1, (g) => {
    const flock = (n, x0, sp = 160, sc = 1, seed = 1, o = {}) => { for (let i = 0; i < n; i++) { const x = x0 + i * sp + (i % 2) * 40 + (o.run ? -t * 300 : 0); sheep(g, x, y + (i % 3) * 26 - 10, sc * (0.9 + (i % 3) * 0.06), i % 2 ? -1 : 1, t, seed + i, { rim: M.rim, graze: o.run ? 0 : undefined }); } };
    if (m === 'ridgeWalk') { const x = lerp(CX() - 600, CX() + 300, k); flock(3, x - 700, 150, 0.85); actor(g, { who: 'david', x, y, s, facing: 1, pose: walkPose(t * 6), rim: { color: M.rim, dir: [0.9, -0.4], w: 5 }, gear: { staff: true, sling: true }, t }); }
    if (m === 'shepherd') { flock(3, CX() - 820, 170); flock(3, CX() + 260, 180, 1, 7); actor(g, { who: 'david', x: CX() - 180, y, s: 1.05, facing: 1, pose: breathe(P('relaxed'), t), expr: 'smile', rim, gear: { staff: true, bag: true }, t }); }
    if (m === 'far') { for (let i = 0; i < 9; i++) sheep(g, CX() + 260 + (i % 5) * 70, GY + 10 + Math.floor(i / 5) * 24, 0.32, i % 2 ? 1 : -1, t, i, { rim: M.rim }); actor(g, { who: 'david', x: CX() + 200, y: GY + 8, s: 0.36, facing: 1, pose: breathe(P('relaxed'), t), rim, gear: { staff: true }, t }); }
    if (m === 'alone') { poly(g, [[CX() - 160, y + 4], [CX() - 120, y - 70], [CX() + 30, y - 80], [CX() + 70, y + 4]], shade(M.dark, 0.1)); actor(g, { who: 'david', x: CX() - 60, y: y - 74, s, facing: 1, pose: breathe(P('sit'), t), expr: 'sad', rim, t, shadow: false }); flock(3, CX() + 300, 180); }
    if (m === 'few') flock(3, CX() - 300, 260, 1, 4);
    if (m === 'lion') { flock(3, CX() - 900, 160, 1, 2, { run: true }); const lx = lerp(CX() + 700, CX() + 250, ease.out(prog(t, 0, 1.4))); lion(g, lx, y, 1.2, -1, t, { rimC: M.rim, lamb: t > 1.4, leap: t < 1.4 ? Math.sin(t * 4) * 0.3 : 0 }); }
    if (m === 'rescue') { const dx = lerp(CX() - 900, CX() - 120, ease.out(prog(t, 0, 1.6))); const hit = t > 1.6;
      lion(g, hit ? lerp(CX() + 220, CX() + 900, ease.in(prog(t, 1.7, d))) : CX() + 220, y, 1.2, hit ? 1 : -1, t, { rimC: M.rim, lamb: !hit, leap: hit ? 0.4 : 0 });
      if (hit) sheep(g, CX() + 120, y, 0.6, -1, t, 2, { lamb: true, graze: 0, rim: M.rim });
      actor(g, { who: 'david', x: dx, y, s, facing: 1, pose: t < 1.6 ? walkPose(t * 11, { run: true }) : posesAt(t - 1.6, [[0, 'kick'], [0.4, 'ready']]), expr: 'determined', rim, gear: { staff: true }, t });
      if (hit && t < 2.2) FX.rings(g, CX() + 160, y - 120, t - 1.6, { count: 3, r0: 20, r1: 240, color: '#fff3e0', a: 0.7 }); }
    if (m === 'bear') { bear(g, CX() + 260, y, 1.3, -1, t, { rimC: M.rim, rear: ease.out(prog(t, 0.3, 1.0)) * 0.6 }); actor(g, { who: 'david', x: CX() - 280, y, s, facing: 1, pose: breathe(P('ready'), t), expr: 'determined', rim, gear: { staff: true }, t }); }
    if (m === 'practice' || m === 'montage' || m === 'seen') {
      const dx = m === 'seen' ? CX() - 80 : CX() - 380, tx = CX() + 520, ty = y - 210, cyc = m === 'montage' ? (t % 1.4) : t, thr = m === 'montage' ? 0.8 : 1.2;
      seg(g, [[tx, y], [tx, ty + 30]], 10, shade(M.dark, -0.1)); circle(g, tx, ty, 34, '#c8a46a'); ring(g, tx, ty, 22, 5, '#8a5a2a');
      const thrown = cyc > thr; actor(g, { who: 'david', x: dx, y, s: m === 'seen' ? 0.7 : s, facing: 1, pose: thrown ? custom.throw : custom.sling, expr: 'determined', rim, gear: { sling: true, whirl: thrown ? 0 : 1.8, stone: !thrown, bag: true }, t });
      if (thrown) { const u = clamp((cyc - thr) / 0.35); if (u < 1) stone(g, lerp(dx + 80, tx, u), lerp(y - 230, ty, u) - Math.sin(u * Math.PI) * 60, 9); else { FX.rings(g, tx, ty, cyc - thr - 0.35, { count: 2, r0: 20, r1: 140, color: '#fff3e0', a: 0.6 }); FX.sparkle(g, tx, ty, 40, '#fff3dc', 1 - clamp((cyc - thr - 0.35) / 0.5)); } }
      if (m === 'montage') UI.badge(g, { str: `DIA ${Math.round(lerp(1, 365, t / d))}`, a: 1 });
      if (m === 'seen') FX.godRays(g, dx, -300, { angle: Math.PI / 2, spread: 0.45, len: 1500, color: '#fff3dc', a: 0.14 * ease.inOut(prog(t, 0.6, 1.8)), t });
      flock(2, CX() - 900, 170);
    }
    if (m === 'night') { glow(g, CX() + 60, y - 30, 220, M.practical, 0.5); for (let i = 0; i < 5; i++) seg(g, [[CX() + 40 + i * 10, y], [CX() + 60, y - 50 - Math.sin(t * 9 + i) * 12]], 7, alpha(i % 2 ? '#ffb04a' : '#ffe08a', 0.8));
      actor(g, { who: 'david', x: CX() - 140, y, s, facing: 1, pose: breathe(P('sit'), t), expr: 'neutral', rim: { color: M.practical, dir: [1, -0.2], w: 4.5 }, gear: { sling: true }, t, shadow: false }); flock(3, CX() + 300, 170, 1, 5); }
    if (m === 'noAudience') { g.save(); g.globalAlpha *= 0.45; lion(g, CX() - 300, y, 1, 1, t, { rimC: M.rim }); bear(g, CX() + 360, y, 1.1, -1, t, { rimC: M.rim }); g.restore(); }
  });
  if (['lion', 'rescue', 'bear'].includes(m)) { veil(g, '#203060', 0.22, 'soft-light'); UI.badge(g, { str: 'MEMÓRIA', a: 0.7, size: V(30, 34) }); }
  FX.dust(g, t, { count: 30, color: night ? '#cfd9ff' : M.key, a: 0.3 });
};

// ======================= HOUSE (Jesse, Samuel) =======================
K.house = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode;
  const night = m === 'secret';
  const hz = ['arrive', 'lineup'].includes(m) ? [1.12, 1.18] : [1.45, 1.55], hfx = { secret: CX() - 250, anoint: CX() - 250, eldest: CX() + 60, jesse: CX() - 20 }[m] ?? CX();
  const cam = camAt(lerp(hz[0], hz[1], k), hfx + lerp(-20, 30, k), GYv(), 0.9);
  const { GY, M } = house(g, t, cam, { mood: night ? 'night' : 'dusk' });
  const rim = { color: M.practical, dir: [0.9, -0.4], w: 4.5 }, y = GY + 30, s = 1.0, talk = tk(info, p);
  layer(g, cam, 1, (g) => {
    if (m === 'secret' || m === 'anoint') {
      const pourA = ease.inOut(prog(t, 0.3, 1.2)); const sx = CX() - 380, dX = CX() - 120;
      actor(g, { who: 'samuel', x: sx, y, s, facing: 1, pose: posesAt(t, [[0, 'stand'], [0.3, custom.pour]], 0.6), expr: 'smile', rim, t });
      actor(g, { who: 'david', x: dX, y, s, facing: -1, pose: breathe(P('kneel'), t), expr: m === 'anoint' ? 'awe' : 'sleepy', rim, t, look: [0, -1] });
      const hp = handPos({ x: sx, y, s, facing: 1, pose: custom.pour }); oilHorn(g, hp[0], hp[1] - 10, lerp(0, 0.9, pourA), 1.1);
      if (pourA > 0.6) for (let i = 0; i < 6; i++) { const yy = hp[1] + 30 + ((t * 160 + i * 22) % 110); circle(g, hp[0] + 70, yy, 4, alpha('#ffe7a0', 0.9)); }
      if (m === 'anoint') { FX.godRays(g, dX, -300, { angle: Math.PI / 2, spread: 0.5, len: 1500, color: '#fff3dc', a: 0.16 * ease.inOut(prog(t, 0.3, 1.2)), t }); for (let i = 0; i < 8; i++) FX.sparkle(g, dX - 80 + (i * 53) % 180, y - 300 + (i * 71) % 220 - t * 20, 14, '#fff3dc', 0.6 * Math.abs(Math.sin(t * 3 + i))); }
    }
    if (m === 'arrive') { actor(g, { who: 'samuel', x: lerp(CX() - 900, CX() - 260, ease.out(k)), y, s, facing: 1, pose: walkPose(t * 5.6), expr: 'neutral', rim, t });
      actor(g, { who: 'jesse', x: CX() + 260, y, s, facing: -1, pose: posesAt(t, [[0, 'stand'], [d * 0.6, 'wave']]), expr: 'surprised', rim, t }); }
    if (m === 'eldest') { actor(g, { who: 'samuel', x: CX() - 260, y, s, facing: 1, pose: breathe(P('stand'), t), expr: 'smile', look: [0.5, -0.9], rim, t });
      actor(g, { who: 'eliabe', x: CX() + 120, y, s: 1.08, facing: -1, pose: breathe(P('crossArms'), t), expr: 'smirk', rim, t });
      actor(g, { who: 'jesse', x: CX() + 420, y, s, facing: -1, pose: breathe(P('stand'), t), expr: 'happy', rim, t }); }
    if (m === 'lineup') { actor(g, { who: 'samuel', x: CX() - 420, y, s, facing: 1, pose: breathe(P('think'), t), expr: 'thinking', rim, t });
      for (let i = 0; i < 6; i++) { const x = CX() + 700 - (t * 330 - i * 260); if (x < CX() - 340 || x > E.W + 200) continue; actor(g, { who: i === 0 ? 'eliabe' : 'brother', x, y, s: 1 - i * 0.03, facing: -1, pose: walkPose(t * 5.6 + i), expr: 'neutral', rim, t }); } }
    if (m === 'jesse') { actor(g, { who: 'jesse', x: CX() + 160, y, s, facing: -1, pose: breathe(posesAt(t, [[0, 'talk'], [0.8, 'explain']]), t), expr: 'smile', talk, rim, t });
      actor(g, { who: 'david', x: CX() - 200, y, s, facing: 1, pose: breathe(P('stand'), t), expr: 'smile', rim, gear: { sling: true }, t }); }
  });
  FX.dust(g, t, { count: 30, color: M.practical, a: 0.3 });
};

// ======================= TENT (Saul) =======================
const armorOn = (g, o, s, slip = 0) => { const hx = o.x + 3 * s, hy = o.y - 208 * s; rr(g, o.x - 22 * s, o.y - 176 * s, 46 * s, 80 * s, 10 * s); g.fillStyle = BRONZE; g.fill(); g.strokeStyle = shade(BRONZE, -0.35); g.lineWidth = 3; g.stroke(); helmet(g, hx, hy + slip * 18 * s, 26 * s * 1.35, o.facing, null, { crest: false }); sword(g, o.x - 14 * s, o.y - 100 * s, 1.35, 120 * s, 8 * s); };
K.tent = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d), m = p.mode, talk = tk(info, p);
  if (m === 'messenger') { const cam = camAt(lerp(1.05, 1.1, k), CX(), GYv(), 0.86); const { GY, M } = camp(g, t, cam);
    layer(g, cam, 1, (g) => { tent(g, CX() + 200, GY + 30, 700, 460, '#6a1f2a', { lit: 1, light: M.practical, open: 0.6 }); crown(g, CX() + 200, GY - 470, 30); actor(g, { who: 'soldier', x: lerp(CX() - 700, CX() + 160, ease.in(k)), y: GY + 40, s: 1, facing: 1, pose: walkPose(t * 11, { run: true }), expr: 'surprised', rim: { color: M.rim, dir: [-0.8, -0.5] }, gear: { spear: true }, t }); });
    FX.dust(g, t, { count: 30, color: M.key, a: 0.3 }); return; }
  const tz = m === 'enter' ? [1.25, 1.3] : [1.5, 1.6], tfx = m === 'saulKing' ? CX() - 60 : ['armor', 'wobble', 'drop'].includes(m) ? CX() : CX() - 100;
  const cam = camAt(lerp(tz[0], tz[1], k), tfx + lerp(-20, 20, k), GYv(), 0.9);
  const { GY, M } = tentIn(g, t, cam);
  const rim = { color: M.rim, dir: [-0.7, -0.6], w: 4.5 }, y = GY + 30, s = 1.0;
  layer(g, cam, 1, (g) => {
    const throne = (x) => { rr(g, x - 70, y - 260, 140, 260, 12); g.fillStyle = shade('#3a1e1a', -0.2); g.fill(); rr(g, x - 80, y - 90, 160, 24, 8); g.fillStyle = '#6a2a2a'; g.fill(); circle(g, x - 60, y - 262, 12, GOLD); circle(g, x + 60, y - 262, 12, GOLD); };
    if (m === 'saulKing') actor(g, { who: 'saul', x: CX() - 60, y, s: 1.1, facing: 1, pose: breathe(P('stand'), t), expr: 'determined', rim, t });
    const seated = ['enter', 'davidTalk', 'saulNo', 'davidPoint', 'pointUp'].includes(m);
    if (seated) { throne(CX() - 360); actor(g, { who: 'saul', x: CX() - 360, y: y - 4, s: 1.05, facing: 1, pose: breathe(m === 'saulNo' ? posesAt(t, [[0, 'sit'], [0.3, { ...P('sit'), eF: [22, -120], hF: [44, -140] }]]) : P('sit'), t), expr: m === 'saulNo' ? 'worried' : 'thinking', talk: m === 'saulNo' ? talk : 0, rim, t, shadow: false, look: m === 'saulNo' ? [Math.sin(t * 6) * 0.8, 0] : [1, -0.1] }); }
    if (m === 'enter') actor(g, { who: 'david', x: lerp(CX() + 700, CX() + 160, ease.out(k)), y, s, facing: -1, pose: walkPose(t * 5.6), expr: 'neutral', rim, gear: { sling: true }, t });
    if (m === 'davidTalk') actor(g, { who: 'david', x: CX() + 160, y, s, facing: -1, pose: breathe(posesAt(t, [[0, 'talk'], [1, 'explain']]), t), expr: 'determined', talk, rim, gear: { sling: true }, t });
    if (m === 'saulNo') actor(g, { who: 'david', x: CX() + 160, y, s, facing: -1, pose: breathe(P('stand'), t), expr: 'neutral', rim, gear: { sling: true }, t });
    if (m === 'davidPoint') actor(g, { who: 'david', x: CX() + 160, y, s, facing: 1, pose: breathe(posesAt(t, [[0, 'talk'], [0.4, 'point']]), t), expr: 'determined', talk, rim, gear: { sling: true }, t });
    if (m === 'pointUp') { actor(g, { who: 'david', x: CX() + 160, y, s, facing: -1, pose: breathe(posesAt(t, [[0, 'talk'], [1.2, 'pointUp']]), t), expr: 'determined', talk, rim, gear: { sling: true }, t }); FX.godRays(g, CX() + 680, GY - 520, { angle: Math.PI * 0.8, spread: 0.5, len: 1300, color: '#fff3dc', a: 0.12 * ease.inOut(prog(t, 1.2, 2.4)), t }); }
    if (['armor', 'wobble', 'drop'].includes(m)) {
      const dx = m === 'wobble' ? CX() + lerp(0, 120, k) : CX() + 40, sway = m === 'wobble' ? Math.sin(t * 5) * 0.12 * (1 - prog(t, d - 0.6, d)) : 0;
      if (m === 'armor') actor(g, { who: 'saul', x: CX() - 280, y, s: 1.05, facing: 1, pose: breathe(posesAt(t, [[0, 'stand'], [0.4, 'holdFront']]), t), expr: 'smile', rim, t });
      const o = { who: 'david', x: dx, y, s, facing: m === 'armor' ? -1 : 1, pose: m === 'wobble' ? (t < d - 0.6 ? walkPose(t * 3) : P('shrug')) : P('stand'), expr: m === 'drop' ? 'happy' : 'worried', rim, t, rot: sway };
      actor(g, o);
      if (m !== 'drop') { const on = m === 'armor' ? ease.out(prog(t, 0.6, 1.6)) : 1; g.save(); g.globalAlpha *= on; g.translate(0, (1 - on) * -120); armorOn(g, { x: dx, y, facing: o.facing }, s * 0.88, m === 'wobble' ? 0.6 : 0); g.restore(); }
      else { const f = ease.in(prog(t, 0, 0.6)); helmet(g, dx + 40 + f * 60, lerp(y - 180, y - 30, f), 34, 1, null, { crest: false }); rr(g, dx - 160, lerp(y - 150, y - 26, f), 70, 26, 8); g.fillStyle = BRONZE; g.fill(); sword(g, dx - 300, y - 8, 0.03, 150, 9); if (t > 0.5 && t < 1.2) FX.rings(g, dx, y - 20, t - 0.5, { count: 2, r0: 20, r1: 200, color: '#fff3e0', a: 0.5 }); }
    }
  });
  FX.dust(g, t, { count: 40, color: M.practical, a: 0.35 });
};

// ======================= BROOK =======================
K.brook = (g, t, info, p) => {
  const d = info.dur, k = ease.inOut(t / d);
  const cam = camAt(lerp(1.15, 1.25, k), CX() + lerp(-60, 0, k), GYv(), 0.8);
  const { GY, M } = brook(g, t, cam);
  layer(g, cam, 1, (g) => {
    const x = CX() - 60, pick = t > 0.8;
    actor(g, { who: 'david', x, y: GY + 20, s: 1.05, facing: 1, pose: breathe(pick ? posesAt(t, [[0.8, 'crouch'], [1.6, { ...P('crouch'), hF: [60, -30] }], [2.4, 'crouch']]) : walkPose(t * 5), t), expr: 'determined', rim: { color: M.rim, dir: [0.8, -0.5], w: 4.5 }, gear: { staff: false, bag: true }, t });
    const n = Math.min(5, Math.floor(clamp((t - 1) / (d - 1.4)) * 5.99));
    for (let i = 0; i < 5; i++) stone(g, x + 120 + i * 42, GY + 70 + (i % 2) * 10, 13, i, i < n ? '#ffe7a0' : '#fff3dc');
    for (let i = 0; i < n; i++) FX.sparkle(g, x + 120 + i * 42, GY + 60, 16, '#fff3dc', 0.6);
  });
  UI.badge(g, { str: `${Math.min(5, Math.floor(clamp((t - 1) / (d - 1.4)) * 5.99))}/5`, a: ease.out(prog(t, 1, 1.4)) });
  FX.dust(g, t, { count: 30, color: M.key, a: 0.3 });
};

// ======================= FREEZE (stone in mid-air) =======================
K.freeze = (g, t, info, p) => {
  const d = info.dur, cam = camAt(1.35 + 0.04 * t, CX(), GYv(), 0.86, { r: -0.02 + 0.01 * t });
  const { GY, M } = valley(g, 0, cam, { israel: 'idle', phil: 'idle' });
  layer(g, cam, 1, (g) => {
    const s = 0.8, y = GY + 12;
    actor(g, { who: 'david', x: CX() - 380, y, s, facing: 1, pose: custom.throw, expr: 'determined', rim: { color: '#cfe0ff', dir: [0.6, -0.8], w: 5 }, gear: { sling: true }, t: 0 });
    actor(g, { who: 'goliath', x: CX() + 380, y, s, facing: -1, pose: walkPose(1.2), expr: 'angry', rim: { color: '#cfe0ff', dir: [0.6, -0.8], w: 5 }, t: 0 });
    const sx = CX() + 40 + t * 8, sy = y - 400; FX.rings(g, sx, sy, t, { count: 3, r0: 40, r1: 260, speed: 0.35, color: '#e8f0ff', a: 0.4 });
    seg(g, [[CX() - 280, y - 330], [sx - 30, sy]], 2, alpha('#ffffff', 0.25)); stone(g, sx, sy, 16, t * 0.3);
  });
  FX.drops(g, t, { count: 40, color: '#d8e4ff', rMax: 8, drift: 3 });
  g.save(); g.globalCompositeOperation = 'soft-light'; g.fillStyle = 'rgba(80,120,255,.35)'; g.fillRect(0, 0, E.W, E.H); g.restore();
};

// ======================= TITLE & END =======================
K.title = (g, t, info) => {
  valley(g, t, { z: 1.05 + 0.03 * t, x: 0, y: 0 }, { israel: 'idle', phil: 'idle' }); veil(g, '#0a0604', 0.35);
  UI.titleCard(g, t, { lines: ['A HISTÓRIA DE', 'DAVI E GOLIAS'], sub: '1 SAMUEL 17', dur: info.dur });
};
K.end = (g, t, info, p) => {
  const tt = p.cont ? t + 5.06 : t;
  UI.endScreen(g, tt, { question: 'Qual é o seu gigante?', cast: CAST, moodColors: [shade(mood('dusk').sky[0], -0.3), mood('dusk').sky[1], mood('dusk').dark], rim: mood('dusk').rim });
  const hx = E.W / 2 + (0 - 2) * Math.min(150, (E.W * 0.85) / 5), y0 = E.H - 170;
  crown(g, E.W / 2 + (2 - 2) * Math.min(150, (E.W * 0.85) / 5) + 3 * 0.9, y0 - 207 * 0.9 * 1.0, 26 * 0.9, ease.out(prog(tt, 0.5, 0.9)));
};
