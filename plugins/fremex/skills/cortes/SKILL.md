---
name: cortes
description: Corta vídeos falados no ritmo de reels - remove silêncios e pausas, tira erros e repetições, seleciona os melhores trechos e monta o gancho dos primeiros segundos. Use quando o usuário pedir para cortar pausas, deixar o vídeo mais dinâmico, tirar erros, encurtar ou escolher os melhores momentos.
when_to_use: Pedidos como corta as pausas, deixa mais dinâmico, tira os erros, reduz para 30 segundos, pega os melhores momentos.
---

# FREMEX · Cortes

## Remover silêncios (automático)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/cortar_silencios.py" entrada.mp4 saida.mp4 --plano
```
Rode primeiro com `--plano`: ele mostra a duração original, a final e os trechos mantidos, sem gerar vídeo. Ajuste e rode sem `--plano`.

| Situação | Ajuste |
|---|---|
| Cortou sílabas ou o fim das palavras | aumente `--margem` (0.15 a 0.25) |
| Ainda sobram pausas | diminua `--min` (0.3) |
| Não cortou nada / ambiente ruidoso | suba `--limiar` (-30) |
| Cortou respirações que deveriam ficar | aumente `--min` (0.7) |

Se o vídeo tem música contínua, o corte por silêncio não funciona, porque a música ocupa as pausas. Nesse caso, corte por trechos (abaixo).

## Cortar por trechos (erros, repetições, melhores momentos)

1. Transcreva com tempo por palavra:
   `python3 "${CLAUDE_SKILL_DIR}/../legendas/scripts/legendas.py" entrada.mp4 --so-arquivos` gera `entrada.srt`.
2. Leia a transcrição e marque:
   - **erros e repetições**: quando a pessoa recomeça a frase, fique com a última versão;
   - **melhores momentos**: frases completas, com começo forte e sem depender de contexto.
3. Mostre ao usuário a lista de trechos (início, fim, texto) e peça aprovação.
4. Monte com FFmpeg (`trim`/`atrim` + `concat`), um trecho por linha:
   ```bash
   ffmpeg -i entrada.mp4 -filter_complex "[0:v]trim=start=12.4:end=18.9,setpts=PTS-STARTPTS[v0];[0:a]atrim=start=12.4:end=18.9,asetpts=PTS-STARTPTS[a0];[0:v]trim=start=31.0:end=40.2,setpts=PTS-STARTPTS[v1];[0:a]atrim=start=31.0:end=40.2,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 18 -c:a aac saida.mp4
   ```

## Gancho

Os 2 primeiros segundos decidem se a pessoa continua assistindo. Se a melhor frase estiver no meio do vídeo, proponha colocá-la no início, como prévia, antes do corte normal.

## Depois de cortar

Refaça as legendas sobre o vídeo cortado. Os tempos mudaram.
