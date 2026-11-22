# Análise em camadas: corte "CUIDADO com gente que te diz" (R8, Jezabel)

> Data: 2026-11-22 · Tipo: análise · Status: vigente

**Resumo:** referência que o Lukas mandou em 22/11 para copiar igual, mudando só as cores para a identidade de cada vídeo. É um corte de 86 s de um pregador de paletó lilás num palco com LED azul-petróleo e roxo, com tipografia mista (condensada pesada na frente e serifa itálica atrás), citações empilhadas, palavras com brilho, tela vermelha, P&B, cartão e cliques. O gerador é `scripts/video/corte_pregacao/gerar_r8.py`, e o kit de som e as fontes estão descritos abaixo.

## Ficha técnica

| Item | Medido |
|---|---|
| Formato | 1080×1920, ~24 qps, 86,2 s (83,5 s de fala + 2,7 s de fecho) |
| Volume | −15,4 LUFS no total; voz −16,5 LUFS; fundo musical −30,9 LUFS (**~14 dB abaixo da voz**) |
| Fundo musical | "pad" de teclado sustentado (Ré, Lá, Sol graves), sem batida, quase inaudível; entra devagar nos primeiros 5 s |
| Fala | sem pausas; cortes secos entre frases |

## Camada 1: vídeo

- **Duas câmeras**: fundo roxo (lateral) e fundo azul-petróleo (frontal), alternando em cortes secos a cada 1 a 4 s; às vezes plano mais fechado do rosto.
- **Câmera parada** dentro de cada plano.
- **P&B** (11–17 s) na citação da fala de outra pessoa ("Ah, se você sair daqui…"), entrando por um **clarão quente** (vazamento de luz laranja da esquerda, ~0,5 s).
- **Zoom com desfoque** na troca para "A Bíblia" (17,0 s): a imagem chega grande e desfocada e assenta em ~0,3 s, com um whoosh.
- **Cartão** (25,9–26,9 s, "Aí Jesus vai dizer"): o vídeo vira um **cartão largo de cantos redondos** no meio da tela preta (mostra o palco aberto) e volta.
- **Tela vermelha** (26,9–29,5 s, "a minha dor é que vocês estão TOLERANDO isso"): o plano inteiro em monocromático vermelho e preto.
- **Fecho**: escurece em ~0,6 s, um **coração branco** pulsa, e entra o **logo** da igreja.

## Camada 2: tipografia (uma fonte na frente, outra atrás)

| Tipo | Como é | Fonte | Exemplo |
|---|---|---|---|
| Legenda simples | 1 ou 2 palavras, branca, pequena (~50 px), no peito (50% da altura), troca a cada palavra/expressão | condensada pesadíssima → **Archivo** peso 850, largura 62 | "Gratidão", "arranjo", "o povo de Deus" |
| Palavra digitada | CAIXA-ALTA gigante (~155 px) **digitada letra a letra** em ~0,7 s, com **palavrinhas soltas em volta** (em cima à esquerda e à direita, embaixo à esquerda e à direita) que aparecem quando são ditas | Archivo | "CUIDADO" + que / te diz / com / gente |
| Citação | bloco **alinhado à esquerda** (x≈8%), linhas grandes (~135 px) com entrelinha apertada (0,84), aspas; **cada linha entra deslizando da esquerda com desfoque** | Archivo | “depois / de tudo / que eu fiz / por você” |
| Combo | palavra forte condensada **na frente** + **serifa itálica colorida atrás e embaixo**, encostada | Archivo + **DM Serif Display Italic** | "Gratidão" + *é laço*; "Doutrina" + *de Jezabel* |
| Serifa lateral | serifa itálica branca, 2 linhas, de um lado; depois outra do lado oposto, mais embaixo | DM Serif Display Italic | *tornar / infidelidade* (esq) · *algo normal / aceitável* (dir) |
| Brilho | palavra na cor do LED com **brilho (glow)**, entra **esticada e borrada na vertical**; repete em sequência | Archivo | NARCISISMO, narcisista ×3 (ciano) |
| Grande | CAIXA-ALTA branca grande | Archivo | TOLERANDO |
| Pilha | palavras grandes empilhadas, a última na cor forte | Archivo | Eu / estou / **chateado** (vermelho) |

**Cores da referência (que mudam conforme o vídeo):** destaque com brilho = ciano #3FD9E8 (a cor do LED do palco); quente (citação no P&B e serifa) = laranja #F0612A; forte = vermelho #E5211E (pilha e tela vermelha). No nosso vídeo, as três cores vêm do ambiente: o destaque é a cor mais forte do fundo, o quente é a cor complementar quente e o forte é a cor mais saturada e escura do ambiente.

## Camada 3: efeitos sonoros (medidos no instrumental separado)

- **Clique** curto (10–20 ms, agudo, centro ~3,7 kHz) em **cada linha de citação** que entra (3,14 · 3,68 · 3,90 · 4,18 · 4,60 · 12,1 · 12,8 · 13,3 · 13,6 · 14,4 s), em cada **serifa** (34,0 s) e em cada palavra da **pilha**.
- **Whoosh** no zoom com desfoque (17,08 s) e no clarão.
- **Glitch** (série de estalos, 21,7–22,4 s) quando entra a palavra com brilho.
- **Som do cartão** (25,98–26,24 s).
- **Brilho/sininho** no coração do fim (84,2 s).
- **Legenda simples não tem som.** O som marca só os textos "especiais".

## Kit recriado

- `kit/clique.wav`, `whoosh.wav`, `glitch.wav`, `cartao.wav`, `fim.wav`: cada efeito isolado do instrumental com passa-altas.
- `kit/pad.wav`: o fundo musical (30–80 s do instrumental com os agudos dos cliques tirados), repetido com fusão longa.
- Fontes em `05-biblioteca/fontes/`: Archivo (variável) e DM Serif Display Italic.

## Conferido

Recriei os primeiros 30 s por cima da própria referência e comparei quadro a quadro (22/11). A posição e o tamanho de CUIDADO e das palavrinhas, da citação, do combo, de NARCISISMO, do cartão e de TOLERANDO batem, com a mesma fonte e o mesmo peso.
