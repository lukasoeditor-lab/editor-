# A legenda dinâmica das referências (como ela funciona de verdade)

> Data: 2026-10-27 · Tipo: guia · Status: vigente

**Resumo:** o que as referências do Lukas fazem com o texto, medido quadro a quadro, e como o evento `frase` do `gerar_projeto.py` reproduz isso. Não é "uma linha embaixo": é um **bloco estreito alinhado à esquerda que cresce palavra por palavra**, com a palavra-chave em serifa itálica na própria linha. Fontes da medição: [r5 "lenha"](../../../03-referencias/analises/2026-10-27-r5-sacrificio.md) e [r2 "correria"](../../../03-referencias/analises/2026-10-27-r2-correria.md), 24 qps, sequências de 6 a 24 quadros por frase.

## O mecanismo (Estilo A)

1. **Uma frase = um bloco.** O bloco nasce quando a 1ª palavra é falada e some inteiro, de uma vez (corte seco), quando a frase seguinte começa. Nada de rolagem.
2. **Coluna estreita, alinhada à esquerda.** Largura ≈ 28–32% do quadro (≈ 310 px em 1080). As palavras quebram sozinhas em 2 a 4 linhas, com entrelinha apertada (≈ 0,88). Palavras anteriores **não se mexem** quando entra a próxima.
3. **Fonte da legenda:** grotesca bold bem fechada (Inter / Helvetica Now ExtraBold), minúscula, **tracking −0,04em** (letras quase encostando), espaço entre palavras ≈ 0,2 em, branca com sombra suave (sem franja colorida), altura ≈ 5% da largura do quadro (≈ 57 px em 1080).
4. **Palavra-chave:** serifa itálica de contraste alto (Playfair Display Italic 700), **2,2×** o corpo da legenda, na **própria linha** (quebra o fluxo: as palavras seguintes continuam abaixo dela), brilho branco difuso em volta. Entra com desfoque 14 px → 0 e escala 1,16 → 1 em ~0,27 s.
5. **Palavra comum:** entra com desfoque 8 px → 0, opacidade 0 → 1 e subida de 8 px em ~0,22 s. Quando se vê um quadro intermediário, a palavra aparece "fantasma" (cinza e desfocada): é só a entrada, não um efeito de saída.
6. **Segundo bloco.** Frases com mais de ~6 palavras abrem um segundo bloco **abaixo e deslocado para a direita** do primeiro ("quando somente você" + "tem que tocar o céu"). Nunca cobrem o rosto.
7. **Âncora que muda.** A posição do bloco muda de frase para frase (x entre 25% e 70% da largura, y entre 50% e 66% da altura, do peito para baixo), sempre longe do rosto e acima do @ do perfil.
8. **Troca de plano:** a cada ~6 s o enquadramento muda em ~4 quadros, normalmente com 1 a 2 quadros de **flash branco** ou luz; o texto da frase seguinte nasce já no plano novo.

## O mecanismo (Estilo B)

Linha única **justificada** (palavras espalhadas pela largura de ~80% do quadro, espaço entre elas grande), peso leve 300, 1 a 2 linhas por frase; objeção em preto e branco com texto amarelo. No gerador: `"modo": "espalhada"` no evento `frase` (cada grupo de palavras vira uma linha justificada).

## Som: o que foi medido

Teste feito no áudio sem voz de 2 referências: ganho de energia nos instantes em que uma palavra nasce contra instantes aleatórios.

| Referência | Palavras testadas | Ganho médio nos nascimentos | Aleatório | Conclusão |
|---|---|---|---|---|
| r5 "lenha" | 120 | −0,75 dB | +0,03 dB | **sem som por palavra** |
| r5, só palavras em serifa | 34 | −1,58 dB | +0,03 dB | **sem som por palavra-chave** |
| r2 "correria" | 87 | −0,87 dB | +0,19 dB | **sem som por palavra** |

O som das referências está em: **música contínua**, **golpes nas trocas de plano e nos flashes** (+2 a +4 dB), **notificação do popup** (+6 dB) e o **impacto da abertura** (+15 dB). Por isso o gerador **não** põe `pop` por palavra (só com `"som_por_palavra": true` no roteiro) e põe impacto apenas quando a frase tem `"impacto": true` (na palavra-chave).

## Como usar

```json
{"tipo": "frase", "w": [["tem", 941.82], ["cara", 942.10], ["de", 942.76], ["crente", 942.96, "s"]], "impacto": false}
```

- Cada palavra: `[texto, tempo_em_que_é_falada, "s" opcional]`. `"s"` = palavra-chave em serifa.
- Opções: `coluna` (fração da largura, 0,30), `ancora` (`[x, y]` em fração do quadro; sem isso alterna posições), `max_bloco` (palavras por bloco, 6), `modo` (`coluna` ou `espalhada`), `impacto` (som grave na palavra-chave).
- Para montar as frases sozinho a partir da transcrição: `uv run scripts/video/corte_pregacao/roteirizar.py palavras.json roteiro.json --ini 940.4 --fim 1016 --destaques "crente,rejeitando"`.

## Erros a evitar (cometidos antes)

- Usar uma linha única com franja vermelha/azul nas letras (o estilo do primeiro concorrente, **não** o das referências r1–r5).
- Pôr som em cada palavra: as referências não fazem isso.
- Palavra-chave maior que a coluna: o gerador encolhe ou desloca para caber na tela; confira nos quadros.
- Bloco cobrindo o rosto ou o @ do perfil: o gerador limita a 46%–72% da altura.
