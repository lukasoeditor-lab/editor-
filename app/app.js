'use strict';

/* ================= Dados ================= */

const STORE_KEY = 'vsense-data-v1';

const CATEGORIES = {
  in: ['Venda', 'Encomenda', 'Parceria', 'Outros recebimentos'],
  out: ['Compra de produto', 'Embalagem', 'Frete', 'Marketing / anúncios', 'Fornecedor', 'Taxas / maquininha', 'Fixo (aluguel, internet...)', 'Outros gastos'],
};
const METHODS = ['Pix', 'Dinheiro', 'Cartão de crédito', 'Cartão de débito', 'Boleto', 'Transferência'];

let db = load();

function load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return normalize(JSON.parse(raw));
  } catch (e) { /* armazenamento indisponível: começa vazio */ }
  return normalize({});
}

function normalize(d) {
  return { tx: d.tx || [], products: d.products || [], bills: d.bills || [] };
}

function save() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(db)); }
  catch (e) { toast('Não foi possível salvar no aparelho'); }
}

const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const today = () => new Date().toISOString().slice(0, 10);

/* ================= Utilidades ================= */

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const money = (v) => brl.format(v || 0);

function parseMoney(s) {
  if (typeof s === 'number') return s;
  s = String(s || '').trim().replace(/[R$\s]/g, '');
  if (s.includes(',')) s = s.replace(/\./g, '').replace(',', '.');
  const n = parseFloat(s);
  return isNaN(n) ? 0 : Math.round(n * 100) / 100;
}

function fmtDate(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const $ = (sel, el = document) => el.querySelector(sel);

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove('show'), 2200);
}

const productById = (id) => db.products.find((p) => p.id === id);

/* ================= Regras de estoque ================= */

// Venda tira do estoque, compra coloca no estoque
function stockEffect(tx, sign) {
  if (!tx.productId || !tx.qty) return;
  const p = productById(tx.productId);
  if (!p) return;
  const delta = tx.type === 'in' ? -tx.qty : tx.qty;
  p.stock = (p.stock || 0) + delta * sign;
}

// Lucro de uma venda = valor recebido - custo das peças vendidas
function saleProfit(tx) {
  if (tx.type !== 'in' || !tx.productId) return null;
  return tx.amount - (tx.unitCost || 0) * (tx.qty || 0);
}

/* ================= Cálculos ================= */

let month = today().slice(0, 7);

function monthTx() {
  return db.tx.filter((t) => t.date.startsWith(month));
}

function summary() {
  const txs = monthTx();
  const sum = (arr) => arr.reduce((a, t) => a + t.amount, 0);
  const ins = txs.filter((t) => t.type === 'in');
  const outs = txs.filter((t) => t.type === 'out');
  const sales = ins.filter((t) => t.productId);

  const allIn = sum(db.tx.filter((t) => t.type === 'in'));
  const allOut = sum(db.tx.filter((t) => t.type === 'out'));

  const open = db.bills.filter((b) => !b.paid);
  const toPay = open.filter((b) => b.kind === 'pagar');
  const toReceive = open.filter((b) => b.kind === 'receber');
  const late = open.filter((b) => b.due && b.due < today());

  return {
    in: sum(ins),
    out: sum(outs),
    result: sum(ins) - sum(outs),
    balance: allIn - allOut,
    salesCount: sales.reduce((a, t) => a + (t.qty || 0), 0),
    salesProfit: sales.reduce((a, t) => a + saleProfit(t), 0),
    toPay: sum(toPay),
    toPayCount: toPay.length,
    toReceive: sum(toReceive),
    toReceiveCount: toReceive.length,
    lateCount: late.length,
    stockCost: db.products.reduce((a, p) => a + Math.max(0, p.stock || 0) * (p.cost || 0), 0),
    stockValue: db.products.reduce((a, p) => a + Math.max(0, p.stock || 0) * (p.price || 0), 0),
    outByCat: groupBy(outs, 'category'),
  };
}

