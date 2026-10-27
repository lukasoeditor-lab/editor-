# Regras do estúdio: os números que valem

> Data: 2026-10-22 · Tipo: guia · Status: vigente

**Resumo:** fonte única dos números técnicos de vídeo (mola, câmera, ritmo, volume, render, revisão). Quando uma skill, tutorial ou conversa disser outro número, vale este arquivo. São pontos de partida testados, não proibições: se a peça pedir outro valor, use e anote no projeto. Mudou um número de vez? Atualize aqui, com a data.

## Movimento

| Regra | Valor de partida |
|---|---|
| Mola padrão (card, botão, balão, notificação, selo) | sobe ~12% além do alvo e assenta em ~0,6 s. No After Effects: chaves lineares 0→100 em 0,25 s + expressão de inércia (amplitude 0,05 · frequência 2 · decaimento 4) |
| Mola em código (HTML, Remotion) | `1 − e^(−ζωt)(cos ω_d·t + (ζω/ω_d)·sen ω_d·t)` com ζ 0,56 e ω ≈ 12; interface mais firme: ζ 0,62–0,78 e ω 13–17. Valor com vários alvos = soma de uma mola por mudança |
| Curva de câmera e troca de cena | cubic-bezier(.86, 0, .07, 1) para trocas rápidas; (.33, 0, .23, 1) para câmera viajando num quadro contínuo |
| Câmera nunca morta | deriva contínua lenta + balanço suave num objeto pai. Parada completa só de propósito, em 2 ou 3 momentos-chave, e anotada no projeto |
| Câmera com propósito | todo movimento além da deriva tem início, fim, curva e um porquê. Nenhum movimento abaixo de ~0,8 s, exceto chicote (~0,27 s) e mergulho em Z (~0,37 s) |
| Entrada e saída | entrar já em movimento (desacelerando); sair acelerando ou com desfoque, cortando no pico. No máximo um quadro congelado |
| Nada antes de ser dito | o elemento entra quando a palavra é falada; a tela só troca depois da fala |
| Ritmo | algo novo a cada ~1 s; troca de cena a cada ~2 s, na primeira palavra da frase; nunca mais de 1,5 s sem nada mudar. Tutorial narrado: storyboard primeiro, cada elemento com propósito, sem poluir |
| Texto de destaque | sempre com acabamento: degradê, brilho, textura ou contorno |
| Digitação na tela | teclado subindo e teclas reais; nunca texto "esticando" por máscara |
| Motion blur | telas e UI: obturador de 70° e fase de 40°; câmera rápida pode ir a 180° |

## Áudio

| Regra | Valor de partida |
|---|---|
| Volume final (narrado) | −14 LUFS integrado, pico real ≤ −1 dBTP; normalizar com `loudnorm` em duas passagens |
| Música sob a voz | ~15 dB abaixo da voz, com volume estável (variação de curto prazo ≤ 2–3 dB) |
| Faixa real num mix sem voz | nivelar o trecho a −19 LUFS antes de somar os efeitos, efeitos ×2,2, limitador e então −14 LUFS |
| Efeitos sonoros | biblioteca nivelada (`scripts/som/nivelar.py`); volume relativo à voz entre 0,2 e 0,6 |
| Sincronia do efeito | `início = evento − pico_ms/1000` (o pico de cada arquivo fica no `catalogo.json` da biblioteca). Alvo: erro mediano ≤ 25 ms |
| Som de cena (ambiência, passos, objetos) | peça só com som de cena: −25 LUFS integrado; com voz, pelo menos 15 LU abaixo dela. Conferir com `scripts/som/verificar_som_de_cena.py` |
| Som que descreve a ação | cada movimento tem o som do que se vê, com a duração do gesto. Som tonal (nota musical) só em momento de hype, troca de cena ou surpresa |
| Batida da música | medir com `scripts/som/batida.py` (beat_this) antes de cortar na batida; o BPM de catálogo costuma estar errado |
| Respiro antes do drop | zerar o instrumental ~0,5 s antes do drop e pôr a palavra-chave no primeiro quadro dele |
| Voz | narração seca, sem reverb nem eco |

## Corte de pregação (Pregue)

Medidos nas 5 referências do Lukas ([estilos-pregue](../03-referencias/analises/2026-10-27-estilos-pregue.md)); valem para cortes verticais de 45 a 75 s.

| Regra | Valor de partida |
|---|---|
| Legenda | 4,5 a 6% da largura (≈ 50–65 px em 1080 px), minúscula, bold 700–800 (estilo B: 300), entrelinha ~0,95, sem caixa; do peito para baixo, nunca no rosto |
| Palavra-chave | serifa itálica 1,8 a 2,2× a legenda; entrada com desfoque 14 px → 0, `scale 1,25 → 1`, 0,27 s `expo.out`; 1 a 3 por frase |
| Entrada de palavra | no quadro em que é falada; 0,14 s com desfoque 6–9 px e subida de 8–16 px |
| Troca de plano / flash | 3 a 4 quadros (≈ 0,13 s) com flash de luz; sem dissolve longo |
| Plano | troca de enquadramento a cada ~6 s (zoom 1,0 ↔ 1,16/1,24; palavra-chave até 1,3 em 1080p de câmera aberta) |
| Popup de notificação | topo, ~85% da largura, 2,5–3 s; dentro do primeiro terço do vídeo |
| Interlúdio escuro | no máximo 2 por corte, 1,5 a 2,5 s, com flash de 0,07 s na entrada |
| Cores | título vermelho #DC2427; amarelo #F7D903 só na fala do "outro" em P&B; resto branco |
| Fecho | queima de filme (0,1–0,55 s) → preto → marca desenhada em ~1,8 s → parada ≥ 2 s |
| Mix | voz −16 LUFS; música 14 dB abaixo; efeitos no nível dos picos da fala; final −14 a −16 LUFS, pico real ≤ −3 dBFS depois do limitador (0,68) |
| Render | 1080×1920, 30 qps, `-q looks`; ~0,5 s por quadro com a grade em 4 núcleos |

## Render e revisão

| Regra | Valor de partida |
|---|---|
| Ciclo de render | prévia leve a cada ajuste (sem desfoque, meia resolução); final uma vez; depois, só o trecho que mudou |
| Caminho do render | pasta sem acento nem "ç" (alguns renderizadores quebram); pasta de saída nova por vídeo |
| Motion blur em HTML | renderizar a 240 qps e juntar 4 quadros em 1 (`tmix=frames=4`) para sair a 60 qps |
| Cor | etiquetar BT.709 na junção (`-colorspace bt709 -color_primaries bt709 -color_trc bt709`) |
| Extrair quadros para revisar | `ffmpeg -i video.mp4 -ss <tempo> ...` (o `-ss` depois do `-i`) |
| Depois de todo render | `scripts/video/detectar_saltos.py`: todo salto que sobrar tem que ser corte de propósito |
| Comparação final | referência e o seu vídeo lado a lado, mesmo tamanho. Além de "está humano?", pergunte "a referência grita mais?" |
| Texto na tela | interface com pelo menos 22 px de texto num vídeo 1080p |
