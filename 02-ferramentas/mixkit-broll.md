# Mixkit (vídeos de apoio / B-roll)

> Data: 2026-11-27 · Tipo: ferramenta · Status: vigente

**Resumo:** banco de vídeos reais e gratuitos, com licença para uso comercial, sem marca d'água, sem conta e sem chave. Serve para os cortes de pregação ganharem imagens de apoio (pessoa chorando, oração, abraço, nascer do sol) por cima da voz do pregador.

- **Como acessar:** a rede do ambiente "Mobile" libera `mixkit.co` (busca) e `assets.mixkit.co` (download) desde 27/11.
- **Buscar:** `curl -s -A "Mozilla/5.0" https://mixkit.co/free-stock-video/<termo-em-ingles>/` e tirar os links `https://assets.mixkit.co/videos/<id>/<id>-360.mp4` do HTML. Termos úteis: sad, crying, lonely, prayer, hope, sunrise, hug, rain, praying, family, worship.
- **Baixar:** troque `-360` por `-1080` (ou `-720`) no link. Nem todo vídeo tem 1080: quando não tem, a resposta é um XML "AccessDenied", e aí vale tentar `-720`.
- **Prévia:** baixe as versões de 360 p e monte um mosaico com ffmpeg (`tile`) para escolher antes de baixar em alta.
- **Uso no estilo 9:** 2 ou 3 cenas de 1,5 a 2 s por corte, na palavra de dor ou de virada, com mergulho suave na entrada e na saída. A voz do pregador continua por baixo.
- **Log:** 27/11, liberado e testado (busca "sad" com 8 vídeos; download de 1080 p, 19 s, 1920×1080). Pexels e Pixabay continuam bloqueados e pedem chave de API.
