---
name: editar-cortes-pregacao
description: Edita cortes verticais (Reels, TikTok, Shorts, 1080x1920, 30 fps) de pregação, palestra e evento em Remotion, em três estilos - motion design (texto gigante, zoom seco, fundo trocado, efeitos sonoros), legenda simples palavra por palavra, e editorial profissional (cartões tipográficos em fundo branco, estouro de luz, preto e branco). Faz transcrição com tempo por palavra, escolha de trechos com gancho, contexto e clímax, câmera que centraliza o orador, voz isolada e mixagem. Use quando o usuário enviar vídeo de pregador, pastor, palestrante ou evento e pedir para editar, cortar, legendar, deixar dinâmico, copiar o estilo de um vídeo de referência, fazer cartões de texto, transições ou efeitos sonoros.
---

# Editar cortes de pregação, palestra e evento (Remotion)

Receita testada neste projeto. O projeto Remotion está na raiz do repositório (`src/corte/` é a composição
`Corte`; `public/` guarda fontes, sons e os planos de cada corte em `public/cortes/X/`).

Leia antes de montar: `references/estilo-visual-e-sonoro.md` (motion design) e
`references/estilo-editorial-cartoes-tipograficos.md` (estilo editorial, com a receita dos cartões).

## Escolha do estilo (o que o usuário pedir vale mais que o padrão)

| Estilo | Quando | Como |
|---|---|---|
| **Motion design** | "dinâmico", texto gigante, zoom, efeitos | `montar_plano.py X ...` (hits, zooms, sfx, destaques com `recorte`) |
| **Simples** | "só a legenda", "sem motion design" | `--simples @arroba`: filmagem original + legenda palavra por palavra com borrão + marca no rodapé |
| **Editorial** | "profissional", "fundo branco com o texto", estilo de referência do usuário | `--simples @arroba --editorial`: cartões tipográficos, estouro de luz, P&B, zoom a cada frase |

Transições pedidas pelo usuário (em `cortes_config.py`): `"transicoes": ["brilho", "preto"]` (uma por emenda:
brilho com clique, esmaecimento por preto), `"pb": [{"de": [...], "ate": [...]}]` (preto e branco entre duas falas).

## Pipeline de um corte (live, palestra ou evento)

1. **Entender o pedido** e escolher o estilo. Duração: **1 a 1,5 min**, com gancho (a frase de impacto antecipada
   por ~4 s), contexto, virada (clímax) e desfecho. Corte curto sem contexto foi reprovado.
2. **Transcrever com tempo por palavra** (`scripts/transcrever.py`, faster-whisper large-v3, áudio como array numpy).
   Ler a transcrição inteira, corrigir palavras erradas em `correcoes` e pôr nomes próprios com maiúscula.
3. **Escolher os trechos** olhando uma folha de contatos do bruto. Descartar onde o orador sai do quadro ou fica
   na borda (não dá para centralizar). Cortar em limite de frase.
4. **Configurar** `scripts/cortes_config.py`: `trechos`, `hits` (motion design), `cartoes` (editorial), `transicoes`, `pb`,
   `enfase`, `correcoes`.
5. **Recorte e câmera**: `ffmpeg -i ed_X.mp4 -an -c copy public/cortes/X/base.mp4`, depois
   `preparar_pessoa.py base.mp4 public/cortes/X rvm.onnx` (~10 min; gera `pessoa.webm` e `camera.json`, câmera
   centralizada na cabeça do orador).
6. **Plano**: `montar_plano.py X pasta_trabalho public/cortes/X [--reusar] [--simples @arroba] [--editorial]` e
   `juntar_plano.py public/cortes/X` (gera `plano_final.json`).
7. **Conferir quadros** com `npx remotion still Corte out/q.png --props=public/cortes/X/plano_final.json --frame=N`
   e uma folha de contatos. Fazer isso antes de renderizar tudo.
8. **Render**: `npx remotion render Corte out/X_mudo.mp4 --props=public/cortes/X/plano_final.json --crf=18 --concurrency=4`
   (~12 min para 78 s; para prévia use `--frames=A-B`).
9. **Áudio**: isolar a voz (ElevenLabs, ver abaixo) → `iso_X.mp3` na pasta de trabalho, depois
   `mixar_audio.py X trab musicas sfx out/X_mudo.mp4 out/X.mp4 public/cortes/X/plano.json --sem-musica`
   (use `plano.json`, não `plano_final.json`).
10. **Comprimir** (`-crf 25 -preset veryfast`, ~35 MB para 78 s), conferir loudness (-14 LUFS) e a correlação
    do arquivo final com a voz isolada (> 0,8), e enviar com `SendUserFile`. Commit e push na branch da sessão.

## Regras de edição (aprendidas com reprovações do usuário)

- **Cortes sem comer fala:** só pausas > 1,2 s viram corte; o ritmo vem de zoom e texto. O fim de cada trecho vai até
  o fim da palavra + 0,34 s (sem passar da próxima palavra); fade de 30 ms nas emendas. O limite só é movido quando
  cai dentro de uma palavra. Nenhum trecho passa da duração do bruto.
