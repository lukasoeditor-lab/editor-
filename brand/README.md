# FREMEX — Marca

Processo em 6 etapas: direção criativa → logotipo → identidade visual → aplicações → website → brand book.
Cada etapa é apresentada para aprovação antes de avançar.

**Etapa atual: 2 — Logotipo** (direção A · Vetor aprovada; aguardando aprovação do logotipo).

- `logos/fremex/` — sistema de 10 versões (gerado por `_build/logo.py`)
- `apresentacao/etapa-2-logotipo.html` — apresentação da Etapa 2 (`python3 brand/_build/presentation2.py`)

## Estrutura

```
brand/
  _build/                 # geradores (Python, sem dependências externas)
    concepts.py           # geometria dos símbolos e letterings em SVG
    presentation.py       # monta a apresentação a partir do template
    etapa-1.template.html
  logos/concepts/         # SVGs conceituais: A-vetor, B-frame, C-iteracao
  apresentacao/           # apresentações de cada etapa
```

Pastas de fontes, ícones, imagens, componentes e o site serão criadas a partir da Etapa 3,
depois que a direção estiver aprovada.

## Regerar

```bash
python3 brand/_build/presentation.py   # também regera os SVGs
```

## Paleta (briefing)

| Cor | HEX | RGB |
|---|---|---|
| Preto profundo | #080A0F | 8 10 15 |
| Azul-marinho | #101D35 | 16 29 53 |
| Azul elétrico | #2459A6 | 36 89 166 |
| Branco gelo | #F3F4F6 | 243 244 246 |
| Azul digital (proposta, não aprovada) | #6A96DE | 106 150 222 |
