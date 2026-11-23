#!/usr/bin/env python3
"""Ilustrações de resposta dos vídeos em videos/<nome>/imagens/pN_resposta.png.

Mistura emojis vetoriais do Noto Emoji (assets/emoji, Apache 2.0) com efeito de adesivo
e desenhos próprios (bandeiras, planetas), no mesmo estilo cartoon do gerar_imagens.py.

Uso: python gerar_imagens_lote.py [01_animais ...]
"""

from __future__ import annotations

import io
import math
import sys
from functools import lru_cache
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFilter

from gerar_imagens import BR, ESC, H, OUT, S, W, brilho, f, faixa, grad

BASE = Path(__file__).resolve().parent
EMOJI = BASE / "assets" / "emoji"

EMO = {
    "baleia": "1f40b", "polvo": "1f419", "coracao": "2764", "leopardo": "1f406", "morcego": "1f987",
    "coala": "1f428", "zzz": "1f4a4", "croissant": "1f950", "montanha": "1f3d4", "igreja": "26ea",
    "canguru": "1f998", "predio": "1f3db", "trofeu": "1f3c6", "bola": "26bd", "estrela": "2b50",
    "pergaminho": "1f4dc", "arvore": "1f333", "arara": "1f99c", "coracao_real": "1fac0", "dente": "1f9b7",
    "mao": "270b", "osso": "1f9b4", "orelha": "1f442", "sol": "2600", "fogo": "1f525",
    "termometro": "1f321", "onda": "1f30a", "lua": "1f319", "vento": "1f4a8", "chave": "1f5dd",
    "calendario": "1f4c5", "leao": "1f981", "arcoiris": "1f308", "balao": "1f4ac", "triangulo": "1f53a",
    "diamante": "1f48e", "elefante": "1f418", "despertador": "23f0", "lua_cheia": "1f315", "africa": "1f30d",
    "formiga": "1f41c", "gota": "1f4a7", "quadro": "1f5bc", "paleta": "1f3a8", "pulmoes": "1fac1",
    "bordo": "1f341", "camisa": "1f455", "livro": "1f4d6", "pena": "2712", "camelo": "1f42a",
    "deserto": "1f3dc", "pizza": "1f355", "saturno": "1fa90", "iene": "1f4b4", "foguete": "1f680",
    "astronauta": "1f468_200d_1f680", "piano": "1f3b9", "atomo": "269b", "ilha": "1f3dd", "peixe": "1f41f",
    "tijolo": "1f9f1", "martelo": "1f528", "kiwi": "1f95d", "ovelha": "1f411", "tubo": "1f9ea",
    "cachalote": "1f433", "cerebro": "1f9e0", "canoa": "1f6f6", "seta_baixo": "2b07", "mergulho": "1f93f",
}


@lru_cache(maxsize=128)
def emoji(nome: str, tam: int) -> Image.Image:
    png = cairosvg.svg2png(url=str(EMOJI / f"emoji_u{EMO[nome]}.svg"), output_width=tam, output_height=tam)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def adesivo(img: Image.Image, borda=14, contorno=6) -> Image.Image:
    """Borda branca + contorno escuro + sombra, como um adesivo."""
    pad = borda + contorno + 20
    base = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    base.alpha_composite(img, (pad, pad))
    a = base.getchannel("A").point(lambda v: 255 if v > 40 else 0)

    def dilatar(m, r):  # dilatação arredondada (blur + limiar)
        return m.filter(ImageFilter.GaussianBlur(r * 0.6)).point(lambda v: 255 if v > 12 else 0) \
            .filter(ImageFilter.GaussianBlur(1))
    a1 = dilatar(a, borda)
    a2 = dilatar(a1, contorno)
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sombra.putalpha(a2.point(lambda v: v * 90 // 255))
    out.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(6)), (0, 10))
    escuro = Image.new("RGBA", base.size, ESC + (255,))
    escuro.putalpha(a2)
    out.alpha_composite(escuro)
    branco = Image.new("RGBA", base.size, BR + (255,))
    branco.putalpha(a1)
    out.alpha_composite(branco)
    out.alpha_composite(base)
    return out


def por(img, el, cx, cy, ang=0):
    if ang:
        el = el.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(el, (int(cx - el.width / 2), int(cy - el.height / 2)))


