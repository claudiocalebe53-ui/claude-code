#!/usr/bin/env python3
"""Gerador automático de vídeos curtos de quiz (9:16, 1080x1920, 60fps).

Uso:
    python gerar.py               # renderiza o vídeo completo -> saida/quiz.mp4
    python gerar.py --teste       # vídeo curto (gancho + 1 pergunta + final)
    python gerar.py --previa      # exporta 1 frame PNG de cada tipo de tela
    python gerar.py --fps 30      # outra taxa de quadros

Depende apenas de Pillow + numpy + ffmpeg (no PATH).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Configuração geral
# ---------------------------------------------------------------------------

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
W, H = 1080, 1920

# Zonas seguras (interface do Reels/Shorts): base e lateral direita livres.
SAFE_L = 70
SAFE_R = 890          # tudo que é "conteúdo" termina aqui (direita livre)
SAFE_BOTTOM = 1540    # nada importante abaixo disso
CX = (SAFE_L + SAFE_R) // 2

# Tempos (segundos)
T_GANCHO = 3.0
T_VINHETA = 1.0
T_TEXTO = 1.0
T_TIMER = 5.0
T_REVELA = 2.0
T_PERGUNTA = T_TEXTO + T_TIMER + T_REVELA
T_FINAL = 4.0

FONTE = ASSETS / "fonts" / "LilitaOne-Regular.ttf"
EMOJI_FONTES = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "C:/Windows/Fonts/seguiemj.ttf",
]

ESCURO = (25, 20, 35)
BRANCO = (255, 255, 255)
VERMELHO = (229, 57, 53)
VERDE = (46, 204, 64)

CORES_FUNDO = [
    (21, 101, 192),   # azul
    (123, 30, 58),    # vinho
    (27, 127, 67),    # verde
    (94, 43, 168),    # roxo
    (142, 27, 27),    # vermelho escuro
]

NIVEIS = {
    "facil": {"nome": "FÁCIL", "c1": (46, 204, 64), "c2": (24, 150, 45)},
    "medio": {"nome": "MÉDIO", "c1": (255, 159, 28), "c2": (224, 110, 0)},
    "dificil": {"nome": "DIFÍCIL", "c1": (235, 60, 55), "c2": (170, 25, 25)},
}

SONS = {
    "tique": "tique-taque",
    "ding": "ding",
    "whoosh": "whoosh",
    "pop": "pop",
    "musica": "musica",
}
EXT_AUDIO = (".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac")


# Pasta do vídeo atual (--projeto videos/<nome>): tem perguntas.json, narracao/ e imagens/.
PROJETO: Path | None = None


def _pastas(sub: str) -> list[Path]:
    return ([PROJETO / sub] if PROJETO else []) + [ASSETS / sub]


def achar_narracao(nome: str) -> Path | None:
    """<projeto>/narracao/<nome>.(wav|mp3|...) — ex.: 00_gancho, vinheta_facil, p1_pergunta."""
    pastas = [PROJETO / "narracao"] if PROJETO else [ASSETS / "narracao"]
    for pasta in pastas:
        for ext in EXT_AUDIO:
            p = pasta / (nome + ext)
            if p.exists():
                return p
    return None


@lru_cache(maxsize=64)
def duracao_audio(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_in_cubic(x):
    x = clamp(x)
    return x ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_cor(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def escurecer(c, f):
    return tuple(int(v * f) for v in c)


@lru_cache(maxsize=64)
def fonte(tamanho: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTE), tamanho)


_ALPHA_LUT: dict[int, list[int]] = {}


def com_opacidade(img: Image.Image, k: float) -> Image.Image:
    """Multiplica o canal alpha por k (0..1)."""
    if k >= 0.999:
        return img
    q = int(clamp(k) * 255)
    lut = _ALPHA_LUT.get(q)
    if lut is None:
        lut = [int(a * q / 255) for a in range(256)]
        _ALPHA_LUT[q] = lut
    out = img.copy()
    out.putalpha(img.getchannel("A").point(lut))
    return out


def colar(canvas: Image.Image, layer: Image.Image, x: float, y: float):
    """alpha_composite com recorte para coordenadas negativas / fora da tela."""
    x, y = int(round(x)), int(round(y))
    lw, lh = layer.size
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(lw, W - x), min(lh, H - y)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (0, 0, lw, lh):
        layer = layer.crop((x0, y0, x1, y1))
    canvas.alpha_composite(layer, (x + x0, y + y0))


def colar_centro(canvas, layer, cx, cy, escala=1.0, opacidade=1.0, angulo=0.0):
    if escala <= 0.01 or opacidade <= 0.01:
        return
    if abs(escala - 1) > 0.002:
        nw = max(1, int(layer.width * escala))
        nh = max(1, int(layer.height * escala))
        layer = layer.resize((nw, nh), Image.BILINEAR)
    if abs(angulo) > 0.05:
        layer = layer.rotate(angulo, resample=Image.BICUBIC, expand=True)
    layer = com_opacidade(layer, opacidade)
    colar(canvas, layer, cx - layer.width / 2, cy - layer.height / 2)


def texto_layer(texto, tamanho, cor=BRANCO, contorno=10, cor_contorno=ESCURO,
                sombra=8) -> Image.Image:
    """Texto com contorno grosso e sombra deslocada, recortado justo."""
    f = fonte(tamanho)
    pad = contorno + sombra + 6
    bbox = f.getbbox(texto, stroke_width=contorno)
    w = bbox[2] - bbox[0] + pad * 2
    h = bbox[3] - bbox[1] + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = pad - bbox[0], pad - bbox[1]
    if sombra:
        d.text((ox, oy + sombra), texto, font=f, fill=cor_contorno,
               stroke_width=contorno, stroke_fill=cor_contorno)
    d.text((ox, oy), texto, font=f, fill=cor, stroke_width=contorno,
           stroke_fill=cor_contorno)
    return img


def quebrar_linhas(texto, tamanho, largura_max):
    f = fonte(tamanho)
    palavras = texto.split()
    linhas, atual = [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if f.getlength(teste) <= largura_max or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


# ---------------------------------------------------------------------------
# Emoji (fonte colorida do sistema). Se não houver, desenha ícone simples.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _fonte_emoji():
    for caminho in EMOJI_FONTES:
        if not os.path.exists(caminho):
            continue
        for tam in (109, 160, 96, 64, 128):
            try:
                return ImageFont.truetype(caminho, tam), tam
            except OSError:
                continue
    return None


@lru_cache(maxsize=32)
def emoji(ch: str, tamanho: int) -> Image.Image | None:
    fe = _fonte_emoji()
    if not fe:
        return None
    f, tam = fe
    img = Image.new("RGBA", (int(tam * 1.4), int(tam * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        d.text((tam * 0.1, tam * 0.1), ch, font=f, embedded_color=True)
    except Exception:
        return None
    bb = img.getbbox()
    if not bb:
        return None
    img = img.crop(bb)
    esc = tamanho / img.height
    return img.resize((max(1, int(img.width * esc)), tamanho), Image.LANCZOS)


def texto_com_emoji(texto, ch, tamanho, **kw):
    """Texto + emoji à direita, num único layer."""
    t = texto_layer(texto, tamanho, **kw)
    e = emoji(ch, int(tamanho * 1.05)) if ch else None
    if e is None:
        return t
    gap = int(tamanho * 0.12)
    w = t.width + gap + e.width
    h = max(t.height, e.height)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(t, (0, (h - t.height) // 2))
    img.alpha_composite(e, (t.width + gap, (h - e.height) // 2 - int(tamanho * 0.04)))
    return img


# ---------------------------------------------------------------------------
# Fundos
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def vinheta_escura() -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = np.clip((d - 0.45) * 210, 0, 170).astype(np.uint8)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.putalpha(Image.fromarray(a, "L"))
    return img


def raios(c1, c2, angulo, n=18, centro=None) -> Image.Image:
    centro = centro or (W / 2, H * 0.42)
    img = Image.new("RGBA", (W, H), c1 + (255,))
    d = ImageDraw.Draw(img)
    r = math.hypot(W, H)
    cx, cy = centro
    passo = 2 * math.pi / n
    for i in range(n):
        a0 = math.radians(angulo) + i * passo
        a1 = a0 + passo / 2
        d.polygon([(cx, cy),
                   (cx + r * math.cos(a0), cy + r * math.sin(a0)),
                   (cx + r * math.cos(a1), cy + r * math.sin(a1))], fill=c2)
    return img


@lru_cache(maxsize=1)
def meio_tom() -> Image.Image:
    """Textura de pontos estilo HQ: pontos maiores nas bordas."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    passo = 30
    for j, y in enumerate(range(0, H + passo, passo)):
        off = (passo // 2) if j % 2 else 0
        for x in range(-passo, W + passo, passo):
            px = x + off
            dist = math.hypot((px - W / 2) / (W / 2), (y - H * 0.45) / (H / 2))
            rr = clamp((dist - 0.25) / 0.9) * passo * 0.42
            if rr > 1:
                d.ellipse((px - rr, y - rr, px + rr, y + rr), fill=(0, 0, 0, 70))
    return img


@lru_cache(maxsize=8)
def padrao_interrogacao(cor: tuple) -> Image.Image:
    """Fundo sólido + '?' em marca d'água, maior que a tela para rolar."""
    tile = 300
    big = Image.new("RGBA", (W + tile, H + tile), cor + (255,))
    f = fonte(150)
    marca = Image.new("RGBA", (tile, tile), (0, 0, 0, 0))
    dm = ImageDraw.Draw(marca)
    dm.text((40, 10), "?", font=f, fill=(255, 255, 255, 28))
    m1 = marca.rotate(-18, resample=Image.BICUBIC)
    m2 = marca.rotate(16, resample=Image.BICUBIC).resize((tile * 2 // 3, tile * 2 // 3))
    for y in range(0, H + tile, tile):
        for x in range(0, W + tile, tile):
            big.alpha_composite(m1, (x, y))
            big.alpha_composite(m2, (x + tile // 2 - 20, y + tile // 2 - 10))
    return big


def fundo_pergunta(cor, t_global) -> Image.Image:
    big = padrao_interrogacao(cor)
    tile = 300
    off = int(t_global * 35) % tile
    frame = big.crop((off, off, off + W, off + H))
    frame.alpha_composite(vinheta_escura())
    return frame


# ---------------------------------------------------------------------------
# Logo e imagens
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4)
def logo(altura: int) -> Image.Image:
    for nome in ("logo.png", "logo.webp", "logo.jpg"):
        p = ASSETS / nome
        if p.exists():
            img = Image.open(p).convert("RGBA")
            esc = altura / img.height
            return img.resize((max(1, int(img.width * esc)), altura), Image.LANCZOS)
    # Placeholder: medalhão amarelo com "?" + "QUIZ"
    s = 4
    a = altura * s
    img = Image.new("RGBA", (a, a), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, a - 1, a - 1), fill=ESCURO)
    m = a * 0.06
    d.ellipse((m, m, a - m, a - m), fill=(255, 205, 0))
    f = fonte(int(a * 0.62))
    d.text((a / 2, a * 0.47), "?", font=f, fill=BRANCO, anchor="mm",
           stroke_width=int(a * 0.045), stroke_fill=ESCURO)
    return img.resize((altura, altura), Image.LANCZOS)


def _cover(img: Image.Image, w, h) -> Image.Image:
    esc = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * esc + 1), int(img.height * esc + 1)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def _resolver_imagem(nome: str) -> Path | None:
    if not nome:
        return None
    for p in (Path(nome), BASE / nome, *(d / nome for d in _pastas("imagens"))):
        if p.exists():
            return p
    print(f"  ! imagem não encontrada: {nome} (usando placeholder)", file=sys.stderr)
    return None


def placeholder(w, h, cor, tipo, texto=""):
    img = Image.new("RGB", (w, h), cor)
    d = ImageDraw.Draw(img)
    # listras diagonais sutis
    claro = lerp_cor(cor, BRANCO, 0.12)
    for x in range(-h, w, 60):
        d.polygon([(x, h), (x + 30, h), (x + 30 + h, 0), (x + h, 0)], fill=claro)
    cx, cy = w / 2, h / 2
    if tipo == "pergunta":
        # ícone de "foto": moldura + sol + montanhas
        bw, bh = w * 0.42, h * 0.5
        x0, y0 = cx - bw / 2, cy - bh / 2
        d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 22, fill=BRANCO, outline=ESCURO, width=8)
        d.ellipse((x0 + bw * 0.62, y0 + bh * 0.16, x0 + bw * 0.82, y0 + bh * 0.16 + bw * 0.2),
                  fill=(255, 196, 0), outline=ESCURO, width=6)
        d.polygon([(x0 + 12, y0 + bh - 12), (x0 + bw * 0.35, y0 + bh * 0.38),
                   (x0 + bw * 0.6, y0 + bh - 12)], fill=cor, outline=ESCURO)
        d.polygon([(x0 + bw * 0.45, y0 + bh - 12), (x0 + bw * 0.68, y0 + bh * 0.55),
                   (x0 + bw - 12, y0 + bh - 12)], fill=escurecer(cor, 0.7), outline=ESCURO)
        f = fonte(int(h * 0.2))
        d.text((x0 + bw * 0.18, y0 + bh * 0.08), "?", font=f, fill=ESCURO)
    else:
        # check verde + texto da resposta
        r = h * 0.2
        ccx, ccy = cx, cy - h * 0.12
        d.ellipse((ccx - r, ccy - r, ccx + r, ccy + r), fill=VERDE, outline=ESCURO, width=8)
        d.line([(ccx - r * 0.5, ccy), (ccx - r * 0.12, ccy + r * 0.4), (ccx + r * 0.52, ccy - r * 0.42)],
               fill=BRANCO, width=int(r * 0.24), joint="curve")
        if texto:
            tam = int(h * 0.2)
            while fonte(tam).getlength(texto) > w * 0.85 and tam > 20:
                tam -= 4
            d.text((cx, cy + h * 0.27), texto, font=fonte(tam), fill=BRANCO, anchor="mm",
                   stroke_width=8, stroke_fill=ESCURO)
    return img


def _borrar(img: Image.Image, raio: float) -> Image.Image:
    """Desfoque forte sem bordas escuras (espelha as margens antes de borrar)."""
    if raio <= 0:
        return img
    m = int(raio * 3)
    w, h = img.size
    grande = Image.new("RGB", (w + 2 * m, h + 2 * m))
    grande.paste(img, (m, m))
    grande.paste(img.transpose(Image.FLIP_LEFT_RIGHT).crop((w - m, 0, w, h)), (0, m))
    grande.paste(img.transpose(Image.FLIP_LEFT_RIGHT).crop((0, 0, m, h)), (w + m, m))
    topo = grande.crop((0, m, w + 2 * m, 2 * m)).transpose(Image.FLIP_TOP_BOTTOM)
    base = grande.crop((0, h, w + 2 * m, h + m)).transpose(Image.FLIP_TOP_BOTTOM)
    grande.paste(topo, (0, 0))
    grande.paste(base, (0, h + m))
    return grande.filter(ImageFilter.GaussianBlur(raio)).crop((m, m, m + w, m + h))


def moldura(img: Image.Image, angulo=-3.0) -> Image.Image:
    """Moldura branca + sombra, levemente inclinada."""
    b = 16
    w, h = img.width + b * 2, img.height + b * 2
    sh = 14
    out = Image.new("RGBA", (w + sh + 30, h + sh + 30), (0, 0, 0, 0))
    sombra = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((15 + sh, 15 + sh, 15 + sh + w, 15 + sh + h), 18,
                                             fill=(0, 0, 0, 110))
    out.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(8)))
    quadro = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(quadro).rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=BRANCO)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width - 1, img.height - 1), 8, fill=255)
    quadro.paste(img.convert("RGB"), (b, b), mask)
    out.alpha_composite(quadro, (15, 15))
    return out.rotate(angulo, resample=Image.BICUBIC, expand=True)


