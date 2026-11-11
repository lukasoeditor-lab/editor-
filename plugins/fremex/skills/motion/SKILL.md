---
name: motion
description: Cria animações e motion graphics por código - vinhetas, títulos animados, lower thirds, abertura e encerramento, explicadores - escolhendo entre os plugins oficiais do HyperFrames e do Remotion ou o template de reels FREMEX, sempre com a identidade do cliente. Use quando o usuário pedir vinheta, animação, título animado, abertura, motion ou um vídeo feito sem filmagem.
when_to_use: Pedidos como faz uma vinheta, anima o logo, cria uma abertura, coloca um título animado, vídeo explicativo animado.
---

# FREMEX · Motion

## Qual ferramenta usar

| Pedido | Ferramenta | Por quê |
|---|---|---|
| Reel de lista, dicas, tutorial em tela (estilo FREMEX) | skill `reels` | template pronto, legenda sincronizada |
| Vinheta, abertura, intro de produto, motion a partir de site | plugin **HyperFrames** (`/hyperframes:hyperframes`) | HTML para vídeo, rápido de iterar |
| Vídeo com dados, muitas variações do mesmo modelo, legendas e áudio complexos | plugin **Remotion** (`/remotion:remotion-create`) | componentes React reutilizáveis |

Se o plugin escolhido não estiver instalado, indique `/fremex:setup`.

## Identidade

Antes de animar, passe ao plugin as regras da marca:

- **Projeto FREMEX:** preto #080A0F, marinho #101D35, azul #2459A6, azul digital #6A96DE, branco gelo #F3F4F6; fontes Archivo, Instrument Serif itálico, IBM Plex Mono. Detalhes em `${CLAUDE_SKILL_DIR}/../reels/references/estilo.md`.
- **Projeto de cliente:** use as cores, fontes e logo de `cliente.md`.

## Encaixar no vídeo editado

Renderize a animação no mesmo tamanho e na mesma taxa de quadros do vídeo final (ex.: 1080x1920, 30 fps) e junte:

```bash
# abertura antes do vídeo
ffmpeg -i vinheta.mp4 -i video.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -c:a aac final.mp4
```
Se a vinheta não tiver áudio, gere silêncio antes (`-f lavfi -i anullsrc=r=48000:cl=stereo` com `-shortest`) para o `concat` funcionar.

Para sobrepor um título com transparência, renderize em ProRes 4444 ou WebM com canal alfa (as duas ferramentas suportam) e use `overlay`.