def girar_matiz(img: Image.Image, graus: float) -> Image.Image:
    a = img.getchannel("A")
    h, s_, v = img.convert("RGB").convert("HSV").split()
    h = h.point(lambda x: int(x + graus * 255 / 360) % 256)
    out = Image.merge("HSV", (h, s_, v)).convert("RGBA")
    out.putalpha(a)
    return out


def emo(img, nome, cx, cy, tam, ang=0, sticker=True, matiz=0):
    e = emoji(nome, tam)
    if matiz:
        e = girar_matiz(e, matiz)
    por(img, adesivo(e) if sticker else e, cx, cy, ang)


def fundo(c1, c2, raios=True, cor_raio=None):
    img = grad(c1, c2)
    if raios:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        cx, cy = W / 2, H * 0.58
        cor = cor_raio or (255, 255, 255, 28)
        for i in range(16):
            a0 = i * math.pi / 8
            d.polygon([(cx, cy), (cx + 1500 * math.cos(a0), cy + 1500 * math.sin(a0)),
                       (cx + 1500 * math.cos(a0 + math.pi / 16), cy + 1500 * math.sin(a0 + math.pi / 16))], fill=cor)
        img.alpha_composite(lay)
    return img


def numero(img, txt, cx, cy, tam=150, cor=(255, 205, 0)):
    d = ImageDraw.Draw(img)
    d.text((cx, cy + 10 * S), txt, font=f(tam * S), fill=ESC, anchor="mm", stroke_width=9 * S, stroke_fill=ESC)
    d.text((cx, cy), txt, font=f(tam * S), fill=cor, anchor="mm", stroke_width=9 * S, stroke_fill=ESC)


def estrelinhas(img, pts, cor=(255, 245, 190)):
    d = ImageDraw.Draw(img)
    for x, y, r in pts:
        brilho(d, x, y, r, cor)


# ---------------------------------------------------------------------------
# Desenhos próprios
# ---------------------------------------------------------------------------