function groupBy(arr, key) {
  const m = {};
  arr.forEach((t) => { m[t[key] || 'Outros'] = (m[t[key] || 'Outros'] || 0) + t.amount; });
  return Object.entries(m).sort((a, b) => b[1] - a[1]);
}

/* ================= Telas ================= */

let tab = 'inicio';
const ui = { txFilter: 'all', txSearch: '', billFilter: 'pagar', billShowPaid: false };

function render() {
  document.querySelectorAll('.tabbar button').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
  $('#fab').style.display = tab === 'mais' ? 'none' : '';
  const v = $('#view');
  v.innerHTML = { inicio: viewHome, lancamentos: viewTx, produtos: viewProducts, contas: viewBills, mais: viewMore }[tab]();
}

function viewHome() {
  const s = summary();
  const maxCat = s.outByCat[0]?.[1] || 1;
  const recent = [...db.tx].sort(byDateDesc).slice(0, 5);
  const lowStock = db.products.filter((p) => (p.stock || 0) <= (p.minStock ?? 2));

  return `
    <div class="hero">
      <div class="label">Saldo em caixa (tudo que entrou − tudo que saiu)</div>
      <div class="value ${s.balance < 0 ? 'neg' : ''}">${money(s.balance)}</div>
      <div class="row">
        <span>Resultado do mês: <b class="${s.result < 0 ? 'neg' : 'pos'}">${money(s.result)}</b></span>
      </div>
    </div>

    <div class="grid">
      <div class="card"><div class="label">Recebido no mês</div><div class="value pos">${money(s.in)}</div></div>
      <div class="card"><div class="label">Gasto no mês</div><div class="value neg">${money(s.out)}</div></div>
      <div class="card"><div class="label">Lucro nas vendas</div><div class="value accent">${money(s.salesProfit)}</div><div class="hint">${s.salesCount} peça(s) vendida(s)</div></div>
      <div class="card"><div class="label">Estoque (custo)</div><div class="value">${money(s.stockCost)}</div><div class="hint">vale ${money(s.stockValue)} na venda</div></div>
      <div class="card"><div class="label">Estou devendo</div><div class="value neg">${money(s.toPay)}</div><div class="hint">${s.toPayCount} conta(s) a pagar</div></div>
      <div class="card"><div class="label">Me devem</div><div class="value warn">${money(s.toReceive)}</div><div class="hint">${s.toReceiveCount} a receber</div></div>
    </div>

    ${s.lateCount ? `<h3>Atenção</h3><div class="item"><div class="ico out">!</div><div class="main"><div class="title">${s.lateCount} conta(s) vencida(s)</div><div class="sub">Veja na aba Contas</div></div></div>` : ''}
    ${lowStock.length ? `<h3>Estoque baixo</h3><div class="list">${lowStock.map((p) => `
      <div class="item"><div class="ico">▣</div><div class="main"><div class="title">${esc(p.name)}</div><div class="sub">Restam ${p.stock || 0} un.</div></div></div>`).join('')}</div>` : ''}

    <h3>Para onde foi o dinheiro (mês)</h3>
    ${s.outByCat.length ? s.outByCat.map(([cat, v]) => `
      <div class="bar-row">
        <div class="top"><span>${esc(cat)}</span><b>${money(v)}</b></div>
        <div class="bar"><div style="width:${(v / maxCat) * 100}%"></div></div>
      </div>`).join('') : '<div class="empty">Nenhum gasto neste mês.</div>'}

    <h3>Últimos lançamentos</h3>
    ${recent.length ? `<div class="list">${recent.map(txItem).join('')}</div>` : '<div class="empty">Toque no + para registrar sua primeira venda ou gasto.</div>'}
  `;
}

const byDateDesc = (a, b) => (b.date + (b.created || '')).localeCompare(a.date + (a.created || ''));

