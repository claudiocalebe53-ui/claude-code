#!/usr/bin/env python3
"""Sintetiza os efeitos sonoros e a trilha de fundo (100% originais, sem direitos de terceiros).

Gera em assets/sons/:
    tique-taque.wav  (1s em loop: tique + taque)
    ding.wav         (sino de acerto, duas notas)
    whoosh.wav       (varredura de ruído para as vinhetas)
    pop.wav          (bolha curta)
    musica.wav       (loop animado de 16 compassos a 120 BPM)

Uso: python gerar_sons.py   (só precisa de numpy)
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 48000
SAIDA = Path(__file__).resolve().parent / "assets" / "sons"
rng = np.random.default_rng(7)


def t_(dur):
    return np.arange(int(SR * dur)) / SR


def salvar(nome, x, pico=0.89):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    m = np.max(np.abs(x)) or 1.0
    x = x / m * pico
    dados = (x * 32767).astype("<i2").tobytes()
    SAIDA.mkdir(parents=True, exist_ok=True)
    with wave.open(str(SAIDA / f"{nome}.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dados)
    print(f"  {SAIDA / (nome + '.wav')}  ({len(x) / SR:.2f}s)")


def passa_baixa(x, corte):
    """Filtro de 1 polo (corte em Hz, pode ser array por amostra)."""
    corte = np.broadcast_to(np.asarray(corte, dtype=np.float64), x.shape)
    a = 1 - np.exp(-2 * np.pi * corte / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def passa_alta(x, corte):
    return x - passa_baixa(x, corte)


def colocar(dest, som, inicio, ganho=1.0):
    i = int(inicio * SR)
    if i >= len(dest):
        return
    n = min(len(som), len(dest) - i)
    dest[i:i + n] += som[:n] * ganho


# ---------------------------------------------------------------------------
# Efeitos
# ---------------------------------------------------------------------------

def clique(freq, dur=0.045, brilho=0.5):
    t = t_(dur)
    env = np.exp(-t / 0.008)
    tom = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.3 * t)
    ruido = passa_alta(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.003)
    return (tom * env + brilho * ruido) * 0.8


def tique_taque():
    x = np.zeros(SR)
    colocar(x, clique(2600), 0.0)
    colocar(x, clique(1750, brilho=0.35), 0.5, 0.85)
    return x


def ding():
    def sino(f, dur=1.6):
        t = t_(dur)
        parciais = [(1, 1.0, 0.9), (2.0, 0.45, 0.5), (2.76, 0.3, 0.35), (5.4, 0.12, 0.15)]
        s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / d) for k, a, d in parciais)
        ataque = np.minimum(1, t / 0.003)
        return s * ataque
    x = np.zeros(int(SR * 1.8))
    colocar(x, sino(1046.5), 0.0, 0.8)      # C6
    colocar(x, sino(1568.0), 0.09, 1.0)     # G6
    return x


def whoosh(dur=0.6):
    t = t_(dur)
    k = t / dur
    ruido = rng.standard_normal(len(t))
    corte = 300 + 5200 * np.sin(np.pi * k) ** 2      # sobe e desce
    s = passa_baixa(ruido, corte)
    s = passa_alta(s, 150)
    env = np.sin(np.pi * np.clip(k * 1.15, 0, 1)) ** 1.5
    return s * env


def pop():
    t = t_(0.12)
    freq = 900 * np.exp(-t / 0.018) + 180
    fase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t / 0.03) * np.minimum(1, t / 0.0015)
    return np.sin(fase) * env


# ---------------------------------------------------------------------------
# Trilha: pop/eletrônico animado, I–V–vi–IV em Dó, 120 BPM, 16 compassos
# ---------------------------------------------------------------------------

BPM = 120
BEAT = 60 / BPM


def hz(nota_midi):
    return 440 * 2 ** ((nota_midi - 69) / 12)


def bumbo():
    t = t_(0.35)
    f = 48 + 110 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.14)


def palma():
    t = t_(0.2)
    r = passa_alta(rng.standard_normal(len(t)), 900)
    env = np.exp(-t / 0.06) * (1 + 0.8 * np.exp(-((t - 0.012) / 0.004) ** 2))
    return r * env * 0.6


def chimbal(aberto=False):
    t = t_(0.18 if aberto else 0.05)
    r = passa_alta(rng.standard_normal(len(t)), 7000)
    return r * np.exp(-t / (0.06 if aberto else 0.012)) * 0.35


def baixo(nota, dur):
    t = t_(dur)
    f = hz(nota)
    serra = 2 * ((f * t) % 1) - 1
    s = passa_baixa(serra, 600 + 900 * np.exp(-t / 0.08))
    env = np.minimum(1, t / 0.005) * np.exp(-t / 0.5) * np.minimum(1, (dur - t) / 0.02)
    return (s + 0.6 * np.sin(2 * np.pi * f * t)) * env


def pluck(nota, dur=0.4):
    t = t_(dur)
    f = hz(nota)
    quad = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * 2 * t) * 0.3
    s = passa_baixa(quad, 1200 + 4000 * np.exp(-t / 0.05))
    return s * np.exp(-t / 0.16) * np.minimum(1, t / 0.002)


def pad(notas, dur):
    t = t_(dur)
    s = np.zeros(len(t))
    for n in notas:
        for desafina in (-0.12, 0.12):
            f = hz(n + desafina)
            s += 2 * ((f * t) % 1) - 1
    s = passa_baixa(s, 900)
    env = np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.3)
    return s * env / len(notas)


def musica():
    compassos = 16
    total = compassos * 4 * BEAT
    x = np.zeros(int(SR * total) + SR)
    # (raiz do baixo, notas do acorde)
    acordes = [
        (36, [60, 64, 67]),   # C
        (43, [59, 62, 67]),   # G
        (45, [60, 64, 69]),   # Am
        (41, [60, 65, 69]),   # F
    ]
    padrao_arp = [0, 1, 2, 1, 0, 2, 1, 2]
    melodia = [  # (tempo em beats dentro de 4 compassos, nota, duração em beats)
        (0, 76, 1), (1, 79, 0.5), (1.5, 76, 0.5), (2, 74, 1), (3, 72, 1),
        (4, 74, 1.5), (5.5, 71, 0.5), (6, 74, 1), (7, 79, 1),
        (8, 76, 1), (9, 72, 0.5), (9.5, 76, 0.5), (10, 81, 1.5), (11.5, 79, 0.5),
        (12, 77, 1), (13, 76, 0.5), (13.5, 74, 0.5), (14, 72, 2),
    ]
    k_b, k_p = bumbo(), palma()
    hh_f, hh_a = chimbal(), chimbal(True)
    for c in range(compassos):
        raiz, notas = acordes[c % 4]
        t0 = c * 4 * BEAT
        intro = c < 2
        colocar(x, pad(notas, 4 * BEAT), t0, 0.22)
        for b in range(4):
            tb = t0 + b * BEAT
            if not intro or b in (0, 2):
                colocar(x, k_b, tb, 0.9)
            if not intro and b in (1, 3):
                colocar(x, k_p, tb, 0.5)
            colocar(x, hh_f, tb, 0.25)
            colocar(x, hh_a if b == 3 else hh_f, tb + BEAT / 2, 0.35)
            # baixo em colcheias com oitava no contratempo
            colocar(x, baixo(raiz, BEAT / 2 * 0.9), tb, 0.45)
            colocar(x, baixo(raiz + 12, BEAT / 2 * 0.9), tb + BEAT / 2, 0.3)
        for i, idx in enumerate(padrao_arp):
            colocar(x, pluck(notas[idx] + 12, 0.35), t0 + i * BEAT / 2, 0.16)
        if c >= 4:  # melodia entra no 5º compasso, ciclo de 4 compassos
            base = (c - 4) % 4
            for tb, nota, db in melodia:
                if int(tb // 4) == base:
                    colocar(x, pluck(nota, db * BEAT * 0.95), t0 + (tb % 4) * BEAT, 0.22)
    # dobra a cauda sobre o começo para o loop não ter emenda
    n = int(SR * total)
    x[: len(x) - n] += x[n:]
    x = x[:n]
    # estéreo leve: atraso curto no canal direito
    d = int(SR * 0.012)
    dir_ = np.concatenate([x[-d:], x[:-d]])
    return np.stack([x, 0.85 * x + 0.15 * dir_], axis=1)


def main():
    print("Gerando sons em", SAIDA)
    salvar("tique-taque", tique_taque())
    salvar("ding", ding())
    salvar("whoosh", whoosh())
    salvar("pop", pop())
    salvar("musica", musica(), pico=0.8)


if __name__ == "__main__":
    main()
