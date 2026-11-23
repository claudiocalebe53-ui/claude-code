#!/usr/bin/env python3
"""Corta uma narração única (todas as falas em sequência) em um clipe por fala.

    python cortar_narracao.py --projeto videos/01_animais --audio narracao.mp4 --modelo <pasta do modelo>

Usa faster-whisper (modelo CTranslate2 local) para transcrever com tempo de cada palavra,
alinha o texto com as falas esperadas do perguntas.json e corta no meio da pausa mais
próxima de cada fronteira. Gera <projeto>/narracao/{00_gancho, vinheta_*, pN_pergunta,
pN_resposta, 99_final}.wav e um relatório do que foi ouvido em cada clipe.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import numpy as np

NOMES_NIVEL = {"facil": "Nível fácil!", "medio": "Nível médio!", "dificil": "Nível difícil!"}


def norm(p: str) -> str:
    p = unicodedata.normalize("NFD", p.lower())
    p = "".join(c for c in p if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", p)


def tokens(texto: str) -> list[str]:
    return [t for t in (norm(x) for x in texto.split()) if t]


def falas_esperadas(dados: dict) -> list[tuple[str, str]]:
    falas = [("00_gancho", dados["gancho"]["fala"])]
    nivel = None
    for i, q in enumerate(dados["perguntas"], 1):
        if q["nivel"] != nivel:
            nivel = q["nivel"]
            falas.append((f"vinheta_{nivel}", NOMES_NIVEL[nivel]))
        falas.append((f"p{i}_pergunta", q.get("fala_pergunta", q["texto"])))
        falas.append((f"p{i}_resposta", q["fala_resposta"]))
    falas.append(("99_final", dados["final"]["fala"]))
    return falas


def silencios(audio: Path) -> list[tuple[float, float]]:
    out = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(audio), "-af",
                          "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    fim = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    return list(zip(ini, fim))


def transcrever(audio: Path, modelo: str):
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(audio), "-f", "f32le",
                          "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(np.frombuffer(raw, np.float32), language="pt", word_timestamps=True)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--modelo", required=True, help="pasta do modelo faster-whisper (CTranslate2)")
    a = ap.parse_args()
    proj, audio = Path(a.projeto), Path(a.audio)
    dados = json.loads((proj / "perguntas.json").read_text(encoding="utf-8"))
    falas = falas_esperadas(dados)

    palavras = transcrever(audio, a.modelo)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                "csv=p=0", str(audio)], capture_output=True, text=True).stdout)

    # alinha tokens esperados x ouvidos
    esp, dono = [], []
    for k, (_, txt) in enumerate(falas):
        for t in tokens(txt):
            esp.append(t)
            dono.append(k)
    ouv, ouv_idx = [], []
    for j, (_, _, w) in enumerate(palavras):
        for t in tokens(w):
            ouv.append(t)
            ouv_idx.append(j)
    sm = difflib.SequenceMatcher(None, esp, ouv, autojunk=False)
    por_fala: dict[int, list[int]] = {k: [] for k in range(len(falas))}
    for b in sm.get_matching_blocks():
        for d in range(b.size):
            por_fala[dono[b.a + d]].append(ouv_idx[b.b + d])
    # fala sem casamento (ex.: "Canberra" ouvido como "Camberra"): usa as palavras que
    # sobraram entre a fala anterior e a seguinte
    for k, v in por_fala.items():
        if v:
            continue
        antes = max((max(por_fala[i]) for i in range(k) if por_fala[i]), default=-1)
        depois = min((min(por_fala[i]) for i in range(k + 1, len(falas)) if por_fala[i]), default=len(palavras))
        por_fala[k] = list(range(antes + 1, depois))
    faltando = [falas[k][0] for k, v in por_fala.items() if not v]
    if faltando:
        raise SystemExit(f"não reconheci estas falas no áudio: {faltando}")

    # fronteiras: meio da pausa mais próxima entre o fim de uma fala e o início da próxima
    sil = silencios(audio)
    cortes = [0.0]
    for k in range(len(falas) - 1):
        fim = palavras[max(por_fala[k])][1]
        ini = palavras[min(por_fala[k + 1])][0]
        alvo = (fim + ini) / 2
        cand = [(abs((s + e) / 2 - alvo), (s + e) / 2) for s, e in sil
                if e > fim - 0.3 and s < ini + 0.3]
        cortes.append(min(cand)[1] if cand else alvo)
    cortes.append(dur)

    pasta = proj / "narracao"
    pasta.mkdir(parents=True, exist_ok=True)
    rel = []
    for k, (nome, txt) in enumerate(falas):
        a0, a1 = cortes[k], cortes[k + 1]
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(audio), "-vn", "-ss", f"{a0:.3f}",
                        "-to", f"{a1:.3f}", "-af",
                        "aresample=48000,silenceremove=start_periods=1:start_threshold=-40dB,"
                        "areverse,silenceremove=start_periods=1:start_threshold=-40dB,areverse,"
                        "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse",
                        "-ac", "1", "-c:a", "pcm_s16le", str(pasta / f"{nome}.wav")], check=True)
        ouvido = " ".join(w for s, e, w in palavras if a0 <= (s + e) / 2 < a1)
        rel.append(f"{nome:16s} {a0:6.2f}-{a1:6.2f}  esperado: {txt}\n{'':16s} {'':13s}  ouvido:   {ouvido}")
    (pasta / "relatorio.txt").write_text("\n".join(rel) + "\n", encoding="utf-8")
    print("\n".join(rel))


if __name__ == "__main__":
    main()
