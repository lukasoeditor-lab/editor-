# Estilos da Pregue: o que as 5 referências ensinam

> Data: 2026-10-27 · Tipo: análise · Status: vigente

**Resumo:** síntese das cinco referências que o Lukas enviou para definir o visual dos vídeos da Pregue – Além do Púlpito. Quatro estilos (A a D), com os números medidos, o mapa de som e a receita para reproduzir cada um em HyperFrames. A skill que usa tudo isto é a [corte-de-pregacao](../../.agents/skills/corte-de-pregacao/SKILL.md). Análises individuais: [A](2026-10-27-r5-sacrificio.md) · [B](2026-10-27-r2-correria.md) · [C1](2026-10-27-r1-tempestade.md) · [C2](2026-10-27-r4-silencio.md) · [D](2026-10-27-r3-gridcut.md).

## Os quatro estilos

| | A. Legenda + serifa | B. Leve + cor que muda | C. Cinema com IA | D. Tutorial gráfico |
|---|---|---|---|---|
| Referência | r5 "lenha" | r2 "correria" | r1 "tempestade", r4 "silêncio" | r3 "Grid Cut" |
| Formato | 9:16, 41 s | 9:16, 37 s | 3:2, 84–88 s | 4:3, 34 s |
| Uso na Pregue | **corte de pregação (padrão)** | corte reflexivo, mais calmo | devocional e história bíblica com B-roll | dica, aula, bastidor |
| Legenda base | sans bold minúscula pequena, palavra a palavra | sans leve (300), espalhada | sans bold minúscula minúscula, no canto (esq. ou dir.) | Helvetica bold em tamanhos diferentes |
| Palavra-chave | serifa itálica 2× maior, entra desfocada | amarelo (objeção em P&B) | serifa **vermelha** gigante, caixa-alta | uma palavra 5–8× maior |
| Cor | laranja × petróleo, texto branco | vermelho → petróleo → P&B | azul-aço frio, vermelho #DC2427 | neutro, branco e preto |
| Transição | troca de enquadramento 4 quadros, queima de filme no fim | flash de luz 3–4 quadros, mudança de grade | montagem rápida (0,1–0,4 s), flash estourado | flash branco, Grid Cut |
| CTA | popup de notificação "seguir" | assinatura final | — | linha final pequena |
| Fecho | queima de filme + assinatura | preto + assinatura | — | palavra entre aspas |
| Loudness | −14,1 LUFS | −14,1 LUFS | −14,3 / −14,4 LUFS | −14,3 LUFS |

Todos os cinco masters ficam entre **−14,1 e −14,4 LUFS** (LRA 2 a 3,8), o que confirma o −14 LUFS de [regras.md](../../06-metodo/regras.md).

## Regras comuns (valem para os quatro)

1. **Texto sempre acompanha a fala**: a palavra entra no quadro em que é dita; nada entra antes.
2. **Legenda pequena**, 4,5 a 6% da largura (≈ 42 px em 720 px, ≈ 50–65 px em 1080 px), nunca sobre o rosto.
3. **Um destaque por frase** (no máximo 3): é o que dá a "voz" do estilo.
4. **O vídeo é a estrela**: sem cartões brancos, sem molduras, sem sticker; a diferença está na tipografia e na cor.
5. **Grão e contraste**: grade cinematográfica com sombras frias, pele quente, grão visível, vinheta leve.
6. **Transição curta (3 a 4 quadros ≈ 0,13 s)**, com flash de luz ou queima de filme; nunca dissolve longo.
7. **Fecho limpo**: preto + marca desenhada ou palavra final. Nada de "obrigado".

## Receita em HyperFrames (valores de partida)

