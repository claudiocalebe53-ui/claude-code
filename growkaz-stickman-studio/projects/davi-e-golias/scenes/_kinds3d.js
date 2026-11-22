// _kinds3d.js — low-poly 3D Valley of Elah (two hills, brook, tents, armies, figures).
import { E, V, mood, ease, prog, lerp, shade, mix } from '/engine/core.js';
import { POSES, walkPose } from '/engine/rig2d.js';
import * as UI from '/engine/ui2d.js';
import { DAVID, GOLIAS } from './cast.js';

function hill(T, x, z, r, h, color) { const m = T.sphere(1, T.mat(color, { flat: true }), x, 0, z); m.scale.set(r, h, r * 0.7); return m; }
function build(T, o) {
  const M = mood(o.mood || 'dusk');
  const st = T.stage({ mood: o.mood || 'dusk', fov: V(38, 55), fog: [18, 90], keyPos: [14, 9, -10], keyIntensity: 3.2, ambient: 1.6, shadowSize: 34 });
  st.add(T.ground(240, 240, shade(M.floor, -0.1)));
  st.add(hill(T, -22, 0, 16, 7, shade(M.floor, 0.05)), hill(T, 22, 0, 16, 7, shade(M.floor, 0.02)), hill(T, -40, -30, 26, 14, mix(M.wall, M.dark, 0.5)), hill(T, 40, -34, 26, 15, mix(M.wall, M.dark, 0.5)), hill(T, 0, -70, 50, 18, mix(M.sky[1], M.dark, 0.6)));
  const brook = T.plane(1.4, 120, T.mat(mix(M.sky[1], M.dark, 0.35), { roughness: 0.2, metalness: 0.3 })); brook.rotation.x = -Math.PI / 2; brook.position.set(1, 0.03, 0); st.add(brook);
  for (const [x, z, c] of [[-28, -3, '#6a5a48'], [-25, 4, '#7a6a52'], [-30, 3, '#5a4a3a'], [27, -2, '#7a3a2a'], [30, 4, '#6a2a22'], [25, 5, '#7a4a2a']]) st.add(T.cone(1.6, 2.2, shade(c, -0.15), x, 7.2, z, 4));
  const r = (n) => { let s = n; return () => (s = (s * 9301 + 49297) % 233280) / 233280; };
  if (o.armies !== false) {
    const isr = T.crowd3D({ rows: 4, perRow: 26, width: 14, step: 0.8, rise: 0.3, colors: ['#3a3040', '#4a3c4a', '#2e2636'], seed: 3, y0: 4.6 }); isr.position.set(-12, 0, 0); isr.rotation.y = Math.PI / 2; st.add(isr);
    const phi = T.crowd3D({ rows: 4, perRow: 26, width: 14, step: 0.8, rise: 0.3, colors: ['#5a2a20', '#6a3020', '#4a2018'], seed: 5, y0: 4.6 }); phi.position.set(12, 0, 0); phi.rotation.y = -Math.PI / 2; st.add(phi);
  }
  const R = r(7); for (let i = 0; i < 40; i++) st.add(T.sphere(0.3 + R() * 0.5, T.mat(shade(M.dark, 0.1), { flat: true }), -14 + R() * 28, 0.1, -20 + R() * 40));
  const out = { stage: st };
  if (o.figures) { const d = T.figure3D(DAVID, { rim: M.rim, pose: POSES.stand, s: 0.88 }); d.position.set(-2, 0, 2); d.rotation.y = 0.2; st.add(d); out.david = d; }
  if (o.goliath) { const gl = T.figure3D(GOLIAS, { rim: M.rim, pose: POSES.crossArms, s: 1.75 }); gl.position.set(3, 0, 0); gl.rotation.y = Math.PI; st.add(gl); }
  return out;
}
export const K3 = {
  valley3d: (p) => ({
    kind: '3d',
    init(T) { const m = p.mode; return build(T, { mood: m === 'golden' ? 'golden' : 'dusk', armies: m !== 'empty' && m !== 'golden', figures: m === 'golden', goliath: false }); },
    draw(s, t, info, T) {
      const m = p.mode, d = info.dur;
      if (m === 'empty') T.dolly(s.stage.camera, t, [[0, { pos: [2, 9, 46], look: [0, 3, 0], fov: 40 }], [d, { pos: [1, 7.5, 36], look: [0, 3, 0], fov: 40 }]]);
      if (m === 'armies') T.orbit(s.stage.camera, t, { target: [0, 4, 0], radius: [42, 36], height: [18, 14], from: -0.35, to: 0.35, dur: d });
      if (m === 'watch') T.dolly(s.stage.camera, t, [[0, { pos: [-4, 8, 22], look: [-12, 6, 0], fov: 38 }], [d, { pos: [-2, 7.5, 18], look: [-11, 5.8, 0], fov: 38 }]]);
      if (m === 'golden') { T.orbit(s.stage.camera, t, { target: [-2, 1.2, 2], radius: [8, 6.5], height: [2.6, 2.0], from: 0.9, to: 1.4, dur: d }); s.david?.setPose(walkPose(0)); }
    },
  }),
};
