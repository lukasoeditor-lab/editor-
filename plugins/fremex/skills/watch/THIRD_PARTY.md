# Watch · componente de terceiros

Esta skill não foi criada pela FREMEX. Ela é redistribuída sem alterações, sob a licença MIT do autor.

- **Projeto original:** https://github.com/bradautomates/claude-video (pasta `skills/watch`, versão 0.3.2)
- **Autor:** Bradley Bonanno
- **Licença:** MIT. O texto completo está em `LICENSE`, nesta pasta.

**Revisão de segurança feita pela FREMEX em 11/11/2026:**
- Os scripts acessam só os serviços que o SKILL.md descreve: Google Gemini, Groq, OpenAI e os instaladores oficiais do uv e do PyTorch.
- As chaves de API são enviadas apenas no cabeçalho da requisição ao serviço correspondente.
- Não foram encontrados `eval`, `exec` nem `shell=True`.
