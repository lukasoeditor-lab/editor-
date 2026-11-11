---
name: audio
description: Trata o áudio de vídeos - limpa ruído da voz, adiciona trilha sonora com ducking automático (a música abaixa quando alguém fala) e normaliza o volume para -14 LUFS, padrão das redes sociais. Use quando o usuário pedir para melhorar o som, tirar ruído, colocar música de fundo ou deixar o volume certo.
when_to_use: Pedidos como melhora o áudio, tira o barulho, coloca uma música de fundo, o som tá baixo, abaixa a música quando eu falo.
---

# FREMEX · Áudio

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/tratar_audio.py" entrada.mp4 saida.mp4 --limpar --musica trilha.mp3 --ducking
```

| Opção | O que faz |
|---|---|
| `--limpar` | corta graves abaixo de 80 Hz e reduz ruído constante (ventilador, ar-condicionado) |
| `--musica arquivo` | trilha de fundo, repetida até o fim do vídeo |
| `--volume-musica 0.25` | volume da trilha (0.15 discreto, 0.35 presente) |
| `--ducking` | a trilha abaixa sozinha quando há fala |
| `--lufs -14` | volume final; -14 é o padrão das redes |

## Regras

- **Música precisa de licença.** Use só trilhas que o usuário enviou ou bibliotecas com licença para uso comercial. Nunca baixe música de vídeos de terceiros. Se o usuário não tiver trilha, peça para ele escolher uma de uma biblioteca licenciada.
- A limpeza é leve de propósito. Ruído forte (vento, multidão) não sai por completo: avise o usuário em vez de exagerar e deixar a voz metálica.
- Confira o resultado: `ffmpeg -i saida.mp4 -af ebur128 -f null -`. A linha `I:` deve ficar perto de -14 LUFS.
- O tratamento de áudio vem antes das legendas e depois dos cortes.
