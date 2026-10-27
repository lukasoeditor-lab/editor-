# Roteiro 2: ferramentas de edição

> Data: 2026-10-27 · Projeto: editor-

- **Pedido:** seguir `setup/2-instalar.md` e deixar o estúdio pronto para editar vídeo com IA.
- **Feito:**
  - Os instaladores do modelo são só para Mac e Windows; aqui (Linux na nuvem) as mesmas etapas foram feitas à mão.
  - Programas base já existiam (git, node, ffmpeg 6.1.1, uv 0.11.32). Codex 0.164.0 instalado por npm.
  - `uv sync` em modo leve: Python 3.11.17 no `.venv` com as bibliotecas de som, legenda, quadros e referências.
  - Skills do estúdio ligadas uma a uma em `.claude/skills/` (a pasta já tinha as skills do pacote de edição e não foi substituída). Skills externas instaladas: HyperFrames, Remotion, transitions-dev, watch e humanizer.
  - 56 efeitos sonoros gerados em `05-biblioteca/som/sfx`.
  - ai-memory ligado também ao Codex (`--no-service`).
  - Docs de `02-ferramentas/` atualizados com versões e caminhos; `inventario.md` regenerado.
- **Decisões:**
  - Sem a IA de áudio (torch, beat_this, audio-separator): o site do PyTorch é bloqueado nesta nuvem. Voz isolada continua possível com o `audio-separator` instalado por `pip`, como foi feito nos cortes.
  - EffectCraft e After Effects ficaram como "não instalado": o EffectCraft só tem versão para Mac e Windows; o After Effects é pago e opcional.
- **Verificação:** `uv run setup/conferir.py` disse "Essencial pronto". Os itens com `--` são opcionais. O Chromium do Playwright não baixou (site bloqueado), mas o Chromium do sistema serve para render.
- **Próximo:** o Lukas fecha e abre a IA nesta pasta (skills e MCP novos só aparecem em sessão nova); aprovar os ganchos do Codex com `/hooks`; login do Codex; roteiro 3, `setup/3-referencias.md`. Para a IA de áudio e o EffectCraft, rodar o instalador no Mac ou Windows do Lukas.
