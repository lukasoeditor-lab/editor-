---
name: narracao
description: Gera narração (voz em off) para vídeos a partir do roteiro usando o conector do ElevenLabs - escolhe a voz em português adequada, gera, baixa o áudio e prepara os tempos das palavras para sincronizar legendas e cenas. Use quando o usuário pedir narração, locução, voz em off ou um vídeo sem a própria voz.
when_to_use: Pedidos como coloca uma narração, gera a voz, quero uma locução, faz o vídeo com voz de IA.
---

# FREMEX · Narração

## Antes de gerar

1. Confirme que o conector do ElevenLabs está ativo (`/mcp`). Se não estiver, peça para o usuário conectar em claude.ai → Configurações → Conectores, ou para gravar a própria voz.
2. **Avise o custo:** cada geração consome créditos da conta ElevenLabs do usuário. O plano gratuito **não permite uso comercial**, então o uso para cliente exige plano pago.
3. Tenha o texto aprovado (skill `roteiro`).

## Gerar

1. Liste vozes com `languages: ["pt"]` e os filtros que combinam com o pedido (gênero, idade, `use_cases: ["social_media"]` ou `["advertisement"]`). Se o cliente tem voz definida em `cliente.md`, use a mesma.
2. Diga qual voz escolheu e por quê, numa frase.
3. Gere a fala. Não repita a chamada para "tentar de novo": cada chamada cobra créditos.
4. Acompanhe o status até terminar e baixe o MP3 para `trabalho/narracao.mp3`.

Se o download for bloqueado pela rede, explique ao usuário e peça para baixar pelo link mostrado no ElevenLabs e salvar na pasta do projeto.

## Depois

- Tempos das palavras: `python3 "${CLAUDE_SKILL_DIR}/../reels/scripts/palavras.py" trabalho/narracao.mp3 trabalho/palavras.json`
- Volume final é tratado na exportação (-14 LUFS).
- Registre em `cliente.md` a voz usada, para manter a consistência nos próximos vídeos.

## Regras

- Nunca clone a voz de uma pessoa sem autorização por escrito dela.
- Informe ao cliente que a narração foi gerada por IA.