# ---------------------------------------------------------------------------
# Elementos da pergunta
# ---------------------------------------------------------------------------

BTN_W, BTN_H, BTN_GAP = SAFE_R - SAFE_L, 112, 22
BTN_Y0 = 880
IMG_W, IMG_H = 560, 380
IMG_CY = 625
IMG_CX = CX
BTN_X0 = SAFE_L
TOPO_Y = 170
BAR_Y, BAR_H = 1488, 34
BAR_X0, BAR_X1 = SAFE_L, SAFE_R
LOGO_XY = (SAFE_L - 10, 58)
POS_FINAL = {"titulo": (CX + 20, 520), "emoji": (CX + 20, 800), "balao": (CX + 20, 1050), "siga": (CX + 20, 1320)}
GANCHO_LARG = 960
BLUR_MAX = 16
TAM_TEXTO = 74
FORMATO = "vertical"


def configurar_formato(fmt: str):
    """'vertical' (1080x1920, Shorts/Reels) ou 'horizontal' (1920x1080, YouTube longo)."""
    global W, H, CX, SAFE_L, SAFE_R, IMG_W, IMG_H, IMG_CX, IMG_CY, BTN_W, BTN_X0, BTN_Y0, TOPO_Y
    global BAR_Y, BAR_X0, BAR_X1, LOGO_XY, POS_FINAL, GANCHO_LARG, FORMATO, BLUR_MAX, TAM_TEXTO
    FORMATO = fmt
    if fmt != "horizontal":
        return
    W, H = 1920, 1080
    SAFE_L, SAFE_R = 80, 1840
    CX = W // 2
    TOPO_Y = 70
    IMG_W, IMG_H = 640, 434
    IMG_CX, IMG_CY = 500, 600
    BTN_X0, BTN_W, BTN_Y0 = 1000, 830, 335
    BAR_X0, BAR_X1, BAR_Y = 120, 1800, 968
    LOGO_XY = (W - 84 - 50, 40)
    POS_FINAL = {"titulo": (W / 2, 250), "emoji": (W / 2 - 230, 580), "balao": (W / 2 + 180, 580),
                 "siga": (W / 2, 860)}
    GANCHO_LARG = 1500
    BLUR_MAX = 26
    TAM_TEXTO = 90
