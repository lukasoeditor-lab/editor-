# Análise: devocional "tempestade" (Estilo C, cinema com IA e apresentador)

> Data: 2026-10-27 · Tipo: análise · Status: vigente

**Resumo:** vídeo horizontal (3:2) de 88 s com um apresentador falando para a câmera e cenas de cinema geradas por IA (tempestade, barco, Jesus sobre as águas) que ilustram a história. Abertura de ~25 s é um trailer rápido com títulos gigantes em serifa vermelha; depois vem a fala com legenda pequena e cortes para cenas de IA. É a referência para vídeos explicativos e devocionais com B-roll gerado, não para cortes de altar. Mídia: `03-referencias/motion/2026-10-27-r1-tempestade.mp4`. Origem: arquivo enviado pelo Lukas em 27/10/2026.

## Ficha

| Item | Valor medido |
|---|---|
| Formato | 1080×720 (3:2), 24 qps, 88,6 s |
| Trocas de plano | 22 detectadas; 12 delas nos primeiros 2 s (montagem rápida de abertura), depois aos 3,2 · 8,5 · 11,0 · 14,8 · 16,7 · 18,5 · 22,4 · 23,6 · 25,3 s; o resto é um plano contínuo do apresentador |
| Loudness | −14,3 LUFS, pico +0,9 dBFS (passa de 0: limitar), LRA 3,5 |
| Voz isolada | −16,4 LUFS; música + efeitos −22,0 LUFS (música ~5,6 dB abaixo da voz, mais alta que o padrão do estúdio) |
| BPM | ~96, trilha cinematográfica contínua |

## Estrutura

| Tempo | O que aparece |
|---|---|
| 0–2 | Montagem relâmpago (cada plano 0,1 a 0,4 s): imagens em preto e branco estourado, ondas, mão estendida; palavras vermelhas "ROUBADO" aparecem com fade e leve desfoque |
| 2–8 | Cenas de IA mais longas: título **"JESUS"** em serifa vermelha gigante ocupando toda a largura, por cima do mar; depois "PEDRO" menor sobre o rosto do personagem; legenda branca bold minúscula no pé da imagem ("sobre aquilo", "que deveria fazer") |
| 8–25 | Alterna apresentador e cenas de IA: Pedro afundando, mão estendida, "estende a mão" com a segunda palavra apagada |
| 25–86 | Apresentador em plano fechado, fundo laranja/azul-petróleo. Legenda **minúscula, branca, no canto esquerdo inferior**, 1 a 3 palavras por vez, quase sem animação (troca seca); a última palavra de cada grupo fica cinza e desfocada |
| 86–88 | Fecho |

## Gramática de movimento

| Recurso | Onde | Como |
|---|---|---|
| Título em serifa vermelha | primeiros 10 s | caixa-alta, serifa de alto contraste (tipo Bodoni/Didot), vermelha (~#DC2427 medido, #D9050C no "ROUBADO"); gigante, largura quase total (JESUS) ou média (PEDRO); entra com fade + leve zoom de 4–6 quadros e sai com fade |
| Legenda de cena | pé do quadro, centro | branca, sans bold minúscula, tamanho médio (~3% da largura) |
| Legenda de apresentador | canto esquerdo, ~28–30% da altura de baixo | branca, sans bold, minúscula, **muito pequena** (~1,5–2% da largura), troca seca |
| Palavra apagada | última do grupo | cinza e desfocada antes de sumir |
| Cenas de IA | cortes a cada 2–6 s | câmera sempre em movimento (empurrão, deriva), grade fria azul-aço com contraste alto; rostos e mãos em plano fechado; nenhum corte seco "parado" |
| Apresentador | plano fixo | grade quente à esquerda e luz azul-petróleo estourada à direita (luz de contra); sem punch-in |

## Tipografia

- Título: serifa Didone condensada, maiúscula → Playfair Display 700/900 em caixa-alta, cor #DC2427.
- Legenda: grotesca neutra bold (Helvetica Now / Inter) minúscula → Inter 700.

## Som

- Trilha cinematográfica contínua (BPM ~96); a análise acha golpes fortes (+15 dB sobre a mediana) em 0,3–0,6 s: impacto/trailer de abertura que acompanha a montagem rápida e o aparecimento de "ROUBADO". Depois a faixa fica mais estável.
- Música mais alta que a do corte vertical (~5,6 dB abaixo da voz); para o estúdio, siga as regras em [06-metodo/regras.md](../../06-metodo/regras.md) (~15 dB) a menos que o vídeo seja trailer.

## O que copiar

1. Abertura de trailer: 2 s de montagem muito rápida + título gigante em serifa vermelha.
2. Legenda do apresentador pequena e discreta (não disputa com o rosto).
3. Cenas de IA com câmera sempre em movimento e grade fria para ilustrar histórias bíblicas.

## Cuidados

- Pessoas reais geradas por IA: não use rosto de pessoa real sem autorização; mantenha personagens fictícios.
- Pico acima de 0 dBFS no arquivo de origem: aplicar limitador a −1 dBTP.
