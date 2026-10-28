# Aprendizados

> Data: 2026-10-22 · Tipo: dados · Status: vigente

**Como usar:** uma entrada por aprendizado, a mais nova no topo: data, projeto, o que aconteceu e o que fazer da próxima vez. Quando o aprendizado vira um número fixo, ele sobe para [regras.md](regras.md) e aqui fica só o link.

## 2026-10-27 — Legenda dinâmica: aprender a mecânica, não só a aparência
- **Projeto:** corte 2 (Cara de crente)
- **O que aconteceu:** a v1 usou a legenda antiga (uma linha com franja colorida) e o Lukas notou que não era o estilo das referências. Medindo quadro a quadro: a legenda das referências é um bloco estreito alinhado à esquerda que cresce palavra por palavra, com a palavra-chave em serifa itálica na própria linha; o "fantasma" cinza que aparece é só a entrada da palavra. E não há som por palavra (120 nascimentos medidos, nenhum ganho de energia).
- **Da próxima vez:** montar a legenda com o evento `frase` (`references/legenda-dinamica.md`), comparar os quadros com a referência lado a lado antes de renderizar e não inventar som por palavra.

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


## 2026-10-28: música Can't Forget You (Vybeq)

- A parte animada com bateria entra em **36,1 s**. O Lukas pediu para cortar antes disso e recomeçar do início da música, repetindo até o fim. Use `"musica": {"loop_ate": 36.0}` no roteiro. Medido: com o loop, nenhum trecho passa do nível calmo da introdução.

## 2026-10-28: sem zoom e com câmera parada (estilo E)

- O Lukas disse que os zooms a cada legenda e a câmera deslizando atrás do pregador davam dor de cabeça. No estilo E: **sem punch-in** (padrão agora, `punch_in` desligado) e **sem som de zoom**; o recorte vertical só se mexe quando o pregador chega perto da borda (zona morta) e depois suaviza. Efeitos só nas trocas de cena, no fade preto/P&B e no fecho.
- Antes de renderizar, olhe 10 quadros de `prep/base.mp4`: o pregador tem de aparecer inteiro em todos.
- Escolha de corte: a melhor parte é a que fala direto com a vida de quem assiste (promessa, "Deus está se lembrando de você"), não só a boa história. Releia a pregação toda e confira **quem** está falando (o @ de baixo é do pregador).