LETRAS = "ABCD"


def botao(letra, texto, cor_circulo=VERMELHO, destaque=False) -> Image.Image:
    pad = 14
    img = Image.new("RGBA", (BTN_W + pad * 2, BTN_H + pad * 2 + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0 = pad, pad
    r = BTN_H // 2
    # sombra sólida embaixo
    d.rounded_rectangle((x0, y0 + 9, x0 + BTN_W, y0 + BTN_H + 9), r, fill=(0, 0, 0, 90))
    if destaque:
        d.rounded_rectangle((x0 - 8, y0 - 8, x0 + BTN_W + 8, y0 + BTN_H + 8), r + 8, fill=VERDE)
    d.rounded_rectangle((x0, y0, x0 + BTN_W, y0 + BTN_H), r, fill=BRANCO, outline=ESCURO, width=5)
    # círculo da letra
    cr = 42
    ccx, ccy = x0 + 16 + cr, y0 + BTN_H / 2
    d.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr), fill=cor_circulo, outline=ESCURO, width=5)
    d.text((ccx, ccy + 2), letra, font=fonte(54), fill=BRANCO, anchor="mm",
           stroke_width=4, stroke_fill=ESCURO)
    tam = 60
    while fonte(tam).getlength(texto) > BTN_W - 170 and tam > 28:
        tam -= 2
    d.text((ccx + cr + 30, ccy + 3), texto, font=fonte(tam), fill=ESCURO, anchor="lm")
    return img


