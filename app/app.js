'use strict';

/* ================= Dados ================= */

const STORE_KEY = 'vsense-data-v1';
const FAIR_EXPENSE = 'Feira (barraca, transporte, alimentação)';

const CATEGORIES = {
  in: ['Venda', 'Encomenda', 'Revenda / atacado', 'Kit presente', 'Outros recebimentos'],
  out: ['Essências', 'Frascos e válvulas', 'Varetas e tampas', 'Álcool / base', 'Rótulos e etiquetas', 'Embalagem', 'Compra de produto pronto', FAIR_EXPENSE, 'Frete', 'Marketing / anúncios', 'Fornecedor', 'Taxas / maquininha', 'Fixo (aluguel, internet...)', 'Outros gastos'],
};
const METHODS = ['Pix', 'Dinheiro', 'Cartão de crédito', 'Cartão de débito', 'Boleto', 'Transferência'];

// Catálogo de fragrâncias da V'Sensi
const DEFAULT_FRAGRANCES = [
  'Cascas e Folhas', 'Styllo', 'Frutas Vermelhas', 'Alecrim e Maracujá', 'Pitanga Negra', 'Cereja e Avelã',
  'Chiclete', 'Marruá', 'Chá Branco', 'Melancia', 'Carro Novo', 'Folha Seca', 'Morango', 'Morango e Champanhe',
  'Any Any', 'Mamãe Baby', 'Cheirinho de Bebê', 'Hugo Boss', 'Dubai', 'Limão Siciliano', 'Lavanda', 'Trousseau',
  'Vanilla/Daslu', 'Vanilla', 'Silver', 'Amora', 'Confort', 'Carmen Steffens', 'Melancia Baby', 'Roupa Nova',
  'Patchouli', 'Duda', 'Pitaya', 'Flor de Algodão', '212 VIP', 'Oportunitty', 'Baby Kids', 'Brisas', 'Talco',
  'Bamboo', 'Canela',
];

// Produtos da V'Sensi com preço de varejo e atacado (custo é preenchido pela dona)
const DEFAULT_PRODUCTS = [
  { name: 'Home Spray', price: 30, wholesale: 20 },
  { name: 'Difusor', price: 35, wholesale: 25 },
  { name: 'Sabonete Líquido', price: 30, wholesale: 22 },
  { name: 'Limpador Perfumado', price: 30, wholesale: 22 },
  { name: 'Eliminex', price: 30, wholesale: 22 },
];

// Feiras fixas da semana: quinta de manhã em Toritama, quinta à tarde e sexta em Santa Cruz
const FAIR_PLACES = ['Toritama', 'Santa Cruz do Capibaribe'];
const FAIR_PERIODS = ['Manhã', 'Tarde', 'Dia todo'];
const FAIR_WEEK = [
  { weekday: 4, place: 'Toritama', period: 'Manhã' },
  { weekday: 4, place: 'Santa Cruz do Capibaribe', period: 'Tarde' },
  { weekday: 5, place: 'Santa Cruz do Capibaribe', period: 'Dia todo' },
];

let db = load();

function load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return normalize(JSON.parse(raw));
  } catch (e) { /* armazenamento indisponível: começa vazio */ }
  return normalize({});
}

function normalize(d) {
  const products = d.products || [];
  if (!d.catalogV1) {
    DEFAULT_PRODUCTS.forEach((dp) => {
      if (!products.some((p) => p.name.toLowerCase() === dp.name.toLowerCase())) {
        products.push({ id: Math.random().toString(36).slice(2, 10), cost: 0, stock: 0, minStock: 0, ...dp });
      }
    });
  }
  return {
    catalogV1: true,
    tx: d.tx || [],
    products,
    bills: d.bills || [],
    fairs: d.fairs || [],
    fragrances: d.fragrances || [...DEFAULT_FRAGRANCES],
  };
}

function save() {
  saveLocal();
  markDirty();
  flush();
}

function saveLocal() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(db)); } catch (e) { /* sem armazenamento local */ }
}

/* ================= Nuvem (db do Artifact) =================
   Cada registro vira um documento: tx/<id>, products/<id>, bills/<id>, fairs/<id>
   e meta/settings guarda o catálogo de fragrâncias. O aparelho guarda uma cópia
   local e a lista do que ainda não subiu, para a venda feita sem internet na
   feira não se perder. */

const COLS = ['tx', 'products', 'bills', 'fairs'];
const DIRTY_KEY = 'vsensi-dirty-v1';
const settingsDoc = () => ({ fragrances: db.fragrances, catalogV1: true });
let cloud = null;
let syncState = 'local';
let known = localMap();
let dirty = new Set(readDirty());
let flushing = false;

function readDirty() {
  try { return JSON.parse(localStorage.getItem(DIRTY_KEY) || '[]'); } catch (e) { return []; }
}
function saveDirty() {
  try { localStorage.setItem(DIRTY_KEY, JSON.stringify([...dirty])); } catch (e) { /* ignora */ }
}

function localMap() {
  const m = {};
  COLS.forEach((c) => db[c].forEach((item) => { m[`${c}/${item.id}`] = JSON.stringify(item); }));
  m['meta/settings'] = JSON.stringify(settingsDoc());
  return m;
}

function localValue(key) {
  if (key === 'meta/settings') return settingsDoc();
  const [c, id] = key.split('/');
  const item = (db[c] || []).find((x) => x.id === id);
  return item ? JSON.parse(JSON.stringify(item)) : null;
}

function markDirty() {
  const now = localMap();
  Object.keys(now).forEach((k) => { if (now[k] !== known[k]) dirty.add(k); });
  Object.keys(known).forEach((k) => { if (!(k in now)) dirty.add(k); });
  known = now;
  saveDirty();
}

async function flush() {
  if (!cloud || flushing || !dirty.size) return;
  flushing = true;
  try {
    for (const key of [...dirty]) {
      const value = localValue(key);
      try {
        if (value) await cloud.doc(key).set(value);
        else await cloud.doc(key).delete();
        dirty.delete(key);
      } catch (e) {
        if (e && e.code === 'invalid_argument') { dirty.delete(key); continue; }
        if (e && e.code === 'quota_exceeded') toast('A nuvem está cheia: faça um backup e apague dados antigos');
        syncState = 'offline';
        break;
      }
    }
  } finally {
    flushing = false;
    saveDirty();
    if (syncState !== 'offline' && !dirty.size) syncState = 'nuvem';
    if (tab === 'mais') render();
  }
}

function applyRemote(col, docs) {
  const remote = docs.map((d) => ({ ...JSON.parse(JSON.stringify(d.data())), id: d.id }));
  const keep = db[col].filter((item) => dirty.has(`${col}/${item.id}`));
  const merged = remote.filter((item) => !dirty.has(`${col}/${item.id}`)).concat(keep);
  db[col] = merged;
  Object.keys(known).forEach((k) => { if (k.startsWith(col + '/')) delete known[k]; });
  merged.forEach((item) => { known[`${col}/${item.id}`] = JSON.stringify(item); });
}

async function connectCloud() {
  if (!window.claude || !window.claude.use) return;
  let ns = null;
  try { ns = await window.claude.use('db'); } catch (e) { ns = null; }
  if (!ns) { if (session.mode === 'loading') { session.mode = 'noid'; render(); } return; }
  cloud = ns;
  syncState = 'conectando';
  try {
    const meta = await cloud.doc('meta/settings').get();
    const remoteProducts = await cloud.collection('products').limit(1).get();
    if (!meta.exists && remoteProducts.empty) {
      // Primeira vez na nuvem: sobe tudo que está neste aparelho
      Object.keys(localMap()).forEach((k) => dirty.add(k));
      saveDirty();
    }
  } catch (e) { syncState = 'offline'; }

  const loadTimer = setTimeout(() => { if (syncState === 'conectando') { syncState = 'offline'; render(); } }, 10000);
  const onData = () => {
    clearTimeout(loadTimer);
    syncState = dirty.size ? 'enviando' : 'nuvem';
    saveLocal();
    render();
    flush();
  };
  COLS.forEach((col) => {
    cloud.collection(col).onSnapshot((snap) => {
      applyRemote(col, snap.docs);
      if (!snap.metadata.fromCache) onData(); else { saveLocal(); render(); }
    }, () => { syncState = 'offline'; render(); });
  });
  cloud.doc('meta/settings').onSnapshot((snap) => {
    if (snap.exists && !dirty.has('meta/settings')) {
      const d = snap.data();
      if (Array.isArray(d.fragrances)) db.fragrances = [...d.fragrances];
      known['meta/settings'] = JSON.stringify(settingsDoc());
      saveLocal(); render();
    }
  }, () => {});
  flush();
  initTeam();
  window.addEventListener('online', flush);
  setInterval(() => { if (dirty.size) flush(); }, 30000);
}

