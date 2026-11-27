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
- **Começo do vídeo:** se o pregador está pequeno/andando nos primeiros segundos (imagem borrada no corte vertical), abra com **cartão** com a voz do gancho, sem fade no primeiro quadro (o vídeo não pode aparecer no quadro 0). O pregador entra depois, num trecho em que está parado.

## 2026-10-29: melhorar a imagem do pregador com IA (Real-ESRGAN)

- O cliente pediu o trecho do altar/voto do corte 3 "em ótima qualidade". Funcionou: recorte cru do trecho (sem ampliar), **realesr-general-x4v3** (spandrel + torch, CPU, ~4,8 s por quadro), mistura **55% IA + 45% lanczos** (só IA fica com cara de pintura/plástico), depois unsharp leve + grão fino (noise=4). Exemplo: `scripts/video/corte_pregacao/exemplo_ampliar_ia.py`. Peso: github.com/xinntao/Real-ESRGAN releases v0.2.5.0.
- Só vale para trechos curtos de vídeo (9 s = ~22 min). Cartões não precisam. Render final com `-q delivery`.

## 2026-11-19: câmera do corte vertical (fonte horizontal)

- O Lukas quer **câmera parada**: em cada trecho o recorte vertical fica fixo, centrado onde o pregador passa a maior parte do tempo. Se ele sair do quadro, a imagem **não** vai atrás dele; ele volta. Nada de câmera deslizando.
- Para achar o pregador de paletó claro: máscara de cor clara + exclusão do que fica parado no mesmo lugar (púlpito, telão); amostra a 4 quadros/s.
- O ffmpeg do contêiner novo (6.1) recusa opção errada de filtro com "Option not found" na lista global: confira o nome dos parâmetros (no `colorbalance` o meio-tom é `rm/gm/bm`, não `ms`).
- **Fonte com áudio mais curto que o vídeo:** confira `ffprobe` do stream de áudio. No corte "Betânia" o áudio acabava em 83,4 s, no meio de "coração". Solução: emendar a mesma palavra dita antes pelo pregador (isolada e conferida com o Whisper), mantendo o vídeo do trecho final. Avise o Lukas quando fizer isso.
- **Fim do gancho:** termine o trecho no silêncio real depois da última palavra (vale de energia), senão entra o começo da palavra seguinte.
- **Pregador que anda muito (Pr. Wilton):** o quadro fica parado e, quando ele se afasta do centro, corta seco para um quadro novo centrado nele (como os cortes de plano da referência R7). Nada de câmera deslizando. Pedido do cliente: só esmaecimento preto entre cenas e **sem efeito sonoro** (`"sem_sfx": true` e evento `escurece` no roteiro).
- **Disco:** renders longos encheram o disco do contêiner. Antes de renderizar, apague projetos e quadros antigos em /tmp/work e o cache do pip/uv.

## 2026-11-19: voz natural nas emendas (corte "Cuidado")

- O Lukas **não quer** a pausa de leitura depois dos cartões (a voz parava e ficava estranho). Padrão agora: **sem pausa**, o cartão fica enquanto ele fala.
- O fim de cada trecho vem do **silêncio real da voz** (energia abaixo do limiar por 120 ms) + 0,12 s de rabo natural, nunca do fim da palavra do Whisper. Gritos ("cuidado!") duram bem mais do que o Whisper marca: confira a energia e estenda.
- Depois de montar, rode a checagem de emenda: nível da voz nos 80 ms antes de cada corte que não é contínuo; se estiver alto, a fala foi cortada.

## 2026-11-20: cor dos cartões vem do vídeo (corte "Cuidado")

- O cliente achou que a imagem parecia IA: era o filtro de nitidez e cor que eu aplicava. O Lukas mandou a fonte limpa. **Regra:** não aplicar nitidez, contraste ou saturação no vídeo do pregador; só recorte e escala.
- Os cartões de frase (fundo + texto que entram com desfoque para cima) passam a usar a **cor predominante do vídeo**, normalmente a roupa do pregador. Aqui a camisa verde-oliva virou #3E5530 (cartão escuro, texto #E9EDE0) e #E9EDE0 (cartão claro, texto #3E5530).
- Música: o cliente pediu mais alto duas vezes; neste corte ficou ~6 dB acima do −14 dB padrão (volume 2,0 na faixa da música).

## 2026-11-21: fonte de celular com sala cheia de eco (corte "A graça", Pr. Wilton)