def bandeira(tipo, w=520, h=350, ang=-4) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tipo == "russia":
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 43, 30)]):
            d.rectangle((0, i * h / 3, w, (i + 1) * h / 3), fill=c)
    elif tipo == "franca":
        for i, c in enumerate([(0, 85, 164), (255, 255, 255), (239, 65, 53)]):
            d.rectangle((i * w / 3, 0, (i + 1) * w / 3, h), fill=c)
    elif tipo == "vaticano":
        d.rectangle((0, 0, w / 2, h), fill=(255, 225, 0))
        d.rectangle((w / 2, 0, w, h), fill=BR)
        cx, cy = w * 0.75, h * 0.5
        for ang_ in (35, -35):  # chaves cruzadas simplificadas
            r = math.radians(ang_)
            dx, dy = math.sin(r) * 95, -math.cos(r) * 95
            d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=(200, 160, 0), width=16)
            d.ellipse((cx + dx - 22, cy + dy - 22, cx + dx + 22, cy + dy + 22), outline=(200, 160, 0), width=12)
        d.polygon([(cx - 40, cy - 120), (cx + 40, cy - 120), (cx + 30, cy - 70), (cx - 30, cy - 70)], fill=(220, 170, 0))
    elif tipo == "brasil":
        d.rectangle((0, 0, w, h), fill=(0, 155, 58))
        m = 34
        d.polygon([(w / 2, m), (w - m, h / 2), (w / 2, h - m), (m, h / 2)], fill=(255, 223, 0))
        r = h * 0.27
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=(0, 39, 118))
        faixa_ = Image.new("L", (w, h), 0)
        ImageDraw.Draw(faixa_).arc((w / 2 - r * 2.2, h / 2 - r * 0.6, w / 2 + r * 2.2, h / 2 + r * 3.6), 235, 305,
                                   fill=255, width=int(r * 0.22))
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=255)
        branco = Image.new("RGBA", (w, h), BR + (255,))
        img.paste(branco, (0, 0), Image.composite(faixa_, Image.new("L", (w, h), 0), mask))
        d = ImageDraw.Draw(img)
        for x, y in [(-0.4, 0.3), (-0.1, 0.45), (0.2, 0.35), (0.45, 0.1), (0.0, 0.7), (-0.55, -0.05), (0.3, 0.62)]:
            sx, sy = w / 2 + x * r, h / 2 + y * r
            d.ellipse((sx - 5, sy - 5, sx + 5, sy + 5), fill=BR)
    elif tipo == "italia":
        for i, c in enumerate([(0, 146, 70), (255, 255, 255), (206, 43, 55)]):
            d.rectangle((i * w / 3, 0, (i + 1) * w / 3, h), fill=c)
    elif tipo == "turquia":
        d.rectangle((0, 0, w, h), fill=(227, 10, 23))
        cx, cy, r = w * 0.4, h / 2, h * 0.27
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BR)
        r2 = r * 0.8
        d.ellipse((cx - r2 + r * 0.25, cy - r2, cx + r2 + r * 0.25, cy + r2), fill=(227, 10, 23))
        sx, sy, sr = w * 0.6, h / 2, h * 0.11
        d.polygon([(sx + sr * math.cos(math.radians(a_ * 72)), sy + sr * math.sin(math.radians(a_ * 72))) if k == 0 else
                   (sx + sr * 0.4 * math.cos(math.radians(a_ * 72 + 36)), sy + sr * 0.4 * math.sin(math.radians(a_ * 72 + 36)))
                   for a_ in range(5) for k in (0, 1)], fill=BR)
    elif tipo == "suecia":
        d.rectangle((0, 0, w, h), fill=(0, 106, 167))
        t = h * 0.2
        d.rectangle((w * 0.3, 0, w * 0.3 + t, h), fill=(254, 204, 0))
        d.rectangle((0, h / 2 - t / 2, w, h / 2 + t / 2), fill=(254, 204, 0))
    # contorno, ondulação leve e sombra
    borda = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    ImageDraw.Draw(borda).rounded_rectangle((0, 0, w + 23, h + 23), 22, fill=ESC)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=255)
    borda.paste(img, (12, 12), mask)
    brilho_ = Image.new("RGBA", borda.size, (0, 0, 0, 0))
    db = ImageDraw.Draw(brilho_)
    for i in range(0, w, 6):
        k = math.sin(i / w * math.pi * 2.2)
        db.line([(12 + i, 12), (12 + i, 12 + h)], fill=(255, 255, 255, int(30 + 30 * k)) if k > 0 else (0, 0, 0, int(-40 * k)))
    m2 = Image.new("L", borda.size, 0)
    m2.paste(mask, (12, 12))
    brilho_.putalpha(Image.composite(brilho_.getchannel("A"), Image.new("L", borda.size, 0), m2))
    borda.alpha_composite(brilho_)
    return borda.rotate(ang, resample=Image.BICUBIC, expand=True)


