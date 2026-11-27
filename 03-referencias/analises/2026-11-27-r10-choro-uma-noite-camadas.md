# R10 "O choro pode durar uma noite" (Pr. Alexandre): análise em camadas

> Data: 2026-11-27 · Tipo: análise · Status: vigente

**Resumo:** referência do estilo 10, enviada pelo Lukas em 27/11 (55 s, 576×1024). É o **estilo 9** (mesma legenda, mesma assinatura com foto) mais imagens de apoio, cartão digitado, clarão de luz, um trecho em sépia e uma chamada final. O gerador continua sendo o `gerar_r9.py`, agora com as chaves `broll`, `cartoes`, `clarao` e `cta`.

## Estrutura

| Tempo | O que acontece |
|---|---|
| 0–4,5 | Gancho com o pregador em plano médio: "O choro, ele pode durar uma noite, mas a alegria vem pela manhã" |
| 4,5–6,5 | Pregador ("o que o salmista está dizendo é que…") |
| 6,5–8,0 | **Fusão lenta (1,5 s)** do pregador para uma mulher chorando em **P&B**. A legenda continua por cima |
| 11–12,5 | Mergulho no preto e outra mulher chorando, em cor (12,5–22) |
| 22–23,5 | Fusão de volta para o pregador |
| 23,6–24,3 | **Clarão laranja (1 quadro) e branco (~0,5 s)** |
| 24,3–28,3 | **Cartão digitado:** fundo cinza quente #AAAAA3, texto grafite em caixa-alta (Plus Jakarta 800, tracking negativo), alinhado à esquerda a 8,5% da largura e 43% da altura, letra por letra no tempo da fala, com cursor. Ex.: "EU TÔ DIZENDO QUE: / O DIA DE ONTEM / NÃO SERÁ O DE HOJE" |
| 28,3–29,2 | Clarão e branco de novo, volta para o pregador |
| 36,5–42 | Trecho em **sépia** depois de um mergulho no preto; termina num **flash branco** |
| 43–50 | Plano mais **fechado** do pregador |
| 51,8–53,8 | Escurece até o preto |
| 53,8–55 | **"COMENTE / EU CREIO"** pequeno, centrado, em Jakarta 800 branca no preto |

## Som

- **Voz:** −17 LUFS.
- **Música:** calma, cinematográfica, com pulsos graves a cada ~3,5 s, ~7 dB abaixo da voz (−24 LUFS).
- **Efeitos:** nenhum perceptível.

## Como fazer (gerador)

- **Montagem:** `exemplo_r10_build.py` faz a base. São dois verticais da janela, aberto 456×810 e fechado 380×676, que acompanham o pregador com a posição suavizada. A sépia vem do `colorchannelmixer`. As emendas entre trechos colados na fonte não se sobrepõem, e o `ovs.json` força o fim quando a fala termina baixinho.
- **Roteiros:** `exemplo_r10_roteiros.py` tem as páginas à mão, o cartão (faixas de palavras por linha), as imagens de apoio (id do Mixkit, palavra inicial e final, P&B, x do recorte) e as trocas.
- **Imagens de apoio:** vêm do Mixkit (ver `02-ferramentas/mixkit-broll.md`) e são recortadas em 9:16 no ponto escolhido. Ficam em câmera lenta de até 1,6× quando são curtas, e entram e saem com fusão de 1 s.
