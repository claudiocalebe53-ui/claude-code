// thumbnail: giant Goliath, David with sling, flying stone, big title.
import { E, mood, layer, veil, glow, text, alpha, shade, seg, circle, registerShot, FONTS, linGrad, rr, poly } from '/engine/core.js';
import { POSES, breathe } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import { valley, GYv } from './_sets.js';
import { actor, stone, sling } from './_props.js';

registerShot('t1', { draw(g) {
  const t = 0.4, M = mood('dusk');
  valley(g, t, { z: 1.25, x: 120, y: 40 }, { israel: 'idle', phil: 'idle', sunPos: [E.W * 0.68, E.H * 0.42] });
  glow(g, E.W * 0.68, E.H * 0.42, 900, '#ffb050', 0.55);
  FX.godRays(g, E.W * 0.68, E.H * 0.42, { count: 14, angle: Math.PI, spread: Math.PI * 2, len: 1800, color: '#ffd08a', a: 0.12, t });
  veil(g, '#000', 0.15);
  // Goliath, huge, low angle
  const rim = { color: '#ffd08a', dir: [-0.6, -0.8], w: 7 };
  actor(g, { who: 'goliath', x: E.W * 0.76, y: E.H * 1.18, s: 2.05, facing: -1, pose: { ...POSES.point, hF: [70, -190] }, expr: 'shocked', rim, t, look: [-1, -0.2] });
  // David, foreground left
  const dx = E.W * 0.17, dy = E.H * 1.12;
  actor(g, { who: 'david', x: dx, y: dy, s: 2.25, facing: 1, pose: { ...POSES.point, eF: [36, -176], hF: [74, -170], eB: [-22, -150], hB: [-40, -130], kF: [18, -50], fF: [30, 0] }, expr: 'angry', rim: { color: '#ffe0a0', dir: [1, -0.4], w: 8 }, t, gear: { bag: true } });
  sling(g, dx + 74 * 2.25 * 0.88, dy - 170 * 2.25 * 0.88, 0.9, { len: 140, w: 6, swing: 2 });
  // stone with motion trail toward the forehead
  const sx = E.W * 0.6, sy = E.H * 0.36;
  for (let i = 1; i <= 12; i++) circle(g, sx - i * 26, sy + i * 7, 22 - i * 1.4, alpha('#fff1d0', 0.32 - i * 0.025));
  glow(g, sx, sy, 200, '#fff3dc', 0.9); stone(g, sx, sy, 34);
  FX.speedLines(g, 0.3, { cx: sx, cy: sy, count: 26, a: 0.35, inner: 80 });
  // title
  const T = (s, x, y, size, col, rot = 0) => { g.save(); g.translate(x, y); g.rotate(rot); text(g, s, 0, 0, { size, color: col, font: FONTS.title, weight: 700, align: 'left', stroke: size * 0.2, strokeColor: '#140804', spacing: 2 }); g.restore(); };
  T('DAVI', 70, 150, 190, '#ffffff', -0.04);
  T('vs', 560, 160, 110, '#ffcf3a', -0.04);
  T('GOLIAS', 70, 330, 190, '#ffcf3a', -0.04);
  // tag
  g.save(); g.translate(90, 470); g.rotate(-0.04); rr(g, 0, -50, 540, 96, 18); g.fillStyle = '#e0302a'; g.fill(); g.lineWidth = 8; g.strokeStyle = '#140804'; g.stroke();
  text(g, 'SÓ 1 PEDRA!', 270, 0, { size: 70, color: '#ffffff', font: FONTS.title, weight: 700 }); g.restore();
  // vignette for punch
  g.fillStyle = linGrad(g, 0, 0, E.W, 0, [alpha('#000', 0.45), alpha('#000', 0), alpha('#000', 0)]); g.fillRect(0, 0, E.W, E.H);
} });