| Efeito | Como fazer | Valores |
|---|---|---|
| Legenda sans | texto minúsculo, Inter 700 (ou Montserrat 700), `letter-spacing: -0.02em`, entrelinha 0,95 | tamanho 4,8% da largura; sombra 0 3px 14px rgba(0,0,0,.55); cada palavra `fromTo` opacidade 0→1, `y` +8→0, `blur(6px)→0`, 0,14 s `power3.out` |
| Palavra-chave serifa | Playfair Display Italic 700, 1,8 a 2,2× o tamanho da sans | entra com `blur(14px)→0`, `scale 1.25→1`, 0,27 s `expo.out`; brilho `text-shadow: 0 0 18px rgba(255,255,255,.35)` |
| Palavra apagada | última palavra do grupo | `opacity .35` + `blur(3px)` nos últimos 0,2 s antes de sumir |
| Popup de notificação | banner branco arredondado, avatar + nome + texto | topo; desce 0,3 s com overshoot 8% e `blur(8px)→0`; fica 2,5–3 s; sai subindo em 0,25 s |
| Flash de luz | gradiente radial quente (#FFD27A → #FF6A00 → transparente) em `mix-blend-mode: screen` | opacidade 0→0,9→0 em 4 quadros sobre o corte |
| Queima de filme | flash laranja/vermelho com borda cromática (vermelho/ciano 2 px) em 5 quadros | no fim do vídeo, antes do preto |
| Troca de grade | animar a saturação do plano (media-treatment) vermelho → petróleo → P&B | 0,4 s `power2.inOut`; P&B só para a fala do "outro" |
| Legenda amarela | cor #F7D903 | só dentro do trecho em P&B |
| Assinatura | traço desenhado: máscara que revela da esquerda para a direita | 1,8 s `power2.inOut`; depois fica parada ≥ 2 s |
| Título vermelho gigante | Playfair Display 900 caixa-alta | cor #DC2427; largura 60–100%; fade 4 quadros; `scale 1.04→1` |
| Grid Cut | grade 10×N de quadrados; cada um troca no instante `ordem_aleatória_fixa × 0,5 s / total` | total 0,5 s; ordem fixa (seed), nunca `Math.random` |
| Flash branco | opacidade 0→1→0 em 3 quadros | `mix-blend-mode: screen` |

## Mapa de som (o que os cinco vídeos fazem)

| Momento | Som | Nível sobre a música |
|---|---|---|
| Abertura (título ou primeira palavra) | impacto grave curto + cauda | +15 a +17 dB, ~0,4 s |
| Troca de plano / flash | whoosh curto (0,2–0,5 s) + toque seco | +2 a +4 dB |
| Palavra-chave em serifa | quase nada ou um "hit" grave baixo (sem tonal) | +1 a +2 dB |
| Popup de notificação | som de notificação curto (tonal agudo) | +6 dB |
| Fecho (queima de filme) | transiente + cauda, depois silêncio com a música caindo | +3 dB, queda de 6 a 10 dB |
| Cama de música | contínua, estável | voz −14 LUFS; música 10 a 15 dB abaixo da voz (nos cortes verticais da referência a música ficou mais alta, ~3 a 6 dB abaixo: use isso só em trailer) |

**Limites da medição:** a separação de voz deixa resíduo de fala na faixa de música (nos dois cortes verticais a "música" mediu mais alta que a voz). Os golpes foram achados por picos de energia e os tipos de efeito foram deduzidos pelo momento visual. Não foi possível ouvir os arquivos; confira de ouvido nos primeiros vídeos.

## Fontes e cores (tokens)

| Token | Valor |
|---|---|
| Sans de legenda | Inter 700 / Montserrat 700 |
| Sans leve (Estilo B) | Inter 300 / Montserrat 300 |
| Serifa de destaque | Playfair Display Italic 700 (itálica) ou Bold 900 (título vermelho) |
| Vermelho de título | #DC2427 (também #D9050C e #FE0001 medidos) |
| Amarelo de objeção | #F7D903 |
| Laranja da cena A | #A75338 |
| Azul-petróleo da cena A | #7EB5C0 |
| Azul-aço das cenas C | grade fria, sombras ~#0D1B2A |
| Branco | #FFFFFF |

## O que NÃO copiar

- Assinatura, nome e foto do popup do Filipe Levak: use a marca da Pregue.
- Trecho de fala, trilha ou cenas de IA dos vídeos: são referências de estilo, não material para republicar.
- CTA do tutorial em espanhol (vende um plugin).