/* ================= Confirmação dentro do app ================= */

function ask(message, okLabel = 'Confirmar') {
  return new Promise((resolve) => {
    const dlg = $('#ask');
    $('#ask-msg').textContent = message;
    $('#ask-ok').textContent = okLabel;
    const done = (v) => { dlg.close(); resolve(v); };
    $('#ask-ok').onclick = () => done(true);
    $('#ask-cancel').onclick = () => done(false);
    dlg.oncancel = (e) => { e.preventDefault(); done(false); };
    dlg.showModal();
  });
}

const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const isoDate = (dt) => `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
const today = () => isoDate(new Date());

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
const priceFor = (p, wholesale) => (wholesale && p.wholesale ? p.wholesale : p.price) || 0;
const lowStock = (p) => (p.minStock ?? 2) > 0 && (p.stock || 0) <= p.minStock;
const fairById = (id) => db.fairs.find((f) => f.id === id);

function parseDate(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

const weekday = (iso) => parseDate(iso).toLocaleDateString('pt-BR', { weekday: 'long' }).replace('-feira', '');

function fairLabel(f, short) {
  if (!f) return '';
  const place = short ? f.place.replace(' do Capibaribe', '') : f.place;
  return `${place} · ${weekday(f.date)} ${fmtDate(f.date).slice(0, 5)} · ${f.period}`;
}

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

const isSale = (t) => t.type === 'in' && (t.productId || t.fragrance);
const pieces = (t) => t.qty || 1;

// Ranking por quantidade vendida: [{ name, qty, total }]
function rank(txs, keyFn) {
  const m = {};
  txs.filter(isSale).forEach((t) => {
    const k = keyFn(t);
    if (!k) return;
    m[k] = m[k] || { name: k, qty: 0, total: 0 };
    m[k].qty += pieces(t);
    m[k].total += t.amount;
  });
  return Object.values(m).sort((a, b) => b.qty - a.qty || b.total - a.total);
}

const rankFragrances = (txs) => rank(txs, (t) => t.fragrance);
const rankProducts = (txs) => rank(txs, (t) => productById(t.productId)?.name);

function fairStats(f) {
  const txs = db.tx.filter((t) => t.fairId === f.id);
  const sales = txs.filter((t) => t.type === 'in');
  const expenses = txs.filter((t) => t.type === 'out');
  const sold = sales.reduce((a, t) => a + t.amount, 0);
  const cost = sales.reduce((a, t) => a + (t.unitCost || 0) * (t.productId ? t.qty || 0 : 0), 0);
  const spent = expenses.reduce((a, t) => a + t.amount, 0);
  return {
    txs, sales, expenses, sold, cost, spent,
    pieces: sales.filter(isSale).reduce((a, t) => a + pieces(t), 0),
    net: sold - cost - spent,
    byMethod: groupBy(sales, 'method'),
    wholesale: sales.filter((t) => t.category === 'Revenda / atacado').reduce((a, t) => a + t.amount, 0),
  };
}


/* ================= Equipe e acesso =================
   O login é a conta do Claude (Google ou e-mail). No primeiro acesso a pessoa
   se cadastra na equipe (members/<id>) e o CEO define a função (roles/<id>).
   O vendedor só vê feiras e produtos, sem custos nem lucro. */

const APP_LINK = 'https://claude.ai/artifact/2EfkaNsFeg2xMRJXZE46re';
const ROLES = {
  ceo: { label: 'CEO / Dono', desc: 'Vê tudo e aprova a equipe' },
  gerente: { label: 'Gerente', desc: 'Vê tudo e aprova funcionários' },
  financeiro: { label: 'Financeiro', desc: 'Caixa, contas e relatórios' },
  vendedor: { label: 'Vendedor(a)', desc: 'Registra vendas nas feiras' },
};
const PERMS = {
  ceo: ['inicio', 'feiras', 'lancamentos', 'produtos', 'contas', 'custos', 'editar', 'equipe', 'equipe-ceo', 'backup'],
  gerente: ['inicio', 'feiras', 'lancamentos', 'produtos', 'contas', 'custos', 'editar', 'equipe', 'backup'],
  financeiro: ['inicio', 'feiras', 'lancamentos', 'produtos', 'contas', 'custos', 'editar', 'backup'],
  vendedor: ['feiras', 'produtos'],
};
const TAB_ORDER = ['inicio', 'feiras', 'lancamentos', 'produtos', 'contas'];

// mode: local (fora do Claude) | loading | noid | register | pending | blocked | team
const session = { mode: 'local', id: null, role: 'ceo', me: null, isOwner: false };
const SESSION_KEY = 'vsensi-session-v1';

// Abre com a última função conhecida, para funcionar na feira mesmo sem sinal
if (window.claude) {
  session.mode = 'loading';
  try {
    const cached = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    if (cached && cached.role) { session.mode = 'team'; session.role = cached.role; session.id = cached.id; }
  } catch (e) { /* sem cache */ }
}
const team = { members: {}, roles: {}, profiles: {}, mine: null, mineLoaded: false, membersSub: false };
let userNs = null;

function can(perm) {
  if (perm === 'mais') return true;
  if (session.mode !== 'team') return true;
  if ((PERMS[session.role] || []).includes(perm)) return true;
  // O dono do link nunca fica trancado fora da gestão da equipe
  return session.isOwner && perm.startsWith('equipe');
}

const firstTab = () => TAB_ORDER.find(can) || 'feiras';
const roleLabel = (r) => (ROLES[r] || {}).label || 'Sem função';
const hasCeo = () => Object.values(team.roles).some((r) => r.active && r.role === 'ceo');

function memberName(id) {
  if (!id) return 'Sem vendedor';
  return team.members[id]?.name || (id === session.id ? team.mine?.name : '') || team.profiles[id]?.name || 'Membro da equipe';
}

function isCpf(v) {
  const d = String(v).replace(/\D/g, '');
  if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
  for (const n of [9, 10]) {
    let sum = 0;
    for (let i = 0; i < n; i++) sum += Number(d[i]) * (n + 1 - i);
    const check = ((sum * 10) % 11) % 10;
    if (check !== Number(d[n])) return false;
  }
  return true;
}

function maskCpf(v) {
  const d = String(v).replace(/\D/g, '').slice(0, 11);
  return d.replace(/^(\d{3})(\d)/, '$1.$2').replace(/^(\d{3}\.\d{3})(\d)/, '$1.$2').replace(/(\.\d{3})(\d{1,2})$/, '$1-$2');
}

function maskPhone(v) {
  const d = String(v).replace(/\D/g, '').slice(0, 11);
  if (d.length <= 2) return d;
  if (d.length <= 7) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, d.length - 4)}-${d.slice(-4)}`;
}

const hiddenCpf = (cpf) => (cpf ? `***.${cpf.slice(4, 7)}.${cpf.slice(8, 11)}-**` : '');

async function initTeam() {
  try { userNs = await window.claude.use('user'); } catch (e) { userNs = null; }
  const id = userNs ? await userNs.id() : null;
  if (!id) { session.mode = 'noid'; render(); return; }
  session.id = id;
  session.me = await userNs.me();
  session.isOwner = session.me.isOwner;
  session.mode = 'loading';
  render();
  cloud.collection('roles').onSnapshot((snap) => {
    team.roles = Object.fromEntries(snap.docs.map((d) => [d.id, { ...d.data() }]));
    updateSession();
  }, () => {});
  cloud.doc('members/' + id).onSnapshot((snap) => {
    team.mine = snap.exists ? { ...snap.data() } : null;
    team.mineLoaded = true;
    updateSession();
  }, () => { team.mineLoaded = true; updateSession(); });
}

function updateSession() {
  const r = team.roles[session.id];
  if (r && r.active) { session.mode = 'team'; session.role = r.role; }
  else if (!team.mineLoaded) session.mode = 'loading';
  else if (!team.mine) session.mode = 'register';
  else session.mode = r && r.active === false ? 'blocked' : 'pending';
  try {
    if (session.mode === 'team') localStorage.setItem(SESSION_KEY, JSON.stringify({ id: session.id, role: session.role }));
    else if (session.mode !== 'loading') localStorage.removeItem(SESSION_KEY);
  } catch (e) { /* ignora */ }
  if (session.mode === 'team') {
    if (!can(tab)) tab = firstTab();
    if (can('equipe') && !team.membersSub) subscribeMembers();
  }
  render();
}

function subscribeMembers() {
  team.membersSub = true;
  cloud.collection('members').onSnapshot(async (snap) => {
    team.members = Object.fromEntries(snap.docs.map((d) => [d.id, { ...d.data() }]));
    if (userNs) {
      try { team.profiles = await userNs.profiles(Object.keys(team.members)); } catch (e) { /* sem fotos */ }
    }
    render();
  }, () => {});
}

