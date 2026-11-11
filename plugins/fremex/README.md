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

## Como usar

Coloque os vídeos numa pasta, abra o Claude Code nela e diga o que quer:

```
/fremex:editar transforma esse vídeo em reels de 30 segundos, corta as pausas e coloca legenda
```

O Claude assiste o material, monta o plano de edição, pede seu ok, executa, revisa e entrega.

## Habilidades (skills)

| Comando | O que faz |
|---|---|
| `/fremex:setup` | Configura o computador: Node.js, FFmpeg, Git, Python, yt-dlp, plugins do Remotion e do HyperFrames, VoiceStudio, Watch e contas |
| `/fremex:editar` | **Ponto de entrada.** Recebe o vídeo e o pedido e coordena todas as outras skills |
| `/fremex:briefing` | Organiza o pedido do cliente e cria a ficha do cliente (marca, cores, tom), lida em todo job |
| `/fremex:roteiro` | Roteiros de reels: ganchos, narração com tempo, cenas e legenda do post |
| `/fremex:analisar-referencia` | Assiste um vídeo de referência e transforma o estilo num guia aplicável |
| `/fremex:watch` | Assiste vídeos (link ou arquivo): quadros e transcrição. Componente de terceiros, licença MIT |
| `/fremex:cortes` | Remove silêncios e pausas, tira erros, seleciona os melhores trechos e monta o gancho |
| `/fremex:reenquadrar` | 16:9 ↔ 9:16 ↔ 4:5 ↔ 1:1, com fundo desfocado, corte ou barras |
| `/fremex:audio` | Limpa a voz, adiciona trilha com ducking e normaliza em -14 LUFS |
| `/fremex:legendas` | Legenda palavra por palavra gravada no vídeo e arquivo .srt (transcrição local) |
| `/fremex:narracao` | Narração com VoiceStudio (local e gratuito) ou ElevenLabs (nuvem) e tempos das palavras para sincronizar |
| `/fremex:motion` | Vinhetas e animações com HyperFrames, Remotion ou o template FREMEX |
| `/fremex:reels` | Reel animado no estilo FREMEX, sem filmagem, com narração e render local |
| `/fremex:capa` | Capa ou thumbnail a partir de um quadro do vídeo |
| `/fremex:exportar` | Versões por plataforma, com nome padronizado e conferência técnica |
| `/fremex:entrega` | Checklist, pasta final, envio ao Drive e mensagem de aprovação para o cliente |

## Requisitos e custos

- Claude Code exige plano pago do Claude (Pro ou superior).
- ElevenLabs: o plano gratuito não permite uso comercial.
- VoiceStudio: aplicativo gratuito (AGPL-3.0). O modelo de voz padrão (OmniVoice) tem pesos CC-BY-NC, sem uso comercial. Para clientes, escolha um modelo com licença comercial.
- Remotion: gratuito para indivíduos e equipes de até 3 pessoas. Empresas maiores precisam de licença.
- HyperFrames: código aberto. Requer Node.js 22+ e FFmpeg.

*Produto independente. A FREMEX não tem vínculo com a Anthropic, a HeyGen, a Remotion ou a ElevenLabs.*
