# Segundo cérebro: modelo, memória e perfil

> Data: 2026-10-27 · Projeto: editor-

- **Pedido:** transformar a pasta no segundo cérebro para vídeo com IA, seguindo `setup/1-segundo-cerebro.md`.
- **Feito:**
  - Modelo `estudio-ia` trazido para a pasta (remoto `modelo`; `git pull modelo main` puxa novidades). O pacote de edição de vídeo foi mantido: `README.md` virou `README-meu.md`, `CLAUDE.md` virou `CLAUDE-editor.md`, e os dois `.gitignore` foram juntados.
  - ai-memory 3.2.8 instalado e ligado ao Claude Code. Bloco de instruções no fim do `AGENTS.md` e skills `ai-memory-*` em `.agents/skills/`.
  - `.ai-memory.toml` criado (projeto `lukas-estudio`).
  - Perfil preenchido em `01-sobre-mim/perfil.md` (status vigente).
  - Primeiro fato gravado na memória: `perfil/lukas-e-segundo-cerebro.md`.
- **Decisões:**
  - Ficou na branch de trabalho `ccr-7f3b221f-0cvhjq` em vez de criar `main`, porque `git checkout -B main` apagaria o pacote de edição da pasta.
  - Sem serviço automático (systemd) na nuvem: o servidor foi iniciado na mão com `ai-memory serve --transport http`.
- **Verificação:** busca "Lukas" na memória achou a página; servidor respondeu `{"status":"ok"}`. Ficou sem conferir o teste final com uma sessão nova ("o que você sabe sobre mim e sobre este estúdio?"), que depende de fechar e abrir a IA.
- **Próximo:** abrir a IA de novo dentro desta pasta e fazer a pergunta de teste; depois o roteiro 2, `setup/2-instalar.md`. Na nuvem a memória some quando a sessão acaba: repetir `ai-memory setup` no computador do Lukas.