function txItem(t) {
  const p = t.productId && productById(t.productId);
  const profit = saleProfit(t);
  const sub = [fmtDate(t.date), t.category, t.method, p ? `${t.qty}× ${p.name}` : ''].filter(Boolean).map(esc).join(' · ');
  return `
    <div class="item" data-edit-tx="${t.id}">
      <div class="ico ${t.type}">${t.type === 'in' ? '↓' : '↑'}</div>
      <div class="main">
        <div class="title">${esc(t.desc || t.category)}</div>
        <div class="sub">${sub}</div>
      </div>
      <div class="amount ${t.type === 'in' ? 'pos' : 'neg'}">
        ${t.type === 'in' ? '+' : '−'} ${money(t.amount)}
        ${profit !== null ? `<div class="sub">lucro ${money(profit)}</div>` : ''}
      </div>
    </div>`;
}

function viewTx() {
  const q = ui.txSearch.toLowerCase();
  const list = monthTx()
    .filter((t) => ui.txFilter === 'all' || t.type === ui.txFilter)
    .filter((t) => !q || [t.desc, t.category, t.method, productById(t.productId)?.name].join(' ').toLowerCase().includes(q))
    .sort(byDateDesc);
  const total = list.reduce((a, t) => a + (t.type === 'in' ? t.amount : -t.amount), 0);

  return `
    <h1>Lançamentos</h1>
    <div class="segmented" data-seg="txFilter">
      ${[['all', 'Todos'], ['in', 'Entradas'], ['out', 'Saídas']].map(([k, l]) => `<button data-val="${k}" class="${ui.txFilter === k ? 'active' : ''}">${l}</button>`).join('')}
    </div>
    <input class="search" id="tx-search" placeholder="Buscar..." value="${esc(ui.txSearch)}">
    <div class="sub" style="margin-bottom:10px;color:var(--muted)">${list.length} lançamento(s) · total <b class="${total < 0 ? 'neg' : 'pos'}">${money(total)}</b></div>
    ${list.length ? `<div class="list">${list.map(txItem).join('')}</div>` : '<div class="empty">Nada por aqui neste mês.</div>'}
  `;
}

function viewProducts() {
  const list = [...db.products].sort((a, b) => a.name.localeCompare(b.name));
  return `
    <h1>Produtos</h1>
    ${list.length ? `<div class="list">${list.map((p) => {
      const margin = p.price ? ((p.price - p.cost) / p.price) * 100 : 0;
      const sold = db.tx.filter((t) => t.type === 'in' && t.productId === p.id);
      const soldQty = sold.reduce((a, t) => a + (t.qty || 0), 0);
      const profit = sold.reduce((a, t) => a + saleProfit(t), 0);
      return `
        <div class="item" data-edit-product="${p.id}">
          <div class="ico">▣</div>
          <div class="main">
            <div class="title">${esc(p.name)}</div>
            <div class="sub">Custo ${money(p.cost)} · Venda ${money(p.price)} · Margem <b class="${margin < 0 ? 'neg' : 'accent'}">${margin.toFixed(0)}%</b></div>
            <div class="sub">Estoque <b class="${(p.stock || 0) <= (p.minStock ?? 2) ? 'warn' : ''}">${p.stock || 0}</b> · Vendidos ${soldQty} · Lucro total ${money(profit)}</div>
          </div>
        </div>`;
    }).join('')}</div>` : '<div class="empty">Cadastre seus produtos com custo e preço de venda para o app calcular o lucro automaticamente.</div>'}
  `;
}

