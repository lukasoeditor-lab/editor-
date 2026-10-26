---
name: editar-cortes-pregacao
description: Edita cortes verticais de pregação (Reels, TikTok, Shorts, 1080x1920, 30 fps) em Remotion no estilo dinâmico de referência, com cortes e zoom no rosto, legendas e textos animados (motion design), cor e vinheta, e efeitos sonoros sincronizados com a fala. Use quando o usuário enviar um vídeo de pregador/pastor/ministração e pedir para editar, criar um corte, legendar, "deixar dinâmico", "no estilo do vídeo que te mandei", adicionar efeitos sonoros, zoom, texto gigante, ou copiar o estilo de outro corte.
---

# Editar cortes de pregação (Remotion)

Receita testada neste projeto. O projeto Remotion já existe na raiz do repositório
(`src/VideoVertical.tsx` é o exemplo funcional; `public/` guarda vídeo, fonte e sons).

O estilo visual e sonoro completo está em `references/estilo-visual-e-sonoro.md`. Leia antes de
montar a edição. Os números de tempo abaixo vieram da análise de um corte de referência de 74 s.

## Fluxo

1. **Entender o pedido.** Confirme: vídeo-base, música de fundo (se houver), título/textos, se há
   trechos específicos (ex.: "preto e branco de 1 a 6 s"). O que o usuário pedir expressamente
   vale mais que o estilo padrão.
2. **Preparar.** Copie o vídeo para `public/video.mp4`. Meça com `ffprobe` (duração, fps,
   resolução) e ajuste `durationInFrames` em `src/Root.tsx` (duração × 30). Composição:
   1080x1920, 30 fps.
3. **Transcrever com tempo por palavra** (obrigatório antes de qualquer efeito):
   ```
   ffmpeg -y -i public/video.mp4 -vn -ac 1 -ar 16000 audio.wav
   python3 -I .claude/skills/editar-cortes-pregacao/scripts/transcrever.py audio.wav src/transcricao.json
   ```
   Mostre a transcrição ao usuário **antes de criar legendas** e peça correção de palavras erradas.
4. **Sincronizar pela fala, não pelo relógio.** Cada efeito cai na palavra-chave, no tempo da
   transcrição. Se o tempo pedido pelo usuário não bate com a fala, use o da fala e **avise a
   diferença e o motivo**. Para confirmar uma palavra em tempo exato, transcreva fatias curtas do
   áudio (com 0,5 s de silêncio antes e depois).
5. **Localizar o rosto** com frames de contato e grade (`drawgrid`) para ancorar o zoom
   (`transformOrigin`). Câmeras em movimento tiram o rosto do quadro: rastreie por pontos-chave e
   interpole (`FACE_TRACK` em `src/VideoVertical.tsx`). Avise o usuário nos trechos sem rosto.
6. **Montar a edição** seguindo o guia de estilo (itens abaixo).
7. **Prévia curta primeiro** (6–10 s com som), mande ao usuário e só então renderize tudo. Use
   `SendUserFile`.
8. **Conferir tecnicamente** o que não dá para ouvir/ver: quadros-chave em folha de contato,
   volume por trecho (`volumedetect`), amostras estouradas (>= 32700) antes/depois.
9. **Commit e push** na branch indicada pela sessão. Se o push for recusado (403), é permissão do
   app do GitHub no repositório: oriente o usuário a reconectar em https://claude.ai/connect-github.

## Efeitos (parâmetros que funcionaram)

- **Zoom seco:** sobe da escala anterior para a nova em **2 quadros** e segura (1,3x, depois 1,6x).
- **Tremida:** ~8 quadros, amplitude 28 px, decai a zero (`random()` do Remotion, nunca
  `Math.random()`). Some escala extra (`1 + 2*amp/1080`) enquanto treme para não aparecer borda.
- **Clarão branco:** 2 quadros, camada branca opacidade 1.
- **Borrão:** `blur(10px)` decaindo em ~6 quadros.
- **Preto e branco forte:** `grayscale(1) contrast(1.8) brightness(1.05)` só no intervalo pedido.
- **Texto gigante:** fonte Anton (`@fontsource/anton`, copie o `.woff2` para `public/fonts/` e use
  `loadFont` de `@remotion/fonts`), 200 px, branca, maiúscula, centro, entra com escala 1,25→1.
- **Legenda padrão e especiais** (palavra de emoção serifada, texto espalhado, clímax empilhado):
  ver `references/estilo-visual-e-sonoro.md`.
- **Texto atrás do pregador:** exige recorte da pessoa por quadro (modelo de segmentação via pip);
  ficam bordas imperfeitas. Avise antes e mostre um teste.

## Som

- **A voz manda.** O áudio de pregação já vem perto de 0 dB: some efeitos sem abaixar a voz e
  estoura. Abaixe a voz (~0,55) por ~0,5 s em cada impacto (`volume` por quadro em `<OffthreadVideo>`).