- **Legenda sempre na mesma altura:** uma linha só, reduzida em conjunto se for larga. (Linhas de 1 e 2 linhas em
  alturas diferentes pareciam "legenda em cima e depois embaixo".)
- **Filmagem original na maior parte:** o fundo novo (orador recortado) vale só em 2 a 4 destaques (`"recorte": True`).
- **Orador centralizado** (câmera virtual pela cabeça, sem passar da borda e sem mostrar a legenda queimada do rodapé).
- **Isolar a voz do áudio já editado** (não fatiar uma voz isolada de uma edição antiga: dessincroniza).
- **Corte de transmissão:** o orador pode sair do quadro; descarte esse trecho em vez de fingir que está ok.

## Efeitos (parâmetros que funcionaram)

- **Zoom seco** em 2 quadros (1,15 a 1,5x); **tremida** ~8 quadros, 26 px; **clarão** 2 quadros; **borrão** 10 px em ~6 quadros.
- **Preto e branco:** `grayscale(1) contrast(1.35)`, rampa de 5 quadros na entrada, 2 na saída.
- **Brilho** (emenda): luz sobe em 5 quadros até o corte e some em 11, com clique no corte.
- **Estouro de luz** (cartões): faixa de luz vertical + branco, ~11 quadros em volta do corte.
- **Cartão tipográfico:** fundo branco, palavra-chave 224 px em serifa itálica (preto, vinho `#8a0f1c`, azul `#1c2c8c`),
  conectivos 58 px em sans, entrelinha apertada, cada palavra entra na hora em que é dita.
- **Legenda simples:** Inter Bold 64 px, tracking -0.045em, maiúscula, ~49% da altura, borrão 14 px → 0 em 6 quadros.
- **Texto atrás do orador:** exige recorte por quadro; mostre um teste antes.

## Som

- **A voz manda.** `mixar_audio.py` normaliza a voz em -20 LUFS, escala os efeitos pelo pico da voz, recua a voz nos
  impactos e **para com erro se a voz não ficar 6 dB acima** de música+efeitos. Final em -14 LUFS (duas passadas).
- **Música é opcional** (`--sem-musica`). Só usar arquivo enviado pelo usuário, com licença confirmada.
- **Alinhar pelo pico** do efeito: `PICO` em `montar_plano.py` (whoosh 0,25 s, impacto 0,09 s, estalo 0,13 s, clique 0,03 s).
- **Efeitos** em `public/sfx/` (`el_*.mp3`, gerados no ElevenLabs): impacto, impacto2, whoosh, whoosh2, estalo, riser, clique.
  Gerar um novo: `eleven_text_to_sound_v2`, nó `sfx`, **uma chamada só** (repetir cobra de novo), ~0,5 centavo.
  O clique veio com duas batidas: cortei só a primeira (`ffmpeg -ss 0.33 -t 0.35`).
- **Voz isolada (ElevenLabs `audio_isolation`, ~13 centavos por 78 s):** subir o `mp3` da voz
  (`creative_create_asset_upload` + PUT + `creative_finalize_asset_upload` com `flow_id`), gerar com
  `generations_count: 1` e baixar pela URL assinada. **O limite de pedidos (429) é comum:** tente uma vez, espere
  e tente de novo mais tarde, sem repetir em sequência. Se não liberar, use `afftdn` + passa-altas localmente e avise
  o usuário que sobra um pouco de instrumental.

## Ambiente (armadilhas já encontradas)

- **Chrome:** `remotion.config.ts` usa o `chrome-headless-shell` de `/opt/pw-browsers/`. Para a skill `motionmaxxing`,
  `CHROME_PATH=/opt/pw-browsers/chromium` está em `.claude/settings.json`.
- **Rede:** o Whisper vem do Hugging Face (liberar `*.hf.co`); YouTube bloqueia download de datacenter; arquivo grande do
  Drive só por link público. Guie o usuário passo a passo (ele não sabe onde ficam as configurações).
- **GitHub push 403:** permissão do app; peça para reconectar em https://claude.ai/connect-github.
- **Gerar muita saída** (ElevenLabs, render longo): diga o custo e rode em segundo plano com `Monitor`.
- **`pkill -f` mata o próprio shell**: selecione o pid com `ps` + `awk`.
- Plugins instalados no meio da conversa só valem em sessão nova.

## O que não prometer

- Não ouço áudio nem identifico músicas e sons de outro vídeo: leio transcrição e números (volume, picos). O "soou bom"
  é do usuário. Peça que confirme o som.
- Copiar o **estilo** (ritmo, tipografia, cor, tipos de efeito) é ok; não reaproveitar marca, logo, imagens, música ou
  texto de terceiros. Cenas de filme/série (inserts) só com o clipe enviado pelo usuário ou autorização dele.
- Fontes pagas: usar a gratuita mais parecida e avisar (hoje: Playfair itálico e Inter).
- A escolha dos cartões e dos destaques é feita por mim lendo a fala, não é automática.
