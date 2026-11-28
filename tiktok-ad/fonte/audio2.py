import sys, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
import json
TL = json.load(open(sys.argv[2])); VO_PATH = sys.argv[3]
DUR = TL["END"] + 0.1
N = int(SR * DUR)
rng = np.random.default_rng(7)
music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); send = np.zeros((N, 2))

def t_(d): return np.arange(int(d * SR)) / SR
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def vlp(x, fc):
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) * np.ones(len(x)) / SR)
    y = np.empty(len(x)); s1 = s2 = 0.0
    for i in range(len(x)):
        s1 += a[i] * (x[i] - s1); s2 += a[i] * (s1 - s2); y[i] = s2
    return y
def add(buf, x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    x = x[: N - i]
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        x = np.stack([x * l * 1.414, x * r * 1.414], 1)
    buf[i:i + len(x)] += x * g
def saw(f, t): return 2 * ((f * t) % 1) - 1
def noise(d): return rng.uniform(-1, 1, int(d * SR))

# ---------- grid ----------
BAR = 2.25; BEAT = BAR / 4; NS = TL['NS']; C = TL['C']
T0 = NS[7] - 9 * BAR; BUILD = 8; NBARS = 12
def beat(k): return T0 + k * BEAT
CH = [  # (bass root Hz, chord tones Hz)  Am F C G
    (55.00, [220.0, 261.63, 329.63]),
    (43.65, [174.61, 220.0, 261.63]),
    (65.41, [196.0, 261.63, 329.63]),
    (49.00, [196.0, 246.94, 293.66]),
]
def chord_at(k_bar): return CH[k_bar % 4]

# ---------- instruments ----------
def kick(g=1.0):
    t = t_(0.45); f = 45 + 110 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 7.5)
    x[:300] += noise(300 / SR) * np.linspace(.6, 0, 300)
    return np.tanh(x * 1.6) * g
def clap():
    t = t_(0.25); n = bp(noise(0.25), 900, 6000)
    env = np.exp(-t * 22)
    for d in (0.0, 0.011, 0.022): env += np.exp(-np.clip(t - d, 0, None) * 200) * (t >= d) * .5
    return n * env * .8 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * .3
def hat(d=0.045):
    t = t_(d); return hp(noise(d), 7000) * np.exp(-t * (6 / d))
def snare():
    t = t_(0.18); return bp(noise(.18), 1200, 7000) * np.exp(-t * 26) + np.sin(2*np.pi*210*t)*np.exp(-t*35)*.4
def pluck(f, d=0.28, bright=3500):
    t = t_(d); x = saw(f, t) * .6 + saw(f * 1.006, t) * .4
    return lp(x * np.exp(-t * 14), bright)
def pad(freqs, d):
    t = t_(d); x = sum(saw(f * m, t) for f in freqs for m in (0.997, 1.003)) / (len(freqs) * 2)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.3)
    return lp(x, 1400) * env
def bass(f, d):
    t = t_(d); x = np.sin(2 * np.pi * f * t) + .35 * lp(saw(f * 2, t), 500)
    env = np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03)
    return x * env
def sidechain(length, beats_at):
    env = np.ones(length)
    for b in beats_at:
        i = int(b * SR); L = int(0.28 * SR)
        if i >= length: continue
        seg = 1 - .75 * np.exp(-np.arange(min(L, length - i)) / SR * 12)
        env[i:i + len(seg)] = np.minimum(env[i:i + len(seg)], seg)
    return env

# ---------- arrangement ----------
def warp(o):
    A = TL['anch']
    for (a0, a1), (b0, b1) in zip(A, A[1:]):
        if o <= b0: return a1 + (b1 - a1) * (o - a0) / (b0 - a0)
    return A[-1][1] + o - A[-1][0]
