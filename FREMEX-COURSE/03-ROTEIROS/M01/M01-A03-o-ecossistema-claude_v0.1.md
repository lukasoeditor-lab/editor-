# M01-A03 — O ecossistema Claude

| Campo | Valor |
|---|---|
| Módulo | 01 — Fundamentos |
| Trilha | Essencial e Completa |
| Nível | Base |
| Etapa do CRIAR | — |
| Duração estimada | 12 min |
| Formato | Câmera + tela |
| Última verificação técnica | 11/11/2026 · code.claude.com/docs/en/setup · claude.com/pricing |
| Dependências de produção | Diagrama do ecossistema na identidade FREMEX |

## 1. Objetivo de aprendizagem

Diferenciar os modos de usar o Claude (apps de conversa, Claude Code e API) e saber o que cada um exige.

## 2. O que o aluno vai aprender

- O que é o Claude e quem o desenvolve.
- Onde você conversa com ele: web, desktop e celular.
- O que é o Claude Code e em quais lugares ele roda.
- O que é a API e por que este curso quase não a usa diretamente.

## 3. Roteiro de gravação

**[CÂMERA]**

"Claude" é o nome de uma família de modelos de inteligência artificial desenvolvidos pela Anthropic. Só que, no dia a dia, quando alguém diz "usei o Claude", pode estar falando de coisas bem diferentes. Vamos separar.

**[GC]** Modelos · Apps de conversa · Claude Code · API

**[CORTE] [TELA]**

*Diagrama do ecossistema.*

No centro estão os **modelos**. Eles mudam com o tempo: saem versões novas, mais rápidas ou mais capazes. Por isso este curso não depende do nome de um modelo específico. Quando eu precisar falar de modelo, vou mostrar onde você escolhe e como saber qual está usando.

Em volta dos modelos existem formas diferentes de usar o Claude.

**[GC]** 1. Apps de conversa

*Abrir claude.ai no navegador.*

A primeira são os **apps de conversa**: o site claude.ai, o app para computador e o app de celular. É aqui que você conversa, envia arquivos, organiza projetos. No curso, a gente chama isso de **Claude Chat**. Ele tem plano gratuito, com limite de uso.

**[GC]** 2. Claude Code

*Mostrar o Claude Code no terminal e no app Desktop.*

A segunda é o **Claude Code**. Aqui a lógica muda. O Claude Code trabalha dentro de uma pasta no seu computador: lê arquivos, cria arquivos, altera arquivos e roda comandos. Sempre com a sua permissão.

Ele pode ser usado no terminal, no app Desktop (sem precisar do terminal), em extensões de editores de código como o VS Code e na web. ◆ *Confirmar na gravação a lista atual de superfícies.* E tem um ponto importante, que já vimos na aula de custos: o Claude Code **não** está no plano gratuito. Ele exige o plano Pro ou superior, ou uma conta de desenvolvedor.

**[GC]** 3. API

A terceira é a **API**, a porta de entrada para programadores colocarem o Claude dentro dos próprios sistemas. É cobrada por uso, separada da assinatura. Neste curso, a gente não programa direto na API. Ela aparece só quando uma ferramenta pede uma chave, e eu explico isso no módulo 04.

**[CORTE] [CÂMERA]**

Para fixar, pensa assim:

- No **Chat**, você conversa e recebe respostas: texto, ideias, análises, documentos.
- No **Code**, você dá uma tarefa e o Claude trabalha nos seus arquivos.
- A **API** é para quem constrói software.

O mesmo "cérebro" pode estar por trás dos três. O que muda é o que ele consegue tocar. No chat, ele toca a conversa. No Code, ele toca o seu projeto.

Por isso, a pergunta mais importante deste curso não é "qual prompt usar". É: **essa tarefa é de Chat ou de Code?** É exatamente isso que a próxima aula responde.

## 4. Demonstração prática

1. Abrir o claude.ai e mostrar o seletor de modelo.
2. Mostrar o app Desktop do Claude, com a área de Claude Code. ◆
3. Mostrar um terminal com `claude --version`, apenas como prévia do módulo 03.

**O que conferir na tela:** o aluno reconhece onde fica o chat e onde fica o Claude Code. Não há configuração nesta aula.

## 5. Ferramentas necessárias

Navegador com acesso ao claude.ai.

## 6. Exercício ou aplicação

Liste três tarefas da sua rotina e classifique cada uma: Chat, Code ou nenhum dos dois.

## 7. Material complementar

- Diagrama do ecossistema Claude (PDF).
- Página oficial de planos e documentação do Claude Code.

## 8. Resumo final

- "Claude" é uma família de modelos, usada por apps de conversa, pelo Claude Code e pela API.
- O Claude Chat conversa. O Claude Code trabalha nos arquivos do seu computador, com permissão.
- O Claude Code exige plano pago. A API é cobrada por uso e fica fora do foco do curso.

## 9. Notas de produção

- ◆ Confirmar na semana da gravação as superfícies do Claude Code (terminal, Desktop, IDE, web) e o nome atual das áreas no app.
- Não citar nomes de modelos na fala, porque mudam com frequência.