function viewBills() {
  const list = db.bills
    .filter((b) => b.kind === ui.billFilter)
    .filter((b) => ui.billShowPaid || !b.paid)
    .sort((a, b) => (a.paid - b.paid) || (a.due || '9').localeCompare(b.due || '9'));
  const total = list.filter((b) => !b.paid).reduce((a, b) => a + b.amount, 0);

  return `
    <h1>Contas</h1>
    <div class="segmented" data-seg="billFilter">
      <button data-val="pagar" class="${ui.billFilter === 'pagar' ? 'active' : ''}">A pagar (devo)</button>
      <button data-val="receber" class="${ui.billFilter === 'receber' ? 'active' : ''}">A receber (me devem)</button>
    </div>
    <label class="sub" style="display:flex;gap:8px;align-items:center;color:var(--muted);margin-bottom:10px">
      <input type="checkbox" id="show-paid" ${ui.billShowPaid ? 'checked' : ''}> Mostrar já quitadas
    </label>
    <div class="card" style="margin-bottom:12px">
      <div class="label">Total em aberto</div>
      <div class="value ${ui.billFilter === 'pagar' ? 'neg' : 'warn'}">${money(total)}</div>
    </div>
    ${list.length ? `<div class="list">${list.map((b) => {
      const late = !b.paid && b.due && b.due < today();
      const badge = b.paid ? '<span class="badge paid">Quitada</span>' : late ? '<span class="badge late">Vencida</span>' : '<span class="badge open">Em aberto</span>';
      return `
        <div class="item">
          <div class="main" data-edit-bill="${b.id}">
            <div class="title">${esc(b.person || 'Sem nome')}${b.desc ? ' — ' + esc(b.desc) : ''}</div>
            <div class="sub">${b.due ? 'Vence ' + fmtDate(b.due) + ' · ' : ''}${badge}</div>
          </div>
          <div class="amount">${money(b.amount)}</div>
          <button class="icon-btn" data-toggle-bill="${b.id}" title="${b.paid ? 'Reabrir' : 'Marcar como pago'}">${b.paid ? '↺' : '✓'}</button>
        </div>`;
    }).join('')}</div>` : '<div class="empty">Nenhuma conta aqui. 🎉</div>'}
  `;
}

function viewMore() {
  return `
    <h1>Mais</h1>
    <h3>Backup</h3>
    <p class="sub" style="color:var(--muted)">Os dados ficam salvos neste aparelho. Faça backup de vez em quando para não perder nada.</p>
    <button class="btn block" id="export-json">⬇ Baixar backup (.json)</button>
    <button class="btn block" id="import-json">⬆ Restaurar backup</button>
    <button class="btn block" id="export-csv">📊 Exportar lançamentos para planilha (.csv)</button>
    <input type="file" id="import-file" accept="application/json,.json" hidden>
    <h3>Zona de perigo</h3>
    <button class="btn block danger" id="reset">Apagar todos os dados</button>
    <p class="sub" style="color:var(--muted);margin-top:24px;text-align:center">Vsense Gestão · v1</p>
  `;
}

/* ================= Formulários ================= */

function openModal(title, bodyHtml, onSave, extra) {
  const dlg = $('#modal');
  $('#modal-title').textContent = title;
  $('#modal-body').innerHTML = bodyHtml;
  const form = $('#modal-form');
  form.onsubmit = (e) => {
    e.preventDefault();
    if (onSave(new FormData(form)) !== false) { dlg.close(); save(); render(); }
  };
  $('#modal-cancel').onclick = () => dlg.close();
  dlg.showModal();
  $('#modal-body').oninput = null;
  if (extra) extra($('#modal-body'));
}

const opt = (list, sel) => list.map((v) => `<option ${v === sel ? 'selected' : ''}>${esc(v)}</option>`).join('');
const productOptions = (sel) => `<option value="">— nenhum —</option>` +
  db.products.map((p) => `<option value="${p.id}" ${p.id === sel ? 'selected' : ''}>${esc(p.name)} (estoque ${p.stock || 0})</option>`).join('');

