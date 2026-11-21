# Análise em camadas: corte "correria" (R2), para copiar igual

> Data: 2026-11-21 · Tipo: análise · Status: vigente

**Resumo:** segunda análise da referência R2 ("Se correria fosse boa, o coelho seria o rei da floresta"), agora camada por camada e medida quadro a quadro, para recriar o estilo igual. Completa a [primeira análise](2026-10-27-r2-correria.md). O gerador é `scripts/video/corte_pregacao/gerar_correria.py`, o kit de som sai de `scripts/video/corte_pregacao/preparar_kit_correria.py`, e as fontes ficam em `05-biblioteca/fontes/`.

## Ficha técnica

| Item | Medido |
|---|---|
| Formato | 720×1280, 9:16, 23,976 qps, 37,24 s (32,1 s de fala + 5,1 s de assinatura) |
| Volume | −14,1 LUFS no total; voz isolada −16,9 LUFS; música −19,1 LUFS (só **~2,2 dB abaixo da voz**) |
| Música | batida lo-fi/hip-hop calma, **~125 BPM**, quase toda grave (−4 dB até 300 Hz, −23 dB acima de 1 kHz) |
| Ritmo da fala | sem nenhuma pausa: todos os silêncios cortados, uma frase emenda na outra |

## Camada 1: o vídeo do pregador

- **Cortes secos (jump cuts) a cada 1 a 3 s**, alternando plano **aberto** (corpo até o joelho) e **fechado** (meio corpo). Medidos aos 0,96 · 3,92 · 4,38 · 10,39 · 13,72 · 17,64 · 21,19 · 24,86 · 25,44 · 29,28 s. O pregador fica sempre no centro, com a cabeça no terço de cima.
- **Câmera parada** dentro de cada plano (sem zoom nem movimento).
- **Cor:** a do próprio ambiente (palco vermelho-tijolo, LED azul), com um tratamento quente e grão leve. **Não copiamos o tratamento**, porque filtro deixa com cara de IA (pedido do Lukas em 20/11). A cor vem do ambiente do vídeo novo.
- **Preto e branco** em dois momentos, sempre que ele **cita a fala de outra pessoa ou a Bíblia**: "tô numa correria" (14,3–15,6 s) e Salmo 127, "do que adianta…" (19,0–23,2 s). Entra e sai sempre por baixo de uma transição.

## Camada 2: legenda

| Item | Valor |
|---|---|
| Fonte | grotesca **condensada** tipo Helvetica Neue Condensed → usamos **Nimbus Sans Narrow** (clone livre da Helvetica Narrow) com contorno de 0,6 px para engrossar |
| Tamanho | ~73 px no vídeo de 720 → **100 px em 1080** |
| Cor | branca; **amarela #F7D903 no preto e branco** |
| Caixa | minúscula (nomes próprios e "Deus" com maiúscula), sem pontuação |
| Espaçamento | entre letras −0,02em; **1 linha de até 3 palavras = palavras bem separadas** ("gaste   um   tempo"); bloco de 2 a 4 linhas = espaço normal |
| Entrada da palavra | no instante em que é falada: **sobe ~45 px, desfocada e esticada na vertical, e fica nítida em 3 quadros (0,13 s)**; nada de fade lento |
| Saída | o bloco some de uma vez quando o próximo começa |
| Posição | na altura do peito (45 a 55% da altura). Alterna: centro, esquerda (x≈6%) e alinhado à direita. Às vezes um pedaço vai para o outro lado, mais embaixo ("enquanto / dormem" e "vontade / de Deus" à direita) |
| Agrupamento | frases curtas = 1 linha de 2 a 4 palavras; frases importantes = bloco que se monta linha a linha ("estou na boa / perfeita e / agradável") |

## Camada 3: transições (7 no total, todas em fim de frase)

| Tipo | Quando | Como é (quadro a quadro, 24 qps) |
|---|---|---|
| **Queima de filme** | 6,72 · 14,31 · 18,98 · 32,12 s | 5 quadros (~0,2 s): luz creme e laranja estoura por cima de tudo, com manchas vermelhas nas bordas; no pico a tela fica quase toda creme. O corte de plano acontece no pico |
| **Flash branco** | 9,55 · 15,56 · 23,23 s | quadro 1: faixa de luz **prismática** (azul, branco, amarelo, vermelho) varre a partir da esquerda; quadros 2 e 3: **tela toda branca**; quadros 4 e 5: **arco de luz branca** no alto (como uma cúpula) que some subindo |

A queima marca a troca de cor: entra no P&B ou vai para o fim. O flash marca a volta à cor ou uma troca simples de plano.

## Camada 4: som

- **Voz** na frente, sem pausas, sem eco.
- **Música** contínua do começo ao fim, ~2 dB abaixo da voz. Ela termina junto com a assinatura e some em ~0,5 s.
- **Efeito em cada transição** (7 no total): chiado/estalo **agudo** curto (centro em 3 a 4,5 kHz, ~0,15–0,2 s), 3 a 6 dB acima da música só nos agudos. A queima tem um ataque mais seco, e o flash um chiado um pouco mais longo. Não há efeito por palavra nem whoosh grave.
- Kit recriado: `preparar_kit_correria.py` separa a música da voz, tira os efeitos dela e salva os dois efeitos isolados.

## Camada 5: fecho

- Queima de filme → **tela preta** → **assinatura manuscrita** que se desenha da esquerda para a direita em ~1,8 s e fica parada até o fim (5 s no total).
- Fonte manuscrita: **Mrs Saint Delafield**. Na referência a assinatura é do Filipe Levak; no nosso vídeo vai o nome do pregador ou a marca, com o @ embaixo.

## Como recriar (passo a passo)

1. Kit: `python3 preparar_kit_correria.py <referência.mp4> /tmp/work/kit_correria/`.
2. Vídeo do pregador: voz isolada, todos os silêncios cortados (bordas pela energia da voz, ver aprendizados de 19 e 21/11), quadro vertical com o pregador no centro e a cabeça no terço de cima, alternando **aberto** e **fechado** a cada trecho, trechos de citação em P&B (no ffmpeg, `hue=s=0`). Sem nitidez, cor ou grão.
3. Roteiro `blocos` + `transicoes` + `assinatura` (formato no topo do `gerar_correria.py`): transição em cada troca de assunto ou de cor (queima ao entrar no P&B, flash ao voltar), uma a cada 3 a 6 s.
4. `python3 gerar_correria.py roteiro.json proj/`, `hf.sh check`, `snapshot`, `render`, `misturar_audio.py`.

## Conferido

Recriei a própria referência com o gerador e comparei quadro a quadro (21/11): a legenda bate em tamanho, posição, fonte e entrada; a queima e o flash batem quadro a quadro, depois de ajustar o tempo do arco; a assinatura bate.
