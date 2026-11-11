# Guia de estilo de reels FREMEX — análise das referências

**Versão:** 0.1 · **Data:** 11/11/2026

## Material analisado

Pasta de referências no Google Drive com 11 vídeos.

| Status | Quantidade | Detalhe |
|---|---|---|
| Analisados | 8 | Quadros extraídos ao longo de cada vídeo, além de medições de cortes, pausas e volume |
| Não analisados | 3 | O conector do Drive não baixa arquivos desse tamanho: o vídeo "MAPA" (8,7 MB), o vídeo do getkeyframes (11 MB) e o de imóveis (6,4 MB) |

Os vídeos de referência não foram copiados para o repositório, porque são obra de terceiros. Usamos a linguagem, não os arquivos.

## As três famílias de estilo encontradas

| Família | Exemplos | Dá para fazer só com código? |
|---|---|---|
| **A · Interface em movimento** | "100 mil skills", "5 ferramentas", "carrossel com um prompt", "HYPIT" | **Sim.** Telas, cards, terminais e tipografia animados em HTML. É o estilo base da FREMEX |
| **B · Personagem 3D ou pixel** | "Comenta VIRAL", "Criei esse vídeo usando…" | Parcial. Pede personagem e cenários próprios (3D ou ilustração), animados depois por código |
| **C · Apresentador + grafismos** | Vídeo em inglês com apresentador em câmera | Sim, a partir de gravação do apresentador, com grafismos por código por cima |

## O que se repete (a gramática do formato)

### Estrutura

1. **Gancho em até 2 s.** Uma afirmação ou pergunta grande no centro, como "Você só precisa de 5", "Um prompt faz…" ou "Viralizei em 1 semana".
2. **Lista numerada.** Itens 01 a 05, um por vez, cada um com cerca de 6 a 12 s nos vídeos longos.
3. **Prova visual em cada item.** Terminal digitando, card de repositório, checklist marcando, contador subindo.
4. **CTA de comentário.** Uma caixa de comentário com a palavra-chave sendo digitada e o botão "Seguir" virando "Seguindo ✓".

### Ritmo

- Duração entre 29 e 62 s.
- Narração contínua: praticamente sem silêncio nos vídeos medidos.
- Poucos cortes secos. A detecção de cena achou de 0 a 10 cortes por vídeo. A mudança vem por **animação contínua** (cards entrando, número trocando, câmera andando), não por corte.
- Algo se mexe o tempo todo: chão em perspectiva, partículas, brilho pulsando.
- Volume final em **-14 LUFS** em todos os vídeos medidos, que é o padrão das redes.

### Tipografia

- Título em **sans pesada** combinado com **itálico serifado** em uma palavra ("Claude Code *skills*", "Vídeos com o *Claude*", "Quer mais conteúdo *assim?*").
- **Numeral gigante em itálico serifado e com brilho** (01 a 05) no canto superior.
- Rótulos em **monoespaçada** (nome de repositório, comando).
- **Pílulas** com contorno para categorias e números.

### Legenda

- Fica no terço inferior, centralizada, com 2 ou 3 palavras por vez.
- Cada palavra acende quando é falada. A palavra-chave aparece em cor de destaque, e as palavras ainda não ditas ficam apagadas.

### Ambiente

- Fundo quase preto com brilho radial colorido no alto.
- Chão em grade com perspectiva na metade de baixo.
- Uma única cor de destaque por vídeo: azul, laranja ou vermelho.

## Tradução para a FREMEX

| Elemento da referência | Versão FREMEX |
|---|---|
| Fundo escuro com brilho | Preto profundo #080A0F com brilho em azul elétrico #2459A6 |
| Cor de destaque | Azul digital #6A96DE em legendas, numerais e pílulas. Uma segunda cor quente (areia) só em pílulas secundárias |
| Sans pesada | Archivo expandida (a família do lettering FREMEX) |
| Itálico serifado | Instrument Serif itálico. **Nova fonte de acento: precisa da sua aprovação** |
| Monoespaçada | IBM Plex Mono |
| Mascote do Claude | **Não usamos.** É marca da Anthropic. A FREMEX pode criar um elemento ou personagem próprio no futuro |
| CTA "Comenta X" | Mantido, com a palavra do curso (CRIAR) e o símbolo FREMEX |
| Assinatura | "FREMEX · THE CREATIVE EVOLUTION" discreta no rodapé |

## O que melhoramos em relação às referências

- **Sistema, não peça solta.** Tudo vem de tokens da marca, e cada vídeo novo troca só o conteúdo.
- **Render determinístico.** O mesmo arquivo gera sempre o mesmo vídeo, e qualquer ajuste é refeito em segundos.
- **Sem promessas que não podemos provar.** Algumas referências usam números de visualização e seguidores. A FREMEX só mostra números reais e verificáveis.
- **Acessibilidade.** Legenda com contraste alto e tamanho legível em celular.

## Piloto 01

- **Arquivos:** `piloto-01/piloto-01.mp4` (13 s, 1080×1920, 30 fps) e a fonte editável `piloto-01/composicao.html`.
- **Como renderizar:** `node video-lab/render.js video-lab/piloto-01/composicao.html video-lab/piloto-01/piloto-01.mp4 [narracao.mp3]`
- **Narração:** o piloto não tem áudio. As legendas estão sincronizadas com uma narração planejada, e o áudio entra como terceiro argumento do renderizador.
