---
name: dinamico
description: Deixa a edição dinâmica, no estilo dos reels que performam - zoom a cada corte e punch nas palavras fortes, legendas animadas, motion graphics por cima do vídeo (título do gancho, destaques, numerais de lista, lower third, círculo de destaque, barra de progresso, tela de CTA) e efeitos sonoros (whoosh, swipe, pop, click, ding, riser, boom, glitch). É o padrão de toda edição FREMEX. Use quando o usuário pedir edição dinâmica, mais ritmo, motion, efeitos, zoom, efeitos sonoros ou "estilo reels", e sempre como parte da skill editar.
when_to_use: Pedidos como deixa dinâmico, coloca motion e efeitos sonoros, edição estilo reels, mais ritmo, coloca zoom nos cortes, efeitos nas palavras.
---

# FREMEX · Edição dinâmica

Toda edição FREMEX é dinâmica por padrão. Só use uma edição "limpa" (sem zoom, motion ou efeitos) se o usuário pedir.

## Como funciona

Você escreve um arquivo `edicao.json` com a **direção** da edição, ancorada nos tempos da fala, e três scripts aplicam tudo:

| Ordem | Script | O que faz |
|---|---|---|
| 1 | `zoom.py` | zoom alternado a cada corte + punch nas palavras fortes |
| 2 | skill `legendas` | legenda palavra por palavra com "pulo" na palavra falada |
| 3 | `overlay.js` | motion graphics por cima do vídeo (camada transparente) |
| 4 | `sfx.py` | efeitos sonoros nos momentos certos, misturados ao áudio |

Antes: o vídeo já deve estar **cortado, reenquadrado e com o áudio tratado** (skills `cortes`, `reenquadrar`, `audio`). Depois: `exportar`.

```bash
D="${CLAUDE_SKILL_DIR}/scripts"
python3 "$D/zoom.py"   trabalho/04-audio.mp4 edicao.json trabalho/05-zoom.mp4
python3 "${CLAUDE_SKILL_DIR}/../legendas/scripts/legendas.py" trabalho/05-zoom.mp4 --saida trabalho/06-legenda.mp4
node    "$D/overlay.js" trabalho/06-legenda.mp4 edicao.json trabalho/07-motion.mp4
python3 "$D/sfx.py"     trabalho/07-motion.mp4 edicao.json trabalho/08-final.mp4
```
Requisitos: FFmpeg, Python com numpy, Node com Playwright (na nuvem do Claude Code já vem tudo, exceto o faster-whisper das legendas). Tempo de processamento: cerca de 4x a duração do vídeo.

## 1 · Pegue os tempos

Use o `.srt` gerado pela legenda (ou `legendas.py --so-arquivos` no vídeo cortado) para saber **quando** cada palavra é dita. Todos os tempos do `edicao.json` saem dali. Não chute tempos.

## 2 · Escreva o `edicao.json`

```json
{
  "cores": {"destaque": "#6A96DE", "base": "#2459A6"},
  "zoom": {
    "cortes": [3.8, 8.2, 13.5],
    "alternar": 0.08,
    "punches": [{"t": 1.2, "forca": 0.12}, {"t": 6.4, "forca": 0.10}],
    "centro": [0.5, 0.42]
  },
  "overlays": [
    {"tipo": "progresso"},
    {"tipo": "titulo",   "inicio": 0.0,  "fim": 2.4, "texto": "Você edita *rápido*?"},
    {"tipo": "destaque", "inicio": 6.3,  "fim": 8.0, "texto": "3 passos *simples*"},
    {"tipo": "lista",    "inicio": 8.2,  "fim": 11.0, "numero": "01", "texto": "Corte as *pausas*"},
    {"tipo": "circulo",  "inicio": 11.2, "fim": 12.8, "x": 0.5, "y": 0.45, "raio": 0.15},
    {"tipo": "lower",    "inicio": 13.6, "fim": 16.5, "texto": "Nome da pessoa", "sub": "cargo ou @perfil"},
    {"tipo": "cta",      "inicio": 24.0, "fim": 28.0, "texto": "Comenta *EDITAR*", "palavra": "EDITAR"}
  ],
  "sfx": [
    {"t": 0.0,  "tipo": "whoosh", "volume": 0.45},
    {"t": 6.3,  "tipo": "pop",    "volume": 0.5},
    {"t": 8.2,  "tipo": "riser",  "volume": 0.3},
    {"t": 8.2,  "tipo": "boom",   "volume": 0.45},
    {"t": 11.2, "tipo": "click",  "volume": 0.5},
    {"t": 24.0, "tipo": "ding",   "volume": 0.4}
  ]
}
```

