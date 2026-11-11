# Plugin FREMEX para Claude Code

**FREMEX · The Creative Evolution.** Configura o Claude Code para edição de vídeo por código e produz reels no estilo FREMEX.

## Instalar

No terminal:

```bash
claude plugin marketplace add lukasoeditor-lab/editor-
claude plugin install fremex@fremex
```

Abra uma nova sessão do Claude Code e rode:

```
/fremex:setup
```

## Skills

| Comando | O que faz |
|---|---|
| `/fremex:setup` | Diagnostica o computador, instala Node.js, FFmpeg, Git e Python (com sua aprovação), instala os plugins oficiais do Remotion e do HyperFrames e lista as contas para conectar |
| `/fremex:reels` | Produz um reel vertical no estilo FREMEX: roteiro, narração (ElevenLabs), legendas sincronizadas e render em MP4 |

## Requisitos e custos

- Claude Code exige plano pago do Claude (Pro ou superior).
- ElevenLabs: o plano gratuito não permite uso comercial.
- Remotion: gratuito para indivíduos e equipes de até 3 pessoas. Empresas maiores precisam de licença.
- HyperFrames: código aberto. Requer Node.js 22+ e FFmpeg.

*Produto independente. A FREMEX não tem vínculo com a Anthropic, a HeyGen, a Remotion ou a ElevenLabs.*
