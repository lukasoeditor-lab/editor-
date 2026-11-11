---
name: legendas
description: Cria legendas automáticas palavra por palavra no estilo reels (a palavra falada acende em azul FREMEX), grava no vídeo e gera também o arquivo .srt para as plataformas. Transcrição local, sem enviar o áudio para a nuvem. Use quando o usuário pedir legenda, caption, texto na tela acompanhando a fala ou transcrição.
when_to_use: Pedidos como coloca legenda, legenda dinâmica, legenda estilo TikTok, gera o srt, transcreve o vídeo.
---

# FREMEX · Legendas

Requer `pip install faster-whisper` (o setup instala). No primeiro uso, ele baixa um modelo de transcrição de algumas centenas de MB.

## Uso

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/legendas.py" video.mp4 --saida video-legendado.mp4
```

Gera `video.ass` (legenda animada), `video.srt` (legenda simples) e o vídeo com a legenda gravada.

| Opção | Padrão | Quando mudar |
|---|---|---|
| `--palavras` | 3 | 1 ou 2 para ritmo mais agressivo; 4 ou 5 para conteúdo calmo |
| `--idioma` | pt | `en`, `es` etc. quando a fala for em outro idioma |
| `--posicao` | 0.72 | mais alto (0.6) se cobrir o rosto ou a interface da rede |
| `--tamanho` | 78 | maior para vídeos com muito texto pequeno; menor para frases longas |
| `--fonte` | Arial Black | a fonte precisa estar instalada no computador |
| `--cor-destaque` | 6A96DE | cor da marca do cliente, em hexadecimal sem # |
| `--maiusculas` | não | estilo mais "impacto" |
| `--sem-pulo` | não | desliga o "pulo" de escala da palavra falada (edições mais sóbrias) |
| `--so-arquivos` | não | só gerar .ass/.srt, sem gravar no vídeo |
| `--modelo` | small | `medium` se a transcrição errar muitos nomes (mais lento) |

## Revisão obrigatória

1. Leia o `.srt` gerado e corrija nomes próprios, marcas e termos técnicos **no `.ass`**. São os erros mais comuns.
2. Regrave com o `.ass` corrigido:
   ```bash
   ffmpeg -i video.mp4 -vf "ass=video.ass" -c:v libx264 -crf 18 -c:a copy video-legendado.mp4
   ```
3. Extraia 3 quadros e confira se a legenda não cobre rostos nem fica atrás da interface do Instagram ou do TikTok (as faixas inferiores de cerca de 15% são de risco).

## Regras

- Legende sempre **depois** dos cortes. Os tempos mudam quando o vídeo é cortado.
- Entregue também o `.srt`: as plataformas aceitam legenda separada, o que ajuda acessibilidade e busca.
