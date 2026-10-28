---
name: corte-de-pregacao
description: Faz cortes de pregação para Reels, TikTok e Shorts da Pregue – Além do Púlpito, no estilo dinâmico das referências do Lukas (legenda pequena, palavra-chave em serifa itálica, palavras espalhadas, popup de notificação, flash de luz, Grid Cut, preto e branco com legenda amarela, título vermelho, fecho com marca). Usar sempre que o pedido for achar os melhores momentos de uma pregação, cortar, legendar, "fazer motion design", pôr música e efeitos sonoros, ou entregar um corte vertical de pregador; também para legenda de post com CTA de venda e 5 hashtags.
---

# Corte de pregação (Pregue)

> Data: 2026-10-27 · Tipo: guia · Status: vigente

**Resumo:** receita completa para transformar uma pregação longa em cortes verticais de 45 a 75 s, com o visual das referências do Lukas e sem "cara de IA": o vídeo do pregador é a estrela, a tipografia e a cor fazem o resto. Começa em [03-referencias/analises/2026-10-27-estilos-pregue.md](../../../03-referencias/analises/2026-10-27-estilos-pregue.md) (os 4 estilos e os números medidos) e termina com o arquivo no [outputs/](../../../outputs/) e a legenda do post. A escolha do motor e do método geral é da [estudio-video](../estudio-video/SKILL.md); os números fixos moram em [06-metodo/regras.md](../../../06-metodo/regras.md).

## Antes de tudo

1. Leia `01-sobre-mim/perfil.md` (Lukas, Pregue – Além do Púlpito; tom profissional, direto e humanizado; quer clientes e posicionamento) e as análises de `03-referencias/analises/`.
2. **Fluxo combinado com o Lukas:** entregue **um corte por vez** para ele avaliar. Só depois do "está bom" você edita o próximo. Reaproveite o estilo aprovado.
3. Mande o vídeo no chat (SendUserFile) e também salve em `outputs/` (pasta que o app abre).
4. Direitos: as músicas comerciais podem derrubar o áudio do post; avise uma vez. O pregador do vídeo precisa autorizar o uso no perfil da Pregue; credite na legenda.

## Escolher o estilo

| Pedido | Estilo | Referência |
|---|---|---|
| Corte de pregação padrão | **A**: legenda sans pequena + palavra-chave em serifa itálica | [r5](../../../03-referencias/analises/2026-10-27-r5-sacrificio.md) |
| Corte mais calmo ou reflexivo | **B**: legenda leve espalhada, flash de luz, P&B com legenda amarela para a "objeção" | [r2](../../../03-referencias/analises/2026-10-27-r2-correria.md) |
| Devocional, história bíblica | **C**: apresentador + cenas de IA, título em serifa vermelha | [r1](../../../03-referencias/analises/2026-10-27-r1-tempestade.md), [r4](../../../03-referencias/analises/2026-10-27-r4-silencio.md) |
| Estilo básico, só legenda (pedido de 28/10) | **E**: CAIXA-ALTA, 1 a 3 palavras no meio do corpo, sem serifa; + transição com som a cada troca de cena e, no ponto de tensão, **fade para preto → preto e branco → fade para preto → cor** (evento `pb`) | [r6](../../../03-referencias/analises/2026-10-28-r6-basico-ericmello.md) |
| Dica, aula, bastidor | **D**: palavras em todos os tamanhos, Grid Cut, flash branco | [r3](../../../03-referencias/analises/2026-10-27-r3-gridcut.md) |

## O fluxo (cada passo tem um comando)