function txForm(existing, presetType) {
  const t = existing || { type: presetType || 'in', date: today(), qty: 1 };
  const isEdit = !!existing;

  const body = `
    <div class="segmented" id="type-seg">
      <button type="button" data-val="in" class="${t.type === 'in' ? 'active' : ''}">↓ Entrada</button>
      <button type="button" data-val="out" class="${t.type === 'out' ? 'active' : ''}">↑ Saída</button>
    </div>
    <input type="hidden" name="type" value="${t.type}">
    <div class="field"><label>Valor total (R$)</label><input name="amount" inputmode="decimal" required placeholder="0,00" value="${t.amount != null ? String(t.amount).replace('.', ',') : ''}"></div>
    <div class="field"><label>Descrição</label><input name="desc" placeholder="Ex.: Venda para Maria" value="${esc(t.desc)}"></div>
    <div class="two">
      <div class="field"><label>Data</label><input type="date" name="date" required value="${t.date}"></div>
      <div class="field"><label>Pagamento</label><select name="method">${opt(METHODS, t.method)}</select></div>
    </div>
    <div class="field"><label>Categoria</label><select name="category" id="cat-select"></select></div>
    <div class="two">
      <div class="field"><label id="prod-label">Produto vendido</label><select name="productId" id="prod-select">${productOptions(t.productId)}</select></div>
      <div class="field"><label>Quantidade</label><input type="number" name="qty" min="1" step="1" value="${t.qty || 1}"></div>
    </div>
    <div class="calc" id="tx-calc" hidden></div>
    ${isEdit ? '<button type="button" class="btn block danger" id="del-tx">Excluir lançamento</button>' : ''}
  `;

  openModal(isEdit ? 'Editar lançamento' : 'Novo lançamento', body, (fd) => {
    const amount = parseMoney(fd.get('amount'));
    if (amount <= 0) { toast('Informe um valor'); return false; }
    const productId = fd.get('productId') || '';
    const p = productById(productId);
    const next = {
      id: t.id || uid(),
      created: t.created || new Date().toISOString(),
      type: fd.get('type'),
      amount,
      desc: fd.get('desc').trim(),
      date: fd.get('date'),
      method: fd.get('method'),
      category: fd.get('category'),
      productId,
      qty: productId ? Math.max(1, parseInt(fd.get('qty'), 10) || 1) : 0,
      unitCost: p ? (isEdit && t.productId === productId ? t.unitCost : p.cost) : 0,
      billId: t.billId,
    };
    if (isEdit) {
      stockEffect(t, -1);
      db.tx[db.tx.indexOf(t)] = next;
    } else {
      db.tx.push(next);
    }
    stockEffect(next, +1);
    toast(isEdit ? 'Lançamento atualizado' : 'Lançamento salvo');
  }, (root) => {
    const typeInput = root.querySelector('[name=type]');
    const catSel = $('#cat-select', root);
    const prodSel = $('#prod-select', root);
    const calc = $('#tx-calc', root);

    const fillCats = () => {
      const type = typeInput.value;
      catSel.innerHTML = opt(CATEGORIES[type], t.type === type ? t.category : undefined);
      $('#prod-label', root).textContent = type === 'in' ? 'Produto vendido' : 'Produto comprado (repõe estoque)';
    };
    const updateCalc = () => {
      const p = productById(prodSel.value);
      const qty = parseInt(root.querySelector('[name=qty]').value, 10) || 1;
      const amount = parseMoney(root.querySelector('[name=amount]').value);
      if (!p) { calc.hidden = true; return; }
      calc.hidden = false;
      if (typeInput.value === 'in') {
        const cost = p.cost * qty;
        calc.innerHTML = `Custo das peças: <b>${money(cost)}</b> · Lucro desta venda: <b class="${amount - cost < 0 ? 'neg' : 'pos'}">${money(amount - cost)}</b>`;
      } else {
        calc.innerHTML = `Vai adicionar <b>${qty}</b> un. ao estoque de ${esc(p.name)}`;
      }
    };

    $('#type-seg', root).onclick = (e) => {
      const b = e.target.closest('button'); if (!b) return;
      typeInput.value = b.dataset.val;
      root.querySelectorAll('#type-seg button').forEach((x) => x.classList.toggle('active', x === b));
      fillCats(); updateCalc();
    };
    prodSel.onchange = () => {
      const p = productById(prodSel.value);
      const amountEl = root.querySelector('[name=amount]');
      if (p && !amountEl.value) {
        const qty = parseInt(root.querySelector('[name=qty]').value, 10) || 1;
        amountEl.value = String((typeInput.value === 'in' ? p.price : p.cost) * qty).replace('.', ',');
      }
      if (p && !root.querySelector('[name=desc]').value) {
        root.querySelector('[name=desc]').value = (typeInput.value === 'in' ? 'Venda — ' : 'Compra — ') + p.name;
      }
      updateCalc();
    };
    root.oninput = updateCalc;
    fillCats(); updateCalc();

    const del = $('#del-tx', root);
    if (del) del.onclick = () => {
      if (!confirm('Excluir este lançamento?')) return;
      stockEffect(t, -1);
      db.tx = db.tx.filter((x) => x !== t);
      if (t.billId) { const b = db.bills.find((x) => x.id === t.billId); if (b) { b.paid = false; b.txId = null; } }
      save(); $('#modal').close(); render(); toast('Lançamento excluído');
    };
  });
}