def planeta(r, cores, faixas=0, anel=False, crateras=0, mancha=False, sombra=True, brilho_sol=False) -> Image.Image:
    t = int(r * 2 + 40 + (r * 1.6 if anel else 0))
    img = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = t / 2
    corpo = Image.new("RGBA", (t, t), (0, 0, 0, 0))
    dc = ImageDraw.Draw(corpo)
    dc.ellipse((c - r, c - r, c + r, c + r), fill=cores[0])
    for i in range(faixas):
        y = c - r + (i + 0.6) * 2 * r / (faixas + 0.4)
        dc.rectangle((c - r, y, c + r, y + r * 0.16), fill=cores[1 + i % (len(cores) - 1)])
    if mancha:
        dc.ellipse((c + r * 0.1, c + r * 0.2, c + r * 0.55, c + r * 0.45), fill=(200, 90, 60))
    for i in range(crateras):
        a = i * 2.4
        rr = r * (0.1 + 0.05 * (i % 3))
        x, y = c + math.cos(a) * r * 0.5, c + math.sin(a * 1.3) * r * 0.5
        dc.ellipse((x - rr, y - rr, x + rr, y + rr), fill=cores[-1])
    # sombra lateral
    sh = Image.new("L", (t, t), 0)
    ImageDraw.Draw(sh).ellipse((c - r * 0.6, c - r * 1.25, c + r * 1.9, c + r * 1.25), fill=80)
    m = Image.new("L", (t, t), 0)
    ImageDraw.Draw(m).ellipse((c - r, c - r, c + r, c + r), fill=255)
    escuro = Image.new("RGBA", (t, t), (0, 0, 0, 255))
    escuro.putalpha(Image.composite(sh.filter(ImageFilter.GaussianBlur(r * 0.15)), Image.new("L", (t, t), 0), m))
    if sombra:
        corpo.alpha_composite(escuro)
    corpo.putalpha(Image.composite(corpo.getchannel("A"), Image.new("L", (t, t), 0), m))
    if brilho_sol:
        g = Image.new("RGBA", (t, t), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((c - r - 20, c - r - 20, c + r + 20, c + r + 20), fill=(255, 220, 80, 160))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(corpo)
    d = ImageDraw.Draw(img)
    d.ellipse((c - r, c - r, c + r, c + r), outline=ESC, width=OUT)
    d.arc((c - r * 0.75, c - r * 0.75, c + r * 0.75, c + r * 0.75), 200, 245, fill=(255, 255, 255), width=max(4, int(r * 0.07)))
    return img


def sistema_solar(img):
    d = ImageDraw.Draw(img)
    sol = planeta(110, [(255, 210, 50), (255, 180, 30)], sombra=False, brilho_sol=True)
    por(img, sol, -30, H * 0.6)
    specs = [(18, [(170, 160, 150), (120, 110, 100)]), (28, [(235, 190, 110)]), (30, [(40, 130, 230)]),
             (22, [(220, 90, 50)]), (62, [(220, 170, 120), (190, 120, 80), (240, 210, 170)]),
             (52, [(235, 210, 140), (210, 180, 110)]), (38, [(140, 220, 230)]), (36, [(60, 100, 230)])]
    x = 95
    for i, (r, cores) in enumerate(specs):
        r = int(r * 1.25)
        x += r + 12
        y = H * 0.58 + 14 * math.sin(i * 1.2)
        if i == 5:
            d = ImageDraw.Draw(img)
            d.ellipse((x - r * 1.9, y - r * 0.5, x + r * 1.9, y + r * 0.5), outline=ESC, width=14)
            d.ellipse((x - r * 1.9, y - r * 0.5, x + r * 1.9, y + r * 0.5), outline=(240, 220, 160), width=7)
        por(img, planeta(r, cores + [cores[-1]], faixas=4 if r > 45 else 0), x, y)
        d = ImageDraw.Draw(img)
        d.ellipse((x - 24, y + r + 16, x + 24, y + r + 64), fill=(255, 205, 0), outline=ESC, width=5)
        d.text((x, y + r + 41), str(i + 1), font=f(18 * S), fill=ESC, anchor="mm")
        x += r + 12


# ---------------------------------------------------------------------------
# Cenas por vídeo
# ---------------------------------------------------------------------------

def v1(i):
    if i == 1:
        img = fundo((90, 190, 250), (20, 90, 190))
        emo(img, "onda", 180, 600, 170, -8)
        emo(img, "onda", 960, 610, 150, 8)
        emo(img, "baleia", W / 2, H * 0.6, 400)
        return img, "BALEIA-AZUL"
    if i == 2:
        img = fundo((255, 150, 170), (190, 60, 110))
        emo(img, "polvo", W / 2, H * 0.62, 340)
        for k, (x, y) in enumerate([(220, 360), (900, 340), (W / 2 + 10, 270)]):
            emo(img, "coracao", x, y + 80, 130, (-1) ** k * 12)
        return img, "3 CORAÇÕES"
    if i == 3:
        img = fundo((255, 210, 110), (230, 130, 40))
        d = ImageDraw.Draw(img)
        for y in (390, 470, 550, 630):  # linhas de velocidade
            d.rounded_rectangle((70, y, 70 + 260 + (y % 3) * 40, y + 18), 9, fill=(255, 255, 255, 200))
        emo(img, "leopardo", W / 2 + 90, H * 0.62, 380)
        return img, "GUEPARDO"
    if i == 4:
        img = fundo((60, 50, 120), (20, 15, 55), cor_raio=(255, 255, 255, 14))
        estrelinhas(img, [(120, 330, 14), (980, 300, 18), (880, 650, 12), (200, 620, 16), (1030, 520, 10)])
        emo(img, "lua", 880, 430, 220, 0)
        emo(img, "morcego", W / 2 - 60, H * 0.6, 360, -6)
        return img, "MORCEGO"
    img = fundo((150, 220, 150), (60, 150, 90))
    emo(img, "arvore", 230, 520, 330)
    emo(img, "coala", W / 2 + 90, H * 0.62, 340)
    emo(img, "zzz", W / 2 + 330, 330, 150, 10)
    return img, "COALA"


def v2(i):
    if i == 1:
        img = fundo((150, 210, 255), (70, 140, 220))
        por(img, bandeira("russia"), W / 2, H * 0.6)
        return img, "RÚSSIA"
    if i == 2:
        img = fundo((255, 200, 220), (220, 120, 170))
        por(img, bandeira("franca", 460, 310, 5), W / 2 - 80, H * 0.6)
        emo(img, "croissant", W / 2 + 280, H * 0.72, 220, -10)
        return img, "PARIS"
    if i == 3:
        img = fundo((170, 220, 255), (90, 160, 230))
        emo(img, "montanha", W / 2, H * 0.62, 430)
        d = ImageDraw.Draw(img)
        fx, fy = W / 2 + 10, 250
        d.line([(fx, fy), (fx, fy + 120)], fill=ESC, width=10)
        d.polygon([(fx, fy), (fx + 90, fy + 25), (fx, fy + 50)], fill=(230, 40, 40), outline=ESC, width=6)
        return img, "EVEREST"
    if i == 4:
        img = fundo((255, 240, 170), (240, 190, 70))
        por(img, bandeira("vaticano", 440, 300, -5), W / 2 - 110, H * 0.6)
        emo(img, "igreja", W / 2 + 300, H * 0.62, 240, 6)
        return img, "VATICANO"
    img = fundo((255, 180, 120), (220, 100, 60))
    emo(img, "predio", W / 2 - 170, H * 0.62, 300, -4)
    emo(img, "canguru", W / 2 + 200, H * 0.6, 340, 4)
    return img, "CANBERRA"


def v3(i):
    if i == 1:
        img = fundo((140, 215, 255), (60, 150, 230))
        emo(img, "predio", W / 2, H * 0.6, 380)
        return img, "BRASÍLIA"
    if i == 2:
        img = fundo((60, 190, 100), (10, 120, 60))
        for k in range(5):
            x = W / 2 + (k - 2) * 200
            emo(img, "trofeu", x, H * 0.6 + (30 if k % 2 else 0), 170, (k - 2) * 5)
        emo(img, "bola", W - 150, 280, 120)
        return img, "5 COPAS"
    if i == 3:
        img = fundo((60, 120, 220), (20, 50, 140))
        por(img, bandeira("brasil", 460, 320, -4), W / 2 - 120, H * 0.6)
        numero(img, "27", W / 2 + 320, H * 0.52, 130)
        emo(img, "estrela", W / 2 + 320, H * 0.8, 110, 10, sticker=True)
        return img, "27 ESTRELAS"
    if i == 4:
        img = fundo((255, 230, 150), (230, 170, 60))
        por(img, bandeira("brasil", 380, 260, 6), W / 2 + 230, H * 0.6)
        emo(img, "pergaminho", W / 2 - 220, H * 0.6, 300, -8)
        return img, "1822"
    img = fundo((110, 200, 120), (20, 110, 60))
    emo(img, "arvore", 250, H * 0.62, 320, -4)
    emo(img, "arvore", 880, H * 0.66, 280, 4)
    emo(img, "arara", W / 2, H * 0.6, 300)
    return img, "AMAZONAS"


def v4(i):
    if i == 1:
        img = fundo((255, 160, 160), (200, 50, 70))
        emo(img, "coracao_real", W / 2, H * 0.6, 380)
        return img, "CORAÇÃO"
    if i == 2:
        img = fundo((170, 230, 255), (80, 170, 230))
        emo(img, "dente", W / 2 - 200, H * 0.62, 320, -8)
        numero(img, "32", W / 2 + 230, H * 0.62, 190)
        return img, "32 DENTES"
    if i == 3:
        img = fundo((255, 215, 180), (230, 150, 110))
        emo(img, "mao", W / 2, H * 0.62, 380, 6)
        return img, "PELE"
    if i == 4:
        img = fundo((200, 200, 240), (110, 110, 190))
        emo(img, "osso", W / 2 - 220, H * 0.62, 300, -20)
        numero(img, "206", W / 2 + 220, H * 0.62, 170)
        return img, "206 OSSOS"
    img = fundo((255, 220, 170), (230, 160, 90))
    emo(img, "orelha", W / 2 - 150, H * 0.6, 360, -5)
    d = ImageDraw.Draw(img)
    # estribo (desenho simplificado) dentro de um círculo de zoom
    cx, cy, r = W / 2 + 240, H * 0.55, 150
    d.line([(W / 2 - 100, H * 0.55), (cx - r, cy)], fill=ESC, width=8)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BR, outline=ESC, width=OUT)
    d.polygon([(cx - 70, cy + 70), (cx + 70, cy + 70), (cx + 55, cy + 85), (cx - 55, cy + 85)], fill=(240, 225, 200), outline=ESC, width=6)
    d.line([(cx - 60, cy + 70), (cx - 15, cy - 70)], fill=ESC, width=22)
    d.line([(cx + 60, cy + 70), (cx + 15, cy - 70)], fill=ESC, width=22)
    d.line([(cx - 60, cy + 70), (cx - 15, cy - 70)], fill=(240, 225, 200), width=12)
    d.line([(cx + 60, cy + 70), (cx + 15, cy - 70)], fill=(240, 225, 200), width=12)
    d.ellipse((cx - 32, cy - 100, cx + 32, cy - 55), fill=(240, 225, 200), outline=ESC, width=6)
    return img, "ESTRIBO"


