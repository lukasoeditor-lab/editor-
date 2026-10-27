# Avaliação das 24 ferramentas instaladas (para cortes de pregação, palestra e evento)

Critério: serve para editar cortes verticais com a voz do orador? Vale mais o que foi lido por dentro (SKILL.md, scripts)
do que o que foi avaliado só pela descrição. **Nenhuma foi testada com vídeo do usuário.** Onde a coluna diz "descrição",
a nota veio só do README/descrição do pacote.

Legenda: **INCORPORADO** = a ideia já virou regra ou script desta skill. **APOIO** = usar sob demanda. **NÃO** = não serve
para este trabalho (ou duplica o que já existe).

| # | Pacote | Veredito | O que aproveitar / por que não | Base |
|---|---|---|---|---|
| 1 | Video Use | APOIO + INCORPORADO | Regras de produção: fades de 30 ms, nunca cortar dentro de palavra, folga nas bordas, SRT na linha do tempo final, cache da transcrição, **confirmar o plano em palavras antes de cortar** | lido |
| 2 | Herk Edit Kit | NÃO | Kit de HyperFrames/Codex; duplica o fluxo Remotion | descrição |
| 3 | FFmpeg Skill | APOIO | `silence.py --speech-aware` (só pausas entre frases), `sync.py` (**áudio da mesa/lapela + câmera**, útil no evento), `scenes.py --highlights`, `loudness`, `look.py` (folha de contatos), `doctor` | lido |
| 4 | HyperFrames (plugin) | NÃO | Motor alternativo ao Remotion; só se o usuário pedir | descrição |
| 5 | Remotion Skills | APOIO | Já eram do plugin `remotion`; boas práticas de legenda (`createTikTokStyleCaptions`) | lido |
| 6 | Video Shotcraft | NÃO | Vídeo de produto a partir de páginas web | descrição |
| 7 | TikTok video skills | INCORPORADO | `short-form-video`: gancho na tela no 1º quadro, mudança visual a cada 2-4 s, áreas seguras 900x1400. `caption-animation`: palavra por palavra + SRT. `lower-thirds`: faixa com nome. `countdown-video`: NÃO | lido |
| 8 | Motion Graphics (Barty-Bart) | APOIO | `sound-effects`: conferir batida/mix; `motion-broll`: inspira inserts de motion nos momentos da fala. `explainer-*`, `object-separation`: NÃO (já temos recorte RVM) | lido (parcial) |
| 9 | Clipify | APOIO | Achar momentos em vídeo longo; **checar se o fato está em quadro**; cuidado com legenda queimada na fonte (alinhar com o master sem legenda por correlação de áudio) | lido |
| 10 | Claude Shorts | INCORPORADO | Rubrica de pontuação de candidatos (5 critérios com pesos), tabela de candidatos para aprovação, ajuste de bordas em palavra e silêncio | lido |
| 11 | YouTube Agent Skill | INCORPORADO (parte) | `yt-shorts`: o trecho precisa abrir num pensamento completo, ter uma virada e terminar numa frase; escrever **primeira linha nova** e texto de tela diferente da fala; ponto de laço. `yt-edit`: tirar pausa pelo MEIO. `yt-retention`: só com export do YouTube Studio | lido |
| 12 | Claude Video Vision | NÃO | Faz o que o `/watch` já faz | descrição |
| 13 | /watch | APOIO | Analisar vídeo de referência do cliente (quadros + transcrição) | lido |
| 14 | Watch Video | NÃO | Só por comando manual; duplica o `/watch` | descrição |
| 15 | Claude Watch | NÃO | Notas de estudo de aula; duplica o `/watch` | descrição |
| 16 | Omni Captions | APOIO | Converter e traduzir legendas, alinhar legenda ao áudio (`LaiCut` exige chave LattifAI) | lido (parcial) |
| 17 | Color Grade AI | APOIO | LUT de correção para gravação de evento com cor ruim (aplicar com `lut3d` do ffmpeg) | descrição |
| 18 | ElevenLabs Skills | APOIO | Isolador, efeitos, música por API **se houver chave**; sem chave, usar o conector | lido (parcial) |
| 19 | Pexo | NÃO | Vídeo gerado por IA na nuvem, com cobrança | descrição |
| 20 | Visual Skills | NÃO | Prompts para filme/imagem de IA | descrição |
| 21 | Claude Code Video Toolkit | NÃO | Pipeline próprio com serviços de nuvem | descrição |
| 22 | OpenMontage | NÃO | Pipeline agêntico concorrente | descrição |
| 23 | Superpowers | APOIO | Fluxo de planejamento e testes para código; pode ser desligado se atrapalhar | descrição |
| 24 | Skill Creator | APOIO | Evoluir esta skill com avaliações | descrição |

## O que virou ferramenta nesta skill
- `scripts/verificar_plano.py`: confere duração (60-90 s), gancho na tela em até 0,5 s, mudança visual a cada 4 s, volume dos efeitos.
- `scripts/exportar_srt.py`: legenda fechada (`.srt`) na linha do tempo do vídeo final.
- **Faixa com o nome do orador** (`faixa` em `cortes_config.py`, `src/corte/FaixaNome.tsx`), acima dos 320 px de baixo.

## Rubrica para escolher trechos (de Claude Shorts + yt-shorts, adaptada a pregação)
Pontuar 8 a 12 candidatos de 60 a 90 s, de 0 a 100: **gancho 30%**, **sentido sozinho 25%**, **intensidade emocional 20%**,
**densidade de mensagem 15%**, **desfecho 10%**. O candidato deve: (1) abrir num pensamento completo, (2) ter uma virada
(afirmação e depois a prova ou o clímax), (3) terminar numa frase firme, não numa conversa solta, e (4) ter o orador em
quadro e longe da borda. Mostrar a tabela (início-fim, nota, primeira frase, motivo) ao usuário e **só cortar depois da aprovação**.

## Áreas seguras (1080x1920)
Conteúdo no centro de 900x1400. Deixar livres ~120 px em cima, ~120 px à direita e **~320 px embaixo** (interface da rede).
Legenda ~49% da altura; marca e faixa acima de 1500 px.