- Vídeo filmado da plateia (464×832): a voz isolada nunca chega a silêncio de verdade (eco da sala). Com o limiar padrão (p95 × 0,07) o "fim no silêncio" falha. Use **p95 × 0,2** e silêncio de 80 ms, e confira os cortes não contínuos olhando a energia a cada 10–20 ms; quando o Whisper erra o tempo ("fora" / "A graça"), transcreva só aquele pedaço de novo.
- O roteiro antigo tinha `grade` (contraste, grão, vinheta) aplicada no vídeo. Isso também é filtro: agora `"grade": false` desliga (vídeo limpo).
- Cores: ambiente roxo/ameixa e camisa cinza-arroxeada → cartão escuro #3B2D4A (texto #EEE9F0), cartão claro #EEE9F0 (texto #3B2D4A).

## 2026-11-21: primeiro corte no estilo correria (Pr. Alexandre, "O que é fé")

- **Fonte horizontal com o pregador de corpo inteiro:** não há espaço acima da cabeça. Quadro "aberto" = recorte 608×1080 (corpo todo), "fechado" = 468×832 (até a coxa); alternam a cada trecho, como na referência.
- **Pregador que anda:** além do recorte por trecho, um corte seco recentraliza quando ele sai mais de 6% da largura por 0,75 s (`planos()` em `exemplo_correria_build.py`). A voz não é cortada nesses recortes (só a imagem), senão aparece um "buraco" de 24 ms.
- **Trechos colados na fonte não podem se sobrepor:** a borda pela energia pode recuar até antes do fim da palavra anterior do Whisper. Depois de calcular, force o encontro no meio, senão o áudio repete um pedacinho.
- **Fundo de telão branco:** legenda branca nas laterais some. Neste fundo, todo bloco vai centralizado sobre a camisa escura, com sombra escura forte (`sombra` no roteiro do `gerar_correria.py`). O amarelo do P&B precisa da mesma sombra.
- **Quebra de linha:** até ~17 letras por linha, vírgula fecha a linha e a linha não termina em palavra fraca ("que", "de", "uma"…); blocos divididos por igual (4 linhas = 2+2).
- O Whisper às vezes **duplica uma frase** com todas as palavras no mesmo instante ("eu creio que Deus vai fazer" ×2 a 102,34 s). Transcreva o pedaço de novo antes de achar que é repetição.
- **Retorno do Lukas (v1 → v2):** (1) a legenda tem que **mudar de lugar** a cada frase, como na referência (esquerda, direita, centro, diagonal, alturas diferentes, às vezes a última linha pulando para o outro lado), e não ficar só no meio; (2) o amarelo era só da referência: **a cor de destaque vem da identidade do vídeo** (aqui, o lilás do LED do palco, #9A78FF); (3) havia efeito sonoro demais e ele chegava **depois** do texto. Agora: transição comum só a cada 12 s ou mais (as do P&B ficam), o **pico do efeito cai 0,04 s antes do corte** (junto com o clarão, calculado pelo `gerar_correria.py`) e a primeira palavra do bloco seguinte só aparece depois do clarão.

## 2026-11-22: primeiro corte no estilo R8 (Pr. Alexandre, "Deus tem um plano")

- **Cores da identidade:** telão dourado/marrom do vale de ossos → brilho dourado #F6C453, serifa e citação âmbar #E8963F, palavra forte cobre #D9672B. A "tela vermelha" da referência virou **tela dourada e preta** (`hue=s=0,eq=contrast=1.25,colorchannelmixer=rr=1:gg=.62:bb=.16`).
- **Fundo dourado + texto dourado:** o brilho e a serifa precisam de uma sombra escura curta antes do brilho, senão somem no telão.
- **Música:** a referência usa um "pad" quase inaudível; para este, instrumental de "Purifícame" (louvor de teclado) a 12 dB abaixo da voz.
- **Roteiro por índice de palavra** (`exemplo_r8_roteiro.py`): `seg(a, b, especiais)` cria a legenda simples sozinha e encaixa os textos especiais (digita, combo, serif, pilha, brilho, citação) nas palavras certas.
- **Retorno do Lukas (v1 → v2):** (1) no **cartão**, nada de recorte vertical encolhido (mostrava a barriga): o cartão mostra **o palco inteiro** (quadro horizontal 1080×608 no meio da tela preta, `LARGO` no build; `cartao_inset` 34,6 no roteiro) ou o rosto; (2) a **legenda simples** estava pequena: `cap_tam` 68 (antes 50); (3) o **@** subiu para 79% da altura (`handle_y`).

## 2026-11-22: vídeo "antes e depois" para o perfil da Pregue

- Estrutura (28 s, 9:16): "ANTES" (título 1 s) → vídeo bruto horizontal com o som original (6,6 s) → flash + "DEPOIS" (0,9 s) → corte editado em cima + **timeline de editor embaixo** com as faixas reais (vídeo aberto/fechado, textos com os especiais em dourado, efeitos, onda da voz e da música; agulha fixa e conteúdo correndo) → CTA "Quer isso / *no seu vídeo?* / LINK NA BIO / @pregue.oficial".
- Identidade usada (a Pregue não tinha cores definidas no projeto): preto #0B0B0C, off-white #F4F1EA, dourado #E8B04B, Archivo condensada + DM Serif Display Italic. Confirmar com o Lukas.
- O som cru da igreja vem muito alto (−8,7 LUFS): nivele o trecho "antes" em −15 LUFS para não pular de volume.
- HyperFrames: `<video>` com `data-start` não pode ficar dentro de um `div` que também tem `data-start` (o quadro sai errado); deixe os vídeos na raiz.
- Gerador: `scripts/video/promo/antes_depois_gerar.py` (lê `timeline.json` montado a partir do `fc.txt`, do `index.html` e dos áudios do corte).

## 2026-11-22: estilo R8 num depoimento (barbearia, "estourei minha bolha")

- Gancho pedido pelo Lukas: a frase de impacto vai **primeiro** ("tudo isso foi capaz quando eu tomei a decisão, estourei minha BOLHA") e a história começa depois.
- O Whisper ouviu "misturei" onde ele diz "estourei": o Lukas confirmou. Use `FIX` no roteiro.
- O Whisper esticou o "e" depois de "bolha" (11,06–11,92) num silêncio: a borda tirada só do Whisper cortaria "bolha". Conferir a energia: a voz acabou em 11,1 e voltou em 11,9.
- **Ambiente branco** (parede e camisa brancas): ligue `sombra_forte` no `gerar_r8.py` (halo escuro em todo texto), senão a legenda branca e o bege somem.
- Fonte vertical em 4K: "aberto" = quadro inteiro, "fechado" = recorte de 72% centrado no rosto (posição medida segundo a segundo nos quadros; o cv2 não está instalado).

## 2026-11-22: estilo correria num depoimento (barbearia, 59 s → 39,7 s)

- Os nomes dos estilos para o Lukas: "estilo do Filipe Levak" = **correria** (`gerar_correria.py`); "o último estilo do Alexandre" = **R8** (`gerar_r8.py`). Quando ele disser um número ("estilo 6", "estilo 7"), confirme qual é antes de baixar o vídeo.
- Pausas **dentro** das frases também saem (`sem_pausas()`: silêncio de 0,24 s ou mais, 0,07 s de margem; também no começo e no fim do trecho). Sem isso sobravam pausas de 0,3–0,7 s.
- Áudio pouco claro: o Whisper errou "mandei", "fiz", "desfiz", "viu". Corrija com `FIXW` e pule (`PULAR`) as palavras incertas em vez de inventar.
- Sem música: gere com a música e ponha `data-volume="0"` na faixa `music` antes de mixar.
- Vídeo de celular em 4K com rotação (3840×2160, rotação −90): o ffmpeg já gira sozinho; o quadro "fechado" usa recorte de 72% com o rosto a ~32% da altura.

## 2026-11-22: estilo 8 (R8) escolhendo o trecho ("não desistir", aluno da barbearia)

- Numeração que o Lukas usa: **estilo 8 = R8** (`gerar_r8.py`); o estilo do Filipe Levak = correria.
- Link do Drive privado baixa a página de login (HTML de ~900 KB, "moov atom not found"). Peça para ele mudar para "qualquer pessoa com o link"; o conector do Drive não serve para vídeo grande.
- De uma conversa de 2 min, o corte de 31 s junta só as falas do aluno (sem as perguntas do entrevistador): gancho "o segredo… é NÃO DESISTIR" e fecho "é PRATICANDO que a gente chega".
- "Gravatar" no Whisper = **Gravataí** (cidade).
- Clientes da barbearia: sem música de fundo (pedido repetido duas vezes).

## 2026-11-25: retorno do Lukas no corte "Muda o teu ponto de vista" (v1 → v2)

- **Palavras cortadas antes de terminar:** o limiar de "silêncio" estava alto (p95 × 0,12, −18 dB) e o `sem_pausas` cortava o rabo baixo das palavras como se fosse pausa. Agora silêncio = abaixo de **−26 dB** (p95 × 0,05), pausa mínima de 0,30 s e 0,12 s de margem; o fim de cada trecho vai até o primeiro silêncio de verdade e, quando ele emenda na próxima palavra, até o **vale de energia** entre as duas (não pelo tempo do Whisper).
- **Tela tremendo:** o recorte vertical era recalculado em cada pedacinho entre pausas, então o quadro pulava várias vezes por frase. O quadro agora fica **fixo por trecho**.
- **Texto fora da tela:** o `gerar_r8.py` calcula o tamanho de cada texto especial (citação, pilha, serifa, combo, grande, brilho, digitada) para a linha mais longa caber na largura (`cabe()`).
- **Fecho com coração e @:** o Lukas não quer. Não use `fim` no roteiro do R8.

## 2026-11-26 · Estilo 9 ("Íntimos de Deus") e serifa do combo no R8

- **Combo do R8 fora da tela ("o menino de 17 anos"):** a serifa começava na borda esquerda da palavra forte, então frase longa debaixo de palavra curta passava da borda. Agora ela fica centrada sob a palavra forte (`left:50%` + `xPercent:-50` no GSAP).
- **Estilo 9 = `gerar_r9.py`:** legenda palavra a palavra com fade + desfoque; sans Plus Jakarta 700 apertada (−0,06 em) e uma palavra-chave por página em Instrument Serif Italic 1,6× com brilho branco. O bloco fica centrado e alinhado à esquerda em y 0,60. Páginas de até 2 linhas, feitas à mão por frase (a divisão automática deixava palavra sozinha).
- **Estilo 9, o resto:** eco do gancho em P&B com legenda creme maior; assinatura com foto redonda tirada do próprio vídeo; mergulhos no preto entre os trechos. A referência não tem música nem efeito sonoro.
- **Container novo apaga /tmp/work:** reinstalar `audio-separator[cpu]`, `faster-whisper` e o modelo UVR (github), o Whisper turbo (`mobiuslabsgmbh/faster-whisper-large-v3-turbo`) e o HyperFrames 0.8.206 em `/tmp/work/hfinit` com o wrapper `/tmp/work/hf.sh`. O faster-whisper novo falha ao abrir arquivo (`metadata_errors`): passe o áudio como array (soundfile, 16 kHz mono).
- **Pegar só um trecho da pregação do Drive:** `ffmpeg -ss <ini> -t <dur> -i "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t" -c copy` baixa só a janela (segundos, em vez de 2 GB).
- **Fonte .woff2 some no render do HyperFrames:** o `snapshot` mostra a fonte certa, mas o `render` cai na fonte padrão (a serifa saiu como sans). Converta para .ttf (fontTools) e dê nomes únicos às famílias (`sans9`, `serif9`, nunca `serif`). Confira sempre um quadro do render final, não só o snapshot.
- **Estilo 9 v2 (feedback do Lukas):** a legenda "mudava de ângulo" porque cada página era centrada com largura diferente. Na referência a legenda ocupa uma **caixa fixa de 25% a 75% da largura**: o tamanho da letra muda por página para a linha mais longa encher a caixa (medido com as larguras reais da fonte). A palavra só acende, de 0 a 1 em 0,1 s, sem desfoque. Ele quer escurecimentos longos (~1,5 s para cada lado) em vez de corte seco, por isso a base corta só as pausas longas (≥0,7 s). A assinatura fica só com o @ até chegar a foto. Sem música neste estilo.
- **Estilo 9 em vídeo com várias câmeras (Pr. Wilton, 27/11):** o vídeo vertical sai antes, inteiro (`vert.mp4`), com recorte que acompanha o pregador (`sendcmd` mudando o `x` do `crop` 10 vezes por segundo, posição suavizada com gaussiana de 0,6–0,8 s). No plano aberto o recorte é mais fechado (456×810) e no fechado 608×1080. Para achar o pregador: terno azul = pixels com B > R+35 e B > G+15; no plano aberto, a figura escura na faixa do tronco. Quando o pregador sai do palco no começo, a abertura segura no preto (`abre_segura`) com a frase do gancho aparecendo por cima, e acende quando ele volta.
