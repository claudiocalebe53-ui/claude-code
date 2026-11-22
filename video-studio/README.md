# video-studio

Animações 3D em vídeo com **Three.js** + **Remotion** (legendas, áudio e renderização MP4).

## Pacotes

| Pacote | Para quê |
|---|---|
| `three`, `@react-three/fiber`, `@react-three/drei` | Cenas 3D |
| `remotion`, `@remotion/three` | Animar cenas 3D quadro a quadro |
| `@remotion/captions` | Legendas (estilo TikTok, SRT) |
| `@remotion/media`, `@remotion/media-utils` | Áudio/vídeo e visualização de áudio |
| `@remotion/cli`, `@remotion/renderer`, `@remotion/bundler` | Studio e renderização |
| `@remotion/google-fonts` | Fontes |

## Uso

```bash
cd video-studio
npm install
npm run dev       # abre o Remotion Studio (preview no navegador)
npm run render    # gera out/video.mp4
npm run still     # gera out/frame.png
```

Sem internet para baixar o Chrome do Remotion? Aponte para um Chrome local:
`REMOTION_CHROME=/caminho/para/chrome npm run render`

## Exemplo incluído

- `src/Cena3D.tsx` — cubo 3D animado (`ThreeCanvas`, `spring`, `interpolate`) + áudio
- `src/Legendas.tsx` — legendas a partir de `public/legendas.json`
- `public/audio.mp3` — áudio de exemplo (substitua pelo seu)