kicks = []
add(music, pad(CH[0][1], T0 + .2), 0.0, .22); add(send, pad(CH[0][1], T0 + .2), 0, .15)
r = t_(T0); q = r / T0
add(sfx, vlp(noise(T0), 300 + 5000 * q ** 2.5) * q ** 2 * .35 + np.sin(2 * np.pi * np.cumsum(200 + 600 * q ** 2) / SR) * q ** 3 * .08, 0.0)
for bar in range(NBARS):
    root, tones = chord_at(bar)
    b0 = bar * 4; build = bar == BUILD; drop = bar > BUILD
    for k in range(4):
        tb = beat(b0 + k)
        if not build or k < 2: add(music, kick(), tb, .9); kicks.append(tb)
        if (k in (1, 3)) and not build: add(music, clap(), tb, .45)
        if not build:
            add(music, hat(), tb + BEAT / 2, .22 if not drop else .3, .3)
            if drop: add(music, hat(.025), tb + BEAT / 4, .12, -.3); add(music, hat(.025), tb + 3 * BEAT / 4, .12, -.3)
    if build:
        t = beat(b0 + 2)
        while t < beat(b0 + 4) - 1e-6:
            pr = (t - beat(b0 + 2)) / (2 * BEAT)
            add(music, snare(), t, .4 + .6 * pr, rng.uniform(-.2, .2))
            t += BEAT / 4 if pr < .5 else BEAT / 8
    for e in range(8):
        if build and e >= 4: break
        add(music, bass(root, BEAT / 2 * .9), beat(b0) + e * BEAT / 2, .38)
    p = pad(tones, BAR + .05); add(music, p, beat(b0), .16 if not drop else .2); add(send, p, beat(b0), .12)
    if bar >= 1:
        seq = [tones[0] * 2, tones[1] * 2, tones[2] * 2, tones[1] * 2]
        if drop: seq = [tones[0] * 2, tones[2] * 2, tones[1] * 4, tones[2] * 2]
        for s_ in range(16):
            if build and s_ >= 12: break
            pk = pluck(seq[s_ % 4], .22, 2500 if not drop else 5000)
            g = (.07 if bar < 4 else .09) * (1.25 if drop else 1)
            add(music, pk, beat(b0) + s_ * BEAT / 4, g, .35 if s_ % 2 else -.35); add(send, pk, beat(b0) + s_ * BEAT / 4, g * .8)
sc = sidechain(N, kicks); music *= sc[:, None] * .85 + .15
# ---------- SFX ----------
def boom(g=1.0):
    t = t_(1.6); f = 30 + 60 * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    x += lp(noise(1.6), 900) * np.exp(-t * 5) * .5
    return np.tanh(x * 1.3) * g
def whoosh(d=0.45, up=True):
    t = t_(d); pr = t / d
    out = vlp(hp(noise(d), 250), 400 + 6000 * (pr if up else 1 - pr) ** 1.5) * 1.8
    env = np.sin(np.pi * t / d) ** 2
    return out * env
def tick():
    t = t_(.03); return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 220) * .6 + hp(noise(.03), 4000) * np.exp(-t * 300) * .3
def blip(f0=900, f1=520):
    t = t_(.09); f = f1 + (f0 - f1) * np.exp(-t * 50)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
def bell(f, d=1.2):
    t = t_(d); return sum(np.sin(2 * np.pi * f * m * t) * a * np.exp(-t * dk) for m, a, dk in ((1, 1, 3), (2.01, .45, 5), (3.02, .2, 8), (4.2, .1, 12)))
def thump():
    t = t_(.25); f = 55 + 40 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18)
def buzz(d=.35):
    t = t_(d); x = np.sign(np.sin(2 * np.pi * 165 * t)) * (0.6 + .4 * np.sin(2 * np.pi * 24 * t))
    return lp(x, 900) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .02)
def shutter():
    a = hp(noise(.02), 2000) * np.exp(-t_(.02) * 250); b = hp(noise(.035), 1500) * np.exp(-t_(.035) * 160)
    x = np.zeros(int(.12 * SR)); x[:len(a)] += a; i = int(.06 * SR); x[i:i + len(b)] += b * .9
    return x
def eexpo(p): return 1 - 2 ** (-10 * p)
def ticks(a, b, n):
    ts, last = [], -1
    for i in range(1, 2000):
        t = a + (b - a) * i / 2000; k = int(eexpo(i / 2000) * n)
        if k != last: ts.append(t); last = k
    return ts


def at(i, f=0.0): return C[i]['s'] + f * (C[i]['e'] - C[i]['s'])
add(sfx, boom(.7), 0.2)
for cut in NS[1:7]:
    add(sfx, whoosh(.5), cut - .38, .45, rng.uniform(-.3, .3)); add(send, whoosh(.5), cut - .38, .2)
