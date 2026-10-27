# Estilo editorial: fala + cartões tipográficos + inserts (referência do usuário, 63 s, 720x1280)

Aprendido de um vídeo de palestra (barbearia/vendas). Não copiar marca, texto nem imagens dele: só a linguagem de edição.

## Estrutura (≈25 trocas em 63 s: uma a cada 2,5 s em média)
Alterna quatro tipos de plano. Nenhum dura mais que ~6 s sem mudar.
1. **Orador falando** (filmagem original, reenquadrada na vertical), com legenda pequena.
2. **Cartão tipográfico em fundo branco** (1,5 a 3 s): as palavras-chave da frase viram tipografia, sem imagem.
3. **Insert de cena de filme/série** (meme) em cartão com cantos arredondados sobre fundo branco, com a mesma legenda por cima.
4. **Plano em preto e branco** (com grão) para enfatizar uma fala, voltando à cor depois.

## Legenda (a mesma da referência anterior)
Palavra por palavra, 1 a 3 palavras, branca, sans bold tipo Helvetica com tracking negativo, minúscula nos cartões e
maiúscula/minúscula conforme o vídeo, no centro do corpo do orador (~50% da altura), borrão que some em ~0,2 s.
Implementada em `src/corte/LegendasSimples.tsx` (`--simples`).

## Cartão tipográfico (o que o diferencia de edição básica)
- Fundo branco liso, texto que **cresce com a fala**: cada palavra entra no instante em que é dita e o conjunto se
  recompõe (não aparece a frase pronta).
- **Contraste de escala e de família**: palavras-chave GRANDES em serifa itálica (estilo Playfair/“Instrument Serif”),
  conectivos PEQUENOS em sans (“a sua”, “ela precisa”, “uma narrativa”). Proporção ~1:4 a 1:6.
- **Entrelinha negativa**: as linhas se sobrepõem levemente (lockup apertado), alinhadas no centro.
- **Cor como ênfase, no máximo 3 por cartão**: preto, vinho/vermelho escuro e azul-marinho. Cada cor marca um
  conceito (ex.: a ideia central em vinho, a ação em azul). Nunca mais que uma palavra por vez em cor nova.
- Palavras repetidas na fala (“desejo”, “vontade”) trocam de lugar/cor no cartão seguinte, mostrando evolução.
- Duração: o cartão fica só enquanto a frase é dita (1,5 a 3 s); corta em cima da palavra final.

## Transições
- **Estouro de luz → branco → corte**: faixa vertical de luz atravessa o quadro (light leak), a imagem estoura em branco
  e a próxima cena abre do branco. Serve para ir do orador ao cartão e do cartão ao plano em P&B.
- **Corte seco na palavra** quando o cartão branco entra (sem fade); o cartão é parte do ritmo, não um intervalo.
- **P&B com grão** (`grayscale(1) contrast(1.2)` + grão) em 1 a 2 frases de ênfase; volta à cor com outro estouro de luz.
- **Zoom/reenquadramento a cada troca**: nunca dois planos seguidos com o mesmo enquadramento do orador.
- **Borrão de entrada** (blur ~12 px → 0 em 5-6 quadros) nas primeiras palavras de uma cena.

## Insert de cena (meme/B-roll)
Cena curta (2 a 3 s) com a fala por cima, em cartão de cantos arredondados (raio ≈ 6% da largura) centralizado em
fundo branco. Precisa de material de terceiros: **pedir ao usuário o clipe ou a autorização de uso**; não baixar.

## Ritmo e som
- A fala nunca é cortada no meio da palavra; a troca de plano cai no fim da frase ou na palavra de ênfase.
- Não consegui ouvir o áudio: não afirmo quais efeitos sonoros ele usa. Para o som, seguir `estilo-visual-e-sonoro.md`
  (clique/whoosh curtos e baixos nas trocas de cena; voz sempre ≥ 6 dB acima).

## Como aplicar (receita)
1. Transcrever com tempo por palavra e marcar, por frase, o tipo de plano (orador, cartão, insert, P&B).
2. Escolher 1 palavra-conceito por frase para os cartões (em serifa grande) e 2 a 4 conectivos pequenos.
3. Trocar de plano a cada 2 a 4 s; usar P&B só em 1 trecho de ênfase.
4. Transições: estouro de luz com clique ao entrar/sair do cartão, nunca fade lento.
5. Conferir quadros-chave em folha de contato antes de renderizar.
