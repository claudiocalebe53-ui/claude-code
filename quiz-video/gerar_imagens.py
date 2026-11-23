#!/usr/bin/env python3
"""Desenha as ilustrações das perguntas iniciais (estilo cartoon, contorno grosso).

Gera em assets/imagens/: p1_pergunta.png, p1_resposta.png ... p5_resposta.png
Uso: python gerar_imagens.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent
SAIDA = BASE / "assets" / "imagens"
FONTE = BASE / "assets" / "fonts" / "LilitaOne-Regular.ttf"

S = 2                       # desenha em 2x e reduz (antialias)
W, H = 560 * S, 380 * S
ESC = (25, 20, 35)
BR = (255, 255, 255)
OUT = 7 * S                 # espessura do contorno
G = 1                       # unidade da geometria: coordenadas já na tela 2x (1120x760)


def f(t):
    return ImageFont.truetype(str(FONTE), t)


def grad(c1, c2, w=W, h=H):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        k = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip(c1, c2)))
    return img.convert("RGBA")


def salvar(img, nome):
    SAIDA.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").resize((W // S, H // S), Image.LANCZOS).save(SAIDA / f"{nome}.png")
    print(f"  {SAIDA / (nome + '.png')}")


def faixa(img, texto, cor=(46, 204, 64), y=None):
    """Etiqueta arredondada com o texto da resposta."""
    d = ImageDraw.Draw(img)
    fo = f(70 * S)
    tw = fo.getlength(texto)
    pw, ph = tw + 70 * S, 104 * S
    x0 = (W - pw) / 2
    y0 = y if y is not None else H - ph - 26 * S
    d.rounded_rectangle((x0, y0 + 8 * S, x0 + pw, y0 + ph + 8 * S), ph / 2, fill=ESC)
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), ph / 2, fill=cor, outline=ESC, width=OUT)
    d.text((W / 2, y0 + ph / 2 + 3 * S), texto, font=fo, fill=BR, anchor="mm",
           stroke_width=5 * S, stroke_fill=ESC)


def interrogacao(img, x, y, tam=150, ang=12, cor=(255, 205, 0)):
    lay = Image.new("RGBA", (tam * S * 2, tam * S * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = tam * S
    d.text((c, c + 8 * S), "?", font=f(tam * S), fill=ESC, anchor="mm", stroke_width=8 * S, stroke_fill=ESC)
    d.text((c, c), "?", font=f(tam * S), fill=cor, anchor="mm", stroke_width=8 * S, stroke_fill=ESC)
    lay = lay.rotate(ang, resample=Image.BICUBIC)
    img.alpha_composite(lay, (int(x - c), int(y - c)))


def brilho(d, x, y, r, cor=BR):
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.3
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=cor)


def sombra_chao(img, cx, cy, rx, ry, alpha=70):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(0, 0, 0, alpha))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10 * G)))


# ---------------------------------------------------------------------------
# 1. Aranha
# ---------------------------------------------------------------------------

def aranha(numerar=False):
    img = grad((120, 200, 255), (60, 140, 220))
    d = ImageDraw.Draw(img)
    # teia no canto
    cx0, cy0 = 0, 0
    for i in range(9):
        a = math.radians(i * 11.25)
        d.line([(cx0, cy0), (cx0 + 1400 * math.cos(a), cy0 + 1400 * math.sin(a))],
               fill=(235, 245, 255), width=3 * S)
    for r in range(110, 1500, 120):
        pts = [(cx0 + r * math.cos(math.radians(i * 11.25)), cy0 + r * math.sin(math.radians(i * 11.25)))
               for i in range(9)]
        d.line(pts, fill=(235, 245, 255), width=3 * S)

    K = 1.45  # escala da aranha
    cx, cy = W / 2 + 30, H / 2 + (50 if numerar else 10)
    d.line([(cx, 0), (cx, cy - 70 * K)], fill=(240, 240, 255), width=4 * S)
    pontas = []
    for lado in (-1, 1):
        for k in range(4):
            base = (cx + lado * 40 * K, cy - 40 * K + k * 26 * K)
            joelho = (cx + lado * (150 + 15 * abs(k - 1.5)) * K, cy - 120 * K + k * 60 * K)
            pe = (cx + lado * (235 - 22 * abs(k - 1.5)) * K, cy - 10 * K + k * 72 * K)
            d.line([base, joelho, pe], fill=ESC, width=22 * S, joint="curve")
            d.line([base, joelho, pe], fill=(80, 60, 120), width=10 * S, joint="curve")
            pontas.append(pe)
    # abdômen e cabeça
    d.ellipse((cx - 105 * K, cy - 5 * K, cx + 105 * K, cy + 175 * K), fill=(80, 60, 120), outline=ESC, width=OUT)
    d.ellipse((cx - 60 * K, cy + 30 * K, cx - 10 * K, cy + 70 * K), fill=(120, 100, 170))
    d.ellipse((cx - 75 * K, cy - 100 * K, cx + 75 * K, cy + 40 * K), fill=(95, 75, 140), outline=ESC, width=OUT)
    for ex in (-30, 30):
        d.ellipse((cx + (ex - 24) * K, cy - 65 * K, cx + (ex + 24) * K, cy - 13 * K), fill=BR, outline=ESC, width=5 * S)
        d.ellipse((cx + (ex - 9) * K, cy - 45 * K, cx + (ex + 11) * K, cy - 23 * K), fill=ESC)
    d.arc((cx - 28 * K, cy - 20 * K, cx + 28 * K, cy + 20 * K), 20, 160, fill=ESC, width=5 * S)
    if numerar:
        ordem = [0, 1, 2, 3, 7, 6, 5, 4]
        for n, i in enumerate(ordem, 1):
            x, y = pontas[i]
            r = 26 * S
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 205, 0), outline=ESC, width=5 * S)
            d.text((x, y + 2 * S), str(n), font=f(36 * S), fill=ESC, anchor="mm")
        faixa(img, "8 PATAS", y=24 * S)
    else:
        interrogacao(img, 140 * K, 250 * K)
    return img


# ---------------------------------------------------------------------------
# 2. Oceano
# ---------------------------------------------------------------------------

def mar_e_barco():
    img = grad((140, 215, 255), (200, 240, 255))
    d = ImageDraw.Draw(img)
    d.ellipse((W - 230 * G, 40 * G, W - 110 * G, 160 * G), fill=(255, 210, 40), outline=ESC, width=OUT)
    for i, (y, cor) in enumerate([(380, (30, 120, 210)), (450, (20, 95, 185)), (530, (15, 75, 160))]):
        pts = [(0, H)]
        for x in range(0, W + 20, 20):
            pts.append((x, y + 18 * G * math.sin(x / (60 * G) + i * 1.7)))
        pts.append((W, H))
        d.polygon(pts, fill=cor, outline=ESC, width=OUT)
        if i == 0:  # barquinho
            bx, by = 640 * G, 360 * G
            d.polygon([(bx - 110 * G, by), (bx + 110 * G, by), (bx + 75 * G, by + 55 * G), (bx - 75 * G, by + 55 * G)],
                      fill=(200, 60, 50), outline=ESC, width=OUT)
            d.line([(bx, by), (bx, by - 170 * G)], fill=ESC, width=8 * S)
            d.polygon([(bx + 6 * G, by - 165 * G), (bx + 6 * G, by - 20 * G), (bx + 110 * G, by - 20 * G)],
                      fill=BR, outline=ESC, width=OUT)
    interrogacao(img, 250 * G, 200 * G, 170, -10)
    return img


def globo_pacifico():
    img = grad((25, 30, 70), (60, 40, 110))
    d = ImageDraw.Draw(img)
    for x, y, r in [(90, 90, 10), (980, 120, 12), (150, 600, 8), (1020, 560, 10), (870, 60, 7)]:
        brilho(d, x, y, r * G)
    cx, cy, r = W / 2, H / 2 + 75, 290
    R = r / 255
    d.ellipse((cx - r - 10 * R, cy - r - 10 * R, cx + r + 10 * R, cy + r + 10 * R), fill=(120, 190, 255))
    globo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(globo)
    g.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(30, 130, 230))
    verde, ol = (70, 190, 90), ESC
    # Ásia (alto-esquerda), Austrália (baixo-esquerda), Américas (direita)
    g.polygon([(cx - r, cy - 230 * R), (cx - 120 * R, cy - 250 * R), (cx - 60 * R, cy - 190 * R), (cx - 130 * R, cy - 140 * R),
               (cx - 150 * R, cy - 70 * R), (cx - 210 * R, cy - 40 * R), (cx - r, cy - 30 * R)], fill=verde, outline=ol, width=OUT)
    g.polygon([(cx - 230 * R, cy + 90 * R), (cx - 130 * R, cy + 70 * R), (cx - 100 * R, cy + 130 * R),
               (cx - 150 * R, cy + 190 * R), (cx - 240 * R, cy + 170 * R)], fill=(230, 170, 70), outline=ol, width=OUT)
    g.polygon([(cx + 120 * R, cy - r), (cx + 230 * R, cy - 170 * R), (cx + 210 * R, cy - 60 * R), (cx + 150 * R, cy - 40 * R),
               (cx + 160 * R, cy - 120 * R), (cx + 90 * R, cy - 190 * R)], fill=verde, outline=ol, width=OUT)
    g.polygon([(cx + 170 * R, cy + 10 * R), (cx + 250 * R, cy + 40 * R), (cx + 220 * R, cy + 160 * R),
               (cx + 170 * R, cy + 230 * R), (cx + 150 * R, cy + 110 * R)], fill=verde, outline=ol, width=OUT)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    globo.putalpha(Image.composite(globo.getchannel("A"), Image.new("L", img.size, 0), mask))
    img.alpha_composite(globo)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ESC, width=OUT)
    d.arc((cx - r + 40 * R, cy - r + 40 * R, cx + r - 40 * R, cy + r - 40 * R), 200, 250, fill=(180, 225, 255), width=12 * S)
    for dx, dy in [(-40, -20), (40, 60), (0, 140)]:  # ondinhas no Pacífico
        d.arc((cx + (dx - 25) * G, cy + (dy - 10) * G, cx + (dx + 25) * G, cy + (dy + 20) * G), 200, 340,
              fill=(170, 220, 255), width=6 * S)
    faixa(img, "PACÍFICO", y=24 * S)
    return img


# ---------------------------------------------------------------------------
# 3. Caravela de Cabral
# ---------------------------------------------------------------------------

def caravela(d, bx, by, k=1.0):
    def p(x, y):
        return (bx + x * G * k, by + y * G * k)
    d.polygon([p(-190, 0), p(170, 0), p(230, -40), p(150, 80), p(-150, 80), p(-215, -30)],
              fill=(150, 90, 45), outline=ESC, width=OUT)
    d.line([p(-170, 30), p(170, 30)], fill=(110, 60, 30), width=int(6 * S * k))
    for mx, alt, larg in [(-90, 250, 80), (30, 300, 105), (140, 210, 70)]:
        d.line([p(mx, 0), p(mx, -alt)], fill=ESC, width=int(9 * S * k))
        topo, base_ = -alt + 25, -50
        d.polygon([p(mx - larg, topo), p(mx + larg, topo), p(mx + larg * 0.85, base_), p(mx - larg * 0.85, base_)],
                  fill=(250, 245, 230), outline=ESC, width=OUT)
        cy_ = (topo + base_) / 2
        d.line([p(mx, topo + 18), p(mx, base_ - 18)], fill=(210, 30, 40), width=int(20 * S * k))
        d.line([p(mx - larg * 0.55, cy_), p(mx + larg * 0.55, cy_)], fill=(210, 30, 40), width=int(20 * S * k))
    d.polygon([p(30, -300), p(30, -340), p(85, -320)], fill=(210, 30, 40), outline=ESC, width=int(4 * S * k))


def ondas(d, y0, cor=(25, 110, 200), cor2=(15, 85, 170)):
    for i, (yy, c) in enumerate([(y0, cor), (y0 + 60 * G, cor2)]):
        pts = [(0, H)] + [(x, yy + 14 * G * math.sin(x / (45 * G) + i * 2)) for x in range(0, W + 20, 16)] + [(W, H)]
        d.polygon(pts, fill=c, outline=ESC, width=OUT)


def caravela_mar():
    img = grad((255, 190, 120), (255, 235, 190))
    d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 140 * G, 420 * G - 140 * G, W / 2 + 140 * G, 420 * G + 140 * G), fill=(255, 150, 60))
    caravela(d, W / 2 + 40 * G, 520 * G, 1.0)
    ondas(d, 560 * G)
    interrogacao(img, 150 * G, 200 * G, 160, -12)
    return img


def caravela_brasil():
    img = grad((120, 205, 255), (205, 240, 255))
    d = ImageDraw.Draw(img)
    # praia e coqueiros à direita
    d.polygon([(W * 0.62, H), (W * 0.72, 560 * G), (W, 470 * G), (W, H)], fill=(245, 215, 140), outline=ESC, width=OUT)
    d.polygon([(W * 0.78, 520 * G), (W * 0.86, 330 * G), (W, 300 * G), (W, 500 * G)], fill=(40, 150, 70), outline=ESC, width=OUT)
    for tx, ty, h in [(W * 0.83, 540 * G, 290), (W * 0.93, 500 * G, 340)]:
        topo = (tx + 40 * G, ty - h * G)
        d.line([(tx, ty), (tx + 20 * G, ty - h * G * 0.5), topo], fill=ESC, width=22 * S, joint="curve")
        d.line([(tx, ty), (tx + 20 * G, ty - h * G * 0.5), topo], fill=(150, 100, 55), width=12 * S, joint="curve")
        for a in range(0, 360, 60):
            r = math.radians(a)
            fx, fy = topo[0] + 120 * G * math.cos(r), topo[1] + 55 * G * math.sin(r) + 25 * G
            d.line([topo, ((topo[0] + fx) / 2, min(topo[1], fy) - 30 * G), (fx, fy)], fill=ESC, width=24 * S, joint="curve")
            d.line([topo, ((topo[0] + fx) / 2, min(topo[1], fy) - 30 * G), (fx, fy)], fill=(60, 180, 80), width=14 * S, joint="curve")
    caravela(d, W * 0.33, 540 * G, 0.85)
    pts = [(0, H)] + [(x, 590 * G + 12 * G * math.sin(x / (45 * G))) for x in range(0, int(W * 0.68), 16)] + [(W * 0.66, H)]
    d.polygon(pts, fill=(25, 110, 200), outline=ESC, width=OUT)
    faixa(img, "1500", cor=(46, 204, 64), y=24 * S)
    return img


# ---------------------------------------------------------------------------
# 4. Ouro
# ---------------------------------------------------------------------------

def barra(d, x, y, w=220, h=90):
    w, h = w * G, h * G
    topo = [(x + 30 * G, y), (x + w - 30 * G, y), (x + w, y + 40 * G), (x, y + 40 * G)]
    d.polygon([(x, y + 40 * G), (x + w, y + 40 * G), (x + w, y + h), (x, y + h)], fill=(225, 160, 20), outline=ESC, width=OUT)
    d.polygon(topo, fill=(255, 215, 60), outline=ESC, width=OUT)
    d.line([(x + 50 * G, y + 12 * G), (x + 110 * G, y + 12 * G)], fill=(255, 245, 180), width=8 * S)


def ouro_barras():
    img = grad((70, 40, 110), (130, 70, 160))
    d = ImageDraw.Draw(img)
    sombra_chao(img, W / 2, 640 * G, 330 * G, 40 * G)
    d = ImageDraw.Draw(img)
    bx = W / 2 - 330 * G
    for i in range(3):
        barra(d, bx + i * 220 * G, 530 * G)
    for i in range(2):
        barra(d, bx + 110 * G + i * 220 * G, 440 * G)
    barra(d, bx + 220 * G, 350 * G)
    for x, y, r in [(260, 330, 34), (850, 300, 28), (740, 230, 18), (330, 450, 16)]:
        brilho(d, x * G, y * G, r * G, (255, 250, 200))
    interrogacao(img, W / 2, 160 * G, 170, 8)
    return img


def ouro_tabela():
    img = grad((70, 40, 110), (130, 70, 160))
    d = ImageDraw.Draw(img)
    lado = 430
    x0, y0 = W / 2 - lado / 2, 50
    d.rounded_rectangle((x0, y0 + 14, x0 + lado, y0 + lado + 14), 40, fill=ESC)
    d.rounded_rectangle((x0, y0, x0 + lado, y0 + lado), 40, fill=(255, 205, 40), outline=ESC, width=OUT)
    d.text((x0 + 34, y0 + 26), "79", font=f(32 * S), fill=ESC)
    d.text((W / 2, y0 + 225), "Au", font=f(105 * S), fill=BR, anchor="mm", stroke_width=6 * S, stroke_fill=ESC)
    d.text((W / 2, y0 + 370), "Ouro", font=f(34 * S), fill=ESC, anchor="mm")
    for x, y, r in [(250, 140, 36), (880, 200, 30), (860, 470, 22), (230, 460, 20)]:
        brilho(d, x, y, r, (255, 240, 160))
    faixa(img, "Au", y=H - 118 * S)
    return img


# ---------------------------------------------------------------------------
# 5. Osso (raio-X da perna)
# ---------------------------------------------------------------------------

def osso(d, x0, y0, x1, y1, esp, cor, contorno=ESC):
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    e = esp / 2
    for (x, y) in ((x0, y0), (x1, y1)):
        for s in (-1, 1):
            cx, cy = x + nx * e * 0.9 * s, y + ny * e * 0.9 * s
            d.ellipse((cx - e * 1.05, cy - e * 1.05, cx + e * 1.05, cy + e * 1.05), fill=cor, outline=contorno, width=OUT)
    d.polygon([(x0 + nx * e, y0 + ny * e), (x1 + nx * e, y1 + ny * e), (x1 - nx * e, y1 - ny * e), (x0 - nx * e, y0 - ny * e)],
              fill=cor, outline=contorno, width=OUT)
    # recobre as emendas internas
    for (x, y) in ((x0, y0), (x1, y1)):
        for s in (-1, 1):
            cx, cy = x + nx * e * 0.9 * s, y + ny * e * 0.9 * s
            d.ellipse((cx - e * 0.75, cy - e * 0.75, cx + e * 0.75, cy + e * 0.75), fill=cor)
    d.polygon([(x0 + nx * (e - OUT), y0 + ny * (e - OUT)), (x1 + nx * (e - OUT), y1 + ny * (e - OUT)),
               (x1 - nx * (e - OUT), y1 - ny * (e - OUT)), (x0 - nx * (e - OUT), y0 - ny * (e - OUT))], fill=cor)


def perna(destaque=False):
    img = grad((10, 35, 70), (5, 20, 45))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40 * G):
        d.line([(x, 0), (x, H)], fill=(20, 55, 95), width=S)
    for y in range(0, H, 40 * G):
        d.line([(0, y), (W, y)], fill=(20, 55, 95), width=S)
    # silhueta translúcida da perna
    sil = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sil)
    ds.polygon([(40 * G, 250 * G), (560 * G, 300 * G), (950 * G, 330 * G), (1060 * G, 300 * G), (1090 * G, 420 * G),
                (950 * G, 450 * G), (560 * G, 470 * G), (40 * G, 560 * G)], fill=(120, 190, 255, 55))
    img.alpha_composite(sil.filter(ImageFilter.GaussianBlur(14 * G)))
    d = ImageDraw.Draw(img)
    claro = (225, 235, 245)
    femur = (255, 205, 0) if destaque else claro
    if destaque:
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).line([(120 * G, 400 * G), (560 * G, 385 * G)], fill=(255, 220, 60, 150), width=80)
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30 * G)))
        d = ImageDraw.Draw(img)
    # quadril
    d.ellipse((20 * G, 290 * G, 150 * G, 510 * G), fill=claro, outline=ESC, width=OUT)
    osso(d, 130 * G, 400 * G, 560 * G, 385 * G, 52 * G, femur)                 # fêmur
    d.ellipse((575 * G, 335 * G, 625 * G, 380 * G), fill=claro, outline=ESC, width=OUT)  # patela
    osso(d, 620 * G, 400 * G, 950 * G, 385 * G, 44 * G, claro)                 # tíbia
    osso(d, 640 * G, 445 * G, 940 * G, 430 * G, 20 * G, claro)                 # fíbula
    for i in range(4):                                                          # pé
        osso(d, 975 * G, (355 + i * 25) * G, 1080 * G, (330 + i * 30) * G, 15 * G, claro)
    if destaque:
        faixa(img, "FÊMUR", y=40 * S)
    else:
        interrogacao(img, 345 * G, 210 * G, 150, -8)
    return img


def main():
    print("Gerando ilustrações em", SAIDA)
    salvar(aranha(), "p1_pergunta")
    salvar(aranha(numerar=True), "p1_resposta")
    salvar(mar_e_barco(), "p2_pergunta")
    salvar(globo_pacifico(), "p2_resposta")
    salvar(caravela_mar(), "p3_pergunta")
    salvar(caravela_brasil(), "p3_resposta")
    salvar(ouro_barras(), "p4_pergunta")
    salvar(ouro_tabela(), "p4_resposta")
    salvar(perna(), "p5_pergunta")
    salvar(perna(destaque=True), "p5_resposta")


if __name__ == "__main__":
    main()