async function registerMember(form) {
  const fd = new FormData(form);
  const data = {
    name: String(fd.get('name') || '').trim(),
    cpf: maskCpf(fd.get('cpf')),
    phone: maskPhone(fd.get('phone')),
    email: String(fd.get('email') || '').trim(),
    wantedRole: fd.get('role'),
    createdAt: new Date().toISOString(),
  };
  if (data.name.split(/\s+/).length < 2) return toast('Escreva nome e sobrenome');
  if (!isCpf(data.cpf)) return toast('CPF inválido: confira os números');
  if (!ROLES[data.wantedRole]) return toast('Escolha sua função');
  const btn = form.querySelector('button[type=submit]');
  btn.disabled = true; btn.textContent = 'Enviando…';
  try {
    if (team.mine) await cloud.doc('members/' + session.id).update(data);
    else await cloud.doc('members/' + session.id).set(data);
    // Sem CEO cadastrado ainda: a equipe começa sem precisar de aprovação
    if (!hasCeo() && !team.roles[session.id]) {
      try { await cloud.doc('roles/' + session.id).set({ role: data.wantedRole, active: true, by: session.id, at: new Date().toISOString() }); } catch (e) { /* fica aguardando */ }
    }
    toast('Cadastro enviado ✓');
  } catch (e) {
    toast('Não foi possível salvar. Peça para o CEO te dar acesso de edição no link.');
    btn.disabled = false; btn.textContent = 'Entrar na equipe';
  }
}

async function setRole(uid, role, active = true) {
  if (role === 'ceo' && !can('equipe-ceo')) return toast('Só o CEO pode nomear outro CEO');
  try {
    await cloud.doc('roles/' + uid).set({ role, active, by: session.id, at: new Date().toISOString() });
    toast(active ? `${memberName(uid)} agora é ${roleLabel(role)}` : 'Acesso desativado');
  } catch (e) { toast('Sem permissão para mudar a equipe'); }
}

async function rejectMember(uid) {
  if (!(await ask(`Recusar o cadastro de ${memberName(uid)}?`, 'Recusar'))) return;
  try {
    await cloud.doc('members/' + uid).delete();
    await cloud.doc('roles/' + uid).delete();
    toast('Cadastro recusado');
  } catch (e) { toast('Sem permissão para mudar a equipe'); }
}

function memberForm(uid) {
  const m = team.members[uid] || {};
  const r = team.roles[uid] || {};
  const roles = Object.keys(ROLES).filter((k) => k !== 'ceo' || can('equipe-ceo'));
  const body = `
    <div class="profile-card">
      <img class="avatar-lg" data-avatar="${esc(uid)}" alt="">
      <div class="main">
        <div class="title">${esc(m.name || 'Sem nome')}</div>
        <div class="sub">CPF ${esc(m.cpf || '—')}</div>
        <div class="sub">${esc(m.phone || '')}${m.email ? ' · ' + esc(m.email) : ''}</div>
      </div>
    </div>
    <div class="field"><label>Função</label>
      <div class="role-grid" id="role-pick">${roles.map((k) => `
        <button type="button" class="role-opt ${(r.role || m.wantedRole) === k ? 'active' : ''}" data-val="${k}"><b>${ROLES[k].label}</b><small>${ROLES[k].desc}</small></button>`).join('')}
      </div>
    </div>
    <input type="hidden" name="role" value="${esc(r.role || m.wantedRole || 'vendedor')}">
    ${r.active && uid !== session.id ? '<button type="button" class="btn block danger" id="deactivate">Desativar acesso</button>' : ''}
  `;
  openModal(r.active ? 'Membro da equipe' : 'Aprovar cadastro', body, (fd) => {
    setRole(uid, fd.get('role'), true);
    return true;
  }, (root) => {
    $('#modal-ok').textContent = r.active ? 'Salvar função' : 'Aprovar';
    paintAvatars(root);
    root.onclick = (e) => {
      const b = e.target.closest('.role-opt');
      if (b) {
        root.querySelector('[name=role]').value = b.dataset.val;
        root.querySelectorAll('.role-opt').forEach((x) => x.classList.toggle('active', x === b));
      }
    };
    const off = $('#deactivate', root);
    if (off) off.onclick = async () => {
      if (!(await ask(`Desativar o acesso de ${m.name || 'este membro'}? As vendas dele continuam salvas.`, 'Desativar'))) return;
      $('#modal').close();
      setRole(uid, r.role || 'vendedor', false);
    };
  });
}

function profileForm() {
  const m = team.mine || {};
  const body = `
    <div class="field"><label>Nome completo</label><input name="name" required value="${esc(m.name)}"></div>
    <div class="two">
      <div class="field"><label>CPF</label><input name="cpf" inputmode="numeric" data-mask="cpf" required value="${esc(m.cpf)}"></div>
      <div class="field"><label>WhatsApp</label><input name="phone" inputmode="tel" data-mask="phone" value="${esc(m.phone)}"></div>
    </div>
    <div class="field"><label>E-mail</label><input name="email" type="email" value="${esc(m.email)}"></div>
    <input type="hidden" name="role" value="${esc(m.wantedRole || session.role)}">
  `;
  openModal('Meus dados', body, (fd) => {
    const name = String(fd.get('name')).trim();
    const cpf = maskCpf(fd.get('cpf'));
    if (!isCpf(cpf)) { toast('CPF inválido: confira os números'); return false; }
    cloud.doc('members/' + session.id).update({ name, cpf, phone: maskPhone(fd.get('phone')), email: String(fd.get('email')).trim() })
      .then(() => toast('Dados atualizados ✓'), () => toast('Não foi possível salvar'));
    return true;
  });
}

// Fotos vêm da conta do Claude; a URL é posta como atributo, nunca como HTML
function paintAvatars(root = document) {
  root.querySelectorAll('img[data-avatar]').forEach((img) => {
    const id = img.dataset.avatar;
    const url = id === 'me' || id === session.id ? session.me?.avatarUrl : team.profiles[id]?.avatarUrl;
    if (url) img.src = url; else img.removeAttribute('src');
  });
}

function viewGate() {
  const logo = `<img src="logo.png" alt="V'Sensi Aromatizantes" class="gate-logo">`;
  const who = session.me ? `
    <div class="who">
      <img class="avatar" data-avatar="me" alt="">
      <div><div class="title">${esc(session.me.name || 'Sua conta')}</div><div class="sub">Entrou com sua conta Claude (Google ou e-mail)</div></div>
    </div>` : '';
  if (session.mode === 'loading') return `<div class="gate">${logo}<p class="gate-msg">Carregando…</p></div>`;
  if (session.mode === 'noid') return `<div class="gate">${logo}<div class="gate-card"><h2>Entre na sua conta</h2><p class="gate-msg">Para usar o app da equipe, abra este link logado na sua conta do Claude (com Google ou e-mail) e peça acesso ao CEO.</p></div></div>`;
  if (session.mode === 'pending') return `
    <div class="gate">${logo}
      <div class="gate-card">${who}
        <div class="status-pill">⏳ Aguardando aprovação</div>
        <h2>Cadastro enviado!</h2>
        <p class="gate-msg">Avise o CEO da V'Sensi para aprovar seu acesso. Assim que ele aprovar, o app abre aqui sozinho.</p>
        <div class="kv"><span>Nome</span><b>${esc(team.mine?.name)}</b></div>
        <div class="kv"><span>CPF</span><b>${esc(hiddenCpf(team.mine?.cpf))}</b></div>
        <div class="kv"><span>Função pedida</span><b>${esc(roleLabel(team.mine?.wantedRole))}</b></div>
      </div>
    </div>`;
  if (session.mode === 'blocked') return `<div class="gate">${logo}<div class="gate-card">${who}<h2>Acesso desativado</h2><p class="gate-msg">Seu acesso à gestão da V'Sensi foi desativado. Fale com o CEO se isso for um engano.</p></div></div>`;
  const first = !hasCeo();
  return `
    <div class="gate">${logo}
      <form class="gate-card" id="register-form" novalidate>
        <h2>${first ? 'Bem-vindo à gestão V\'Sensi' : 'Entrar na equipe'}</h2>
        <p class="gate-msg">${first ? 'Primeiro acesso: cadastre-se. O primeiro CEO entra direto, sem aprovação.' : 'Preencha seus dados. O CEO vai aprovar seu acesso.'}</p>
        ${who}
        <div class="field"><label for="reg-name">Nome completo</label><input id="reg-name" name="name" autocomplete="name" required value="${esc(session.me?.name || '')}"></div>
        <div class="two">
          <div class="field"><label for="reg-cpf">CPF</label><input id="reg-cpf" name="cpf" inputmode="numeric" data-mask="cpf" placeholder="000.000.000-00" required></div>
          <div class="field"><label for="reg-phone">WhatsApp</label><input id="reg-phone" name="phone" inputmode="tel" data-mask="phone" placeholder="(81) 90000-0000"></div>
        </div>
        <div class="field"><label for="reg-email">E-mail</label><input id="reg-email" name="email" type="email" autocomplete="email" value="${esc(session.me?.email || '')}"></div>
        <div class="field"><label>Sua função</label>
          <div class="role-grid" id="role-pick">${Object.keys(ROLES).map((k) => `
            <button type="button" class="role-opt ${k === (first ? 'ceo' : 'vendedor') ? 'active' : ''}" data-val="${k}"><b>${ROLES[k].label}</b><small>${ROLES[k].desc}</small></button>`).join('')}
          </div>
        </div>
        <input type="hidden" name="role" value="${first ? 'ceo' : 'vendedor'}">
        <button type="submit" class="btn primary block">Entrar na equipe</button>
        <p class="fine">Seu CPF fica visível só para a gestão (CEO e gerentes).</p>
      </form>
    </div>`;
}

