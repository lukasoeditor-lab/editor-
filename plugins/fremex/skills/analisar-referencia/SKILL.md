---
name: analisar-referencia
description: Assiste vídeos de referência (link ou arquivo) e destrincha o estilo - estrutura, gancho, ritmo de cortes, legendas, tipografia, cores, transições, áudio e volume - transformando tudo num guia de estilo aplicável ao vídeo do usuário, sem copiar elementos de terceiros. Use quando o usuário mandar uma referência e disser que quer um vídeo parecido, igual ou nesse estilo.
when_to_use: Pedidos como quero um vídeo igual a esse, faz nesse estilo, analisa esse reel, como esse vídeo foi editado.
---

# FREMEX · Analisar referência

## 1 · Assistir

Use a skill `watch` com detalhe `balanced`. Para links públicos, qualquer motor serve. Para material privado, use `--engine local`.

## 2 · Medir (números, não impressão)

```bash
# duração e formato
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact ref.mp4
# cortes secos (quantidade de trocas de cena)
ffmpeg -i ref.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -c pts_time
# pausas na fala
ffmpeg -i ref.mp4 -af silencedetect=n=-35dB:d=0.4 -f null - 2>&1 | grep -c silence_end
# volume integrado
ffmpeg -i ref.mp4 -af ebur128 -f null - 2>&1 | grep -A1 Integrated | tail -1
# folha de quadros para examinar
ffmpeg -i ref.mp4 -vf "fps=24/<duração>,scale=200:-1,tile=8x3" -frames:v 1 folha.jpg
```
Poucos cortes com muita mudança visual indica animação contínua, não edição de cortes.

## 3 · Guia de estilo

Escreva `estilo-referencia.md` com:

| Elemento | O que observar |
|---|---|
| Estrutura | gancho, quantidade de blocos, CTA |
| Ritmo | duração, cortes por segundo, pausas |
| Legenda | posição, palavras por vez, cor de destaque, animação |
| Tipografia | família (sem serifa / serifada / mono), peso, combinações |
| Cor | fundo, cor de destaque, quantidade de cores |
| Movimento | transições, câmera, elementos sempre em movimento |
| Áudio | narração, trilha, efeitos, LUFS |

Depois, uma seção **"Como aplicar no nosso vídeo"**: o que será mantido (a linguagem) e o que será trocado pela identidade do cliente (cores, fontes, logo, personagem).

## Regras

- Copiamos a **linguagem**, nunca os **elementos**: nada de logos, personagens, mascotes, músicas ou imagens de outros criadores.
- Não baixe nem reutilize trechos da referência no vídeo final.
