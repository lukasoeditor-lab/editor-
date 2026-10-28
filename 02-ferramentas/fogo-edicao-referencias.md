# fogo-edicao-referencias: edição a partir de referências

> Data: 2026-10-28 · Tipo: guia · Status: vigente

**Resumo:** skill que o Lukas mandou (zip `fogo-edicao-referencias.zip`) para analisar vídeos de referência e editar uma gravação original com cortes de pausas, legendas e animações coerentes com a fala. Só texto: uma `SKILL.md` e dois prompts (`references/prompt-01.md` entende a referência; `prompt-02.md` executa a edição).

- **Onde fica:** `.agents/skills/fogo-edicao-referencias/` (o `.claude/skills/` aponta para ela).
- **Quando usar:** pedido para "aprender o estilo" de uma referência e aplicar numa gravação. Para cortes de pregação da Pregue, a skill principal continua sendo `corte-de-pregacao`; esta complementa na análise da referência (guia de estilo com tabela de cenas) e nos cuidados de revisão (emendas, palavras inteiras, texto fora da tela, sem quadro preto).
- **Regras que ela traz:** transcrever com tempos antes de cortar; não cortar sílabas (não usar só limiar de silêncio); animação determinística por tempo/quadro; MP4 H.264, AAC, 9:16, 1080×1920 a 30 fps; não afirmar que o vídeo está pronto se o ambiente não renderizou; não usar mídia de terceiros sem autorização.
- **Credenciais:** nenhuma.
- **Log:** 2026-10-28, instalada a partir do zip enviado pelo Lukas (3 arquivos de texto lidos antes de instalar; nada executável).