def circulo_numero(n: int) -> Image.Image:
    s = 120
    img = Image.new("RGBA", (s + 20, s + 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((10, 18, 10 + s, 18 + s), fill=ESCURO)
    d.ellipse((10, 10, 10 + s, 10 + s), fill=(255, 205, 0), outline=ESCURO, width=7)
    d.text((10 + s / 2, 10 + s / 2 + 3), str(n), font=fonte(78), fill=BRANCO, anchor="mm",
           stroke_width=6, stroke_fill=ESCURO)
    return img


class Pergunta:
    """Pré-renderiza tudo que é estático de uma pergunta."""

    def __init__(self, q: dict, idx: int):
        self.q = q
        self.idx = idx
        self.cor = tuple(q.get("cor_fundo") or CORES_FUNDO[idx % len(CORES_FUNDO)])
        self.correta = int(q["correta"])
        self.num = circulo_numero(idx + 1)

        # Texto: escolhe tamanho que caiba em até 3 linhas
        self.tx0 = SAFE_L + 160
        largura = W - 60 - self.tx0
        tam = TAM_TEXTO
        while True:
            linhas = quebrar_linhas(q["texto"], tam, largura)
            # prefere 2 linhas (3 linhas encostam na imagem); só aceita 3 se a fonte ficar pequena demais
            if len(linhas) <= 2 or (len(linhas) <= 3 and tam <= 54) or tam <= 40:
                break
            tam -= 2
        self.tam = tam
        self.linhas = linhas
        self._cache_texto: dict[int, Image.Image] = {}
        self.total_chars = sum(len(l) for l in linhas)

        # Imagens
        cor_ph = lerp_cor(self.cor, BRANCO, 0.25)
        pq = _resolver_imagem(q.get("imagem_pergunta", ""))
        pr = _resolver_imagem(q.get("imagem_resposta", ""))
        img_q = _cover(Image.open(pq).convert("RGB"), IMG_W, IMG_H) if pq else \
            placeholder(IMG_W, IMG_H, cor_ph, "pergunta")
        if pr:
            img_r = _cover(Image.open(pr).convert("RGB"), IMG_W, IMG_H)
        elif pq:
            img_r = img_q
        else:
            img_r = placeholder(IMG_W, IMG_H, cor_ph, "resposta", q["alternativas"][self.correta])
        self.img_q = moldura(img_q, -3)
        self.img_r = moldura(img_r, -3)
        # Modo "borrado": mostra a imagem da resposta desfocada e revela desembaçando.
        self.borrar = bool(q.get("imagem_borrada", True)) and pr is not None
        if self.borrar:
            raios_blur = [BLUR_MAX, BLUR_MAX * 0.7, BLUR_MAX * 0.47, BLUR_MAX * 0.3, BLUR_MAX * 0.17, 1.5]
            self.niveis_blur = [moldura(_borrar(img_r, r), -3) for r in raios_blur] + [self.img_r]

        alts = q["alternativas"]
        self.botoes = [botao(LETRAS[i], alts[i]) for i in range(4)]
        self.botao_ok = botao(LETRAS[self.correta], alts[self.correta], VERDE, destaque=True)

    def texto_parcial(self, n_chars: int) -> Image.Image:
        n_chars = min(n_chars, self.total_chars)
        if n_chars in self._cache_texto:
            return self._cache_texto[n_chars]
        f = fonte(self.tam)
        lh = int(self.tam * 1.12)
        pad = 24
        img = Image.new("RGBA", (W - self.tx0 + pad, lh * len(self.linhas) + pad * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        resto = n_chars
        for i, linha in enumerate(self.linhas):
            parte = linha[:max(0, resto)]
            resto -= len(linha)
            if not parte:
                break
            y = pad + i * lh
            d.text((pad, y + 7), parte, font=f, fill=ESCURO, stroke_width=9, stroke_fill=ESCURO)
            d.text((pad, y), parte, font=f, fill=BRANCO, stroke_width=9, stroke_fill=ESCURO)
        self._cache_texto[n_chars] = img
        return img

    def altura_texto(self):
        return int(self.tam * 1.12) * len(self.linhas)


_PERGUNTAS: dict[int, Pergunta] = {}


def pergunta_obj(q, idx) -> Pergunta:
    if idx not in _PERGUNTAS:
        _PERGUNTAS[idx] = Pergunta(q, idx)
    return _PERGUNTAS[idx]


def cor_timer(frac):
    """frac 1 -> 0 : verde -> amarelo -> laranja."""
    verde, amarelo, laranja = (46, 204, 64), (255, 214, 0), (255, 120, 20)
    if frac > 0.5:
        return lerp_cor(amarelo, verde, (frac - 0.5) / 0.5)
    return lerp_cor(laranja, amarelo, frac / 0.5)


# ---------------------------------------------------------------------------
# Telas
# ---------------------------------------------------------------------------

def logo_canto(canvas):
    lg = logo(84)
    colar(canvas, lg, *LOGO_XY)


def tela_gancho(t, dados, tg):
    g = dados["gancho"]
    canvas = raios((255, 196, 0), (255, 150, 0), tg * 40, n=20, centro=(W / 2, H * 0.45))
    canvas.alpha_composite(vinheta_escura())

    l1 = _cache_layer(("g1", g["titulo"]), lambda: _titulo_gancho(g))
    l2 = _cache_layer(("g2", g["subtitulo"]), lambda: _faixa(g["subtitulo"], g.get("subtitulo_emoji", ""),
                                                             VERMELHO))
    # zoom-in rápido + leve zoom contínuo
    z = ease_out_back(t / 0.35, 2.2) * (1 + 0.05 * t / T_GANCHO)
    colar_centro(canvas, l1, W / 2, H * 0.40, escala=z, angulo=-3)
    z2 = ease_out_back((t - 0.35) / 0.3, 2.5)
    pulso = 1 + 0.04 * math.sin(max(0, t - 0.7) * 2 * math.pi * 1.6)
    colar_centro(canvas, l2, W / 2, H * 0.40 + l1.height / 2 + 120, escala=z2 * pulso, angulo=2)
    logo_canto(canvas)
    return canvas


def _titulo_gancho(g):
    palavras = g["titulo"].split()
    meio = math.ceil(len(palavras) / 2)
    a = texto_layer(" ".join(palavras[:meio]), 136, contorno=14, sombra=12)
    b = texto_com_emoji(" ".join(palavras[meio:]), g.get("titulo_emoji", ""), 136, contorno=14, sombra=12)
    w = max(a.width, b.width)
    img = Image.new("RGBA", (w, a.height + b.height - 50), (0, 0, 0, 0))
    img.alpha_composite(a, ((w - a.width) // 2, 0))
    img.alpha_composite(b, ((w - b.width) // 2, a.height - 50))
    if img.width > GANCHO_LARG:  # ganchos longos: reduz para caber com margem
        esc = GANCHO_LARG / img.width
        img = img.resize((GANCHO_LARG, int(img.height * esc)), Image.LANCZOS)
    return img


def _faixa(texto, ch, cor, tamanho=100):
    t = texto_com_emoji(texto, ch, tamanho, contorno=9, sombra=0)
    px, py = 50, 20
    img = Image.new("RGBA", (t.width + px * 2, t.height + py * 2 + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 12, img.width - 1, img.height - 1), 34, fill=ESCURO)
    d.rounded_rectangle((0, 0, img.width - 1, img.height - 13), 34, fill=cor, outline=ESCURO, width=7)
    img.alpha_composite(t, (px, py - 6))
    return img


_LAYERS: dict = {}


def _cache_layer(chave, fabrica):
    if chave not in _LAYERS:
        _LAYERS[chave] = fabrica()
    return _LAYERS[chave]


def tela_vinheta(t, nivel, tg, dur=T_VINHETA):
    nv = NIVEIS[nivel]
    canvas = raios(nv["c1"], nv["c2"], tg * 70, n=16, centro=(W / 2, H / 2))
    canvas.alpha_composite(meio_tom())
    canvas.alpha_composite(vinheta_escura())
    card = _cache_layer(("card", nivel), lambda: _cartao_nivel(nivel))
    saida = dur - 0.2
    if t < saida:
        z = ease_out_back(t / 0.28, 2.0)
        op = 1.0
    else:
        k = (t - saida) / 0.2
        z = 1 + 0.5 * ease_in_cubic(k)
        op = 1 - k
    tremor = 6 * math.sin(t * 90) * max(0, 1 - t / 0.35)
    colar_centro(canvas, card, W / 2 + tremor, H * 0.45, escala=z, opacidade=op, angulo=-5)
    logo_canto(canvas)
    return canvas


def _cartao_nivel(nivel):
    nv = NIVEIS[nivel]
    w, h = 820, 440
    img = Image.new("RGBA", (w + 30, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((15, 30, 15 + w, 30 + h), 40, fill=ESCURO)
    d.rounded_rectangle((15, 15, 15 + w, 15 + h), 40, fill=BRANCO, outline=ESCURO, width=10)
    # pontinhos de meio-tom no cartão
    for y in range(40, h, 26):
        for x in range(40 + (13 if (y // 26) % 2 else 0), w, 26):
            rr = 4 * clamp((y - 40) / h * 1.4)
            if rr > 0.6:
                d.ellipse((15 + x - rr, 15 + y - rr, 15 + x + rr, 15 + y + rr),
                          fill=lerp_cor(nv["c1"], BRANCO, 0.55))
    a = texto_layer("NÍVEL", 100, cor=ESCURO, contorno=0, sombra=0)
    b = texto_layer(nv["nome"], 200, cor=nv["c1"], contorno=14, sombra=12)
    img.alpha_composite(a, ((img.width - a.width) // 2, 40))
    img.alpha_composite(b, ((img.width - b.width) // 2, 40 + a.height - 30))
    return img


def tela_pergunta(t, q, idx, tg):
    P = pergunta_obj(q, idx)
    canvas = fundo_pergunta(P.cor, tg)
    logo_canto(canvas)

    # --- topo: número + texto (letra por letra em ~0.8s)
    z = ease_out_back(t / 0.3, 2.0)
    colar_centro(canvas, P.num, SAFE_L + P.num.width / 2 - 10, TOPO_Y + 62, escala=z)
    n = int(P.total_chars * clamp(t / 0.8)) if t < T_TEXTO else P.total_chars
    txt = P.texto_parcial(n)
    ty = TOPO_Y + 62 - txt.height / 2
    colar(canvas, txt, P.tx0 - 24, max(TOPO_Y - 30, ty))

    # --- imagem com moldura (troca na revelação com "flip")
    t_rev = t - (T_TEXTO + T_TIMER)
    zi = ease_out_back((t - 0.15) / 0.35, 1.6)
    if P.borrar:
        # imagem da resposta borrada; na revelação desembaça em ~0.45s com um "pulo"
        niv = P.niveis_blur
        if t_rev < 0:
            img = niv[0]
            esc = zi
        else:
            k = ease_out_cubic(t_rev / 0.45)
            img = niv[min(len(niv) - 1, int(round(k * (len(niv) - 1))))]
            esc = 1 + 0.08 * math.sin(clamp(t_rev / 0.35) * math.pi)
        colar_centro(canvas, img, IMG_CX, IMG_CY, escala=esc)
        if t_rev < 0.15:  # selo "?" sobre a imagem borrada
            sel = _cache_layer("selo_borrado", lambda: texto_layer("?", 170, cor=(255, 205, 0), contorno=12, sombra=10))
            op = 1 - clamp(t_rev / 0.15) if t_rev > 0 else 1
            pul = 1 + 0.06 * math.sin(max(0, t) * 2 * math.pi * 1.2)
            colar_centro(canvas, sel, IMG_CX, IMG_CY, escala=zi * pul, opacidade=op, angulo=8)
    elif t_rev < 0:
        colar_centro(canvas, P.img_q, IMG_CX, IMG_CY, escala=zi)
    else:
        k = t_rev / 0.24
        if k < 0.5:
            img, sx = P.img_q, 1 - k * 2
        else:
            img, sx = P.img_r, (k - 0.5) * 2 if k < 1 else 1.0
        if sx < 0.999:
            nw = max(1, int(img.width * sx))
            img = img.resize((nw, img.height), Image.BILINEAR)
        colar_centro(canvas, img, IMG_CX, IMG_CY)

    # --- botões em cascata (slide + fade, 0.1s entre eles)
    for i in range(4):
        ti = (t - 0.45 - i * 0.1) / 0.28
        if ti <= 0:
            continue
        e = ease_out_cubic(ti)
        x = BTN_X0 - 14 - (1 - e) * 220
        y = BTN_Y0 + i * (BTN_H + BTN_GAP) - 14
        op = e
        layer = P.botoes[i]
        if t_rev >= 0:
            if i == P.correta:
                layer = P.botao_ok
                pulso = 1 + 0.05 * math.sin(clamp(t_rev / 0.4) * math.pi) + \
                    0.015 * math.sin(t_rev * 2 * math.pi * 2)
                colar_centro(canvas, layer, x + layer.width / 2, y + layer.height / 2, escala=pulso)
                continue
            op = lerp(1, 0.55, clamp(t_rev / 0.2))
        colar(canvas, com_opacidade(layer, op), x, y)

    # --- barra de tempo + logo andando
    t_tim = t - T_TEXTO
    aparece = ease_out_cubic((t - 0.7) / 0.3)
    if aparece > 0 and t_rev < 0.35:
        frac = 1 - clamp(t_tim / T_TIMER)
        sai = 1 - clamp(t_rev / 0.35) if t_rev > 0 else 1
        _barra(canvas, frac, aparece * sai, t_tim)
    return canvas


def _barra(canvas, frac, op, t_tim):
    bx0, bx1 = BAR_X0, BAR_X1
    layer = Image.new("RGBA", (bx1 - bx0 + 20, BAR_H + 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = BAR_H // 2
    d.rounded_rectangle((4, 10, layer.width - 5, 10 + BAR_H + 8), r + 4, fill=ESCURO)
    d.rounded_rectangle((4, 4, layer.width - 5, 4 + BAR_H + 8), r + 4, fill=(0, 0, 0, 150),
                        outline=ESCURO, width=5)
    fw = (layer.width - 18) * frac
    if fw > 2:
        c = cor_timer(frac)
        d.rounded_rectangle((9, 9, 9 + max(fw, BAR_H), 9 + BAR_H - 2), r, fill=c)
        d.rounded_rectangle((15, 13, 9 + max(fw, BAR_H) - 6, 13 + 7), 4,
                            fill=lerp_cor(c, BRANCO, 0.45))
    colar(canvas, com_opacidade(layer, op), bx0 - 10, BAR_Y - 4)
    # logo "andando" na ponta da barra
    lg = logo(84)
    passo = max(0.0, t_tim) * 2 * math.pi * 2.2
    bob = abs(math.sin(passo)) * 16
    ang = 9 * math.sin(passo)
    x = bx0 - 10 + 9 + fw
    colar_centro(canvas, lg, x, BAR_Y - 34 - bob, opacidade=op, angulo=ang)


def tela_final(t, dados, tg):
    fnl = dados["final"]
    canvas = raios((94, 43, 168), (70, 25, 135), tg * 35, n=20, centro=(W / 2, H * 0.4))
    canvas.alpha_composite(meio_tom())
    canvas.alpha_composite(vinheta_escura())

    titulo = _cache_layer(("f1", fnl["titulo"]), lambda: _titulo_final(fnl["titulo"]))
    z = ease_out_back(t / 0.35, 2.0)
    colar_centro(canvas, titulo, *POS_FINAL["titulo"], escala=z, angulo=-2)

    # emoji 👇 quicando
    e = emoji(fnl.get("titulo_emoji", ""), 150) if fnl.get("titulo_emoji") else None
    bounce = abs(math.sin(t * math.pi * 2.2)) * 40
    ze = ease_out_back((t - 0.25) / 0.3, 2.0)
    if e is not None:
        colar_centro(canvas, e, POS_FINAL["emoji"][0], POS_FINAL["emoji"][1] + bounce, escala=ze)
    else:
        colar_centro(canvas, _seta(), POS_FINAL["emoji"][0], POS_FINAL["emoji"][1] + bounce, escala=ze)

    # ícone de comentário pulsando
    bal = _cache_layer("balao", _balao)
    zb = ease_out_back((t - 0.45) / 0.35, 2.0) * (1 + 0.05 * math.sin(max(0, t - 0.8) * 7))
    colar_centro(canvas, bal, *POS_FINAL["balao"], escala=zb, angulo=4 * math.sin(t * 3))

    siga = _cache_layer(("siga", fnl["subtitulo"]), lambda: _faixa(fnl["subtitulo"], "", VERMELHO, 78))
    zs = ease_out_back((t - 0.8) / 0.35, 2.0)
    colar_centro(canvas, siga, *POS_FINAL["siga"], escala=zs)
    logo_canto(canvas)
    return canvas


def _titulo_final(texto):
    palavras = texto.split()
    meio = math.ceil(len(palavras) / 2)
    a = texto_layer(" ".join(palavras[:meio]), 130, contorno=13, sombra=11)
    b = texto_layer(" ".join(palavras[meio:]), 130, cor=(255, 205, 0), contorno=13, sombra=11)
    w = max(a.width, b.width)
    img = Image.new("RGBA", (w, a.height + b.height - 40), (0, 0, 0, 0))
    img.alpha_composite(a, ((w - a.width) // 2, 0))
    img.alpha_composite(b, ((w - b.width) // 2, a.height - 40))
    return img


def _seta():
    img = Image.new("RGBA", (160, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(55, 0), (105, 0), (105, 90), (150, 90), (80, 175), (10, 90), (55, 90)],
              fill=(255, 205, 0), outline=ESCURO, width=8)
    return img


def _balao():
    w, h = 300, 230
    img = Image.new("RGBA", (w + 20, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for off, cor in ((12, ESCURO), (0, BRANCO)):
        d.rounded_rectangle((10, 10 + off, 10 + w, 10 + 170 + off), 70, fill=cor, outline=ESCURO, width=9)
        d.polygon([(70, 160 + off), (150, 160 + off), (60, 230 + off)], fill=cor, outline=ESCURO)
    d.line([(70, 163), (150, 163)], fill=BRANCO, width=10)
    d.line([(72, 165), (60, 230)], fill=ESCURO, width=9)
    d.line([(150, 165), (60, 230)], fill=ESCURO, width=9)
    for i in range(3):
        cx = 10 + w / 2 + (i - 1) * 70
        d.ellipse((cx - 22, 95 - 22, cx + 22, 95 + 22), fill=VERMELHO, outline=ESCURO, width=5)
    return img


# ---------------------------------------------------------------------------
# Linha do tempo
# ---------------------------------------------------------------------------

def montar_timeline(dados, teste=False):
    perguntas = dados["perguntas"]
    if teste:
        perguntas = perguntas[:1]
    segs = []
    t = 0.0

    def add(tipo, dur, narr=(), **kw):
        """narr: lista de (arquivo, atraso dentro do segmento)."""
        nonlocal t
        narr = [(p, t + off) for p, off in narr if p]
        segs.append({"tipo": tipo, "ini": t, "dur": dur, "narr": narr, **kw})
        t += dur

    def dur(p):
        return duracao_audio(p) if p else 0.0

    n = achar_narracao("00_gancho")
    add("gancho", max(T_GANCHO, dur(n) + 0.25), [(n, 0.0)])
    nivel_atual = None
    for i, q in enumerate(perguntas):
        nv = q.get("nivel", "facil")
        if nv not in NIVEIS:
            raise ValueError(f"nível inválido na pergunta {i + 1}: {nv}")
        if nv != nivel_atual:
            n = achar_narracao(f"vinheta_{nv}")
            add("vinheta", max(T_VINHETA, dur(n) + 0.15), [(n, 0.03)], nivel=nv)
            nivel_atual = nv
        np_ = achar_narracao(f"p{i + 1}_pergunta")
        nr = achar_narracao(f"p{i + 1}_resposta")
        t_rev = T_TEXTO + T_TIMER
        add("pergunta", t_rev + max(T_REVELA, dur(nr) + 0.45),
            [(np_, 0.15), (nr, t_rev + 0.15)], idx=i)
    n = achar_narracao("99_final")
    add("final", max(T_FINAL, dur(n) + 0.5), [(n, 0.15)])
    return segs, t


def eventos_audio(segs):
    """(som, início, duração de loop ou None, volume). som = chave de SONS ou Path da narração."""
    ev = []
    for s in segs:
        if s["tipo"] == "gancho":
            ev.append(("pop", s["ini"] + 0.02, None, 0.55))
            ev.append(("whoosh", s["ini"], None, 0.45))
        elif s["tipo"] == "vinheta":
            ev.append(("whoosh", s["ini"], None, 0.65))
            ev.append(("pop", s["ini"] + 0.06, None, 0.35))
        elif s["tipo"] == "pergunta":
            ev.append(("pop", s["ini"] + 0.05, None, 0.4))
            for b in range(4):  # botões em cascata
                ev.append(("pop", s["ini"] + 0.5 + b * 0.1, None, 0.22))
            ev.append(("tique", s["ini"] + T_TEXTO, T_TIMER, 0.42))
            ev.append(("ding", s["ini"] + T_TEXTO + T_TIMER, None, 0.6))
        elif s["tipo"] == "final":
            ev.append(("whoosh", s["ini"], None, 0.45))
            ev.append(("pop", s["ini"] + 0.02, None, 0.5))
            ev.append(("pop", s["ini"] + 0.5, None, 0.3))
        for p, ini in s.get("narr", []):
            ev.append((p, ini, None, 1.0))
    return ev


# ---------------------------------------------------------------------------
# Render (multiprocesso)
# ---------------------------------------------------------------------------

_W_DADOS = None
_W_SEGS = None
_W_FPS = 60


def _init_worker(dados, segs, fps, projeto=None, formato="vertical"):
    global _W_DADOS, _W_SEGS, _W_FPS, PROJETO
    _W_DADOS, _W_SEGS, _W_FPS, PROJETO = dados, segs, fps, projeto
    configurar_formato(formato)


def render_tempo(tg, dados, segs) -> Image.Image:
    seg = segs[-1]
    for s in segs:
        if tg < s["ini"] + s["dur"]:
            seg = s
            break
    t = tg - seg["ini"]
    tipo = seg["tipo"]
    if tipo == "gancho":
        return tela_gancho(t, dados, tg)
    if tipo == "vinheta":
        return tela_vinheta(t, seg["nivel"], tg, seg["dur"])
    if tipo == "pergunta":
        return tela_pergunta(t, dados["perguntas"][seg["idx"]], seg["idx"], tg)
    return tela_final(t, dados, tg)


def _render_frame(i):
    img = render_tempo(i / _W_FPS, _W_DADOS, _W_SEGS)
    return img.convert("RGB").tobytes()


def achar_som(chave):
    nome = SONS[chave]
    for ext in EXT_AUDIO:
        p = ASSETS / "sons" / (nome + ext)
        if p.exists():
            return p
    return None


def mixar_audio(video_mudo: Path, saida: Path, segs, total):
    disponiveis = {k: achar_som(k) for k in SONS}
    faltando = [SONS[k] for k, v in disponiveis.items() if v is None]
    tem_narr = any(isinstance(e[0], Path) for e in eventos_audio(segs))
    if all(v is None for v in disponiveis.values()) and not tem_narr:
        shutil.move(str(video_mudo), saida)
        return faltando

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_mudo)]
    filtros, rotulos, narr = [], [], []
    n_in = 1
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    for k, (som, ini, dur, vol) in enumerate(eventos_audio(segs)):
        p = som if isinstance(som, Path) else disponiveis.get(som)
        if p is None:
            continue
        if dur:
            cmd += ["-stream_loop", "-1", "-i", str(p)]
            trim = f"atrim=0:{dur},afade=t=out:st={max(0, dur - 0.15)}:d=0.15,"
        else:
            cmd += ["-i", str(p)]
            trim = ""
        ms = int(ini * 1000)
        filtros.append(f"[{n_in}:a]{fmt},{trim}volume={vol},adelay={ms}:all=1[a{k}]")
        (narr if isinstance(som, Path) else rotulos).append(f"[a{k}]")
        n_in += 1
    if narr:
        filtros.append(f"{''.join(narr)}amix=inputs={len(narr)}:normalize=0:duration=longest,"
                       f"apad,atrim=0:{total},asplit=2[narr][chave]")
        rotulos.append("[narr]")
    if disponiveis.get("musica"):
        cmd += ["-stream_loop", "-1", "-i", str(disponiveis["musica"])]
        filtros.append(f"[{n_in}:a]{fmt},atrim=0:{total},volume=0.38,"
                       f"afade=t=in:d=0.4,afade=t=out:st={total - 1.5}:d=1.5[mus0]")
        if narr:  # ducking: a música abaixa enquanto a narração fala
            filtros.append("[mus0][chave]sidechaincompress=threshold=0.02:ratio=8:attack=15:"
                           "release=350:makeup=1[mus]")
        else:
            filtros.append("[mus0]anull[mus]")
        rotulos.append("[mus]")
        n_in += 1
    elif narr:
        filtros.append("[chave]anullsink")
    filtros.append(f"{''.join(rotulos)}amix=inputs={len(rotulos)}:normalize=0:duration=longest,"
                   f"alimiter=limit=0.95,apad,atrim=0:{total}[aout]")
    cmd += ["-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(saida)]
    subprocess.run(cmd, check=True)
    video_mudo.unlink(missing_ok=True)
    return faltando


def renderizar(dados, saida: Path, fps=60, teste=False, procs=None):
    segs, total = montar_timeline(dados, teste)
    n = int(round(total * fps))
    saida.parent.mkdir(parents=True, exist_ok=True)
    mudo = saida.with_name(saida.stem + ".mudo.mp4")
    print(f"Renderizando {n} frames ({total:.1f}s @ {fps}fps) -> {saida}")
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(mudo)],
        stdin=subprocess.PIPE)
    t0 = time.time()
    procs = procs or max(1, (os.cpu_count() or 2))
    with Pool(procs, initializer=_init_worker, initargs=(dados, segs, fps, PROJETO, FORMATO)) as pool:
        lote = procs * 6  # lotes limitados: evita acumular frames na memória
        feitos = 0
        for ini in range(0, n, lote):
            for buf in pool.map(_render_frame, range(ini, min(n, ini + lote)), chunksize=2):
                ff.stdin.write(buf)
            feitos = min(n, ini + lote)
            el = time.time() - t0
            print(f"\r  {feitos}/{n} frames  ({feitos / max(el, 1e-6):.1f} fps)", end="", flush=True)
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg falhou ao codificar o vídeo")
    print(f"\n  vídeo codificado em {time.time() - t0:.0f}s")
    faltando = mixar_audio(mudo, saida, segs, total)
    if faltando:
        todos = len(faltando) == len(SONS) and not any(s["narr"] for s in segs)
        print("\n⚠️  AVISO: arquivos de som não encontrados em assets/sons/: "
              + ", ".join(f"{f}.(mp3|wav|ogg)" for f in faltando))
        print("   " + ("O vídeo foi gerado SEM SOM." if todos else
                      "O vídeo foi gerado sem esses sons (narração e demais sons foram mixados)."))
    print(f"Pronto: {saida}")


def previa(dados, pasta: Path):
    """Exporta um frame de cada tipo de tela + uma folha de contato."""
    pasta.mkdir(parents=True, exist_ok=True)
    segs, _ = montar_timeline(dados)
    primeira = next(s for s in segs if s["tipo"] == "pergunta")
    vinhetas = [s for s in segs if s["tipo"] == "vinheta"]
    alvos = [("01_gancho", segs[0]["ini"] + 1.4)]
    for k, v in enumerate(vinhetas):
        alvos.append((f"02{chr(97 + k)}_vinheta_{v['nivel']}", v["ini"] + 0.45))
    alvos += [
        ("03_pergunta_digitando", primeira["ini"] + 0.55),
        ("04_pergunta_cronometro", primeira["ini"] + T_TEXTO + 2.6),
        ("05_revelacao", primeira["ini"] + T_TEXTO + T_TIMER + 0.8),
        ("06_final", segs[-1]["ini"] + 2.0),
    ]
    imgs = []
    for nome, tg in alvos:
        img = render_tempo(tg, dados, segs).convert("RGB")
        img.save(pasta / f"{nome}.png")
        imgs.append((nome, img))
        print(f"  {pasta / (nome + '.png')}")
    # folha de contato
    tw, th = (270, 480) if H > W else (480, 270)
    cols = 4
    rows = math.ceil(len(imgs) / cols)
    folha = Image.new("RGB", (cols * (tw + 20) + 20, rows * (th + 70) + 20), (30, 30, 30))
    d = ImageDraw.Draw(folha)
    for k, (nome, img) in enumerate(imgs):
        x = 20 + (k % cols) * (tw + 20)
        y = 20 + (k // cols) * (th + 70)
        folha.paste(img.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 10), nome, font=fonte(22), fill=BRANCO)
    folha.save(pasta / "00_folha_de_contato.png")
    print(f"  {pasta / '00_folha_de_contato.png'}")


def verificar_ambiente():
    if not shutil.which("ffmpeg"):
        sys.exit("ERRO: ffmpeg não encontrado no PATH.")
    if not FONTE.exists():
        sys.exit(f"ERRO: fonte não encontrada: {FONTE}")
    if _fonte_emoji() is None:
        print("aviso: nenhuma fonte de emoji colorida encontrada; emojis serão omitidos.")


def main():
    ap = argparse.ArgumentParser(description="Gerador de vídeos de quiz 9:16")
    ap.add_argument("--projeto", default=None,
                    help="pasta do vídeo (ex.: videos/01_animais) com perguntas.json, narracao/ e imagens/")
    ap.add_argument("--json", default=None)
    ap.add_argument("--formato", choices=["vertical", "horizontal"], default=None,
                    help="padrão: campo 'formato' do JSON, ou vertical")
    ap.add_argument("--saida", default=None)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--teste", action="store_true", help="vídeo curto: gancho + 1 pergunta + final")
    ap.add_argument("--previa", action="store_true", help="exporta 1 frame de cada tela em saida/previa")
    ap.add_argument("--procs", type=int, default=None)
    a = ap.parse_args()

    global PROJETO
    verificar_ambiente()
    nome = "quiz"
    if a.projeto:
        PROJETO = Path(a.projeto).resolve()
        nome = PROJETO.name
    json_path = a.json or (PROJETO / "perguntas.json" if PROJETO else BASE / "perguntas.json")
    with open(json_path, encoding="utf-8") as f:
        dados = json.load(f)
    configurar_formato(a.formato or dados.get("formato", "vertical"))

    if a.previa:
        previa(dados, BASE / "saida" / ("previa" if not PROJETO else f"previa_{nome}"))
        return
    saida = Path(a.saida) if a.saida else BASE / "saida" / (f"{nome}_teste.mp4" if a.teste else f"{nome}.mp4")
    renderizar(dados, saida, fps=a.fps, teste=a.teste, procs=a.procs)


if __name__ == "__main__":
    main()
