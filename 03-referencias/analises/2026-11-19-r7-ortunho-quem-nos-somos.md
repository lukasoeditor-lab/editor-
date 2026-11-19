# R7: corte "Quem que nós somos" (Pr. Rodrigo Ortunho)

> Data: 2026-11-19 · Tipo: análise · Status: vigente

**Resumo:** corte vertical de 26 s enviado pelo Lukas como modelo ("faça do mesmo jeito"). Legenda pequena que se monta palavra a palavra, com a palavra-chave em serifa itálica condensada; cor arroxeada; trecho em preto e branco com passagem pelo preto; cortes de enquadramento (perto/aberto); assinatura com foto e selo; cartão final preto "COMENTE EU CREIO". A música de fundo **não** bate com nenhuma das 5 músicas que o Lukas mandou (comparação de croma: nenhuma acima de 0,35; uma igual daria perto de 1).

## Arquivo
- `SaveClip.App_...mp4`, 720×1280, 30 fps, 26,4 s (baixado do Instagram).

## Fala (transcrição da voz isolada)
"Quem que nós somos, meu irmão? Quem que nós somos? Se Deus não for comigo, quem eu sou? Eu sou um pedidor de esmola, eu sou nada. É Jesus que te fez livre de pedir esmola. Foi Jesus que nos libertou. Foi Jesus que nos fez forte. Diz o Senhor: diga o fraco, forte sou. Quando eu sou fraco, é aí que eu sou forte, diz o Senhor dos exércitos. Aleluia!"

## Linha do tempo (aproximada)
| Tempo | O que acontece |
|---|---|
| 0–0,5 s | Abre do preto (fade in) já com a fala, plano fechado no rosto. Gancho = pergunta "Quem que nós somos?" |
| ~2,5 s | Corte para plano mais aberto com o telão de árvore vermelha atrás (cor quente contra o roxo) |
| ~6,5 s | Mergulho no preto (~0,3 s) e volta em **preto e branco** |
| 7–13 s | P&B: "eu sou nada… é Jesus que te fez livre… foi Jesus que nos libertou" |
| ~13 s | Mergulho no preto e volta à **cor** em "foi Jesus que nos fez forte" |
| 15–18 s | Fala mais forte; outro mergulho curto no escuro em "forte" (~17 s) |
| 18–24 s | Planos alternando perto/aberto a cada frase; "Aleluia!" sozinho em serifa itálica |
| ~25 s | Fade para preto; cartão "COMENTE / EU CREIO" (caixa alta, branco, pequeno, centro) até o fim |

## Legenda
- Pequena (≈ 4 % da altura), branca, centralizada a ~60 % da altura, no máximo 2 linhas, sem caixa nem contorno; sombra leve.
- Sans de peso médio com espaçamento bem apertado (parecida com SF Pro/Inter).
- Monta a frase **palavra a palavra** (a palavra nova entra apagada e acende); a frase inteira fica até a próxima.
- **Palavra-chave** (Jesus, fez, livre, Senhor, sou, forte, Aleluia) em **serifa itálica condensada**, um pouco maior. "Aleluia!" aparece sozinho só em serifa.

## Imagem
- Cor: roxo/azul frio nas sombras, pele preservada; vinheta escura e gradiente preto embaixo (onde fica a assinatura).
- Enquadramento muda a cada frase (corte seco perto ↔ aberto), sem zoom animado.
- Assinatura fixa embaixo: foto redonda com borda em gradiente (estilo Instagram), nome em caixa alta "PR. RODRIGO ORTUNHO" com selo azul de verificado, @ menor embaixo.

## Som
- Voz na frente; música instrumental baixa e constante (tonalidade de lá maior); sem efeitos sonoros marcados nas trocas.

## Como reproduzir no estúdio
- Motor: `gerar_projeto.py` estilo A/B (legenda pequena + serifa na palavra-chave) com `pb` para o trecho P&B, cortes de enquadramento por trecho em vez de zoom animado, cartão `no_fim` "COMENTE / EU CREIO" e assinatura com foto + selo (precisa da foto e do @ do pregador).
- Fonte da serifa condensada: usar a serifa itálica disponível (Playfair Display Italic) ou trocar por uma condensada se o Lukas tiver o arquivo.
