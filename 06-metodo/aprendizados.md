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

## 2026-10-28: corte longo com história (estilo F, ~2 min)

- **Formato que o Lukas aprovou como direção:** abrir com um gancho de impacto (a acusação "ela só pode estar embriagada" + a resposta de Ana), voltar ao contexto da história, e fechar forte ("o tempo de espera termina hoje"). Cortes de 1:30 a 2:00 são aceitos se tiverem contexto e fechamento. Cartões alternam as cores **invertidas** da mesma paleta (lavanda/azul), sem cor nova.
- **Trechos fora de ordem:** o corte pode pegar partes anteriores da pregação (flashback). O mapa de tempo agora acha o trecho que contém o instante (antes assumia ordem cronológica e errava tudo).
- **Verifique a imagem da fonte antes:** a transmissão começa com o vídeo **encolhido no meio de uma tela preta** (até ~60 s). Trechos assim não servem; cubra com cartão ou escolha outro. O detector de azul parado também ignora guitarra e telão.
- **Cartão não passa da emenda** do trecho em que começa; a legenda de 1 palavra também não.
- **Render:** 2 min de vídeo levam ~27 min em 4 núcleos (`--page-motion-blur=off -w 4` dá ~2,3 quadros/s; sem isso ~1,7). Não há como acelerar mais neste ambiente.
- **Transcrição:** Whisper pequeno erra palavras em trechos lentos ("navalha" virou "Ranavalha", "embriagada" veio partida). Corrija a lista de palavras antes de gerar e evite cortar frases cujo texto não deu para confirmar.

## 2026-10-28: feedback do corte 3 v1 (fala cortada, sem legenda, cartão com pregador no meio)

- **Fala cortada:** o fim do trecho NÃO pode vir da faixa que escolho na mão nem do fim da palavra do Whisper (erra 0,2 a 0,8 s). Ache o **vale de energia da voz isolada** perto do fim da última palavra e corte ali (`exemplo_refazer_com_pausas.py`). Voz isolada é obrigatória para o trecho todo: separe uma vez a faixa inteira e reaproveite.
- **Tempo para ler:** cartão com a fala inteira, e depois da última palavra a **voz para e só o texto fica** (pausa de 0,8 a 2,2 s; música segue). Em `info.json`: lista `pausas`; no vídeo, `tpad=stop_mode=clone` repete o último quadro.
- **Legenda sem buracos:** nos trechos de vídeo, blocos de 1 a 3 palavras, sempre um na tela até o próximo começar. A palavra gigante do gancho dura até o fim da fala dela.
- **Troca de cartão (azul ↔ branco) sem pregador no meio:** o cartão novo começa no começo do trecho e entra por **dissolve** (0,3 s) por cima do anterior, que só some depois. No `gerar_projeto.py`: `fade_in`, `fade_out`, `antes` e encadeamento automático.
- **Sequência de cartões:** no máximo 2 seguidos; alterne com vídeo.
- **Imagem:** fonte 720p em corte 9:16 é sempre macia. Ajuda: `hqdn3d` antes do `scale`, `unsharp` depois, enquadramento com a cabeça a ~1/3 do alto e sem o telão azul embaixo (ypos 0,4), zona morta mais estreita (0,28) para o pregador não ficar na borda.
