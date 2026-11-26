# R9 "Íntimos de Deus" (Pr. Wilton Santos): análise em camadas

> Data: 2026-11-26 · Tipo: análise · Status: vigente

**Resumo:** referência do estilo 9, enviada pelo Lukas em 26/11. É um corte calmo de 54 s, vertical 720×1280 a 30 fps, em que quase toda a edição está na legenda. A legenda aparece palavra a palavra em sans geométrica bem apertada, e a palavra-chave entra em serifa itálica maior com brilho branco. Completam o estilo a assinatura com foto, um degradê escuro embaixo e mergulhos lentos no preto. O gerador é `scripts/video/corte_pregacao/gerar_r9.py`.

## Fala e estrutura (54,3 s)

| Tempo | Trecho | Imagem |
|---|---|---|
| 0–10,2 | "Quem constrói intimidade com Deus em dias comuns, não vai desmoronar em tempos difíceis" (gancho) | colorido; sai do preto em 2,8 s |
| 10,2–19,9 | a mesma frase dita de novo: "…em dias de guerras… em dias difíceis" (eco) | **preto e branco** levemente azulado; legenda maior, cor creme, sem serifa |
| 19,9–34,5 | "Talvez alguém ousou dizer que já morreu… não tem mais jeito, mas hoje Deus te trouxe aqui pra te dizer: vai ter milagre no ambiente improvável" | colorido |
| 34,5–51,1 | "Eu quero profetizar que tá chegando um tempo de viver milagres… Lamentações 3:26 diz: bom é ter esperança" | colorido |
| 51,2–53,5 | "Como está a sua esperança, irmão?" (pergunta final) | colorido; termina com corte seco no preto |

## Camadas, de baixo para cima

1. **Vídeo:** plano médio do pregador (do peito para cima), recortado de um vídeo horizontal e fixo, sem zoom nem tremor. A cor original é quente e lavada (não copiar: regra do Lukas, nada de filtro). O trecho do eco é em P&B.
2. **Texto do telão da igreja** ("João 11.40", "se creres, verás") aparece desfocado embaixo. Faz parte da filmagem, não da edição.
3. **Degradê escuro:** escurece forte o terço de baixo (quase preto na borda) e de leve o topo.
4. **Legenda:**
   - **Posição:** bloco centrado na tela e alinhado à esquerda, com o topo em y ≈ 0,60 (altura do peito ou do púlpito). A largura do bloco é a da linha mais longa da página, então as palavras não mudam de lugar enquanto entram.
   - **Página:** até 2 linhas de 2 a 4 palavras, uma frase curta por página. A página some de uma vez quando a próxima começa.
   - **Sans:** geométrica (a mais parecida é a Plus Jakarta Sans 700), branca, com tracking bem negativo (−0,06 em) e entrelinha 1,0. Tem 34 px no vídeo de 720, o que dá 66 px em 1080.
   - **Serifa:** Instrument Serif Italic, 1,6 vez a sans, em uma palavra-chave por página (constrói, intimidade, Deus, desmoronar, milagre, profetizar, esperança, bom, ter…). Tem um brilho branco suave em volta (glow de 10 e 26 px).
   - **Entrada:** cada palavra entra no tempo da fala, com opacidade de 0 a 1 e desfoque de cerca de 7 px até 0, em cerca de 0,15 s. A serifa entra um pouco mais devagar (0,24 s). Não há movimento de posição.
   - **Trecho P&B:** a sans fica cerca de 1,4 vez maior, na cor creme (#ECEADC), sem serifa.
5. **Assinatura:** fixa, centrada em y ≈ 0,77. Tem foto redonda com anel degradê do Instagram e selo azul de verificado, mais o NOME em caixa-alta bold (34 px em 1080) e o @ em caixa-alta embaixo (23 px).
6. **Preto:**
   - **Abertura:** sai do preto em cerca de 2,8 s.
   - **Mergulhos entre os trechos:** escurecem até o preto em cerca de 1,7 s e voltam em cerca de 1,8 s. Um deles é rápido, 0,35 s + 0,4 s. O preto cobre tudo, inclusive legenda e assinatura.
   - **Fim:** corte seco no preto.

## Som

- **Voz:** só a voz do pregador, a cerca de −17 LUFS. A fala continua por baixo dos mergulhos no preto.
- **Música e efeitos:** não há música de fundo nem efeito sonoro. O "instrumental" separado é só eco da voz: some nas pausas e não tem batida regular.

## Como fazer (gerador)

1. `build.py` cuida da base vertical: tira as pausas, mantém o quadro fixo por trecho e põe o P&B no trecho de eco (exemplo em `exemplo_r9_build.py`).
2. `roteiro.py` monta o roteiro: páginas escritas à mão por faixa de palavras, `*` marca a serifa e `escuro` lista os mergulhos (exemplo em `exemplo_r9_roteiro.py`).
3. Rode `python3 gerar_r9.py roteiro.json proj/`, depois `hf.sh render`, depois `misturar_audio.py`.

## Fontes

As duas fontes estão em `05-biblioteca/fontes/`:

- `PlusJakartaSans-700.woff2` e `-800.woff2`, licença OFL, baixadas do npm `@fontsource/plus-jakarta-sans`.
- `InstrumentSerif-Italic.woff2`, licença OFL, do npm `@fontsource/instrument-serif`.

A serifa bate com a da referência. A sans original pode ser outra geométrica parecida, mas a Jakarta foi a mais próxima entre as testadas: Instrument Sans, Inter Tight, Manrope e Jakarta.
