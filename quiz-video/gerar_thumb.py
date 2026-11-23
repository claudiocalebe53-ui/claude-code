#!/usr/bin/env python3
"""Thumbnail do YouTube (1280x720) no estilo dos vídeos de quiz.

    python gerar_thumb.py --projeto videos/06_quiz_longo --numero 35 --linha "PERGUNTAS" \
        --faixa "DO FÁCIL AO IMPOSSÍVEL!" --cartas 2,21,35

As cartas são as imagens de resposta do projeto (pN_resposta.png); a última fica borrada com "?".
Saída: saida/<projeto>_thumb.jpg (+ .png).
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageEnhance

import gerar as G
import gerar_imagens_lote as L

BASE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--numero", default="35")
    ap.add_argument("--linha", default="PERGUNTAS")
    ap.add_argument("--faixa", default="DO FÁCIL AO IMPOSSÍVEL!")
    ap.add_argument("--cartas", default="2,21,35")
    ap.add_argument("--emoji", default="cerebro")
    a = ap.parse_args()

    G.configurar_formato("horizontal")  # compõe em 1920x1080 e reduz para 1280x720
    W, H = G.W, G.H
    proj = Path(a.projeto)

    canvas = G.raios((255, 200, 0), (255, 140, 0), 8, n=22, centro=(W * 0.32, H * 0.5))
    canvas.alpha_composite(G.com_opacidade(G.meio_tom(), 0.45))
    canvas.alpha_composite(G.vinheta_escura())

    # --- colagem de cartas à direita
    nums = [int(x) for x in a.cartas.split(",")]
    poses = [(1500, 300, 10, 0.92), (1220, 600, -8, 0.95), (1610, 730, 5, 1.0)]
    for k, (n, (cx, cy, ang, esc)) in enumerate(zip(nums, poses)):
        img = Image.open(proj / "imagens" / f"p{n}_resposta.png").convert("RGB")
        img = G._cover(img, 640, 434)
        ultima = k == len(nums) - 1
        if ultima:
            img = G._borrar(img, 24)
        carta = G.moldura(img, ang)
        G.colar_centro(canvas, carta, cx, cy, escala=esc * 0.82)
        if ultima:
            q = G.texto_layer("?", 300, cor=(255, 205, 0), contorno=16, sombra=14)
            G.colar_centro(canvas, q, cx, cy - 10, angulo=10)

    # --- texto à esquerda
    num = G.texto_layer(a.numero, 470, cor=(255, 215, 0), contorno=22, sombra=20)
    G.colar_centro(canvas, num, 470, 330, angulo=-4)
    linha = G.texto_layer(a.linha, 175, contorno=16, sombra=14)
    if linha.width > 900:
        linha = linha.resize((900, int(linha.height * 900 / linha.width)), Image.LANCZOS)
    G.colar_centro(canvas, linha, 470, 610, angulo=-4)
    faixa = G._faixa(a.faixa, "", G.VERMELHO, 92)
    if faixa.width > 960:
        faixa = faixa.resize((960, int(faixa.height * 960 / faixa.width)), Image.LANCZOS)
    G.colar_centro(canvas, faixa, 480, 820, angulo=-3)

    # emoji grande de adesivo + selo de tempo
    L.por(canvas, L.adesivo(L.emoji(a.emoji, 230), borda=16, contorno=8), 860, 210, 14)
    selo = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(selo)
    d.ellipse((10, 22, 250, 262 - 10), fill=G.ESCURO)
    d.ellipse((10, 10, 250, 250), fill=G.VERMELHO, outline=G.ESCURO, width=10)
    d.text((130, 120), "5s", font=G.fonte(120), fill=G.BRANCO, anchor="mm", stroke_width=9, stroke_fill=G.ESCURO)
    G.colar_centro(canvas, selo, 1790, 130, angulo=12)

    out = canvas.convert("RGB").resize((1280, 720), Image.LANCZOS)
    out = ImageEnhance.Color(out).enhance(1.08)
    dest = BASE / "saida" / f"{proj.name}_thumb"
    out.save(dest.with_suffix(".png"))
    out.save(dest.with_suffix(".jpg"), quality=92)
    print(dest.with_suffix(".jpg"))


if __name__ == "__main__":
    main()
