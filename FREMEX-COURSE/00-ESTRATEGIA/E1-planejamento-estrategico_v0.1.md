# Etapa 1 — Planejamento estratégico do primeiro curso FREMEX

**Versão:** 0.1 · **Data:** 11/11/2026 · **Status:** em avaliação

Este documento analisa a proposta do curso, aponta lacunas e define a estratégia antes de qualquer produção. Nome comercial (Etapa 2) e currículo definitivo (Etapa 3) só começam depois da sua aprovação.

---

## 1. Leitura da proposta

O curso quer ensinar profissionais criativos a usar o Claude em dois modos, **Claude Chat** (pensar, planejar, escrever) e **Claude Code** (construir, automatizar, produzir arquivos), conectando ferramentas como Remotion, HyperFrames, ElevenLabs, Google Drive e Inkscape.

A proposta tem três pontos muito fortes:

- **Um nicho pouco atendido.** Há bastante conteúdo sobre "prompts para criativos". Quase não há conteúdo que leve um videomaker ou social media do chat até um vídeo renderizado por código.
- **Uma metodologia própria.** O C.R.I.A. dá à FREMEX um método com nome, que pode virar marca registrada da escola.
- **Compromisso com honestidade técnica.** Ensinar custos, limites e permissões reais é um diferencial em um mercado cheio de promessas exageradas.

## 2. Lacunas e riscos encontrados

| # | Lacuna ou risco | Por que importa | Como resolver |
|---|---|---|---|
| 1 | **Escopo muito amplo.** Oito módulos, dez ferramentas e dois públicos. | O risco é virar um curso raso em tudo. | Núcleo obrigatório + trilhas. Ferramentas ensinadas dentro de projetos, não em aulas isoladas de "tour". |
| 2 | **Dois públicos com pontos de partida diferentes.** | O iniciante trava na instalação. O profissional se entedia no básico. | Duas trilhas (Essencial e Completa) e selos de nível em cada aula. |
| 3 | **Custo para acompanhar o curso.** | O Claude Code não está no plano gratuito do Claude. O plano gratuito do ElevenLabs não permite uso comercial. O Remotion exige licença paga para empresas a partir de 4 pessoas. | Tabela de "custo mínimo para acompanhar" na página de vendas e na aula 0. Mostrar alternativas gratuitas sempre que existirem. |
| 4 | **Ferramentas mudam rápido.** | O Claude Code recebe atualizações quase toda semana. Telas, menus e nomes de recursos mudam. | Separar conceitos duradouros de passos de tela. Cada aula técnica leva a data de verificação. Módulo de atualizações e revisão trimestral. |
| 5 | **Windows é a realidade da maioria dos alunos.** | Instalação, terminal, Node.js e FFmpeg são mais difíceis no Windows. | Gravar as demonstrações principais em Windows, com notas para macOS. Kit de instalação com solução de problemas. Mostrar o app Desktop como alternativa ao terminal. |
| 6 | **Projetos concentrados no fim (módulo 7).** | O briefing pede que todo módulo tenha aplicação prática. | Cada módulo termina com uma entrega. Um cliente fictício atravessa o curso inteiro. |
| 7 | **Marca e vínculo com terceiros.** | "Claude" é marca da Anthropic. Remotion, HyperFrames e ElevenLabs também têm marcas e termos próprios. | O nome do curso deve ser da FREMEX. "Claude" aparece só de forma descritiva. Aviso de independência em todos os materiais. Conferir as diretrizes de marca da Anthropic antes do lançamento. |
| 8 | **Uso de dados de clientes reais.** | Alunos vão subir briefings e arquivos de clientes em ferramentas de IA. | Aula e checklist sobre dados sensíveis, contratos e chaves de API. Projetos do curso usam só material fictício ou próprio. |
| 9 | **Verificação técnica incompleta nesta etapa.** | Nesta sessão, o acesso a remotion.dev e hyperframes.heygen.com foi bloqueado pela rede. | Fontes secundárias usadas só para planejar. Verificação na fonte oficial obrigatória antes dos roteiros (Etapa 4). |
| 10 | **Expectativa de resultado.** | Alunos podem esperar que a IA "faça tudo". | Promessa educacional realista. O curso ensina um processo, não garante resultado. |

