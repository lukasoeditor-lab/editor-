---
name: capa
description: Cria a capa (thumbnail) do vídeo no estilo FREMEX - um quadro do próprio vídeo como fundo, título forte com uma palavra de destaque em itálico azul. Formatos 9:16, 16:9 e 4:5. Use quando o usuário pedir capa, thumbnail, miniatura ou imagem de abertura do vídeo.
when_to_use: Pedidos como faz a capa, cria uma thumbnail, imagem para o YouTube, capa do reels.
---

# FREMEX · Capa

Requer, na pasta do projeto: `npm install playwright` e `npx playwright install chromium`.

```bash
node "${CLAUDE_SKILL_DIR}/scripts/capa.js" --video final.mp4 --tempo 3.2 --titulo "Edite vídeos com um método" --destaque "método" --formato 9:16 --saida entregas/capa.png
```

## Como escolher

1. **Quadro:** assista o vídeo (skill `watch`) e escolha um momento com expressão clara, olhos abertos e sem desfoque de movimento. Extraia 3 candidatos e mostre ao usuário.
2. **Título:** até 6 palavras, uma ideia só. A palavra de `--destaque` é a que carrega a promessa ou a curiosidade.
3. **Formato:** 9:16 para Reels e TikTok · 16:9 (1280x720) para YouTube · 4:5 para feed.

## Regras

- Use só imagens do próprio vídeo ou enviadas pelo usuário.
- Nada de setas falsas, números inventados ou promessas que o vídeo não cumpre.
- Confira a legibilidade reduzindo a imagem: o título precisa ser lido no tamanho de miniatura.
