---
name: reenquadrar
description: Converte vídeos entre formatos (horizontal 16:9, vertical 9:16, feed 4:5, quadrado 1:1) sem distorcer - com fundo desfocado, corte inteligente ou barras. Use quando o usuário pedir para transformar um vídeo horizontal em vertical, adaptar para Reels, TikTok, Shorts, feed ou YouTube.
when_to_use: Pedidos como passa para vertical, adapta para reels, deixa no formato do feed, transforma em quadrado.
---

# FREMEX · Reenquadrar

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/reenquadrar.py" entrada.mp4 saida.mp4 --formato 9:16 --modo desfoque
```

| Formato | Tamanho | Uso |
|---|---|---|
| 9:16 | 1080x1920 | Reels, TikTok, Shorts, Stories |
| 4:5 | 1080x1350 | Feed do Instagram |
| 1:1 | 1080x1080 | Feed, anúncios |
| 16:9 | 1920x1080 | YouTube, apresentações |

## Como escolher o modo

- **desfoque** (padrão): mostra o vídeo inteiro, com o fundo preenchido pelo próprio vídeo desfocado. Ideal para telas, slides, paisagens e vídeos com texto nas bordas.
- **corte**: preenche a tela inteira. Ideal para uma pessoa falando. Use `--foco` para manter a pessoa no quadro: assista o vídeo (skill `watch`), veja onde ela está (0 = esquerda, 0.5 = centro, 1 = direita) e ajuste.
- **barras**: barras pretas da marca. Use só quando o cliente pedir.

## Conferência

Extraia um quadro do início, do meio e do fim (`ffmpeg -ss <t> -i saida.mp4 -frames:v 1 q.jpg`) e confira se nada importante (rosto, produto, texto) ficou cortado. Se a pessoa se move muito no modo corte, prefira o modo desfoque ou divida o vídeo em trechos com focos diferentes.
