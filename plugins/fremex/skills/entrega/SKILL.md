---
name: entrega
description: Organiza e entrega o trabalho ao cliente - confere o checklist de qualidade, monta a pasta final com vídeos por plataforma, capa, legendas .srt e texto do post, envia para o Google Drive pelo conector quando disponível e escreve a mensagem de entrega e de pedido de aprovação. Use quando o vídeo estiver pronto e o usuário quiser entregar, enviar para aprovação ou organizar a pasta do cliente.
when_to_use: Pedidos como entrega para o cliente, organiza a pasta final, manda para aprovação, sobe no Drive, escreve a mensagem de entrega.
---

# FREMEX · Entrega

## 1 · Checklist

Percorra `${CLAUDE_SKILL_DIR}/templates/checklist-entrega.md` e marque cada item, mostrando o que falhou. Não entregue com item crítico pendente sem avisar o usuário.

## 2 · Pasta final

```
entregas/<cliente>-<peça>-v<versão>/
  videos/      um arquivo por plataforma (skill exportar)
  capas/       capas (skill capa)
  legendas/    .srt
  post.txt     legenda do post e hashtags (skill roteiro)
  LEIA-ME.txt  o que tem na pasta, versão e data
```

## 3 · Enviar

- **Google Drive:** se o conector estiver ativo, crie a pasta do cliente e envie os arquivos. Confirme com o usuário antes de **compartilhar** qualquer coisa: o Drive também pede aprovação para isso.
- Sem conector, diga ao usuário onde está a pasta para ele enviar.

## 4 · Mensagem

Escreva uma mensagem curta, pronta para o WhatsApp ou e-mail:
- o que foi entregue;
- o link ou o anexo;
- **um** pedido de ação claro ("Aprova até quinta?" ou "Me diz o que ajustar");
- quantas rodadas de ajuste estão incluídas, se o usuário informou.

## 5 · Depois da resposta do cliente

Registre em `cliente.md`, no "Histórico de aprovações", o que foi aprovado ou pedido. Ajustes geram uma nova versão (`v2`): nunca sobrescreva a versão entregue.