function productForm(existing) {
  const p = existing || { stock: 0, minStock: 2 };
  const isEdit = !!existing;
  const num = (v) => (v != null ? String(v).replace('.', ',') : '');
  const body = `
    <div class="field"><label>Nome do produto</label><input name="name" required value="${esc(p.name)}" placeholder="Ex.: Camiseta oversized preta"></div>
    <div class="two">
      <div class="field"><label>Quanto custou (un.)</label><input name="cost" inputmode="decimal" placeholder="0,00" value="${num(p.cost)}"></div>
      <div class="field"><label>Preço de venda</label><input name="price" inputmode="decimal" placeholder="0,00" value="${num(p.price)}"></div>
    </div>
    <div class="two">
      <div class="field"><label>Estoque atual</label><input type="number" name="stock" step="1" value="${p.stock || 0}"></div>
      <div class="field"><label>Avisar quando chegar a</label><input type="number" name="minStock" min="0" step="1" value="${p.minStock ?? 2}"></div>
    </div>
    <div class="calc" id="p-calc"></div>
    ${isEdit ? '<button type="button" class="btn block danger" id="del-p">Excluir produto</button>' : ''}
  `;
  openModal(isEdit ? 'Editar produto' : 'Novo produto', body, (fd) => {
    const next = {
      id: p.id || uid(),
      name: fd.get('name').trim(),
      cost: parseMoney(fd.get('cost')),
      price: parseMoney(fd.get('price')),
      stock: parseInt(fd.get('stock'), 10) || 0,
      minStock: parseInt(fd.get('minStock'), 10) || 0,
    };
    if (isEdit) Object.assign(p, next); else db.products.push(next);
    toast('Produto salvo');
  }, (root) => {
    const calc = $('#p-calc', root);
    const upd = () => {
      const c = parseMoney(root.querySelector('[name=cost]').value);
      const v = parseMoney(root.querySelector('[name=price]').value);
      const s = parseInt(root.querySelector('[name=stock]').value, 10) || 0;
      const m = v ? ((v - c) / v) * 100 : 0;
      calc.innerHTML = `Lucro por peça: <b class="${v - c < 0 ? 'neg' : 'pos'}">${money(v - c)}</b> (${m.toFixed(0)}%) · Investido no estoque: <b>${money(c * s)}</b>`;
    };
    root.oninput = upd; upd();
    const del = $('#del-p', root);
    if (del) del.onclick = () => {
      if (!confirm('Excluir este produto? Os lançamentos continuam salvos.')) return;
      db.products = db.products.filter((x) => x !== p);
      save(); $('#modal').close(); render(); toast('Produto excluído');
    };
  });
}