## 3. O que a pesquisa inicial confirmou

Consulta feita em 11/11/2026. Detalhes, links e status de cada fonte estão em `11-DOCUMENTACAO/fontes-e-verificacoes_v0.1.md`.

**Claude Code** (documentação oficial):

- Precisa de conta Pro, Max, Ultra, Team, Enterprise ou Console. O plano gratuito não inclui Claude Code.
- Roda em macOS 13+, Windows 10 1809+, Ubuntu 20.04+, Debian 10+ e Alpine 3.19+, com 4 GB de RAM ou mais e internet.
- Instalação nativa por um comando no terminal. Há também Homebrew, WinGet e npm.
- Existe um app Desktop para usar o Claude Code sem terminal. Isso é decisivo para iniciantes.
- No Windows, o Git for Windows é opcional e recomendado.

**MCP no Claude Code** (documentação oficial):

- Servidores são adicionados com `claude mcp add`, em três escopos: local, projeto e usuário.
- A documentação alerta para confiar em cada servidor antes de conectar e para o risco de injeção de prompt.
- Esse alerta vira conteúdo obrigatório da aula de segurança.

**Planos do Claude** (página oficial de preços):

- Pro custa US$ 20/mês e inclui Claude Code e Projects.
- Os planos e os limites de uso mudam com frequência. O curso deve apontar para a página oficial, não fixar valores no vídeo.

**Google Drive** (central de ajuda do Claude):

- O conector do Drive é configurado em Personalizar › Conectores no claude.ai.
- Ações como compartilhar, mover ou excluir pedem aprovação.
- Há divergência entre fontes oficiais sobre quais planos têm acesso. Isso precisa ser verificado na Etapa 4.

**Remotion** (fontes secundárias, pendente de verificação oficial):

- É gratuito para indivíduos e equipes de até 3 pessoas.
- Empresas com 4 pessoas ou mais precisam de licença paga.
- Baseado em React. Exige Node.js.

**HyperFrames** (fontes secundárias, pendente de verificação oficial):

- Framework de código aberto da HeyGen que transforma HTML em vídeo renderizado quadro a quadro.
- Segundo terceiros, exige Node.js 22+ e FFmpeg.
- Tem skills para agentes de programação.
- É mais acessível que o Remotion para quem sabe só HTML e CSS.

**ElevenLabs** (fontes secundárias, pendente de verificação oficial):

- O plano gratuito não dá direito comercial. O plano pago mais barato com uso comercial começa por volta de US$ 6/mês, valor a confirmar.
- A API tem planos e créditos separados.
- Existe servidor MCP oficial, que confirmei por uso direto nesta sessão.

**Inkscape:**

- Gratuito e de código aberto.
- Tem interface de linha de comando para exportar SVG/PNG, que o Claude Code pode acionar. A confirmar na documentação 1.x.
- Não encontrei MCP oficial. Não vamos ensinar um.

## 4. Metodologia: de C.R.I.A. para C.R.I.A.R.

### Avaliação do C.R.I.A.

**O que funciona:**

- Fácil de lembrar.
- Em português, "cria" é verbo e substantivo, o que conversa com o público criativo.
- A ordem segue o fluxo real de um job: entender, planejar, produzir e revisar.

**O que falta:**

- **Não diz qual ferramenta usar em cada momento.** Escolher entre Chat e Code é a decisão mais importante do curso.
- **"Integrar" mistura duas coisas:** construir o projeto e conectar ferramentas.
- **Não há etapa de sistematização.** O módulo 8 (bibliotecas, reaproveitamento, fluxos próprios) fica sem lugar no método. É justamente o que transforma um job bem feito em um processo profissional.
- **O papel humano não aparece.** Não fica claro quem decide e quem executa.

### Proposta: método C.R.I.A.R.

Mantém as quatro letras originais e acrescenta um **R final de Reaproveitar**. A sigla vira **CRIAR**, verbo que resume a promessa da FREMEX.

