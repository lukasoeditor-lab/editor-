---
name: narracao
description: Gera narração (voz em off) para vídeos a partir do roteiro usando o VoiceStudio (local e gratuito) ou o ElevenLabs (nuvem) - escolhe a voz em português adequada, gera, baixa o áudio e prepara os tempos das palavras para sincronizar legendas e cenas. Use quando o usuário pedir narração, locução, voz em off ou um vídeo sem a própria voz.
when_to_use: Pedidos como coloca uma narração, gera a voz, quero uma locução, faz o vídeo com voz de IA.
---

# FREMEX · Narração

## Escolher o motor

| Motor | Quando usar | Custo e licença |
|---|---|---|
| **VoiceStudio** (local) | Padrão quando está instalado e aberto: o texto e a voz não saem do computador | Gratuito. **Atenção:** o modelo padrão OmniVoice tem pesos CC-BY-NC, sem uso comercial. Para cliente, use um modelo do Model Manager cuja licença permita uso comercial |
| **ElevenLabs** (nuvem) | Vozes profissionais prontas, ou quando o VoiceStudio não está disponível | Créditos da conta. O plano gratuito não permite uso comercial |

Diga ao usuário qual motor vai usar e por quê. Para uso comercial, confirme a licença do modelo ou do plano **antes** de gerar.

## Com o VoiceStudio

1. Confira se está no ar: `curl http://localhost:3900/health`. Se não estiver, peça para o usuário abrir o aplicativo, ou rodar `/fremex:setup` se não estiver instalado.
2. Pelo MCP `voicestudio` (`/mcp`): `check_health`, `list_voices` e depois `generate_speech` com o texto aprovado e a voz escolhida. Use os IDs de voz que a ferramenta retornar; nunca invente.
3. Sem MCP, use a API compatível:
   ```bash
   curl --fail-with-body http://localhost:3900/v1/audio/speech -H "Content-Type: application/json" --data-binary @fala.json --output trabalho/narracao.wav
   ```
   com `fala.json` = `{"model":"tts-1","voice":"<id da voz>","input":"<texto>","response_format":"wav"}`.
4. Confira se o arquivo é áudio de verdade (`ffprobe trabalho/narracao.wav`): uma resposta de erro pode ser gravada no lugar do áudio.
5. Para criar uma voz nova a partir de uma descrição, use `describe_voice` e depois `design_voice`. Para clonar uma voz, use `clone_voice`, **somente com autorização por escrito da pessoa**.
6. Se o modelo não estiver instalado, informe o tamanho e a licença e peça autorização antes de baixar.

## Com o ElevenLabs

1. Confirme que o conector do ElevenLabs está ativo (`/mcp`). Se não estiver, peça para o usuário conectar em claude.ai → Configurações → Conectores, ou para gravar a própria voz.
2. **Avise o custo:** cada geração consome créditos da conta ElevenLabs do usuário.
3. Liste vozes com `languages: ["pt"]` e os filtros que combinam com o pedido (gênero, idade, `use_cases: ["social_media"]` ou `["advertisement"]`). Se o cliente tem voz definida em `cliente.md`, use a mesma. Diga qual voz escolheu e por quê.
4. Gere a fala. Não repita a chamada para "tentar de novo": cada chamada cobra créditos.
5. Acompanhe o status até terminar e baixe o MP3 para `trabalho/narracao.mp3`. Se o download for bloqueado pela rede, peça para o usuário baixar pelo link do ElevenLabs e salvar na pasta do projeto.

## Depois

- Tempos das palavras: `python3 "${CLAUDE_SKILL_DIR}/../reels/scripts/palavras.py" trabalho/narracao.mp3 trabalho/palavras.json` (troque `.mp3` por `.wav` se a narração veio do VoiceStudio).
- Volume final é tratado na exportação (-14 LUFS).
- Registre em `cliente.md` a voz usada, para manter a consistência nos próximos vídeos.

## Regras

- Nunca clone a voz de uma pessoa sem autorização por escrito dela.
- Informe ao cliente que a narração foi gerada por IA.
