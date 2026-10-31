# V'Sensi Gestão

App de controle financeiro da marca **V'Sensi Aromatizantes**: vendas, gastos, produtos, estoque e contas a pagar/receber.

## O que ele faz

- **Início**: saldo em caixa, recebido e gasto no mês, lucro das vendas, valor do estoque, quanto você deve e quanto te devem, gastos por categoria e alertas de estoque baixo e contas vencidas.
- **Lançamentos**: entradas e saídas com categoria, forma de pagamento (Pix, cartão, dinheiro...) e produto vinculado. Uma venda tira as peças do estoque e calcula o lucro; uma compra repõe o estoque.
- **Produtos**: custo, preço de venda, margem, estoque, peças vendidas e lucro total de cada produto.
- **Contas**: o que você deve (a pagar) e o que te devem (a receber), com vencimento e parcelas. Ao marcar como paga, a conta vira um lançamento no caixa.
- **Mais**: backup (.json), restauração e exportação para planilha (.csv).

## Como usar

O app está na pasta `app/`. É só HTML, CSS e JS, sem instalação.

- Para testar no computador: `cd app && python3 -m http.server` e abra `http://localhost:8000`.
- Para usar no celular: publique a pasta `app/` (GitHub Pages, Netlify, Vercel) e, no navegador do celular, use "Adicionar à tela inicial". Ele abre como aplicativo e funciona offline.

Os dados ficam salvos no próprio aparelho. Faça backup pela aba **Mais** de vez em quando.

## Identidade visual

Cores tiradas da logo: verde-oliva `#8B8854` e bege `#E5E1D9`, definidas no início de `app/styles.css`. Títulos em Cormorant Garamond e textos em Jost (Google Fonts). Os ícones (`icon-*.png`, `apple-touch-icon.png`, `symbol.png`) e a `logo.png` foram gerados a partir da logo oficial.

As categorias de gasto já vêm pensadas para aromatizantes: essências, frascos e válvulas, varetas, álcool/base, rótulos, embalagem, frete etc.