for t in ticks(C[3]['s'], C[5]['s'] + .3, 22): add(sfx, tick(), t, .3, -.2)
for t in ticks(C[10]['s'] - .1, C[10]['s'] + 1.0, 22): add(sfx, tick(), t, .3, .2)
hb = NS[2] + .4
while hb < NS[3] - .4: add(sfx, thump(), hb, .55); add(sfx, thump(), hb + .16, .35); hb += 60 / 72
c0, c1 = warp(7.3), warp(8.8); ch = t_(c1 - c0); q = ch / (c1 - c0)
add(sfx, np.sin(2 * np.pi * np.cumsum(300 + 900 * q ** 2) / SR) * q * .12 * (0.7 + .3 * np.sin(2 * np.pi * 14 * ch)), c0)
add(sfx, bell(1568), c1, .16); add(send, bell(1568), c1, .12)
bz = warp(9.45)
while bz < warp(11.0): add(sfx, buzz(), bz, .2); bz += .6
for t in (C[12]['e'] - .35, at(13, .35), at(14, .25)): add(sfx, blip(1100, 700), t, .22)
add(sfx, shutter(), NS[5] + .1, .5)
for t in (NS[6] + .4, warp(14.56), warp(15.16)): add(sfx, blip(), t, .28, -.3)
bd = BAR; r2 = t_(bd); q = r2 / bd
add(sfx, vlp(noise(bd), 400 + 7000 * q ** 2) * q ** 2 * .55 + np.sin(2 * np.pi * np.cumsum(150 + 900 * q ** 2) / SR) * q ** 2 * .1, NS[7] - BAR)
add(sfx, boom(1.0), NS[7] - .02); add(send, boom(.5), NS[7] - .02, .5)
add(sfx, whoosh(.6, False), NS[7] - .15, .5)
pa = C[19]['s'] + .25; pb = at(19, .5)
for t in ticks(pa, pb, 26): add(sfx, tick(), t, .28)
for f, d in ((2093, 0), (2637, .09)): add(sfx, bell(f, 1.5), pb + .05 + d, .18); add(send, bell(f, 1.5), pb + .05 + d, .15)
add(sfx, blip(1300, 800), at(20) - .1, .3)
for t in (warp(17.95), warp(18.85)): add(sfx, whoosh(.4), t, .25)
TEND = T0 + NBARS * BAR
add(music, kick(), TEND, 1.0); add(sfx, boom(.6), TEND); add(send, pad(CH[0][1], 1.2), TEND, .25)

# ---------- reverb ----------
irl = t_(2.2); ir = lp(noise(2.2) * np.exp(-irl * 3.2), 6000); ir2 = lp(noise(2.2) * np.exp(-irl * 3.2), 6000)
wet = np.stack([fftconvolve(send[:, 0], ir)[:N], fftconvolve(send[:, 1], ir2)[:N]], 1) * .06

# ---------- voice + ducking ----------
vsr, vo = wavfile.read(VO_PATH); vo = vo.astype(np.float64) / 32768
if vo.ndim > 1: vo = vo.mean(1)
v = np.zeros(N); v[:min(N, len(vo))] = vo[:N]
env = np.abs(v); k = int(.04 * SR)
env = np.convolve(env, np.ones(k) / k, 'same'); env = env / (env.max() + 1e-9)
on = (env > .06).astype(float)
duck = np.zeros(N); a_up, a_dn = 1 - np.exp(-1 / (.03 * SR)), 1 - np.exp(-1 / (.35 * SR)); y = 0.0
for i in range(N):
    tgt = on[i]; y += (a_up if tgt > y else a_dn) * (tgt - y); duck[i] = y
mgain = 1 - .6 * duck            # music about -8 dB under the voice
sgain = 1 - .35 * duck           # sfx a bit lower under the voice
bed = (music * .8 + wet) * mgain[:, None]
fx = sfx * sgain[:, None] * .5   # sfx ~ -6 dB vs the previous version
voice = np.stack([v, v], 1) * 1.15
mix = voice + bed * .55 + fx * .6
fade = np.ones(N); fi = int((TL['END'] - .6) * SR); fade[fi:] = np.linspace(1, 0, N - fi) ** 2
mix *= fade[:, None]
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
mix /= np.max(np.abs(mix)) / 0.89
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
for name, b in (('voice', voice), ('bed', bed * .55), ('fx', fx * .6)): print(name, round(20 * np.log10(np.sqrt(np.mean(b ** 2)) + 1e-9), 1), 'dB rms')