- **Alinhar pelo pico, não pelo início do arquivo.** Meça o instante do pico de cada efeito e
  adiante o início do `<Sequence>` por esse tempo (whoosh pico 0,25 s → −8 quadros; impacto
  0,09 s → −3; estalo 0,13 s → −4).
- **Fonte dos efeitos**, em ordem de preferência: (1) arquivos que o usuário mandar;
  (2) **ElevenLabs** (modelo `eleven_text_to_sound_v2`, nó `sfx`; ~0,5 centavo de dólar por efeito):
  uma geração por som, prompt curto e concreto, `generations_count: 1`, **nunca repetir a chamada
  para "tentar de novo"** (cobra de novo), baixar os `.mp3` pelas URLs assinadas para
  `public/sfx/`; (3) síntese local em `scripts/gerar_sfx_sintetico.py` (sons básicos).
- **Música de fundo:** só usar arquivo enviado pelo usuário (pedir confirmação de licença). Fica
  ~20 dB abaixo da voz. Não tente identificar a música.

## Lição do corte C: a voz sumiu

Na primeira mixagem a voz foi baixada para -20 LUFS (a gravação ao vivo vem em -10) mas os efeitos
continuaram com volume absoluto, uns 20 dB acima da voz: o vídeo parecia "mudo, só fundo". Agora
`mixar_audio.py` escala os efeitos pelo pico da voz e **para com erro se a voz não estiver pelo menos
6 dB acima de música+efeitos**. Antes de entregar, confira também a correlação entre o arquivo final e a
voz isolada (deve ser > 0,8; no corte C deu 0,99). Música de fundo é opcional (`--sem-musica`):
o usuário pediu só a voz no corte C.

## Lição do feedback do corte C: contexto, cortes e legenda

- **Duração e estrutura:** 1 a 1,5 min. Abra com um gancho (a frase de impacto antecipada, ~4 s), depois
  contexto, virada (clímax) e desfecho. Corte curto de 35 s sem contexto foi reprovado.
- **Cortes sem comer fala:** só pausas > 1,2 s viram corte; o ritmo vem de zoom e texto. O fim de cada trecho
  vai até o fim da palavra + 0,34 s (sem passar da próxima palavra) e a emenda tem fade de 30 ms.
  Limite de trecho só é movido quando cai dentro de uma palavra (senão "minha" do início sumia).
- **Legenda não pode pular de altura:** sempre uma linha só, altura fixa, reduzida em conjunto se for larga.
  Antes, frases de 2 linhas (palavra de emoção grande) mudavam de posição e pareciam "em cima, depois embaixo".
- **Texto da legenda:** conferir a transcrição inteira e usar `correcoes` em `cortes_config.py`
  (ex.: "pontou" -> "apontou"); nomes próprios (Deus, Jeremias, Senhor) com maiúscula.
- **Escolha do trecho:** olhe uma folha de contatos do bruto. Descarte onde o pastor sai do quadro ou fica
  na borda (no corte A, de 31 s a 42 s do bruto), cortando em limite de frase.
- **Voz isolada:** isole a voz do áudio já editado (não fatie uma isolada de edição antiga, pode dessincronizar).

## Fundo novo só em destaques

O padrão é a filmagem original reenquadrada na vertical (câmera virtual seguindo a cabeça do pastor,
sem passar da borda da imagem e sem mostrar a legenda embutida do rodapé). O fundo novo (pastor recortado)
vale só nos textos marcados com `"recorte": True` na configuração. Trechos em que o pastor fica na
borda da imagem da transmissão devem ser descartados do corte (não dá para centralizar).

## Ambiente (armadilhas já encontradas)

- **Chrome do Remotion não baixa** (rede bloqueada): `remotion.config.ts` aponta para o
  `chrome-headless-shell` pré-instalado em `/opt/pw-browsers/`.
- **Modelo Whisper** vem do Hugging Face. O usuário precisa liberar em *Network access*:
  `huggingface.co`, `cdn-lfs.huggingface.co`, `us.aws.cdn.hf.co`, `cas-server.xethub.hf.co`
  (ou `*.hf.co`). Guie-o passo a passo (ele não sabe onde fica). Se mesmo assim falhar com 403,
  é host faltando: leia o redirect com `curl -s -o /dev/null -w '%{redirect_url}'`.
- `faster-whisper` não lê arquivo (erro no PyAV): passe o áudio como array numpy, como no script.
- **Google Drive:** o conector não lista nem baixa o conteúdo de pastas. Peça os arquivos anexados
  ou links individuais.
- Efeitos pagos/gerados (ElevenLabs): diga o custo antes de gerar em lote; confirme antes de
  qualquer geração longa.
- Plugins instalados no meio da conversa só valem em sessão nova.

## O que não prometer

- Não ouço áudio nem identifico músicas/sons de outro vídeo: leio transcrição e números
  (volume, picos). O julgamento "soou bom" é do usuário.
- Copiar o **estilo** (ritmo, tipografia, cor, tipos de efeito) é ok; não reaproveitar marca,
  logo, imagens, música ou texto do concorrente.
- Fontes pagas: usar a gratuita mais parecida e avisar.