def v5(i):
    ceu = ((30, 25, 80), (10, 10, 35))
    pts = [(90, 300, 10), (1030, 280, 14), (950, 690, 9), (160, 680, 12), (600, 690, 8), (300, 260, 7), (840, 240, 8)]
    if i == 1:
        img = fundo(*ceu, cor_raio=(255, 255, 255, 12))
        estrelinhas(img, pts)
        por(img, planeta(230, [(225, 175, 120), (190, 120, 80), (240, 210, 170), (170, 100, 70)], faixas=6, mancha=True),
            W / 2, H * 0.6)
        return img, "JÚPITER"
    if i == 2:
        img = fundo(*ceu, cor_raio=(255, 255, 255, 12))
        estrelinhas(img, pts)
        por(img, planeta(220, [(225, 90, 50), (190, 60, 35)], crateras=7), W / 2, H * 0.6)
        return img, "MARTE"
    if i == 3:
        img = fundo((60, 30, 70), (20, 10, 30), cor_raio=(255, 200, 100, 18))
        por(img, planeta(330, [(255, 205, 50), (255, 170, 30)], sombra=False, brilho_sol=True), 60, H * 0.6)
        por(img, planeta(110, [(170, 160, 150), (110, 100, 95)], crateras=5), W / 2 + 160, H * 0.6)
        return img, "MERCÚRIO"
    if i == 4:
        img = fundo(*ceu, raios=False)
        estrelinhas(img, pts)
        sistema_solar(img)
        return img, "8 PLANETAS"
    img = fundo((120, 40, 30), (40, 10, 20), cor_raio=(255, 150, 50, 22))
    estrelinhas(img, pts, (255, 220, 160))
    por(img, planeta(210, [(245, 205, 120), (235, 180, 95)], crateras=0), W / 2 - 70, H * 0.6)
    d = ImageDraw.Draw(img)
    for k, (dx, dy, a0, a1) in enumerate([(-60, -60, 190, 300), (40, 30, 200, 330), (-20, 110, 180, 290)]):
        cx_, cy_ = W / 2 - 70 + dx, H * 0.6 + dy
        d.arc((cx_ - 110, cy_ - 40, cx_ + 110, cy_ + 40), a0, a1, fill=(255, 235, 180), width=10)
    emo(img, "fogo", W / 2 + 230, H * 0.5, 170, 10)
    emo(img, "termometro", W / 2 + 300, H * 0.75, 140, -12)
    return img, "VÊNUS"


