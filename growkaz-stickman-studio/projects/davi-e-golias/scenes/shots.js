// shots.js — registers every shot in story/shots.json from its params.k (shot kind). Kinds live in _kindsA/_kindsB/_kinds3d.
import { E, registerShot } from '/engine/core.js';
import { K } from './_kindsA.js';
import './_kindsB.js';
import { K3 } from './_kinds3d.js';

for (const sh of E.shots) {
  const p = sh.params || {};
  if (K3[p.k]) { registerShot(sh.id, K3[p.k](p)); continue; }
  const fn = K[p.k]; if (!fn) continue;
  registerShot(sh.id, { draw: (g, t, info) => fn(g, t, info, p) });
}
