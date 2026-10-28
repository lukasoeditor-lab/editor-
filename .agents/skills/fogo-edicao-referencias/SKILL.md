---
name: fogo-edicao-referencias
description: Analisa vídeos de referência e edita uma gravação original com cortes de pausas, legendas e animações coerentes com a fala. Use para modelar a linguagem de edição de Reels.
---

# Edição por referências

Transforme a gravação do usuário em um vídeo vertical editado, usando as referências para entender ritmo, enquadramento e movimento. Não prometa um render que o ambiente não consegue executar.

## 1. Identificar materiais e ferramentas

Leia os vídeos anexados. Se não conseguir assistir a um arquivo ou ouvir seu áudio, informe a limitação e peça um formato acessível; não invente uma análise. Separe referências de gravações a editar. Descubra as ferramentas disponíveis: transcrição, FFmpeg, editor de código, renderizador e acesso a arquivos.

## 2. Extrair a linguagem visual

Use o método de [prompt-01.md](references/prompt-01.md). Registre os primeiros três segundos, cortes, proporções das telas, hierarquia de texto, entradas e saídas de elementos, relação entre fala e imagem e CTA. Extraia decisões de edição, sem reproduzir marcas, depoimentos ou números como se fossem do usuário. Reutilize mídia de terceiros apenas quando o usuário tiver autorização; quando não houver, crie inserções originais.

## 3. Montar a edição

Use [prompt-02.md](references/prompt-02.md) como pedido de execução. Faça uma transcrição com tempos antes de cortar. Remova erros, tentativas abandonadas, repetições e respirações entre frases, preservando sílabas e terminações. Não use apenas um limiar de silêncio: consoantes fracas também parecem silêncio. Mantenha a velocidade pedida pelo usuário; ao acelerar, preserve o tom da voz e acelere a imagem e as legendas na mesma proporção.

Para cada trecho, ligue uma imagem ou animação ao que está sendo dito. Em tela dividida, mantenha texto e demonstração legíveis num celular. Se houver um prompt secreto, mostre um parágrafo longo desfocado e mantenha o conteúdo completo no material didático; não simule resultados ou estatísticas inexistentes.

Em animação por código, use tempo ou quadro determinístico: a mesma posição da timeline deve produzir a mesma imagem. Evite temporizadores de interface, aleatoriedade não fixada e loops de demonstração que reiniciem sem sentido. Use fontes e recursos locais quando possível.

## 4. Entregar e verificar

Se houver renderizador, exporte MP4 H.264, áudio AAC e proporção 9:16, preferencialmente 1080×1920 a 30 fps. Revise áudio e imagem nas emendas, nas entradas de animação e na palavra de CTA. Verifique palavras inteiras, sincronismo, ausência de quadros pretos e texto fora da tela. Entregue arquivo final e código/projeto editável.

Se estiver apenas num chat sem renderizador, entregue roteiro de edição com tempos e os arquivos de código que conseguir gerar. Explique como abrir e exportar no ambiente escolhido. Uma prévia HTML não equivale a um MP4 pronto. Não publique, contrate serviços ou use recursos pagos sem autorização específica do usuário.
