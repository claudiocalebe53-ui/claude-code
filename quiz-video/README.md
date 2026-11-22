# Gerador de vídeos de quiz (9:16, 1080x1920, 60fps)

Requisitos: Python 3.10+, `pip install pillow numpy`, `ffmpeg` no PATH.

```bash
python gerar.py --previa   # 1 frame PNG de cada tela em saida/previa/
python gerar.py --teste    # vídeo curto (gancho + 1 pergunta + final)
python gerar.py            # vídeo completo -> saida/quiz.mp4
```

- `perguntas.json`: texto, 4 alternativas, `correta` (índice 0–3), `nivel` (facil/medio/dificil),
  `imagem_pergunta` / `imagem_resposta` (opcionais; caminho relativo ao projeto ou a `assets/imagens/`).
  Opcional: `cor_fundo: [r, g, b]`.
- `assets/logo.png`: seu logo (sem ele, usa um medalhão "?" provisório).
- `assets/sons/`: `tique-taque`, `ding`, `whoosh`, `pop`, `musica` (.mp3/.wav/.ogg).
  Os incluídos foram sintetizados por `python gerar_sons.py` (originais, livres de direitos);
  substitua qualquer um por outro arquivo com o mesmo nome. A música abaixa sozinha durante a narração.
  Sons ausentes são pulados com aviso; sem nenhum, o vídeo sai mudo.
- Fonte: Lilita One (OFL) em `assets/fonts/`.
- `assets/narracao/`: narração opcional, um arquivo por fala: `00_gancho`, `vinheta_facil`,
  `vinheta_medio`, `vinheta_dificil`, `p1_pergunta`, `p1_resposta` … `p5_resposta`, `99_final`.
  A pergunta é lida no início do cronômetro e a resposta entra junto com a revelação.
  Telas se alongam automaticamente se a fala for mais longa que o tempo padrão.