| Etapa | Pergunta-chave | Entregável | Onde acontece | Ponto de checagem |
|---|---|---|---|---|
| **C — Compreender** | O que precisa ser feito, para quem e por quê? | Briefing decodificado (1 página) | Claude Chat | Objetivo, público, restrições e critério de sucesso estão escritos? |
| **R — Roteirizar** | Como vamos fazer? | Plano de execução: roteiro, storyboard, especificação técnica, lista de arquivos | Claude Chat | Outra pessoa conseguiria executar só com este plano? |
| **I — Integrar** | Com quais ferramentas e em que ordem? | Projeto construído: arquivos, código, áudio, animação | Claude Code + ferramentas | Roda, está organizado, as credenciais estão seguras? |
| **A — Aprimorar** | Está bom o bastante para entregar? | Versão revisada e renderizada | Claude Code + revisão humana | Passou no checklist de entrega? |
| **R — Reaproveitar** | Como o próximo job começa daqui? | Ativos reutilizáveis: prompts, templates, CLAUDE.md, skills | Claude Chat e Code | O próximo projeto parte de um modelo, não do zero? |

**Princípio que atravessa as cinco etapas:** *você dirige, o Claude propõe e executa.* Toda etapa termina com uma decisão humana.

**Uso didático:**

- Cada aula diz em qual etapa do C.R.I.A.R. ela está.
- Cada projeto é documentado nas cinco etapas.
- O manual traz um modelo de "ficha C.R.I.A.R." para preencher em qualquer job.

## 5. Arquitetura do produto

### Duas trilhas

| Trilha | Para quem | Módulos | Exige terminal? |
|---|---|---|---|
| **Essencial** | Social medias, roteiristas e quem quer começar sem código | 0, 1, 2, 6 + projetos 1 e 2 | Não |
| **Completa** | Quem quer produzir com Claude Code, motion e automação | Todos | Sim, ensinado do zero |

Cada aula leva um selo de nível: **Base**, **Prático** ou **Avançado**.

### Grade proposta (versão de trabalho, a definir na Etapa 3)

| Módulo | Tema | Etapa do método | Entrega do aluno |
|---|---|---|---|
| **00** | Boas-vindas e preparação: custos, contas, como estudar, apresentação do cliente fictício | — | Ambiente pronto, checklist de setup |
| **01** | Fundamentos: IA no mercado criativo, o que é o Claude, Chat × Code × API, o que ele não faz | C | Mapa pessoal de uso de IA |
| **02** | Claude Chat para criativos: prompts, briefings, roteiros, análise de referências, Projects, conectores | C · R | **Projeto 1:** campanha para redes sociais |
| **03** | Claude Code do zero: instalação, app Desktop, terminal básico, pastas e arquivos, CLAUDE.md, permissões, Git básico | I | Primeiro projeto organizado com Claude Code |
| **04** | Integrações: MCP, conectores, Google Drive, ElevenLabs, Inkscape por linha de comando, APIs, chaves e custos | I | Kit de integração configurado e seguro |
| **05** | Motion por código: HyperFrames (HTML → vídeo) e depois Remotion (React), renderização e revisão | I · A | **Projeto 3:** animação com HyperFrames · **Projeto 4:** vídeo com Remotion e ElevenLabs |
| **06** | Social media e marketing: planejamento, calendário, produção em lote, organização de entregas | R · I | **Projeto 2:** vídeo vertical planejado no Chat |
| **07** | Projeto integrador: fluxo completo para o cliente fictício, do briefing à entrega | C.R.I.A.R. | **Projeto 5:** fluxo de trabalho de ponta a ponta |
| **08** | Sistema profissional: biblioteca de prompts, templates, skills, apresentação de entregas, atualização contínua | R (final) | Biblioteca pessoal pronta |
| **+** | Atualizações: aulas curtas quando ferramentas mudarem | — | — |

**Mudanças em relação à estrutura inicial:**

- Entra o módulo 00, de preparação e custos.
- O HyperFrames vem antes do Remotion, porque HTML é mais acessível que React.
- Os projetos foram distribuídos ao longo do curso.
- O módulo 08 vira o "R" final do método.
- Entra o módulo de atualizações.

### Cliente fictício

Todos os projetos usam a mesma marca fictícia, sempre identificada como fictícia. Exemplo: **"Nova Orla"**, marca de bebidas artesanais.

Isso dá continuidade ao curso. O briefing do projeto 1 alimenta o vídeo do projeto 4, e o aluno termina com um portfólio coerente.

### Dimensão estimada

