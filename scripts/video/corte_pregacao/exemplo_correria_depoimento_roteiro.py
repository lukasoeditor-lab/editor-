import json, re
P = json.load(open('/tmp/work/s6/prep/pecas.json')); DUR = P['dur']; pecas = P['pecas']
PULAR = {59, 60, 61, 106}
FIXW = {0: 'mandei', 64: 'fiz', 89: 'desfiz', 137: 'viu', 80: 'de'}
for p in pecas:
    p['ws_o'] = [[FIXW.get(k, w), t] for w, t, k in p['ws_o'] if k not in PULAR]
NOMES = {'deus': 'Deus', 'senhor': 'Senhor', 'criador': 'Criador', 'eduardo': 'Eduardo', 'rian': 'Rian'}
def disp(w):
    w = w.strip()
    k = re.sub(r'[^\wÀ-ú?]', '', w)
    base = k.rstrip('?').lower()
    if base in NOMES: return NOMES[base] + ('?' if k.endswith('?') else '')
    return k.lower()
FRACAS = {'que','o','a','os','as','de','da','do','das','dos','no','na','nas','nos','um','uma','e','em','eu','é','para','pra','se','como','mas','ao'}
def linhas_de(ws, maxc=17):
    """linhas curtas (até ~17 letras ou 3 palavras); vírgula fecha a linha; linha não termina em palavra fraca"""
    L, cur = [], []
    def tam(l): return sum(len(x[0]) for x in l) + len(l) - 1
    for w, t in ws:
        d = disp(w)
        if cur and (tam(cur) + 1 + len(d) > maxc or len(cur) >= 3):
            # se a linha acaba em palavra fraca, leva ela junto para a próxima
            mov = []
            if len(cur) > 1 and cur[-1][0] in FRACAS: mov.insert(0, cur.pop())
            L.append(cur); cur = mov
        cur.append([d, t])
        if w.endswith((',', '.', '?')):
            L.append(cur); cur = []
    if cur: L.append(cur)
    out = []
    for l in L:
        if out and len(l) == 1 and tam(out[-1]) + 1 + len(l[0][0]) <= maxc + 2: out[-1] += l
        else: out.append(l)
    return out
blocos = []; nb = 0
# posições "jogadas" como na referência: (lado, deslocamento de altura)
PADRAO = [('esq', 0.00), ('dir', 0.06), ('centro', -0.03), ('esq', 0.08), ('x30', 0.02), ('dir', -0.02), ('centro', 0.07), ('esq', -0.04)]
OPOSTO = {'esq': 'dir', 'dir': 'esq', 'centro': 'dir', 'x30': 'dir'}
for p in pecas:
    L = linhas_de(p['ws_o'])
    y0 = 0.56 if p['quadro'] == 'aberto' else 0.52
    n = len(L); ng = -(-n // 3); tamanhos = [n // ng + (1 if i < n % ng else 0) for i in range(ng)]
    grupos, k = [], 0
    for t_ in tamanhos: grupos.append(L[k:k + t_]); k += t_
    for g in grupos:
        lado, dy = PADRAO[nb % len(PADRAO)]
        y = round(y0 + dy, 3)
        base = {'y': y, 'amarelo': p['pb']}
        if lado == 'x30': base['x'] = 0.30
        else: base['lado'] = lado
        if len(g) == 3 and nb % 3 == 1:  # a última linha pula para o outro lado, mais embaixo
            blocos.append(dict(base, linhas=g[:2], _par=True))
            blocos.append({'lado': OPOSTO[lado], 'y': round(y + 0.13, 3), 'amarelo': p['pb'], 'linhas': g[2:]})
        else:
            blocos.append(dict(base, linhas=g))
        nb += 1
for i, b in enumerate(blocos):
    j = i + 2 if b.get('_par') else i + 1
    b['fim'] = (blocos[j]['linhas'][0][0][1] - 0.03) if j < len(blocos) else DUR
    b.pop('_par', None)
# transições: queima ao entrar no P&B, flash ao sair; nas outras trocas, alterna, uma a cada ~6 s
ini = [p['o0'] for p in pecas]
tr, ultimo = [], -10
for k, p in enumerate(pecas):
    if k == 0: continue
    t = p['o0']
    if p['pb'] and not pecas[k-1]['pb']: tipo = 'queima'; tr.append({'t': round(t, 3), 'tipo': tipo}); ultimo = t; continue
    elif pecas[k-1]['pb'] and not p['pb']: tipo = 'flash'; tr.append({'t': round(t, 3), 'tipo': tipo}); ultimo = t; continue
    elif t - ultimo >= 12.0 and (k + 1 >= len(pecas) or not pecas[k+1]['pb'] or pecas[k+1]['o0'] - t > 3): tipo = 'flash' if len(tr) % 2 == 0 else 'queima'
    else: continue
    if t - ultimo < 2.0 and tipo not in ('queima',): continue
    tr.append({'t': round(t, 3), 'tipo': tipo}); ultimo = t
for t_ in [x['t'] for x in tr]:
    for b in blocos:
        w0 = b['linhas'][0][0]
        if t_ - 0.05 <= w0[1] < t_ + 0.07: w0[1] = round(t_ + 0.07, 3)
r = {'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'dur': round(DUR, 3), 'musica': 'kit/musica_correria.wav', 'musica_abaixo_db': 2.5,
     'sfx': {'queima': 'kit/sfx_queima.wav', 'flash': 'kit/sfx_flash.wav'}, 'sfx_vol': 0.6,
     'fontes': {'legenda': 'kit/NimbusSansNarrow-Regular.otf', 'assinatura': 'kit/MrsSaintDelafield-Regular.ttf'},
     'sombra': '0 0 34px rgba(0,0,0,.75), 0 0 12px rgba(0,0,0,.55), 0 2px 4px rgba(0,0,0,.5)', 'legenda_tam': 96,
     'cor_destaque': '#4CD28A',
     'blocos': blocos, 'transicoes': tr}
json.dump(r, open('/tmp/work/s6/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(len(blocos), 'blocos;', len(tr), 'transições:', ' '.join(f"{t['t']:.1f}{t['tipo'][0]}" for t in tr))