function viewTeam() {
  const ids = Object.keys(team.members);
  const pending = ids.filter((id) => !team.roles[id]?.active && team.roles[id]?.active !== false);
  const active = ids.filter((id) => team.roles[id]?.active).sort((a, b) => Object.keys(ROLES).indexOf(team.roles[a].role) - Object.keys(ROLES).indexOf(team.roles[b].role));
  const off = ids.filter((id) => team.roles[id]?.active === false);
  const sales = rank(monthTx(), (t) => t.sellerId || '');
  const soldBy = Object.fromEntries(sales.map((r) => [r.name, r]));
  const card = (id, extra = '') => `
    <div class="item member" data-member="${esc(id)}">
      <img class="avatar" data-avatar="${esc(id)}" alt="">
      <div class="main">
        <div class="title">${esc(team.members[id].name || 'Sem nome')}${id === session.id ? ' <small class="you">você</small>' : ''}</div>
        <div class="sub">${esc(team.members[id].phone || hiddenCpf(team.members[id].cpf))}</div>
      </div>
      ${extra}
    </div>`;
  return `
    <h3>Equipe</h3>
    ${pending.length ? `<div class="list">${pending.map((id) => card(id, `
      <div class="pending-actions">
        <span class="badge open">${esc(roleLabel(team.members[id].wantedRole))}?</span>
        <button class="btn primary sm" data-member="${esc(id)}">Aprovar</button>
        <button class="btn sm" data-reject="${esc(id)}">Recusar</button>
      </div>`)).join('')}</div>` : ''}
    <div class="list" style="margin-top:8px">${active.map((id) => card(id, `
      <div class="amount"><span class="badge role-${esc(team.roles[id].role)}">${esc(roleLabel(team.roles[id].role))}</span>
      <div class="sub">${soldBy[id] ? `${soldBy[id].qty} peças · ${money(soldBy[id].total)}` : 'sem vendas no mês'}</div></div>`)).join('')}</div>
    ${off.length ? `<div class="sub" style="color:var(--muted);margin-top:8px">Desativados: ${off.map((id) => esc(team.members[id].name)).join(', ')}</div>` : ''}
    <div class="invite">
      <div class="title">Convidar alguém</div>
      <ol>
        <li>Toque em <b>Compartilhar</b> no topo desta página do Claude.</li>
        <li>Adicione o e-mail da pessoa com permissão de <b>edição</b>.</li>
        <li>Mande o link. Ela entra com a conta Google ou e-mail e se cadastra.</li>
      </ol>
      <div class="link-row"><code id="app-link">${APP_LINK}</code><button class="btn sm" id="copy-link">Copiar</button></div>
    </div>
  `;
}

/* ================= Telas ================= */

let tab = 'inicio';
const ui = { txFilter: 'all', txSearch: '', billFilter: 'pagar', billShowPaid: false, fairId: null, prodView: 'produtos' };

function render() {
  const gated = session.mode !== 'local' && session.mode !== 'team';
  document.body.classList.toggle('gated', gated);
  renderTopAvatar();
  if (gated) { $('#view').innerHTML = viewGate(); paintAvatars(); return; }
  if (!can(tab)) tab = firstTab();
  document.querySelectorAll('.tabbar button').forEach((b) => {
    b.classList.toggle('active', b.dataset.tab === tab);
    b.hidden = !can(b.dataset.tab);
  });
  $('#fab').hidden = tab === 'mais' || (tab === 'produtos' && !can('editar'));
  $('#fab').textContent = tab === 'feiras' && ui.fairId ? '＄' : '+';
  if (ui.fairId && !fairById(ui.fairId)) ui.fairId = null;
  const v = $('#view');
  v.innerHTML = {
    inicio: viewHome,
    feiras: () => (ui.fairId ? viewFairDetail(fairById(ui.fairId)) : viewFairs()),
    lancamentos: viewTx,
    produtos: () => (ui.prodView === 'fragrancias' ? viewFragrances() : viewProducts()),
    contas: viewBills,
    mais: viewMore,
  }[tab]();
  paintAvatars();
}

function renderTopAvatar() {
  const btn = $('#open-more');
  if (session.me && session.mode === 'team') {
    if (!btn.querySelector('img')) { btn.textContent = ''; const img = document.createElement('img'); img.dataset.avatar = 'me'; img.alt = ''; btn.appendChild(img); }
    btn.classList.add('has-avatar');
  } else if (btn.querySelector('img')) { btn.textContent = '⚙'; btn.classList.remove('has-avatar'); }
}

function rankList(rows, limit) {
  if (!rows.length) return '<div class="empty">Nenhuma venda registrada ainda.</div>';
  const max = rows[0].qty || 1;
  return rows.slice(0, limit || rows.length).map((r, i) => `
    <div class="bar-row">
      <div class="top"><span><b class="rank-n ${i < 3 ? 'top3' : ''}">${i + 1}º</b> ${esc(r.name)}</span><span><b>${r.qty} un</b> · ${money(r.total)}</span></div>
      <div class="bar"><div style="width:${(r.qty / max) * 100}%"></div></div>
    </div>`).join('');
}

function fairsInMonth() {
  return db.fairs.filter((f) => f.date.startsWith(month)).sort((a, b) => b.date.localeCompare(a.date) || b.period.localeCompare(a.period));
}

function fairCard(f) {
  const s = fairStats(f);
  const isToday = f.date === today();
  return `
    <div class="item fair ${isToday ? 'today' : ''}" data-open-fair="${f.id}">
      <div class="ico">${f.place.startsWith('Toritama') ? 'T' : f.place.startsWith('Santa Cruz') ? 'SC' : '◆'}</div>
      <div class="main">
        <div class="title">${esc(f.place)} ${isToday ? '<span class="badge open">Hoje</span>' : ''}</div>
        <div class="sub">${esc(weekday(f.date))}, ${fmtDate(f.date)} · ${esc(f.period)}</div>
        <div class="sub">${s.pieces} peça(s)${can('custos') ? ` · líquido <b class="${s.net < 0 ? 'neg' : 'pos'}">${money(s.net)}</b>` : ''}</div>
      </div>
      <div class="amount">${money(s.sold)}</div>
    </div>`;
}

