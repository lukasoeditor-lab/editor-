---
name: setup
description: Configura o computador do usuário para edição de vídeo por código no padrão FREMEX. Verifica e instala Node.js, FFmpeg, Git e Python, instala os plugins oficiais do Remotion e do HyperFrames e mostra quais contas o usuário precisa conectar (ElevenLabs, Google Drive). Use quando o usuário pedir para configurar, instalar, preparar o ambiente FREMEX ou começar a editar vídeos com o Claude.
when_to_use: Pedidos como configura o fremex, prepara meu computador para editar vídeo, instala o que precisa, primeira vez usando o fremex.
---

# FREMEX · Setup do ambiente de vídeo

Você é o assistente de configuração da FREMEX. Seu trabalho é deixar o computador do usuário pronto para produzir vídeos por código e mostrar, com clareza, o que só ele pode fazer: criar contas, conectar serviços e pagar planos.

Fale em português do Brasil, de forma simples. O usuário pode nunca ter usado um terminal.

## Regras

- **Antes de instalar qualquer coisa**, mostre a lista do que falta e peça confirmação. O Claude Code também pede aprovação de cada comando: explique isso ao usuário.
- **Nunca peça para o usuário colar senha, token ou chave de API no chat.** Conexões com serviços são feitas por ele, nas configurações (passo 5).
- **Não invente comandos.** Use só os comandos desta skill. Se algo falhar, mostre o erro exato e siga a seção "Se algo falhar".
- **Seja honesto sobre custos:** o Claude Code exige plano pago do Claude; o ElevenLabs gratuito não permite uso comercial; o Remotion exige licença para empresas com 4 pessoas ou mais.
- Ao final, sempre gere o arquivo `FREMEX-STATUS.md` (passo 6).

## Passo 1 · Apresentar

Explique em 3 linhas o que vai acontecer: diagnóstico, instalação do que faltar (com aprovação), plugins de vídeo e checklist de contas. Pergunte se pode começar.

## Passo 2 · Diagnóstico

Descubra o sistema operacional e rode as verificações abaixo. Não pare se uma falhar: anote e siga.

| Item | Comando | Mínimo |
|---|---|---|
| Node.js | `node --version` | 22 ou mais novo (exigido pelo HyperFrames) |
| npm | `npm --version` | qualquer |
| FFmpeg | `ffmpeg -version` | qualquer (renderização de vídeo) |
| Git | `git --version` | qualquer |
| Python | `python3 --version` (Windows: `python --version`) | 3.10+ (legendas, cortes, Watch) |
| yt-dlp | `yt-dlp --version` | qualquer (assistir vídeos de links, skill Watch) |

Mostre uma tabela com ✅ / ❌ para cada item.

## Passo 3 · Instalar o que falta (com aprovação)

Mostre os comandos do sistema do usuário e peça confirmação antes de rodar.

**Windows (PowerShell):**
```powershell
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install Git.Git
winget install Python.Python.3.12
winget install yt-dlp.yt-dlp
```
Depois de instalar no Windows, peça para o usuário **fechar e abrir o terminal** (ou o Claude Code) para os comandos serem reconhecidos, e rode o diagnóstico de novo.

**macOS (Homebrew):** se `brew --version` falhar, explique que o Homebrew é instalado pelo site oficial brew.sh e peça para o usuário instalar antes.
```bash
brew install node ffmpeg git python yt-dlp
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install -y ffmpeg git python3 python3-pip pipx
pipx install yt-dlp
```
Para Node.js 22+ no Linux, oriente o usuário a usar o instalador oficial em nodejs.org, porque a versão do apt costuma ser antiga.

Confira de novo com o diagnóstico do passo 2.

## Passo 4 · Plugins oficiais de vídeo

Estes são os plugins oficiais publicados pelos próprios fabricantes:

