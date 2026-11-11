---
name: exportar
description: Exporta o vídeo final nas especificações certas de cada plataforma (Reels, TikTok, Shorts, feed, YouTube) com nome padronizado e confere resolução, duração, tamanho e volume. Use quando o vídeo estiver pronto e o usuário pedir para exportar, renderizar a versão final ou gerar versões por rede social.
when_to_use: Pedidos como exporta, gera a versão final, faz uma versão para cada rede, prepara para postar.
---

# FREMEX · Exportar

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/exportar.py" final.mp4 --plataforma reels --nome cliente-campanha-v1 --pasta entregas
```

Plataformas: `reels`, `tiktok`, `shorts` (1080x1920) · `feed` (1080x1350) · `quadrado` (1080x1080) · `youtube` (1920x1080).

O script recusa um vídeo que esteja no formato errado. Nesse caso, use a skill `reenquadrar` antes.

## Nome dos arquivos

`<cliente>-<peça>-v<versão>_<plataforma>_<largura>x<altura>.mp4`, por exemplo `novaorla-lancamento-v2_reels_1080x1920.mp4`. Use letras minúsculas, sem espaços nem acentos.

## Conferência

O script mostra resolução, duração, tamanho e volume. Antes de entregar, confira:

- volume perto de -14 LUFS;
- duração dentro do limite da plataforma, que muda com o tempo; se houver dúvida, confirme nas regras atuais da rede;
- legendas e textos fora das bordas onde ficam os botões da plataforma.