function viewFairs() {
  const fairs = fairsInMonth();
  const todays = db.fairs.filter((f) => f.date === today());
  const upcoming = db.fairs.filter((f) => f.date > today()).sort((a, b) => a.date.localeCompare(b.date)).slice(0, 3);
  const monthTxs = db.tx.filter((t) => t.fairId && fairs.some((f) => f.id === t.fairId));

  // Comparação entre as cidades
  const byPlace = {};
  fairs.forEach((f) => {
    const s = fairStats(f);
    const p = (byPlace[f.place] = byPlace[f.place] || { place: f.place, count: 0, sold: 0, net: 0, pieces: 0 });
    p.count++; p.sold += s.sold; p.net += s.net; p.pieces += s.pieces;
  });
  const places = Object.values(byPlace).sort((a, b) => b.sold - a.sold);
  const totalSold = places.reduce((a, p) => a + p.sold, 0);
  const totalNet = places.reduce((a, p) => a + p.net, 0);
  const totalPieces = places.reduce((a, p) => a + p.pieces, 0);

  return `
    <h1>Feiras</h1>

    ${todays.length ? `<h3>Hoje</h3><div class="list">${todays.map((f) => `
      <div class="today-card">
        <div><div class="title">${esc(f.place)}</div><div class="sub">${esc(f.period)} · ${fairStats(f).pieces} peça(s) · ${money(fairStats(f).sold)}</div></div>
        <button class="btn primary" data-quick-sale="${f.id}">Vender</button>
        <button class="btn" data-open-fair="${f.id}">Ver</button>
      </div>`).join('')}</div>` : ''}

    <div class="two" style="margin-top:12px">
      <button class="btn block" id="setup-week">📅 Montar semana de feira</button>
      <button class="btn block" id="new-fair">+ Feira avulsa</button>
    </div>

    ${upcoming.length ? `<h3>Próximas</h3><div class="list">${upcoming.map(fairCard).join('')}</div>` : ''}

    <h3>Resumo do mês</h3>
    <div class="grid">
      <div class="card"><div class="label">Vendido nas feiras</div><div class="value pos">${money(totalSold)}</div></div>
      ${can('custos')
        ? `<div class="card"><div class="label">Lucro líquido</div><div class="value accent">${money(totalNet)}</div><div class="hint">já tirando custo e gastos</div></div>`
        : `<div class="card"><div class="label">Minhas vendas</div><div class="value accent">${money(monthTxs.filter((t) => t.type === 'in' && t.sellerId === session.id).reduce((a, t) => a + t.amount, 0))}</div></div>`}
      <div class="card"><div class="label">Peças vendidas</div><div class="value">${totalPieces}</div></div>
      <div class="card"><div class="label">Feiras feitas</div><div class="value">${fairs.filter((f) => f.date <= today()).length}</div></div>
    </div>

    ${places.length ? `<h3>Toritama × Santa Cruz</h3><div class="list">${places.map((p) => `
      <div class="item">
        <div class="main">
          <div class="title">${esc(p.place)}</div>
          <div class="sub">${p.count} feira(s) · ${p.pieces} peças · média ${money(p.count ? p.sold / p.count : 0)} por feira</div>
          <div class="bar" style="margin-top:6px"><div style="width:${totalSold ? (p.sold / totalSold) * 100 : 0}%"></div></div>
        </div>
        <div class="amount">${money(p.sold)}${can('custos') ? `<div class="sub">líquido ${money(p.net)}</div>` : ''}</div>
      </div>`).join('')}</div>` : ''}

    <h3>Fragrâncias mais vendidas nas feiras (mês)</h3>
    ${rankList(rankFragrances(monthTxs), 10)}

    <h3>Produtos mais vendidos nas feiras (mês)</h3>
    ${rankList(rankProducts(monthTxs), 10)}

    ${can('equipe') && session.mode === 'team' ? `<h3>Vendedores do mês</h3>${rankList(rank(monthTxs, (t) => memberName(t.sellerId)), 10)}` : ''}

    <h3>Feiras do mês</h3>
    ${fairs.length ? `<div class="list">${fairs.map(fairCard).join('')}</div>` : '<div class="empty">Nenhuma feira neste mês. Toque em “Montar semana de feira”.</div>'}
  `;
}

function viewFairDetail(f) {
  const s = fairStats(f);
  const sales = [...s.sales].sort(byDateDesc);
  return `
    <button class="back" data-close-fair>‹ Feiras</button>
    <h1>${esc(f.place)}</h1>
    <div class="sub" style="color:var(--muted);margin:-8px 0 14px">${esc(weekday(f.date))}, ${fmtDate(f.date)} · ${esc(f.period)}${f.notes ? ' · ' + esc(f.notes) : ''}</div>

    <div class="hero">
      <div class="label">Vendido nesta feira</div>
      <div class="value">${money(s.sold)}</div>
      <div class="row"><span>${s.pieces} peça(s)</span>${can('custos') ? `<span>Lucro líquido: <b>${money(s.net)}</b></span>` : ''}</div>
    </div>

    ${can('custos') ? `<div class="grid">
      <div class="card"><div class="label">Custo das peças</div><div class="value">${money(s.cost)}</div></div>
      <div class="card"><div class="label">Gastos da feira</div><div class="value neg">${money(s.spent)}</div><div class="hint">barraca, transporte...</div></div>
    </div>` : ''}

    <div class="two" style="margin-top:12px">
      <button class="btn primary block" data-quick-sale="${f.id}">＄ Registrar venda</button>
      ${can('custos') ? `<button class="btn block" data-fair-expense="${f.id}">− Gasto da feira</button>` : ''}
    </div>

    ${s.sold ? `<h3>Varejo × Atacado</h3><div class="chips"><span class="chip static">Varejo <b>${money(s.sold - s.wholesale)}</b></span><span class="chip static">Atacado <b>${money(s.wholesale)}</b></span></div>` : ''}
    ${s.byMethod.length ? `<h3>Como pagaram</h3><div class="chips">${s.byMethod.map(([m, v]) => `<span class="chip static">${esc(m)} <b>${money(v)}</b></span>`).join('')}</div>` : ''}

    <h3>Fragrâncias que mais saíram</h3>
    ${rankList(rankFragrances(s.txs))}

    <h3>Produtos que mais saíram</h3>
    ${rankList(rankProducts(s.txs))}

    ${session.mode === 'team' && can('equipe') ? `<h3>Quem vendeu</h3>${rankList(rank(s.txs, (t) => memberName(t.sellerId)))}` : ''}

    <h3>Vendas (${sales.length})</h3>
    ${sales.length ? `<div class="list">${sales.map(txItem).join('')}</div>` : '<div class="empty">Nenhuma venda ainda. Toque em “Registrar venda”.</div>'}

    ${s.expenses.length && can('custos') ? `<h3>Gastos</h3><div class="list">${s.expenses.map(txItem).join('')}</div>` : ''}

    ${can('editar') ? `<button class="btn block ghost" style="margin-top:20px" data-edit-fair="${f.id}">Editar feira</button>` : ''}
  `;
}

function viewFragrances() {
  const mTx = monthTx();
  const ranked = rankFragrances(mTx);
  const all = rankFragrances(db.tx);
  const soldNames = new Set(ranked.map((r) => r.name));
  const stuck = db.fragrances.filter((f) => !soldNames.has(f));
  const allQty = Object.fromEntries(all.map((r) => [r.name, r.qty]));

  return `
    <h1>Produtos</h1>
    ${prodSeg()}
    <h3>Ranking do mês</h3>
    ${rankList(ranked)}

    ${stuck.length && ranked.length ? `<h3>Não venderam neste mês (${stuck.length})</h3>
      <div class="chips">${stuck.map((f) => `<span class="chip static">${esc(f)}</span>`).join('')}</div>` : ''}

    <h3>Catálogo (${db.fragrances.length})</h3>
    <div class="list">${[...db.fragrances].sort((a, b) => a.localeCompare(b)).map((f) => `
      <div class="item" ${can('editar') ? `data-edit-fragrance="${esc(f)}"` : ''}>
        <div class="ico">❦</div>
        <div class="main"><div class="title">${esc(f)}</div></div>
        <div class="sub">${allQty[f] || 0} vendida(s) no total</div>
      </div>`).join('')}</div>
  `;
}

const prodSeg = () => `
  <div class="segmented" data-seg="prodView">
    <button data-val="produtos" class="${ui.prodView === 'produtos' ? 'active' : ''}">Produtos</button>
    <button data-val="fragrancias" class="${ui.prodView === 'fragrancias' ? 'active' : ''}">Fragrâncias</button>
  </div>`;