- 9 a 10 módulos, entre 55 e 65 aulas de 8 a 15 minutos.
- Cerca de 10 a 12 horas de vídeo na trilha completa e 4 a 5 horas na essencial.
- É uma estimativa para planejar produção. O número final sai do currículo aprovado.

## 6. Materiais e formatos

| Material | Formato de produção (editável) | Formato do aluno |
|---|---|---|
| Manual principal | Markdown/HTML com a identidade FREMEX | PDF diagramado |
| Biblioteca de prompts | Markdown organizado por finalidade | PDF + arquivos .md para copiar |
| Arquivos de projeto | Pastas de projeto com código, briefings e assets | ZIP por projeto |
| Checklists | Markdown | PDF de 1 página |
| Guias rápidos | Markdown | PDF + página web |
| Atividades | Markdown com gabarito separado | PDF |
| Glossário | Markdown | PDF + seção do manual |
| Roteiros de gravação | Markdown com marcações de tela e fala | Uso interno |

Tudo é produzido em fontes editáveis neste repositório, versionado (`_v0.1`, `_v1.0`) e exportado para os formatos finais na Etapa 5.

## 7. Padrão de aula

Cada aula segue os nove itens do briefing e mais quatro campos:

- **Etapa do C.R.I.A.R.**
- **Nível** (Base, Prático ou Avançado)
- **Data da última verificação técnica**
- **O que conferir na tela**: os resultados que o aluno precisa ver para saber que deu certo

Os roteiros serão escritos para fala natural, com marcações separadas para tela, corte e demonstração.

## 8. Comercial (diretrizes preliminares)

- **Nome:** o nome principal deve ser da FREMEX. "Claude" entra no subtítulo, de forma descritiva. As três opções saem na Etapa 2.
- **Promessa:** realista. Exemplo de direção: *"aprender um método para planejar, produzir e entregar projetos criativos usando Claude Chat e Claude Code"*. Sem promessa de ganho, viralização ou resultado garantido.
- **Transparência:** custo mínimo para acompanhar, requisitos de computador e aviso de independência visíveis antes da compra.
- **Plataforma:** pacote independente da plataforma (vídeos, PDFs, ZIPs, textos de página). O que muda entre Cakto, Kiwify e Hotmart é tratado na Etapa 7.
- **Provas sociais:** nenhuma inventada. No lançamento, use o que for real: demonstrações, projetos de exemplo e aulas gratuitas.

## 9. Plano de produção e aprovações

| Etapa | Entrega | Aprovação |
|---|---|---|
| 1 · Planejamento | Este documento | **Agora** |
| 2 · Posicionamento | 3 opções de nome, subtítulo e proposta de valor | Antes do currículo |
| 3 · Currículo | Grade definitiva com aulas, objetivos e projetos | Antes dos roteiros |
| 4 · Conteúdo | Roteiros módulo a módulo, com verificação técnica | Por módulo |
| 5 · Materiais | Manual, prompts, checklists, guias, glossário | Por material |
| 6 · Projetos | Arquivos dos 5 projetos testados de ponta a ponta | Por projeto |
| 7 · Comercialização | Página de vendas, descrição, oferta, requisitos de publicação | Final |

## 10. Decisões que preciso de você

1. **Quem apresenta as aulas?** Você na câmera, voz em off com tela ou os dois? Isso muda o estilo dos roteiros.
2. **Sistema operacional das demonstrações:** posso gravar em Windows como padrão, com notas para macOS?
3. **Duas trilhas (Essencial e Completa) ou um curso único?**
4. **Requisito de assinatura:** posso deixar explícito que a trilha completa exige pelo menos o plano Pro do Claude, que é pago?
5. **Tamanho do curso:** completo, com cerca de 10 a 12 horas, ou uma primeira versão menor para lançar antes?
6. **Cliente fictício "Nova Orla":** aprova a ideia, ou prefere outro segmento?
7. **Rede da sessão:** para verificar a documentação oficial na Etapa 4, preciso que os sites remotion.dev, hyperframes.heygen.com, elevenlabs.io, inkscape.org e support.claude.com sejam liberados nas configurações de rede do ambiente.

*Material independente. A FREMEX não tem vínculo oficial com a Anthropic nem com os fabricantes das ferramentas citadas.*
