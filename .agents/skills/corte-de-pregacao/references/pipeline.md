# Pipeline de um corte de pregação, passo a passo

> Data: 2026-10-27 · Tipo: guia · Status: vigente

**Resumo:** detalhes que a [SKILL.md](../SKILL.md) só aponta: como ter o vídeo, achar os melhores momentos, preparar, renderizar, medir, entregar e escrever a legenda do post. Tudo foi feito e testado em 27/10/2026 (3 cortes da pregação "A Unção de Davi", Lukas / Pregue).

## 1. Ter o vídeo

| Situação | O que fazer |
|---|---|
| Link do YouTube | em nuvem o `yt-dlp` costuma ser bloqueado (proxy 403 e "confirme que você não é um robô"). Peça o arquivo |
| Arquivo no Google Drive | com o link "qualquer pessoa com o link", `curl -L "https://drive.google.com/uc?export=download&id=<ID>"` devolve uma página de aviso para arquivos grandes: leia o formulário (`action`, `confirm`, `uuid`) e baixe de `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t&uuid=<UUID>`. 520 MB baixaram em ~1 min |
| Arquivo pelo anexo do app | o app guarda em `~/.claude/uploads/<sessão>/`; leia de lá |
| Rede | se o Lukas liberar `youtube.com`, `youtu.be`, `googlevideo.com`, `ytimg.com`, o download pode funcionar, mas o YouTube ainda pode pedir cookies (arquivo `cookies.txt` de uma conta secundária, nunca commitado) |

## 2. Achar 3 cortes que viralizam

1. Extraia o áudio (16 kHz mono) e transcreva com o `faster-whisper` modelo `small`, `language="pt"`, `vad_filter=True`. Em CPU, uma pregação de 47 min leva ~20 min. O modelo baixa de `huggingface.co` (`Systran/faster-whisper-small`); `openaipublic.azureedge.net` costuma estar bloqueado.
2. Leia a transcrição inteira. Procure: afirmação forte e curta, contraste ("quem nasce uma vez morre duas…"), pergunta que o público tem, acusação branda ("cara de crente, mas Deus está rejeitando"), promessa, e o **versículo certo no momento certo**.
3. Cada corte tem: gancho nos primeiros 3 s, uma ideia só, 45 a 75 s depois de tirar as pausas, fecho que fecha o raciocínio.
4. Limites reais: ignore leitura longa de texto bíblico (corte do meio), apresentação de livros e avisos, e trechos que critiquem outras religiões (polêmica; avise o Lukas antes de usar).
5. Entregue uma tabela (tempo, título, por que prende) e espere o Lukas escolher a ordem; o fluxo é um por vez.

## 3. Preparar

`preparar_corte.py` aceita vários trechos para "costurar" a ideia (pule leitura longa ou digressão). Escolha o início na primeira palavra e o fim logo depois da última; o script deixa 0,17 s de som em volta de cada pausa cortada (pausas acima de 0,55 s).

- **Recorte 9:16:** segue o centro do pregador; a câmera aberta (1080p) vira 1080×1920 com ~1,8× de ampliação, então evite punch-in acima de 1,3×.
- **Voz isolada:** `--isolar-voz` com o modelo UVR-MDX-NET-Voc_FT.onnx (66 MB, baixa de `github.com/TRvlvr/model_repo/releases`). Nos testes a pregação já estava limpa e o ganho foi pequeno (ruído de fundo −45 dB nos dois), mas a regra do Lukas é isolar a voz.
- **Transcrição com palavras:** `--transcrever` grava `palavras.json` com o tempo de cada palavra; **corrija** os erros (nomes bíblicos, "misericórdia", "cantando") antes de legendar.

## 4. Render

- Prévia sem render: `npx hyperframes snapshot --at t1,t2,...` (a cada efeito).
- Render final: em 4 núcleos, 1080×1920 com grade e motion-blur, ~0,5 s por quadro (corte de 70 s: ~27 min; de 48 s: ~19 min). Rode destacado: `(setsid nohup <hyperframes> render . -o ../render.mp4 -q looks --quiet > render.log 2>&1 < /dev/null &)` e vigie o arquivo.
- Plugin do Claude: o comando é `node <raiz-do-plugin>/skills/hyperframes/scripts/plugin-cli.mjs` (nunca `npx hyperframes@latest` se o plugin estiver instalado).

## 5. Áudio

| Faixa | Nível |
|---|---|
| Voz | −16 LUFS integrado (o gerador/preparo já normaliza) |
| Música | 14 dB abaixo da voz (`abaixo_da_voz_db`), com entrada de 1,2 s e saída de 3,2 s; se a música for curta, ela é repetida com fusão de 2,5 s |
| Efeitos | biblioteca nivelada × fator por categoria; impacto no nível dos picos da fala (≈ −13 a −17 dBFS em janela de 0,3 s) |
| Final | −15 a −16 LUFS, pico real ≤ −3 dBFS depois do limitador de 0,68 |

Música com voz cantada (ex.: "Purifícame") compete com o pregador: use 2 a 3 dB mais baixo que a regra.

## 6. Entrega

1. Copie o final para `outputs/corteN_assunto_vK.mp4` (nova versão = novo arquivo).
2. `SendUserFile` com legenda curta (formato, duração, o que mudou).
3. Resumo em português simples: o que tem, o que foi medido, o que não foi ouvido, o que falta aprovar.
4. Registre na anotação da sessão e, se o estilo mudou, atualize [estilos-pregue](../../../../03-referencias/analises/2026-10-27-estilos-pregue.md).

## 7. Legenda do post (modelo da Pregue)

Estrutura: **gancho** (frase mais forte do corte) → **valor** (1 a 2 linhas com o texto bíblico) → **CTA de venda** (o serviço: cortes, edição, posicionamento de pregadores) → **chamada de interação** → **crédito** → **5 hashtags**.

```
Deus não quer o seu sacrifício. Ele quer a sua obediência. 🔥

"Melhor é obedecer do que sacrificar" (1 Samuel 15:22).
Uma pregação assim pode alcançar milhares, mas só se for cortada, editada e publicada do jeito certo.

✂️ Na Pregue – Além do Púlpito eu transformo a sua pregação em cortes prontos para Reels, Shorts e TikTok:
✅ cortes dos momentos que mais prendem
✅ legenda dinâmica e motion design profissional
✅ trilha, efeitos e a identidade da sua marca

👇 Chame no direct com a palavra PREGUE e peça o seu orçamento.

🎥 Pregação: <nome do pregador>

#Pregue #AlémDoPúlpito #EdiçãoDeCortes #PregaçãoViral #MarketingCristão
```

Preço e prazo só entram se o Lukas informar; use prova social (quantos pregadores atendidos) quando ele tiver.