function viewHome() {
  const s = summary();
  const maxCat = s.outByCat[0]?.[1] || 1;
  const recent = [...db.tx].sort(byDateDesc).slice(0, 5);
  const lowStockList = db.products.filter(lowStock);
  const noCost = db.products.filter((p) => !p.cost);

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
    ${noCost.length ? `<h3>Falta informar</h3><div class="item" data-goto-products><div class="ico warn">!</div><div class="main"><div class="title">Custo de ${noCost.length} produto(s)</div><div class="sub">Sem o custo, o lucro aparece igual ao valor vendido. Toque para preencher.</div></div></div>` : ''}
    ${lowStockList.length ? `<h3>Estoque baixo</h3><div class="list">${lowStockList.map((p) => `
      <div class="item"><div class="ico">▣</div><div class="main"><div class="title">${esc(p.name)}</div><div class="sub">Restam ${p.stock || 0} un.</div></div></div>`).join('')}</div>` : ''}

    <h3>Fragrâncias mais vendidas (mês)</h3>
    ${rankList(rankFragrances(monthTx()), 5)}

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
  const profit = can('custos') ? saleProfit(t) : null;
  const f = t.fairId && fairById(t.fairId);
  const editable = can('editar') || (t.sellerId && t.sellerId === session.id);
  const seller = session.mode === 'team' && can('equipe') && t.sellerId ? memberName(t.sellerId).split(' ')[0] : '';
  const sub = [fmtDate(t.date), f ? 'Feira ' + f.place.replace(' do Capibaribe', '') : t.category, t.method, p && t.qty > 1 ? `${t.qty} un.` : '', seller].filter(Boolean).map(esc).join(' · ');
  return `
    <div class="item" ${editable ? `data-edit-tx="${t.id}"` : ''}>
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
    .filter((t) => !q || [t.desc, t.category, t.method, t.fragrance, productById(t.productId)?.name, fairById(t.fairId)?.place].join(' ').toLowerCase().includes(q))
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
    ${prodSeg()}
    ${list.length ? `<div class="list">${list.map((p) => {
      const margin = p.price ? ((p.price - p.cost) / p.price) * 100 : 0;
      const marginW = p.wholesale ? ((p.wholesale - p.cost) / p.wholesale) * 100 : 0;
      const sold = db.tx.filter((t) => t.type === 'in' && t.productId === p.id);
      const soldQty = sold.reduce((a, t) => a + (t.qty || 0), 0);
      const profit = sold.reduce((a, t) => a + saleProfit(t), 0);
      return `
        <div class="item" ${can('editar') ? `data-edit-product="${p.id}"` : ''}>
          <div class="ico">▣</div>
          <div class="main">
            <div class="title">${esc(p.name)}</div>
            <div class="sub">Varejo <b>${money(p.price)}</b>${p.wholesale ? ` · Atacado <b>${money(p.wholesale)}</b>` : ''}</div>
            ${can('custos') ? `<div class="sub">${p.cost ? `Custo ${money(p.cost)} · Margem <b class="${margin < 0 ? 'neg' : 'accent'}">${margin.toFixed(0)}%</b>${p.wholesale ? ` / <b class="${marginW < 0 ? 'neg' : 'accent'}">${marginW.toFixed(0)}%</b> atacado` : ''}` : '<b class="warn">Custo não informado</b>'}</div>` : ''}
            <div class="sub">Estoque <b class="${lowStock(p) ? 'warn' : ''}">${p.stock || 0}</b> · Vendidos ${soldQty}${can('custos') ? ` · Lucro total ${money(profit)}` : ''}</div>
          </div>
        </div>`;
    }).join('')}</div>` : '<div class="empty">Cadastre seus produtos (ex.: Home spray 250ml, Difusor 250ml, Água de lençol) com custo e preço de venda. A fragrância você escolhe na hora da venda.</div>'}
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
  const profile = session.mode === 'team' ? `
    <div class="profile-card">
      <img class="avatar-lg" data-avatar="me" alt="">
      <div class="main">
        <div class="title">${esc(team.mine?.name || session.me?.name || 'Você')}</div>
        <span class="badge role-${esc(session.role)}">${esc(roleLabel(session.role))}</span>
        <div class="sub">${esc([hiddenCpf(team.mine?.cpf), team.mine?.phone].filter(Boolean).join(' · '))}</div>
      </div>
      <button class="btn sm" id="edit-profile">Editar</button>
    </div>` : '';
  if (session.mode === 'team' && !can('backup')) {
    return `${profile}<p class="sub" style="color:var(--muted);margin-top:24px;text-align:center">V'Sensi Gestão · v5</p>`;
  }
  return `
    ${profile || `<div style="text-align:center;margin:8px 0 4px"><img src="logo.png" alt="V'Sensi Aromatizantes" style="max-width:260px;width:80%"></div>`}
    ${session.mode === 'team' && can('equipe') ? viewTeam() : ''}
    <h3>Dados na nuvem</h3>
    <div class="item">
      <div class="ico ${syncState === 'nuvem' ? 'in' : syncState === 'offline' ? 'warn' : ''}">${syncState === 'nuvem' ? '✓' : syncState === 'offline' ? '!' : '↻'}</div>
      <div class="main">
        <div class="title">${{ nuvem: 'Salvos na nuvem', conectando: 'Conectando à nuvem…', enviando: 'Enviando para a nuvem…', offline: 'Sem conexão com a nuvem', local: 'Salvos só neste aparelho' }[syncState]}</div>
        <div class="sub">${syncState === 'local' ? 'Abra o app pelo link do Claude para sincronizar entre aparelhos.' : dirty.size ? `${dirty.size} alteração(ões) esperando internet. Nada se perde: o app envia sozinho.` : 'Abra o link em qualquer aparelho e os dados aparecem iguais.'}</div>
      </div>
    </div>
    <h3>Backup</h3>
    <p class="sub" style="color:var(--muted)">Guarde uma cópia de vez em quando, por segurança.</p>
    <button class="btn block" id="export-json">⬇ Baixar backup (.json)</button>
    <button class="btn block" id="import-json">⬆ Restaurar backup</button>
    <button class="btn block" id="export-csv">📊 Exportar lançamentos para planilha (.csv)</button>
    <input type="file" id="import-file" accept="application/json,.json" hidden>
    ${can('equipe-ceo') ? `<h3>Zona de perigo</h3>
    <button class="btn block danger" id="reset">Apagar todos os dados</button>` : ''}
    <p class="sub" style="color:var(--muted);margin-top:24px;text-align:center">V'Sensi Gestão · v5</p>
  `;
}

/* ================= Formulários ================= */

function openModal(title, bodyHtml, onSave, extra) {
  const dlg = $('#modal');
  $('#modal-title').textContent = title;
  $('#modal-body').innerHTML = bodyHtml;
  $('#modal-body').onclick = null;
  $('#modal-ok').textContent = 'Salvar';
  $('#modal-cancel').textContent = 'Cancelar';
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

const fragranceOptions = (sel) => `<option value="">— nenhuma —</option>` +
  [...db.fragrances].sort((a, b) => a.localeCompare(b)).map((f) => `<option ${f === sel ? 'selected' : ''}>${esc(f)}</option>`).join('');
const fairOptions = (sel) => `<option value="">— nenhuma —</option>` +
  [...db.fairs].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 40)
    .map((f) => `<option value="${f.id}" ${f.id === sel ? 'selected' : ''}>${esc(fairLabel(f, true))}</option>`).join('');

function txForm(existing, preset = {}) {
  const t = existing || { type: 'in', date: today(), qty: 1, ...preset };
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
    <div class="two">
      <div class="field"><label>Fragrância</label><select name="fragrance">${fragranceOptions(t.fragrance)}</select></div>
      <div class="field"><label>Feira</label><select name="fairId">${fairOptions(t.fairId)}</select></div>
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
      fragrance: fd.get('fragrance') || '',
      fairId: fd.get('fairId') || '',
      sellerId: t.sellerId || session.id || '',
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
        const wholesale = root.querySelector('[name=category]').value === 'Revenda / atacado';
        amountEl.value = String((typeInput.value === 'in' ? priceFor(p, wholesale) : p.cost) * qty).replace('.', ',');
      }
      if (p && !root.querySelector('[name=desc]').value) {
        root.querySelector('[name=desc]').value = (typeInput.value === 'in' ? 'Venda — ' : 'Compra — ') + p.name;
      }
      updateCalc();
    };
    root.oninput = updateCalc;
    fillCats(); updateCalc();

    const del = $('#del-tx', root);
    if (del) del.onclick = async () => {
      if (!(await ask('Excluir este lançamento?', 'Excluir'))) return;
      stockEffect(t, -1);
      db.tx = db.tx.filter((x) => x !== t);
      if (t.billId) { const b = db.bills.find((x) => x.id === t.billId); if (b) { b.paid = false; b.txId = null; } }
      save(); $('#modal').close(); render(); toast('Lançamento excluído');
    };
  });
}