**HyperFrames (HeyGen) — vídeo a partir de HTML:**
```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

**Remotion — vídeo com React:**
```bash
claude plugin marketplace add remotion-dev/claude-code-plugin
claude plugin install remotion@remotion
```

Depois:
- Rode `npx hyperframes doctor` para conferir o ambiente do HyperFrames.
- Avise que os plugins só aparecem numa **nova sessão** do Claude Code (ou depois de `/reload-plugins`).

**Ferramentas do estúdio FREMEX** (legendas, cortes, capas e reels):
```bash
pip install faster-whisper numpy
```
Explique que, no primeiro uso, o faster-whisper baixa um modelo de transcrição da internet (algumas centenas de MB). No Windows, use `python -m pip install faster-whisper numpy` se `pip` não for reconhecido.

Para capas e reels, que renderizam páginas HTML, o Playwright é instalado **na pasta de cada projeto**, quando a skill precisar:
```bash
npm install playwright
npx playwright install chromium
```

**VoiceStudio · voz local e gratuita (opcional, recomendado):** aplicativo de código aberto que gera narração, cria e clona vozes, dubla e transcreve **no próprio computador**, sem custo por uso. Pergunte se o usuário quer instalar e explique antes:
- precisa de cerca de **10 GB livres** em disco; placa de vídeo NVIDIA acelera, mas não é obrigatória;
- o modelo padrão (OmniVoice, cerca de 2,3 GB) tem pesos com licença **CC-BY-NC, que não permite uso comercial**. Para trabalho de cliente, escolha no aplicativo (Model Manager) um mecanismo cuja licença permita uso comercial, ou use o ElevenLabs com plano pago.

Confira memória, disco e placa de vídeo. Depois instale com o instalador oficial:

Windows (PowerShell):
```powershell
irm https://voicestudio.sh/install.ps1 | iex
```
macOS e Linux:
```bash
curl -fsSL https://voicestudio.sh/install | sh
```
Abra o aplicativo, deixe o próprio app baixar o que precisa e **deixe a pergunta de estatísticas de uso para o usuário responder**. Confira se está no ar:
```bash
curl http://localhost:3900/health
```
Conecte ao Claude Code (servidor MCP do próprio VoiceStudio):
```bash
claude mcp add --transport http --scope user voicestudio http://localhost:3900/mcp/
```
O VoiceStudio precisa estar aberto para o Claude usar a voz. Antes de baixar qualquer modelo, informe o tamanho e a licença e peça autorização.

**Watch (assistir vídeos):** rode a configuração da própria skill e siga as perguntas dela:
```bash
python3 "${CLAUDE_SKILL_DIR}/../watch/scripts/setup.py" --json
```
Recomende o motor **local** para material de clientes, porque o vídeo não sai do computador. O motor Gemini envia o vídeo ao Google: explique isso antes, se o usuário quiser usá-lo.

## Passo 5 · Contas e conexões (o usuário faz)

Explique que estas etapas exigem login e, às vezes, pagamento, então quem faz é o usuário:

| Serviço | Para quê | Como conectar | Custo |
|---|---|---|---|
| **Claude** (plano Pro ou superior) | Usar o Claude Code | Já está em uso, se o Claude Code abriu | Pago |
| **VoiceStudio** | Narração local e gratuita (instalado acima) | Aplicativo aberto + `/mcp` mostra `voicestudio` | Gratuito; atenção à licença do modelo |
| **ElevenLabs** | Narração na nuvem, vozes profissionais | claude.ai → Configurações → Conectores → ElevenLabs. Depois, no Claude Code, `/mcp` mostra se está ativo | Gratuito sem uso comercial; pago para clientes |
| **Google Drive** | Organizar e entregar arquivos | claude.ai → Configurações → Conectores → Google Drive | Gratuito com espaço limitado |

Peça para o usuário avisar quando terminar e confira o que estiver disponível com `/mcp`.

## Passo 6 · Relatório

Crie `FREMEX-STATUS.md` na pasta atual com:
- data e sistema operacional;
- tabela do diagnóstico final (✅ / ❌);
- plugins instalados;
- conexões confirmadas e pendentes;
- próximos passos: "Abra uma nova sessão, coloque um vídeo na pasta e peça: `/fremex:editar transforma esse vídeo em reels com legenda`".

Termine com uma mensagem curta: o que ficou pronto, o que falta e o primeiro comando para testar.

## Se algo falhar

1. Mostre o erro exatamente como apareceu.
2. Erros comuns:
   - **"não é reconhecido como comando" / "command not found"** depois de instalar: feche e abra o terminal.
   - **winget não existe**: o Windows está desatualizado; oriente a atualizar pelo Windows Update ou instalar o "App Installer" pela Microsoft Store.
   - **`claude plugin` falhou**: confira a internet e a versão com `claude --version`; atualize com `claude update`.
3. Se não resolver, registre no `FREMEX-STATUS.md` como pendente e siga para os próximos passos.