def urano():
    p = planeta(170, [(150, 225, 235), (120, 200, 215)])
    lay = Image.new("RGBA", (p.width + 60, p.height + 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = lay.width / 2, lay.height / 2
    anel = (cx - 105, cy - 270, cx + 105, cy + 270)
    d.ellipse(anel, outline=ESC, width=22)
    d.ellipse(anel, outline=(200, 240, 250), width=10)
    lay.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))
    d = ImageDraw.Draw(lay)  # parte da frente do anel
    d.arc(anel, -60, 60, fill=ESC, width=22)
    d.arc(anel, -60, 60, fill=(200, 240, 250), width=10)
    return lay.rotate(-8, resample=Image.BICUBIC, expand=True)


def v6(i):
    ceu = ((30, 25, 80), (10, 10, 35))
    pts = [(90, 300, 10), (1030, 280, 14), (950, 690, 9), (160, 680, 12), (600, 700, 8), (300, 260, 7), (840, 240, 8)]
    X, Y = W / 2, H * 0.62
    cenas = {
        1: (((255, 200, 120), (230, 120, 60)), [("sol", X - 330, Y, 220, 0)], ("366", X + 110, Y, 180), "366 DIAS"),
        2: (((255, 210, 110), (220, 130, 40)), [("leao", X, Y, 380, 0)], None, "LEÃO"),
        3: (((140, 210, 255), (70, 140, 230)), [("arcoiris", X, Y, 420, 0)], None, "7 CORES"),
        4: (((120, 210, 140), (40, 140, 80)), [("balao", X + 300, Y - 60, 200, 8)], None, "PORTUGUÊS"),
        5: (((255, 190, 200), (220, 100, 130)), [], ("3", X + 230, Y, 220), "3 LADOS"),
        6: (((150, 230, 170), (40, 150, 90)), [("diamante", X, Y, 360, 0, 275)], None, "VERDE"),
        7: (((220, 230, 200), (140, 170, 110)), [("elefante", X, Y, 400, 0)], None, "ELEFANTE"),
        8: (((255, 230, 150), (240, 170, 60)), [("despertador", X - 200, Y, 300, -8)], ("60", X + 220, Y, 180), "60 MINUTOS"),
        9: (ceu, [("lua_cheia", X, Y, 380, 0)], None, "LUA"),
        10: (((140, 210, 255), (50, 120, 210)), [("africa", X, Y, 400, 0)], None, "ÁFRICA"),
        11: (((200, 235, 160), (110, 180, 80)), [("formiga", X - 190, Y, 320, -10)], ("6", X + 230, Y, 200), "6 PATAS"),
        12: (((170, 225, 255), (70, 150, 230)), [("gota", X - 230, Y, 300, 0)], ("H2O", X + 170, Y, 150), "H2O"),
        13: (((255, 225, 170), (210, 160, 90)), [("quadro", X - 90, Y, 360, -4), ("paleta", X + 290, Y + 40, 200, 12)], None, "DA VINCI"),
        14: (((190, 230, 255), (100, 170, 230)), [("pulmoes", X, Y, 380, 0)], None, "OXIGÊNIO"),
        15: (((255, 190, 170), (210, 70, 60)), [("bordo", X, Y, 390, -6)], None, "OTTAWA"),
        16: (((110, 210, 120), (30, 130, 60)), [("camisa", X - 230, Y - 10, 260, -8), ("bola", X - 60, Y + 100, 140, 0)], ("11", X + 230, Y, 190), "11 JOGADORES"),
        17: (((220, 225, 235), (150, 160, 180)), [("termometro", X - 170, Y, 330, -10)], ("Hg", X + 200, Y, 180), "MERCÚRIO"),
        18: (((255, 235, 190), (210, 170, 110)), [("livro", X - 80, Y, 340, -4), ("pena", X + 280, Y - 30, 210, 10)], None, "MACHADO DE ASSIS"),
        19: (((255, 220, 140), (230, 160, 70)), [("deserto", X - 110, Y, 360, 0), ("camelo", X + 260, Y + 40, 240, 0)], None, "SAARA"),
        20: (((170, 230, 190), (60, 160, 100)), [("pizza", X + 300, Y + 40, 220, 10)], None, "ITÁLIA"),
        21: (ceu, [("saturno", X, Y, 420, 0)], None, "SATURNO"),
        22: (((255, 220, 220), (220, 120, 140)), [("iene", X, Y, 400, -6)], None, "IENE"),
        23: (ceu, [("lua_cheia", X + 300, Y - 60, 200, 0), ("astronauta", X - 110, Y, 340, 0), ("foguete", X + 250, Y + 120, 150, 30)], None, "1969"),
        24: (((210, 200, 240), (120, 100, 190)), [("piano", X, Y, 400, 0)], None, "PIANO"),
        25: (((170, 220, 255), (70, 120, 220)), [("atomo", X - 190, Y, 320, 0)], ("H", X + 220, Y, 220), "HIDROGÊNIO"),
        26: (((255, 200, 190), (200, 60, 60)), [], None, "ANCARA"),
        27: (ceu, [], None, "URANO"),
        28: (((180, 220, 255), (80, 140, 220)), [("canoa", X + 300, Y + 70, 210, 0), ("onda", X + 280, Y + 160, 140, 0)], None, "RIO SENA"),
        29: (((170, 220, 255), (60, 130, 210)), [("ilha", X + 300, Y + 40, 230, 0)], None, "SUÉCIA"),
        30: (((40, 90, 170), (5, 15, 50)), [("mergulho", X - 230, Y - 40, 230, -15), ("peixe", X + 280, Y - 60, 150, 0),
                                              ("seta_baixo", X + 20, Y + 30, 240, 0)], None, "FOSSA DAS MARIANAS"),
        31: (((230, 200, 190), (170, 110, 100)), [("tijolo", X - 150, Y, 320, -8), ("martelo", X + 230, Y - 20, 260, 20)], None, "1989"),
        32: (ceu, [], None, "MERCÚRIO"),
        33: (((190, 235, 170), (80, 160, 90)), [("ovelha", X - 180, Y, 300, 0), ("kiwi", X + 240, Y + 30, 220, 10)], None, "WELLINGTON"),
        34: (((220, 200, 255), (130, 90, 210)), [("tubo", X - 220, Y, 300, -12)], ("118", X + 180, Y, 170), "118 ELEMENTOS"),
        35: (((120, 190, 240), (20, 70, 160)), [("cachalote", X - 90, Y + 10, 380, 0), ("cerebro", X + 320, Y - 80, 170, 10)], None, "CACHALOTE"),
    }
    (c1, c2), els, num, rot = cenas[i]
    escuro = c1 == ceu[0]
    img = fundo(c1, c2, cor_raio=(255, 255, 255, 12) if escuro else None)
    if escuro or i == 30:
        estrelinhas(img, pts)
    if i == 4:
        por(img, bandeira("brasil", 460, 320, -4), X - 120, Y)
    if i == 20:
        por(img, bandeira("italia", 470, 320, -4), X - 120, Y)
    if i == 26:
        por(img, bandeira("turquia", 560, 370, -4), X, Y)
    if i == 28:
        por(img, bandeira("franca", 440, 300, -4), X - 140, Y)
    if i == 29:
        por(img, bandeira("suecia", 470, 320, -4), X - 120, Y)
    if i == 27:
        por(img, urano(), X, Y)
    if i == 32:
        por(img, planeta(280, [(255, 205, 50), (255, 170, 30)], sombra=False, brilho_sol=True), -40, Y)
        por(img, planeta(85, [(170, 160, 150), (110, 100, 95)], crateras=5), X + 60, Y)
        por(img, planeta(130, [(225, 90, 50), (190, 60, 35)], crateras=4), X + 340, Y + 20)
    if i == 5:  # triângulo desenhado
        d = ImageDraw.Draw(img)
        tri = [(X - 190, Y - 170), (X - 20, Y + 140), (X - 360, Y + 140)]
        d.polygon([(x, y + 14) for x, y in tri], fill=ESC)
        d.polygon(tri, fill=(255, 90, 90), outline=ESC, width=OUT)
    for el in els:
        if len(el) == 6:
            emo(img, *el[:5], matiz=el[5])
        else:
            emo(img, *el)
    if num:
        numero(img, num[0], num[1], num[2], num[3])
    return img, rot


CENAS = {"01_animais": v1, "02_geografia": v2, "03_brasil": v3, "04_corpo_humano": v4, "05_espaco": v5, "06_quiz_longo": v6}


def main():
    nomes = sys.argv[1:] or list(CENAS)
    for nome in nomes:
        pasta = BASE / "videos" / nome / "imagens"
        pasta.mkdir(parents=True, exist_ok=True)
        n = 35 if nome == "06_quiz_longo" else 5
        for i in range(1, n + 1):
            img, rotulo = CENAS[nome](i)
            faixa(img, rotulo, y=24 * S)
            img.convert("RGB").resize((W // S, H // S), Image.LANCZOS).save(pasta / f"p{i}_resposta.png")
        print(f"  {pasta}/p1..p{n}_resposta.png")


if __name__ == "__main__":
    main()