// Venda rápida na barraca: toca no produto, na fragrância e no pagamento
function quickSaleForm(fair) {
  const counts = Object.fromEntries(rankFragrances(db.tx).map((r) => [r.name, r.qty]));
  const frags = [...db.fragrances].sort((a, b) => (counts[b] || 0) - (counts[a] || 0) || a.localeCompare(b));
  const quickMethods = METHODS.slice(0, 4);
  const sel = { product: db.products.length === 1 ? db.products[0].id : '', fragrance: '', method: 'Pix', qty: 1, manual: false, wholesale: false };
  let refresh = () => {};

  const body = `
    <div class="sub" style="color:var(--muted);margin:-8px 0 12px">${esc(fairLabel(fair))}</div>
    <div class="segmented" id="qs-channel">
      <button type="button" data-val="varejo" class="active">Varejo</button>
      <button type="button" data-val="atacado">Atacado</button>
    </div>
    ${db.products.length ? `
      <div class="field"><label>Produto</label>
        <div class="chips" id="qs-products">${db.products.map((p) => `
          <button type="button" class="chip ${sel.product === p.id ? 'active' : ''}" data-val="${p.id}">${esc(p.name)} <small data-price="${p.id}">${money(p.price)}</small></button>`).join('')}
        </div>
      </div>` : '<div class="calc">Dica: cadastre seus produtos na aba Produtos para o app calcular o lucro de cada venda.</div>'}
    <div class="field"><label>Fragrância</label>
      <input id="qs-search" placeholder="Buscar fragrância..." autocomplete="off">
      <div class="chips scroll" id="qs-frags">${frags.map((f) => `<button type="button" class="chip" data-val="${esc(f)}">${esc(f)}</button>`).join('')}</div>
    </div>
    <div class="two">
      <div class="field"><label>Quantidade</label>
        <div class="stepper"><button type="button" data-step="-1">−</button><span id="qs-qty">1</span><button type="button" data-step="1">+</button></div>
      </div>
      <div class="field"><label>Valor total (R$)</label><input name="amount" id="qs-amount" inputmode="decimal" placeholder="0,00"></div>
    </div>
    <div class="field"><label>Pagamento</label>
      <div class="chips" id="qs-methods">${quickMethods.map((m) => `<button type="button" class="chip ${m === sel.method ? 'active' : ''}" data-val="${m}">${m}</button>`).join('')}</div>
    </div>
    <div class="calc" id="qs-calc"></div>
  `;

  openModal('Nova venda', body, () => {
    const amount = parseMoney($('#qs-amount').value);
    const p = productById(sel.product);
    if (!p && !sel.fragrance) { toast('Escolha o produto ou a fragrância'); return false; }
    if (amount <= 0) { toast('Informe o valor'); return false; }
    const tx = {
      id: uid(), created: new Date().toISOString(),
      type: 'in', amount, date: fair.date, method: sel.method, category: sel.wholesale ? 'Revenda / atacado' : 'Venda',
      desc: [p?.name, sel.fragrance].filter(Boolean).join(' — '),
      productId: sel.product, qty: sel.qty, unitCost: p ? p.cost : 0,
      fragrance: sel.fragrance, fairId: fair.id, sellerId: session.id || '',
    };
    db.tx.push(tx);
    stockEffect(tx, +1);
    save(); render();
    toast(`Venda registrada: ${money(amount)} ✓`);
    // Mantém aberto e limpo para a próxima venda
    sel.fragrance = ''; sel.qty = 1; sel.manual = false;
    $('#qs-search').value = '';
    $('#modal-body').querySelectorAll('#qs-frags .chip').forEach((c) => { c.hidden = false; });
    refresh();
    return false;
  }, (root) => {
    $('#modal-ok').textContent = 'Registrar venda';
    $('#modal-cancel').textContent = 'Fechar';
    root.onclick = (e) => {
      const chip = e.target.closest('.chip[data-val]');
      const step = e.target.closest('[data-step]');
      const channel = e.target.closest('#qs-channel button');
      if (channel) { sel.wholesale = channel.dataset.val === 'atacado'; sel.manual = false; refresh(); return; }
      if (chip) {
        const group = chip.parentElement.id;
        if (group === 'qs-products') { sel.product = chip.dataset.val; sel.manual = false; }
        if (group === 'qs-frags') sel.fragrance = chip.dataset.val;
        if (group === 'qs-methods') sel.method = chip.dataset.val;
        refresh();
      }
      if (step) { sel.qty = Math.max(1, sel.qty + Number(step.dataset.step)); refresh(); }
    };
    root.oninput = (e) => {
      if (e.target.id === 'qs-search') {
        const q = e.target.value.toLowerCase();
        root.querySelectorAll('#qs-frags .chip').forEach((c) => { c.hidden = !c.dataset.val.toLowerCase().includes(q); });
      }
      if (e.target.id === 'qs-amount') { sel.manual = true; refresh(); }
    };
    refresh = () => {
      root.querySelectorAll('#qs-products .chip').forEach((c) => c.classList.toggle('active', c.dataset.val === sel.product));
      root.querySelectorAll('#qs-frags .chip').forEach((c) => c.classList.toggle('active', c.dataset.val === sel.fragrance));
      root.querySelectorAll('#qs-methods .chip').forEach((c) => c.classList.toggle('active', c.dataset.val === sel.method));
      root.querySelectorAll('#qs-channel button').forEach((b) => b.classList.toggle('active', (b.dataset.val === 'atacado') === sel.wholesale));
      root.querySelectorAll('[data-price]').forEach((el) => { el.textContent = money(priceFor(productById(el.dataset.price), sel.wholesale)); });
      $('#qs-qty').textContent = sel.qty;
      const p = productById(sel.product);
      const amountEl = $('#qs-amount');
      if (p && !sel.manual) amountEl.value = String(priceFor(p, sel.wholesale) * sel.qty).replace('.', ',');
      if (!p && !sel.manual) amountEl.value = '';
      const amount = parseMoney(amountEl.value);
      const parts = [sel.qty + '×', p?.name, sel.fragrance, sel.wholesale ? '(atacado)' : ''].filter(Boolean).join(' ');
      $('#qs-calc').innerHTML = `${esc(parts)}${p && p.cost && can('custos') ? ` · lucro <b class="pos">${money(amount - p.cost * sel.qty)}</b>` : ''}`;
    };
    refresh();
  });
}

function fairForm(existing) {
  const f = existing || { date: today(), period: 'Manhã', place: FAIR_PLACES[0] };
  const isEdit = !!existing;
  const places = [...new Set([...FAIR_PLACES, ...db.fairs.map((x) => x.place)])];
  const body = `
    <div class="field"><label>Local</label>
      <input name="place" list="place-list" required value="${esc(f.place)}">
      <datalist id="place-list">${places.map((p) => `<option value="${esc(p)}">`).join('')}</datalist>
    </div>
    <div class="two">
      <div class="field"><label>Data</label><input type="date" name="date" required value="${f.date}"></div>
      <div class="field"><label>Período</label><select name="period">${opt(FAIR_PERIODS, f.period)}</select></div>
    </div>
    <div class="field"><label>Observação</label><input name="notes" value="${esc(f.notes)}" placeholder="Ex.: chuva, movimento fraco..."></div>
    ${isEdit ? '<button type="button" class="btn block danger" id="del-fair">Excluir feira</button>' : ''}
  `;
  openModal(isEdit ? 'Editar feira' : 'Nova feira', body, (fd) => {
    const data = { place: fd.get('place').trim(), date: fd.get('date'), period: fd.get('period'), notes: fd.get('notes').trim() };
    if (isEdit) Object.assign(f, data);
    else { const nf = { id: uid(), ...data }; db.fairs.push(nf); ui.fairId = nf.id; }
    toast('Feira salva');
  }, (root) => {
    const del = $('#del-fair', root);
    if (del) del.onclick = async () => {
      if (!(await ask('Excluir esta feira? As vendas continuam salvas no caixa.', 'Excluir'))) return;
      db.tx.forEach((t) => { if (t.fairId === f.id) t.fairId = ''; });
      db.fairs = db.fairs.filter((x) => x !== f);
      ui.fairId = null;
      save(); $('#modal').close(); render(); toast('Feira excluída');
    };
  });
}

// Cria as feiras da semana (quinta e sexta), sem duplicar as que já existem
function setupWeek() {
  const now = parseDate(today());
  const dow = now.getDay();
  const thursday = new Date(now);
  thursday.setDate(now.getDate() + (dow === 5 ? -1 : (4 - dow + 7) % 7));
  let created = 0;
  FAIR_WEEK.forEach((w) => {
    const d = new Date(thursday);
    d.setDate(thursday.getDate() + (w.weekday - 4));
    const date = isoDate(d);
    if (db.fairs.some((f) => f.date === date && f.place === w.place && f.period === w.period)) return;
    db.fairs.push({ id: uid(), date, place: w.place, period: w.period, notes: '' });
    created++;
  });
  save(); render();
  toast(created ? `${created} feira(s) criada(s) para ${fmtDate(isoDate(thursday)).slice(0, 5)}` : 'A semana já está montada');
}

function fragranceForm(existing) {
  const isEdit = existing != null;
  const body = `
    <div class="field"><label>Nome da fragrância</label><input name="name" required value="${esc(existing)}" placeholder="Ex.: Lavanda"></div>
    ${isEdit ? '<button type="button" class="btn block danger" id="del-frag">Remover do catálogo</button>' : ''}
  `;
  openModal(isEdit ? 'Editar fragrância' : 'Nova fragrância', body, (fd) => {
    const name = fd.get('name').trim();
    if (!name) return false;
    if (name !== existing && db.fragrances.includes(name)) { toast('Essa fragrância já existe'); return false; }
    if (isEdit) {
      db.fragrances[db.fragrances.indexOf(existing)] = name;
      db.tx.forEach((t) => { if (t.fragrance === existing) t.fragrance = name; });
    } else db.fragrances.push(name);
    toast('Fragrância salva');
  }, (root) => {
    const del = $('#del-frag', root);
    if (del) del.onclick = async () => {
      if (!(await ask(`Remover “${existing}” do catálogo? As vendas antigas continuam no histórico.`, 'Remover'))) return;
      db.fragrances = db.fragrances.filter((x) => x !== existing);
      save(); $('#modal').close(); render(); toast('Fragrância removida');
    };
  });
}