function billForm(existing) {
  const b = existing || { kind: ui.billFilter, due: today() };
  const isEdit = !!existing;
  const body = `
    <div class="field"><label>Tipo</label>
      <select name="kind">
        <option value="pagar" ${b.kind === 'pagar' ? 'selected' : ''}>A pagar — eu devo</option>
        <option value="receber" ${b.kind === 'receber' ? 'selected' : ''}>A receber — me devem</option>
      </select>
    </div>
    <div class="field"><label>Quem</label><input name="person" required value="${esc(b.person)}" placeholder="Fornecedor, cliente..."></div>
    <div class="field"><label>Referente a</label><input name="desc" value="${esc(b.desc)}" placeholder="Ex.: Lote de 50 camisetas"></div>
    <div class="two">
      <div class="field"><label>Valor (R$)</label><input name="amount" inputmode="decimal" required value="${b.amount != null ? String(b.amount).replace('.', ',') : ''}" placeholder="0,00"></div>
      <div class="field"><label>Vencimento</label><input type="date" name="due" value="${b.due || ''}"></div>
    </div>
    ${isEdit ? '' : `<div class="field"><label>Parcelas (repete todo mês)</label><input type="number" name="parts" min="1" max="48" value="1"></div>`}
    ${isEdit ? '<button type="button" class="btn block danger" id="del-b">Excluir conta</button>' : ''}
  `;
  openModal(isEdit ? 'Editar conta' : 'Nova conta', body, (fd) => {
    const amount = parseMoney(fd.get('amount'));
    if (amount <= 0) { toast('Informe um valor'); return false; }
    const base = { kind: fd.get('kind'), person: fd.get('person').trim(), desc: fd.get('desc').trim(), amount, due: fd.get('due') };
    if (isEdit) { Object.assign(b, base); toast('Conta atualizada'); return; }
    const parts = Math.max(1, parseInt(fd.get('parts'), 10) || 1);
    for (let i = 0; i < parts; i++) {
      db.bills.push({
        ...base,
        id: uid(),
        paid: false,
        due: base.due ? addMonths(base.due, i) : '',
        desc: parts > 1 ? `${base.desc} (${i + 1}/${parts})`.trim() : base.desc,
      });
    }
    ui.billFilter = base.kind;
    toast(parts > 1 ? `${parts} parcelas criadas` : 'Conta salva');
  }, (root) => {
    const del = $('#del-b', root);
    if (del) del.onclick = () => {
      if (!confirm('Excluir esta conta?')) return;
      db.bills = db.bills.filter((x) => x !== b);
      save(); $('#modal').close(); render(); toast('Conta excluída');
    };
  });
}

function addMonths(iso, n) {
  const [y, m, d] = iso.split('-').map(Number);
  const dt = new Date(y, m - 1 + n, 1);
  const last = new Date(dt.getFullYear(), dt.getMonth() + 1, 0).getDate();
  dt.setDate(Math.min(d, last));
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
}

// Quitar uma conta gera o lançamento correspondente no caixa
function toggleBill(id) {
  const b = db.bills.find((x) => x.id === id);
  if (!b) return;
  if (!b.paid) {
    const tx = {
      id: uid(), created: new Date().toISOString(),
      type: b.kind === 'pagar' ? 'out' : 'in',
      amount: b.amount,
      desc: `${b.kind === 'pagar' ? 'Pagamento' : 'Recebimento'} — ${b.person}${b.desc ? ' · ' + b.desc : ''}`,
      date: today(), method: 'Pix',
      category: b.kind === 'pagar' ? 'Fornecedor' : 'Outros recebimentos',
      productId: '', qty: 0, billId: b.id,
    };
    db.tx.push(tx);
    b.paid = true; b.paidDate = today(); b.txId = tx.id;
    toast(b.kind === 'pagar' ? 'Conta paga e lançada como saída' : 'Recebido e lançado como entrada');
  } else {
    db.tx = db.tx.filter((t) => t.id !== b.txId);
    b.paid = false; b.paidDate = null; b.txId = null;
    toast('Conta reaberta');
  }
  save(); render();
}

