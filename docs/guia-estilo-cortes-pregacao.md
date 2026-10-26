# Guia de estilo: cortes de pregação dinâmicos

Receita extraída da análise quadro a quadro de um corte de referência
(74 s, 720x1280, 30 fps, pregação sobre o filho pródigo). Serve de base
para editar os cortes deste projeto em Remotion.

## 1. Estrutura e ritmo

| Momento | O que acontece na referência | Regra |
|---|---|---|
| Gancho (0–2 s) | Começa no meio de uma frase forte ("Não precisa colocar nada no lugar"), sem introdução | Abrir na frase mais impactante, nunca em silêncio ou saudação |
| Desenvolvimento | Fala contínua, sem respiros: os silêncios foram cortados | Remover pausas maiores que ~0,25 s (jump cut) |
| Respiro dramático (15,0–16,5 s) | Tela preta de 1,5 s com palavras soltas, a fala continua por baixo | Um "respiro" preto por corte, antes da virada da mensagem |
| Drop (16,5 s) | Corte seco para plano aberto da plateia + impacto grave muito forte | Depois do respiro, voltar com plano aberto e boom |
| Clímax (65–71 s) | Frase final em texto gigante empilhado, revelado palavra a palavra | A frase-chave final sempre vira tipografia gigante |
| Final (72–74 s) | Plano aberto da plateia e tela preta com "DISPONÍVEL NO YOUTUBE" | Encerrar com plano aberto + cartela curta |

- 23 cortes de câmera em 74 s: **um corte a cada ~3 s** em média, mais curtos (0,3–1 s) nos trechos intensos.
- Cada plano tem **movimento contínuo de câmera virtual**: zoom lento para dentro ou para fora (~5–10% ao longo do plano), nunca parado.
- Alterna **close no rosto** (emoção), **plano médio** (gestos) e **plano aberto da plateia** (escala, reação). Os closes caem nas frases mais emocionais.

## 2. Legendas e tipografia

**Legenda padrão** (a maior parte do vídeo)
- 2–3 palavras por vez, minúsculas, sem pontuação.
- Sans-serif geométrica seminegrito (estilo Poppins/Montserrat SemiBold), espaçamento entre letras levemente apertado.
- Branca, centralizada, a ~57% da altura da tela (logo abaixo do peito do pregador).
- Tamanho moderado (~4% da altura): a legenda não compete com o rosto.
- Troca exatamente no tempo das palavras.

**Palavra de emoção** (ex.: "vem *quebrado*")
- A palavra-chave entra em **serifada itálica**, bem maior (~2,5x), logo abaixo da palavra sans pequena.
- Entrada com desfoque → nítido + leve subida (~6 quadros).

**Texto espalhado** (abertura, respiro preto, clímax)
- Cada palavra num ponto diferente da tela, em zigue-zague, entrando uma a uma (~3 quadros de intervalo).
- Entrada com máscara de baixo para cima (a palavra "nasce" de uma linha invisível) ou desfoque → nítido.
- As palavras ficam na tela até o próximo corte.

**Texto atrás do pregador** (efeito de profundidade)
- Algumas palavras ficam atrás da cabeça/corpo do pregador, que passa na frente.
- Exige recorte da pessoa quadro a quadro (segmentação).

**Clímax empilhado** ("Eu / não / desisto / de ser / pai")
- Sans em negrito, gigante (~15% da largura por linha), alinhada à esquerda, uma palavra por linha, entrelinha bem fechada.
- Revelada palavra a palavra no tempo da fala; a última palavra pode surgir letra a letra.

**Acabamento do texto**: leve aberração cromática (franja vermelha/ciano) e leve brilho.

## 3. Cor e textura

- Saturação bem mais alta que o bruto (**~1,8x** a saturação média do seu vídeo original).
- Azul dominante empurrado para o ciano/azul elétrico, pretos esmagados, contraste alto.
- **Vinheta** escura nas bordas.
- **Granulação/meio-tom** fino por cima de tudo (textura de "filme").
- Nitidez reforçada (o material é ampliado de um vídeo horizontal).
- Marca d'água pequena centralizada no topo.

## 4. Som

- A voz é a camada principal e fica sempre clara.
- Há uma **cama sonora estéreo** constante e baixa (~20 dB abaixo da voz): ambiência/música de fundo.
- **Boom grave** (sub < 100 Hz) nos momentos-chave: subida antes do respiro (14,5–15 s), drop enorme no corte para a plateia (16,5 s), e reforços em 23 s, 25 s, 42,8 s, 65,7 s e no final (72 s).
- Efeitos curtos de impacto acompanham cortes e entradas de texto importantes.

## 5. Como aplicar nos cortes deste projeto

1. Transcrever com tempo por palavra (Whisper large-v3) e cortar os silêncios.
2. Marcar na transcrição: gancho, palavras de emoção, ponto do respiro, frase do clímax.
3. Montar os planos com zoom virtual contínuo e punch-ins no rosto nas frases fortes.
4. Legenda padrão em toda a fala; estilos especiais só nos pontos marcados.
5. Aplicar cor, vinheta e granulação no vídeo inteiro.
6. Som: cama baixa + whoosh/impacto nos pontos marcados + boom no drop, com ducking da voz para não distorcer.
