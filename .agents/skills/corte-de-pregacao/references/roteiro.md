# Roteiro de eventos (`roteiro.json`)

> Data: 2026-10-27 · Tipo: guia · Status: vigente

**Resumo:** formato do arquivo que o `gerar_projeto.py` lê. Todos os tempos são segundos do vídeo **original** (os mesmos de `palavras.json`); o script converte para o tempo do corte, já sem as pausas. Exemplo real e completo: [assets/roteiro.exemplo.json](../assets/roteiro.exemplo.json) (corte "Cara de crente").

## Campos gerais

| Campo | Para quê |
|---|---|
| `estilo` | `"A"` (sans bold 800 + serifa) ou `"B"` (sans leve 300 com palavras bem espaçadas) |
| `rotulo_topo` | texto pequeno no topo (ex.: `"ALÉM DO PÚLPITO"`); vazio some |
| `logo` | PNG do @ (fundo preto, texto branco); o script remove o fundo, 36% da largura, a 76% da altura |
| `cauda` | segundos de tela final depois da última fala (padrão 1,5) |
| `musica` | `{"arquivo", "inicio", "abaixo_da_voz_db"}` (14 por padrão) |
| `punch_in` | `false` para desligar os zooms de câmera nos eventos |
| `cor_titulo`, `cor_objecao` | vermelho do título (#DC2427) e amarelo da objeção (#F7D903) |
| `grade` | JSON do `media-treatment` (padrão: deep-contrast 0,7, sombras azuis, realces quentes, vinheta e grão) |

## Eventos

Cada evento tem `"tipo"`. Palavras são `["texto", tempo_da_fala]`.

| Tipo | Campos | Visual |
|---|---|---|
| `cap` | `w`: lista de palavras/grupos; `cor: "amarelo"` opcional | legenda de 1 linha no peito; cada grupo entra no tempo da fala |
| `emph` | `lead`: frase curta em cima; `serif`: palavra-chave; `impacto`, `glitch`, `tamanho` | frase pequena + palavra grande em serifa itálica; `impacto` treme e dispara o hit grave; `glitch` separa as cores |
| `scatter` | `w`: `[texto, tempo, x, y]`; `serifa_ultima` | palavras em pontos diferentes da tela (1080×1920) |
| `beat` | `w` (com x, y), `t0`, `t1` | interlúdio em fundo escuro com palavras espalhadas e flash de entrada |
| `list` | `linhas`: até 3 listas de palavras | lista escalonada (esquerda/direita/esquerda) |
| `final` | `serif1`, `serif2` | duas palavras gigantes em serifa até o fim, com flash e tremida |
| `notificacao` | `t`, `dur` (2,8), `nome`, `texto` | popup branco no topo (CTA "seguir") com som de notificação |
| `titulo` | `t`, `dur` (1,6), `texto`, `cor`, `tamanho`, `largura` | título gigante em serifa caixa-alta vermelha |
| `flash` | `t`, `modo`: `luz`, `branco`, `filme` | flash de luz (warm), branco ou queima de filme (diagonal laranja com borda cromática) |
| `bw` | `t0`, `t1` | trecho em preto e branco (blend `saturation`) com legenda amarela por cima via `cor` |
| `gridcut` | `t`, `dur` (0,5), `cor` | quadrados cobrem e descobrem a imagem em ordem fixa (seed), com punch-in escondido no meio |
| `assinatura` | `t`, `texto`, `sub` | fundo preto, marca desenhada (revelação da esquerda para a direita), traço e subtítulo |

## Receita de um corte (45 a 75 s)

1. 0–3 s: gancho. `titulo` (se a frase for uma pergunta forte) ou `emph` com impacto na 1ª frase.
2. A cada frase: uma `cap`; palavras que carregam a ideia viram `emph` (no máximo 3 por frase, 8 a 12 no corte).
3. Primeiro terço: uma `notificacao` (CTA de seguir).
4. Troca de ideia: `flash` (`luz`) ou `gridcut`; ideia contrária ("objeção"): `bw` + legenda amarela.
5. 1 ou 2 `beat` em momentos de clímax (mudança de ritmo).
6. Fecho: `final` com as duas últimas palavras ou `flash` `filme` + `assinatura`.

Posições do `scatter` e do `beat` precisam caber em 1080×1920; palavras grandes em `serifa_ultima` ficam com `x` pequeno (≈ 100) para não sair da tela.

## Como deixar o tempo exato

- Use o tempo da palavra que o Whisper dá em `palavras.json` e **ouça/veja** o corte: palavras trocadas viram tempo errado. Se uma palavra nasce antes de ser dita, atrase `ts` em 0,05 a 0,1 s.
- Em cortes que pulam trechos (vários `--trechos`), o tempo continua em segundos do original: o script sabe onde cada trecho começa.