/* ================= Backup ================= */

function download(name, content, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

function exportCsv() {
  const head = ['Data', 'Tipo', 'Descrição', 'Categoria', 'Pagamento', 'Produto', 'Qtd', 'Valor', 'Lucro'];
  const rows = [...db.tx].sort(byDateDesc).map((t) => [
    fmtDate(t.date), t.type === 'in' ? 'Entrada' : 'Saída', t.desc, t.category, t.method,
    productById(t.productId)?.name || '', t.qty || '',
    t.amount.toFixed(2).replace('.', ','),
    saleProfit(t) !== null ? saleProfit(t).toFixed(2).replace('.', ',') : '',
  ]);
  const csv = [head, ...rows].map((r) => r.map((c) => `"${String(c ?? '').replace(/"/g, '""')}"`).join(';')).join('\n');
  download(`vsense-lancamentos-${today()}.csv`, '﻿' + csv, 'text/csv');
}

/* ================= Eventos ================= */

document.addEventListener('click', (e) => {
  const tabBtn = e.target.closest('.tabbar button');
  if (tabBtn) { tab = tabBtn.dataset.tab; render(); window.scrollTo(0, 0); return; }

  const seg = e.target.closest('[data-seg] button');
  if (seg) { ui[seg.parentElement.dataset.seg] = seg.dataset.val; render(); return; }

  const el = e.target.closest('[data-edit-tx],[data-edit-product],[data-edit-bill],[data-toggle-bill]');
  if (el) {
    if (el.dataset.toggleBill) return toggleBill(el.dataset.toggleBill);
    if (el.dataset.editTx) return txForm(db.tx.find((t) => t.id === el.dataset.editTx));
    if (el.dataset.editProduct) return productForm(productById(el.dataset.editProduct));
    if (el.dataset.editBill) return billForm(db.bills.find((b) => b.id === el.dataset.editBill));
  }

  switch (e.target.id) {
    case 'export-json': download(`vsense-backup-${today()}.json`, JSON.stringify(db, null, 2), 'application/json'); break;
    case 'import-json': $('#import-file').click(); break;
    case 'export-csv': exportCsv(); break;
    case 'reset':
      if (confirm('Apagar TODOS os dados? Faça um backup antes.') && confirm('Tem certeza mesmo?')) {
        db = normalize({}); save(); render(); toast('Dados apagados');
      }
      break;
  }
});

document.addEventListener('input', (e) => {
  if (e.target.id === 'tx-search') {
    ui.txSearch = e.target.value;
    const pos = e.target.selectionStart;
    render();
    const s = $('#tx-search'); s.focus(); s.setSelectionRange(pos, pos);
  }
});

document.addEventListener('change', (e) => {
  if (e.target.id === 'show-paid') { ui.billShowPaid = e.target.checked; render(); }
  if (e.target.id === 'import-file' && e.target.files[0]) {
    const r = new FileReader();
    r.onload = () => {
      try {
        const data = normalize(JSON.parse(r.result));
        if (!confirm(`Restaurar backup com ${data.tx.length} lançamentos, ${data.products.length} produtos e ${data.bills.length} contas? Os dados atuais serão substituídos.`)) return;
        db = data; save(); render(); toast('Backup restaurado');
      } catch { toast('Arquivo inválido'); }
    };
    r.readAsText(e.target.files[0]);
  }
});

$('#fab').onclick = () => {
  if (tab === 'produtos') productForm();
  else if (tab === 'contas') billForm();
  else txForm(null, ui.txFilter === 'out' ? 'out' : 'in');
};

const monthInput = $('#month');
monthInput.value = month;
monthInput.onchange = () => { month = monthInput.value || today().slice(0, 7); render(); };

if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

render();
