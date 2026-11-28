import sys, json, subprocess, numpy as np
from scipy.io import wavfile

src, out_wav, out_json = sys.argv[1:4]
SPEED = 1.06; OFFSET = 0.35; PAD = 0.04; GAP_IN = 0.05; GAP_PH = 0.12
sr, x = wavfile.read(src); x = x.astype(np.float64) / 32768

# speech chunks (between silences detected at -40dB/0.12s)
sil = [(0.699,0.856),(1.822,2.049),(3.237,3.375),(3.732,4.106),(4.985,5.148),(5.960,6.103),(6.729,7.025),(7.740,7.879),(9.240,9.478),(11.232,11.606),(12.505,12.737),(13.719,14.029),(15.990,16.266),(17.198,17.343),(18.259,18.532),(19.838,20.089),(20.895,21.047),(21.713,21.971),(24.624,24.888),(28.481,28.745)]
edges = [0.03] + [v for s in sil for v in s] + [30.53]
chunks = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]
assert len(chunks) == 21
# phrase id per chunk (aligned to script by syllable timing)
PH = [1,1, 2, 3,3,3, 4,4,4,4, 5,5, 6,6,6, 7,7,7, 8, 9,9]
TEXT = ["Conheça o", "T900.", "Feito pra quem não para.", "Tela", "gigante,", "nítida em qualquer luz.",
        "Batimento,", "oxigênio", "e pressão…", "24 horas no seu pulso.", "Carrega sem fio.", "É só encostar.",
        "Atende ligação direto do pulso.", "Com NFC", "e GPS.", "E olha ele de verdade:", "um visual", "pra cada dia.",
        "Ainda vem com duas pulseiras extras e capinha!", "Tudo isso por só 53 reais, com frete grátis!", "Toca no carrinho e garante o seu!"]

parts, cues, t = [], [], 0.0
fade = int(0.008 * sr)
for i, (a, b) in enumerate(chunks):
    a = max(0, a - PAD); b = min(len(x) / sr, b + PAD)
    seg = x[int(a * sr):int(b * sr)].copy()
    seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    if i > 0:
        g = GAP_PH if PH[i] != PH[i - 1] else GAP_IN
        parts.append(np.zeros(int(g * sr))); t += g
    cues.append({"i": i, "ph": PH[i], "text": TEXT[i], "s": OFFSET + (t + PAD) / SPEED, "e": OFFSET + (t + len(seg) / sr - PAD) / SPEED})
    parts.append(seg); t += len(seg) / sr
y = np.concatenate(parts)
tmp = out_wav + '.tmp.wav'
wavfile.write(tmp, sr, (y * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'atempo={SPEED},adelay={int(OFFSET*1000)}:all=1', out_wav], check=True)
phr = {}
for c in cues:
    p = phr.setdefault(c["ph"], {"s": c["s"], "e": c["e"]}); p["e"] = c["e"]
json.dump({"chunks": cues, "phrases": phr, "end": OFFSET + t / SPEED}, open(out_json, 'w'), indent=1, ensure_ascii=False)
for k, v in phr.items(): print(k, round(v["s"], 2), round(v["e"], 2))
print('voice end', round(OFFSET + t / SPEED, 2))
