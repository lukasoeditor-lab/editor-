# Aprendizados

> Data: 2026-10-22 · Tipo: dados · Status: vigente

**Como usar:** uma entrada por aprendizado, a mais nova no topo: data, projeto, o que aconteceu e o que fazer da próxima vez. Quando o aprendizado vira um número fixo, ele sobe para [regras.md](regras.md) e aqui fica só o link.

## 2026-10-27 — Estilo "cara de IA" vs. estilo profissional dos cortes
- **Projeto:** cortes da pregação "A Unção de Davi" (corte 1 e 2) e análise das 5 referências do Lukas
- **O que aconteceu:** o corte 1 saiu com cartões brancos/coloridos e animação feita com PIL; o Lukas disse que parecia IA e pediu o estilo das referências (vídeo sempre na tela, legenda mínima, palavra-chave em serifa itálica, flashes curtos, cor com sentido).
- **Da próxima vez:** começar pela skill `corte-de-pregacao` e pelas análises de `03-referencias/analises/`; fazer um corte por vez; usar HyperFrames (HTML/GSAP) e a biblioteca de efeitos, e conferir quadros do render antes de entregar.

## 2026-10-27 — Efeitos sonoros mais altos que a voz
- **Projeto:** corte 1 (v3)
- **O que aconteceu:** os impactos saíram 12 dB acima da fala (−8 dBFS contra −20 dBFS de média).
- **Da próxima vez:** o fator de volume por categoria (em `gerar_projeto.py`) mira o nível dos picos da fala; medir janelas de 0,3 s no arquivo final.

## 2026-10-27 — Ambiente de nuvem
- **O que aconteceu:** CDN do GSAP, YouTube, `download.pytorch.org` e o site do Playwright são bloqueados; Drive com link público, GitHub, HuggingFace e PyPI funcionam.
- **Da próxima vez:** GSAP vem do npm (`npm pack gsap`); vídeo vem de arquivo ou Drive; torch/beat_this/audio-separator `--extra cpu` só no computador do Lukas.

<!-- Modelo:
## AAAA-MM-DD — título curto
- **Projeto:** 04-projetos/AAAA-MM-DD-tema
- **O que aconteceu:**
- **Da próxima vez:**
-->