- `*palavra*` vira itálico na cor de destaque.
- `cores`: use as cores do cliente (`cliente.md`). Sem cliente, use as da FREMEX (padrão).
- `y` (0 = topo, 1 = base) muda a altura de qualquer overlay. Os padrões já evitam a área da legenda.
- `riser`: informe o tempo em que ele deve **terminar** (o corte ou a revelação).

## 3 · Regras de direção (o que separa dinâmico de poluído)

**Ritmo**
- Um corte de enquadramento (`cortes`) a cada 3 a 6 segundos, sempre numa troca de frase, nunca no meio de uma palavra.
- Um punch a cada 4 a 8 segundos, na palavra mais forte da frase (número, promessa, contraste). Nunca dois punches a menos de 1,5 s.

**Motion graphics**
- `titulo` no gancho (0 a 2,5 s), sempre. Até 6 palavras.
- Um `destaque` para cada ideia-chave: números, promessas, nomes de ferramentas. Máximo 1 a cada 5 s.
- `lista` quando o vídeo enumera passos ou dicas.
- `circulo` para apontar algo na tela (produto, detalhe, interface). Assista o vídeo para saber `x` e `y`.
- `lower` na primeira aparição de uma pessoa ou marca.
- `progresso` em vídeos com mais de 20 s.
- `cta` nos últimos 3 a 5 s, se o roteiro tiver chamada.
- Nunca cubra o rosto nem o produto. Confira nos quadros de revisão.

**Efeitos sonoros**
- `whoosh` ou `swipe` em transições e entradas de título. `pop` nos destaques. `click` em círculos e interfaces. `riser` + `boom` na revelação principal (uma vez por vídeo). `ding` no CTA ou num acerto. `glitch` só em conteúdo de tecnologia, com moderação.
- Volume entre 0,3 e 0,5. O efeito acompanha a fala, nunca compete com ela.
- Média de 1 efeito a cada 3 a 4 s. Mais que isso cansa.

**Estilo por objetivo**
| Objetivo | Intensidade |
|---|---|
| Entretenimento, tendência | alta: punches frequentes, todos os efeitos |
| Educativo, tutorial | média: lista, círculo, destaques, poucos efeitos |
| Institucional, depoimento, luxo | baixa: `alternar` 0.04, poucos punches, só `whoosh` e `ding` |

## 4 · Revise

1. Extraia um quadro no meio de cada overlay (`ffmpeg -ss <t> -i 08-final.mp4 -frames:v 1 q.jpg`) e confira se nada cobre o rosto, o produto ou a legenda.
2. Ouça os efeitos: volume perto de -14 LUFS no final (`ffmpeg -i 08-final.mp4 -af ebur128 -f null -`).
3. Mostre ao usuário a folha de quadros e a lista de efeitos usados, e ajuste o `edicao.json` se ele pedir mais ou menos intensidade.

## Efeitos sonoros: biblioteca e licença

A biblioteca (`whoosh`, `swipe`, `pop`, `click`, `ding`, `riser`, `boom`, `glitch`) é **gerada por síntese** pelo `gerar_sfx.py`. Os sons são da FREMEX e podem ser usados em qualquer trabalho. O usuário pode usar os próprios efeitos passando o caminho do arquivo em `tipo`, desde que tenha licença para eles.
