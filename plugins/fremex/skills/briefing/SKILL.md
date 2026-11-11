---
name: briefing
description: Transforma o pedido de um cliente (mensagem, áudio transcrito, e-mail, conversa) em briefing claro e cria a ficha do cliente (marca, cores, tom, restrições) que o Claude consulta em todos os vídeos seguintes. Use quando chegar um job novo, um cliente novo, um pedido confuso ou quando o usuário quiser organizar as informações de um cliente.
when_to_use: Pedidos como chegou um cliente novo, organiza esse pedido, o cliente mandou isso, cria a ficha do cliente, monta o briefing.
---

# FREMEX · Briefing e ficha do cliente

O objetivo é que o usuário nunca precise explicar duas vezes como é um cliente.

## Cliente novo · `cliente.md`

1. Peça ao usuário o que ele tiver: site, Instagram, manual de marca, logo, vídeos anteriores e mensagens do cliente.
2. Preencha `${CLAUDE_SKILL_DIR}/templates/cliente.md` e salve como `clientes/<nome>/cliente.md`.
3. Com o material visual em mãos, extraia as cores (hexadecimal), as fontes e o tom de voz. O que não puder ser confirmado fica marcado como **a confirmar com o cliente**.
4. Crie `clientes/<nome>/CLAUDE.md` com uma linha: `Antes de qualquer trabalho para este cliente, leia cliente.md nesta pasta.` Assim o Claude Code carrega a ficha sozinho quando trabalhar nessa pasta.

## Pedido novo · `briefing.md`

1. Cole o pedido do cliente como está.
2. Preencha `${CLAUDE_SKILL_DIR}/templates/briefing.md`: objetivo, público, peças, formato, prazo, restrições e critério de aprovação.
3. Liste as **perguntas para o cliente**: tudo o que está faltando ou ambíguo, no máximo 5, em linguagem simples, prontas para copiar e mandar no WhatsApp.
4. Mostre ao usuário o briefing de uma página e as perguntas.

## Regras

- Não invente informação do cliente. O que faltar vira pergunta.
- Dados pessoais do cliente (telefone, documentos, endereço) não entram na ficha.
- Atualize `cliente.md` sempre que o cliente aprovar ou recusar algo, na seção "Histórico de aprovações". É isso que faz o Claude aprender o gosto do cliente.
