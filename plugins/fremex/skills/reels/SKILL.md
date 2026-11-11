---
name: reels
description: Produz reels verticais (1080x1920) no estilo FREMEX - interface em movimento, numerais em itálico com brilho, legendas palavra por palavra, chão em perspectiva, paleta preto e azul - com narração do ElevenLabs e render local para MP4. Use quando o usuário pedir um reel, vídeo curto, vídeo vertical, vídeo para Instagram, TikTok ou Shorts no padrão FREMEX.
when_to_use: Pedidos como faz um reel sobre um tema, cria um vídeo vertical, vídeo para Instagram, TikTok ou Shorts no estilo FREMEX.
---

# FREMEX · Reels

Você produz reels no estilo FREMEX. Leia `${CLAUDE_SKILL_DIR}/references/estilo.md` antes de começar: ele define a estrutura, o ritmo, a tipografia e as cores.

Fale em português do Brasil. Mostre cada etapa e peça aprovação nos pontos marcados com **[aprovação]**.

## Antes de começar

Confira rapidamente: `node --version` (22+) e `ffmpeg -version`. Se faltar algo, peça para o usuário rodar `/fremex:setup`.

## Fluxo (Método CRIAR)

### 1. Compreender
Pergunte apenas o que faltar: tema, público, objetivo do vídeo, palavra do CTA ("Comenta ___"), duração (padrão 15 a 30 s).

### 2. Roteirizar **[aprovação]**
Escreva:
- **Gancho** (até 2 s), **3 a 5 itens numerados** e **CTA de comentário**.
- O texto exato da narração. Conte cerca de 2,5 palavras por segundo.
- Para cada item: título curto, rótulo mono, duas pílulas e o conteúdo do card (checklist, terminal digitando, cards em leque ou quadros).
Não use números de visualizações, seguidores ou promessas de resultado.

### 3. Integrar
1. **Pasta do projeto:** crie `reel-<tema>/` e copie `${CLAUDE_SKILL_DIR}/template/composicao.html` e `${CLAUDE_SKILL_DIR}/scripts/render.js` para dentro dela.
2. **Narração:** se o conector do ElevenLabs estiver disponível (`/mcp`), liste vozes em português (`languages: ["pt"]`), escolha uma que combine com o pedido, diga qual escolheu e gere a fala. Informe que gerar voz consome créditos da conta do usuário. Baixe o MP3 para `narracao.mp3`. Sem ElevenLabs, peça para o usuário gravar a narração e salvar como `narracao.mp3`.
3. **Tempos das palavras:** rode `python3 ${CLAUDE_SKILL_DIR}/scripts/palavras.py narracao.mp3 palavras.json`. Se o faster-whisper não estiver instalado, estime os tempos dividindo a duração do áudio pelas palavras e avise que a sincronia fica aproximada.
4. **Composição:** edite `composicao.html`:
   - `WORDS`: os tempos de `palavras.json`, com a palavra-chave entre `*asteriscos*` (fica azul).
   - `DURATION`: duração do áudio + 0,5 s.
   - `STAGES` e `STAGE_STARTS`: cada item começa no tempo da palavra que o anuncia.
   - Cena 1 (gancho), cena 3 (CTA) e a palavra digitada na caixa de comentário.
5. **Dependência do render:** na pasta do projeto, `npm install playwright` e `npx playwright install chromium`.
6. **Render:** `node render.js composicao.html reel.mp4 narracao.mp3`.

### 4. Aprimorar **[aprovação]**
1. Gere uma folha de quadros para revisar: `ffmpeg -i reel.mp4 -vf "fps=24/<duração>,scale=270:-1,tile=8x3" -frames:v 1 revisao.jpg` e examine a imagem.
2. Verifique: textos sobrepostos, legenda fora de sincronia, texto cortado, contraste.
3. Confira o volume: `ffmpeg -i reel.mp4 -af ebur128 -f null -`. O alvo é perto de -14 LUFS (o render já normaliza).
4. Corrija, renderize de novo e entregue `reel.mp4` com o resumo do que foi feito.

### 5. Reaproveitar
Salve na pasta: roteiro final, `palavras.json` e a composição. Sugira transformar o vídeo numa série com a mesma estrutura.

## Regras de marca
- Cores: preto #080A0F, marinho #101D35, azul #2459A6, azul digital #6A96DE (texto e linhas no escuro), branco gelo #F3F4F6.
- Fontes: Archivo (títulos), Instrument Serif itálico (palavra de acento e numerais), IBM Plex Mono (rótulos), IBM Plex Sans (apoio).
- Não use o mascote do Claude nem logos de terceiros como personagem do vídeo.
- Rodapé discreto: "FREMEX · THE CREATIVE EVOLUTION".