function productForm(existing) {
  const p = existing || { stock: 0, minStock: 0 };
  const isEdit = !!existing;
  const num = (v) => (v != null ? String(v).replace('.', ',') : '');
  const body = `
    <div class="field"><label>Nome do produto</label><input name="name" required value="${esc(p.name)}" placeholder="Ex.: Home spray Lavanda 250ml"></div>
    <div class="two">
      <div class="field"><label>Quanto custou (un.)</label><input name="cost" inputmode="decimal" placeholder="0,00" value="${num(p.cost)}"></div>
      <div class="field"><label>Preço varejo</label><input name="price" inputmode="decimal" placeholder="0,00" value="${num(p.price)}"></div>
    </div>
    <div class="field"><label>Preço atacado</label><input name="wholesale" inputmode="decimal" placeholder="0,00" value="${num(p.wholesale)}"></div>
    <div class="two">
      <div class="field"><label>Estoque atual</label><input type="number" name="stock" step="1" value="${p.stock || 0}"></div>
      <div class="field"><label>Avisar quando chegar a</label><input type="number" name="minStock" min="0" step="1" value="${p.minStock ?? 0}"></div>
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
      wholesale: parseMoney(fd.get('wholesale')),
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
      const w = parseMoney(root.querySelector('[name=wholesale]').value);
      calc.innerHTML = c
        ? `Lucro por peça: varejo <b class="${v - c < 0 ? 'neg' : 'pos'}">${money(v - c)}</b> (${m.toFixed(0)}%)${w ? ` · atacado <b class="${w - c < 0 ? 'neg' : 'pos'}">${money(w - c)}</b>` : ''} · Investido no estoque: <b>${money(c * s)}</b>`
        : 'Informe quanto custa produzir uma unidade para o app calcular o lucro.';
    };
    root.oninput = upd; upd();
    const del = $('#del-p', root);
    if (del) del.onclick = async () => {
      if (!(await ask('Excluir este produto? Os lançamentos continuam salvos.', 'Excluir'))) return;
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
    <div class="field"><label>Referente a</label><input name="desc" value="${esc(b.desc)}" placeholder="Ex.: 1L de essência de lavanda"></div>
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
    if (del) del.onclick = async () => {
      if (!(await ask('Excluir esta conta?', 'Excluir'))) return;
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

async function download(name, content, type) {
  const dl = window.claude && window.claude.use ? await window.claude.use('downloads').catch(() => null) : null;
  if (dl) {
    try { await dl.save({ filename: name, data: content }); } catch (e) { if (e && e.code === 'unavailable') toast('Download indisponível aqui'); }
    return;
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

function exportCsv() {
  const head = ['Data', 'Tipo', 'Descrição', 'Categoria', 'Pagamento', 'Produto', 'Fragrância', 'Feira', 'Qtd', 'Valor', 'Lucro'];
  const rows = [...db.tx].sort(byDateDesc).map((t) => [
    fmtDate(t.date), t.type === 'in' ? 'Entrada' : 'Saída', t.desc, t.category, t.method,
    productById(t.productId)?.name || '', t.fragrance || '', fairLabel(fairById(t.fairId)), t.qty || '',
    t.amount.toFixed(2).replace('.', ','),
    saleProfit(t) !== null ? saleProfit(t).toFixed(2).replace('.', ',') : '',
  ]);
  const csv = [head, ...rows].map((r) => r.map((c) => `"${String(c ?? '').replace(/"/g, '""')}"`).join(';')).join('\n');
  download(`vsensi-lancamentos-${today()}.csv`, '﻿' + csv, 'text/csv');
}

/* ================= Eventos ================= */

document.addEventListener('click', (e) => {
  const tabBtn = e.target.closest('.tabbar button');
  if (tabBtn) { if (tab === tabBtn.dataset.tab) ui.fairId = null; tab = tabBtn.dataset.tab; render(); window.scrollTo(0, 0); return; }

  const seg = e.target.closest('[data-seg] button');
  if (seg) { ui[seg.parentElement.dataset.seg] = seg.dataset.val; render(); return; }

  if (e.target.closest('[data-goto-products]')) { tab = 'produtos'; ui.prodView = 'produtos'; render(); window.scrollTo(0, 0); return; }
  const mem = e.target.closest('[data-member],[data-reject],.role-opt,#edit-profile,#copy-link');
  if (mem) {
    if (mem.dataset.reject) return rejectMember(mem.dataset.reject);
    if (mem.dataset.member) return memberForm(mem.dataset.member);
    if (mem.id === 'edit-profile') return profileForm();
    if (mem.id === 'copy-link') {
      navigator.clipboard.writeText(APP_LINK).then(() => toast('Link copiado'), () => { const r = document.createRange(); r.selectNode($('#app-link')); getSelection().removeAllRanges(); getSelection().addRange(r); toast('Link selecionado: copie'); });
      return;
    }
    if (mem.closest('#register-form')) {
      const form = mem.closest('form');
      form.querySelector('[name=role]').value = mem.dataset.val;
      form.querySelectorAll('.role-opt').forEach((x) => x.classList.toggle('active', x === mem));
      return;
    }
  }
  const el = e.target.closest('[data-quick-sale],[data-fair-expense],[data-edit-fair],[data-open-fair],[data-close-fair],[data-edit-fragrance],[data-edit-tx],[data-edit-product],[data-edit-bill],[data-toggle-bill]');
  if (el) {
    if (el.dataset.quickSale) return quickSaleForm(fairById(el.dataset.quickSale));
    if (el.dataset.fairExpense) return txForm(null, { type: 'out', fairId: el.dataset.fairExpense, category: FAIR_EXPENSE, date: fairById(el.dataset.fairExpense).date });
    if (el.dataset.editFair) return fairForm(fairById(el.dataset.editFair));
    if (el.dataset.openFair) { ui.fairId = el.dataset.openFair; render(); window.scrollTo(0, 0); return; }
    if (el.hasAttribute('data-close-fair')) { ui.fairId = null; render(); return; }
    if (el.dataset.editFragrance != null) return fragranceForm(el.dataset.editFragrance);
    if (el.dataset.toggleBill) return toggleBill(el.dataset.toggleBill);
    if (el.dataset.editTx) return txForm(db.tx.find((t) => t.id === el.dataset.editTx));
    if (el.dataset.editProduct) return productForm(productById(el.dataset.editProduct));
    if (el.dataset.editBill) return billForm(db.bills.find((b) => b.id === el.dataset.editBill));
  }

  switch (e.target.closest('[id]')?.id) {
    case 'open-more': tab = 'mais'; render(); window.scrollTo(0, 0); break;
    case 'setup-week': setupWeek(); break;
    case 'new-fair': fairForm(); break;
    case 'export-json': download(`vsensi-backup-${today()}.json`, JSON.stringify(db, null, 2), 'application/json'); break;
    case 'import-json': $('#import-file').click(); break;
    case 'export-csv': exportCsv(); break;
    case 'reset':
      ask('Apagar TODOS os dados, inclusive da nuvem? Faça um backup antes.', 'Apagar tudo').then((ok) => {
        if (ok) { db = normalize({}); save(); render(); toast('Dados apagados'); }
      });
      break;
  }
});

document.addEventListener('submit', (e) => {
  if (e.target.id === 'register-form') { e.preventDefault(); registerMember(e.target); }
});

document.addEventListener('input', (e) => {
  if (e.target.dataset.mask === 'cpf') e.target.value = maskCpf(e.target.value);
  if (e.target.dataset.mask === 'phone') e.target.value = maskPhone(e.target.value);
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
    r.onload = async () => {
      let data;
      try { data = normalize(JSON.parse(r.result)); } catch { toast('Arquivo inválido'); return; }
      if (!(await ask(`Restaurar backup com ${data.tx.length} lançamentos, ${data.products.length} produtos, ${data.fairs.length} feiras e ${data.bills.length} contas? Os dados atuais serão substituídos.`, 'Restaurar'))) return;
      db = data; save(); render(); toast('Backup restaurado');
    };
    e.target.value = '';
    r.readAsText(e.target.files[0]);
  }
});

$('#fab').onclick = () => {
  if (tab === 'feiras') {
    const f = fairById(ui.fairId) || db.fairs.find((x) => x.date === today());
    return f ? quickSaleForm(f) : fairForm();
  }
  if (tab === 'produtos') return ui.prodView === 'fragrancias' ? fragranceForm() : productForm();
  if (tab === 'contas') return billForm();
  txForm(null, { type: ui.txFilter === 'out' ? 'out' : 'in' });
};

const monthInput = $('#month');
monthInput.value = month;
monthInput.onchange = () => { month = monthInput.value || today().slice(0, 7); render(); };

if ('serviceWorker' in navigator && location.protocol.startsWith('http') && window.top === window) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

render();
connectCloud();
