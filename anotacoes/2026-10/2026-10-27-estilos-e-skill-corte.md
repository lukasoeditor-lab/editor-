# Estilos da Pregue e skill corte-de-pregacao

> Data: 2026-10-27 · Projeto: editor-

- **Pedido:** assistir 5 vídeos de referência do Lukas, aprender texto, fontes, efeitos e som, e pôr tudo no cérebro com uma skill melhorada.
- **Feito:**
  - 5 referências organizadas em `03-referencias/motion/` (catalogadas; o `.mp4` não vai para o git) e analisadas em `03-referencias/analises/` (uma por vídeo + a síntese `2026-10-27-estilos-pregue.md` com 4 estilos, números medidos, mapa de som e receita em HyperFrames).
  - Skill nova `.agents/skills/corte-de-pregacao/` (fluxo de 10 passos, regras, referências `pipeline.md` e `roteiro.md`, exemplo `roteiro.exemplo.json` do corte 2).
  - Scripts novos em `scripts/video/corte_pregacao/`: `preparar_corte.py`, `gerar_projeto.py`, `misturar_audio.py` (todos com `--autoteste`).
  - Efeitos novos no gerador, testados em quadros do HyperFrames: popup de notificação, título vermelho, flash de luz/branco/queima de filme, Grid Cut, preto e branco com legenda amarela, assinatura final.
  - Números novos em `06-metodo/regras.md`, aprendizados, doc `02-ferramentas/isolar-voz.md`, ponteiro na `estudio-video`.
- **Decisões:**
  - Estilo A (legenda sans + palavra-chave em serifa itálica) é o padrão dos cortes; B, C e D são variações por tipo de vídeo.
  - Playfair Display é a aproximação da serifa itálica das referências (a fonte original não está nas fontes incluídas).
- **Verificação:** os 3 autotestes passaram; o projeto de teste com todos os efeitos passou no `check` (0 erros) e os quadros foram conferidos. Não foi renderizado um vídeo completo com os efeitos novos. Os tipos de efeito sonoro das referências foram deduzidos por análise de áudio (a separação deixa resíduo); ninguém ouviu os arquivos.
- **Próximo:** aplicar a skill ao corte 3 e refazer o corte 1 no estilo novo, se o Lukas aprovar; conferir de ouvido os primeiros cortes.