1. **Ter o vídeo.** O YouTube costuma bloquear o download na nuvem; peça o arquivo (Drive com link público baixa por `curl`, ver `references/pipeline.md`).
2. **Transcrever e escolher 3 cortes.** `uv run scripts/video/corte_pregacao/preparar_corte.py ... --transcrever` ou o `faster-whisper` direto. Critério dos cortes e como ler a transcrição: `references/pipeline.md` §2. Entregue ao Lukas uma tabela com tempo, resumo, por que viraliza.
3. **Escolher os trechos de cada corte** (início e fim em segundos do original, cortando o que não ajuda a ideia) e **corrigir a transcrição** (o Whisper erra nomes bíblicos e gíria; use a fala real).
4. **Preparar:** `uv run scripts/video/corte_pregacao/preparar_corte.py pregacao.mp4 04-projetos/AAAA-MM-DD-corte1/preparo --trechos "940.4:953.8,954.1:958.8" --isolar-voz --modelo-voz <UVR-MDX-NET-Voc_FT.onnx>`. Faz: recorte vertical que segue o pregador, pausas longas cortadas, voz isolada e normalizada em −16 LUFS.
5. **Escrever o roteiro** (`roteiro.json`): use **`frase`** (a legenda dinâmica das referências: bloco estreito que cresce palavra por palavra, palavra-chave em serifa; ver `references/legenda-dinamica.md`). `uv run scripts/video/corte_pregacao/roteirizar.py palavras.json roteiro.json --ini ... --fim ...` monta as frases sozinho; depois corrija o texto, escolha as palavras-chave e ponha os efeitos. Tipos de evento: `references/roteiro.md`; exemplo: `assets/roteiro.exemplo.json`. Regras: no máximo 1 a 3 destaques por frase; popup de notificação no primeiro terço; 1 interlúdio preto por corte, no máximo 2; fecho limpo.
6. **Gerar o projeto:** `uv run scripts/video/corte_pregacao/gerar_projeto.py roteiro.json preparo/ projeto/ --hf "<comando do hyperframes>"`. Cria o HyperFrames com legenda, efeitos, SFX da biblioteca (`05-biblioteca/som/sfx`), música e a cor de cinema (`media-treatment`).
7. **Conferir:** `npx hyperframes check --json` (zero erros) e `snapshot --at ...` em cada efeito. **Olhe os quadros** antes de renderizar.
8. **Renderizar** (`hyperframes render . -o ../render.mp4 -q looks`), em segundo plano e destacado do terminal (leva ~0,5 s por quadro com a grade: um corte de 50 s sai em ~20 min em 4 núcleos).
9. **Misturar o áudio:** `uv run scripts/video/corte_pregacao/misturar_audio.py projeto/index.html render.mp4 final.mp4`. Meça: voz −16 LUFS, final −14 a −16 LUFS, pico real ≤ −1 dBTP, efeitos no nível dos picos da fala.
10. **Entregar** (SendUserFile + `outputs/`) e escrever a **legenda do post**: gancho + valor + CTA de venda da edição de cortes + 5 hashtags (modelo em `references/pipeline.md` §7).

## Câmera aberta (palco inteiro, pregador pequeno)

`preparar_corte.py --rastreio cor --zoom 1.5 --ypos 0.4` segue o paletó azul (o rastreio por brilho segue os músicos) e calcula uma curva de recorte por trecho. Confira os quadros de `prep/base.mp4` antes de renderizar. A fonte em 720p fica mais macia quando ampliada; avise o Lukas e peça arquivo melhor se existir. O @ de baixo é o do **pregador** (imagem em `logo`), não o da Pregue.

## Regras que valem sempre

- **Não corte a fala no meio nem logo depois da última palavra** (pedido do Lukas em 28/10): o início do trecho fica ~0,15 s antes da 1ª palavra; o fim fica **0,7 a 1,2 s depois** da última palavra, sem passar do início da fala seguinte (menos 0,1 s). Meça a energia do áudio (50 ms) em volta do corte: a palavra final tem cauda de reverberação. O vídeo termina com o pregador ainda na tela (`cauda` curta, 0,5 s), nunca com tela vazia.

- **Sem zoom e sem câmera deslizante** (pedido do Lukas em 28/10): no estilo E o `punch_in` já vem desligado e o recorte usa zona morta.

- **Legenda = evento `frase`** (bloco estreito alinhado à esquerda, tracking −0,04em, palavra-chave em serifa na própria linha). **Não** usar legenda de uma linha com franja colorida: esse foi o erro do corte 2 v1.
- **Sem som por palavra:** nas referências nenhuma palavra tem efeito sonoro (medido). O som está na música, nas trocas de plano/flashes, no popup e no impacto de abertura.
- **Texto acompanha a fala**, nunca antes. Nada cobre o rosto.
- **Sem cartões brancos.** O vídeo fica na tela; o destaque é tipografia, cor e flash curto (3 a 4 quadros).
- **Cor com sentido:** vermelho (#DC2427) só em título; amarelo (#F7D903) só na fala do "outro" em P&B.
- **Um efeito sonoro por causa visível**, no nível da fala: impacto na palavra-chave, whoosh na troca, notificação no popup. Música 14 dB abaixo da voz.
- **Marca:** @pregue.oficial embaixo (36% da largura) e "ALÉM DO PÚLPITO" no topo; nada de assinatura de terceiros.
- Confira de **ouvido** os dois primeiros cortes: as medições não substituem.

## O que dá errado (já aconteceu)

| Sintoma | Causa e conserto |
|---|---|
| `check` com `request_failed` do GSAP | CDN bloqueado: o gerador usa `assets/gsap.min.js` (baixado do npm) |
| Render some quando o comando de espera sai | rode o render destacado (`setsid nohup ... &`), nunca preso ao terminal |
| Impacto mais alto que a voz | volume dos SFX: o gerador usa fatores por categoria; confirme com a medição do passo 9 |
| Pico acima de 0 dBFS no MP4 | limitador do misturador baixo (`--teto 0.68`) |
| Texto sai da tela | palavra grande: o gerador ajusta o tamanho à largura; em `scatter` use `x` pequeno para a última palavra |
| Elemento com `.` no id | seletores inválidos: use ids sem ponto |
| Voz separada soa estranha | confira de ouvido; se houver chiado, use `--isolar-voz` desligado (a fala já era limpa nos testes) |
