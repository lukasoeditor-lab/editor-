# Análise: corte de pregação "lenha" (Estilo A, o mais próximo do que o Lukas quer)

> Data: 2026-10-27 · Tipo: análise · Status: vigente

**Resumo:** corte vertical de 41 s de uma pregação, com legenda pequena em negrito, palavra-chave grande em serifa itálica que nasce desfocada, um popup de notificação pedindo para seguir e um fecho com "queima de filme" e assinatura desenhada. É a referência principal para os cortes da Pregue. Mídia: `03-referencias/motion/2026-10-27-r5-sacrificio.mp4`. Origem: arquivo enviado pelo Lukas em 27/10/2026 (perfil que ele admira: o editor do Filipe Levak).

## Ficha

| Item | Valor medido |
|---|---|
| Formato | 720×1280, 9:16, 29,97 qps, 41,4 s |
| Trocas de plano | 6: aos 2,0 · 7,8 · 13,3 · 15,7 · 25,7 · 36,5 s (cada uma dura ~4 quadros, ~0,13 s) |
| Plano médio por trecho | ~6 s; o que dá movimento é o texto, não o corte |
| Loudness do arquivo final | −14,1 LUFS, pico −1,5 dBFS, LRA 2,2 |
| Voz isolada | −18,8 LUFS (a separação deixou resíduo de voz na faixa de música; trate como estimativa) |
| BPM da música | ~92 (batida lenta, cama contínua) |
| Cena | palco laranja-avermelhado com letreiro azul-claro gigante atrás do pastor; roupa verde-petróleo escura |

## Estrutura (o que acontece, no tempo)

| Tempo | O que aparece |
|---|---|
| 0,0–2,0 | Plano médio. Legenda branca, 1 palavra por vez, empilhada no peito: "ninguém / pode / buscar" e a palavra-chave em serifa itálica ("lenha") entra desfocada e fica nítida |
| 2,0 | Troca de plano (zoom de enquadramento) |
| 2,0–7,8 | Frases curtas: a legenda cresce em bloco de 2 a 4 linhas e some quando a frase acaba. Palavras-chave em serifa itálica: "do **pastor**", "**ninguém**", "**você**" (a serifa aparece 1 a 3 vezes por frase) |
| 7,8–13,3 | Mesmo plano, palavras espalhadas pelo corpo ("quando somente você tem que tocar o céu" em 4 posições diferentes) |
| 13,3 | Plano aberto, pastor ajoelhado: legenda simples "dobrar o joelho" |
| 15,7–16,3 | Corte; **popup de notificação** desce do topo (banner branco com foto, nome e "aproveita pra me seguir") e fica ~2,7 s |
| 16,3–25,7 | Frases: "cada vez que você ora / serve / oferta"; serifa em "colocando" e "oferta" |
| 25,7 | Troca de plano |
| 25,7–35 | "existe fogo" em serifa grande; palavras espalhadas; "recursos" em serifa apagada |
| 35,3 | Último destaque: "**valioso**" em serifa e "a **Deus**" em sans negrito |
| 36,5–37 | **Queima de filme** (flash laranja/vermelho com "FILM" na borda) cobre a imagem |
| 37–41,4 | Fundo preto; assinatura manuscrita branca é desenhada traço a traço em ~1,8 s e fica parada |

## Gramática de movimento (texto)

| Recurso | Onde | Como |
|---|---|---|
| Legenda sans | peito do pastor, centro horizontal, ~55% da altura | negrito, minúscula, entrelinha apertada (≈0,9), letras quase encostadas; ~4,5 a 6% da largura do quadro (≈ 42 px em 720 px); branca com sombra suave |
| Entrada de palavra | cada palavra no instante em que é falada | fade de 3–4 quadros, sobe uns 6–10 px; as palavras anteriores ficam; o bloco inteiro some quando a frase muda |
| Serifa itálica (palavra-chave) | no meio do bloco, ~2× o tamanho da sans | entra com desfoque ~10–14 px e opacidade baixa e fica nítida em ~8 quadros (0,27 s); brilho suave em volta; sem tremida |
| Posição das palavras | blocos de 1 a 4 linhas | a próxima palavra cai na linha de baixo ou ao lado; às vezes a palavra fica "solta" longe do bloco |
| Palavra apagada | fim de frase | a última palavra fica em cinza claro, com desfoque, quase transparente, antes de sumir |
| Popup de notificação | topo, ~85% da largura, ~5% da altura, margem ~1,5% | desce com leve overshoot e desfoque; avatar redondo + nome em negrito + texto curto; some sozinho. Serve de CTA ("seguir") sem interromper a fala |
| Troca de plano | 6 vezes em 36 s | enquadramento muda (mais aberto/mais fechado) em ~4 quadros com mistura rápida; o texto continua |
| Fecho | 36,5–41,4 s | queima de filme (2 a 4 quadros) → preto → assinatura desenhada → parada; nada mais |

## Tipografia (aproximação com fontes que o estúdio tem)

| Papel | Na referência | Use aqui |
|---|---|---|
| Legenda | grotesca neo-realista bold (parece Helvetica Now / Inter Display Bold), minúscula | Inter 700 ou Montserrat 700 |
| Palavra-chave | serifa itálica de alto contraste, estilo editorial | Playfair Display Italic 700 (a mais próxima das fontes incluídas); alternativa fora da lista: PP Editorial New Italic |
| Assinatura | caligrafia fina, traço contínuo | desenhar a marca da Pregue com traço animado (ver skill `corte-de-pregacao`) |

## Cor

- Cena: fundo laranja-queimado (~#A75338 medido), letreiro azul-claro (~#7EB5C0), roupa em verde-petróleo escuro: contraste complementar laranja × azul-petróleo.
- Grade: sombras frias esverdeadas, pele quente, grão de filme visível, vinheta leve.
- Texto: branco puro; nenhuma cor de destaque (o destaque vem da fonte serifada e do desfoque, não da cor).

## Som (medido, com limites)

| Tempo | Evento visual | Evento sonoro estimado |
|---|---|---|
| 16,2 | popup de notificação | transiente claro (+6 dB sobre a cama): som de notificação curto |
| 25,5 | "existe fogo" em serifa | golpe grave (+1,6 dB), seguido de subida de intensidade |
| 26,8–34 | blocos de palavras | série de golpes graves de música/impacto (+4 a +6 dB) alinhados às frases |
| 36,5 | queima de filme | transiente + cauda; depois a música cai e a assinatura fica quase em silêncio |

Cama de música sempre presente, estável, sem pausas; a voz fica no primeiro plano. Número completo e limites da medição estão em [estilos-pregue](2026-10-27-estilos-pregue.md).

## O que copiar

1. Legenda mínima: pequena, bold, sem caixa, sem fundo, palavra a palavra.
2. Uma palavra-chave por frase em serifa itálica com desfoque de entrada; no máximo 3 por frase.
3. Popup de notificação como CTA no primeiro terço do vídeo.
4. Fecho: queima de filme → preto → marca desenhada.
5. Texto nunca cobre o rosto: fica do peito para baixo.

## O que não copiar

- A assinatura é do Filipe Levak. Use a marca da Pregue / Lukas.
- O nome e a foto do popup: troque pelos da Pregue.
