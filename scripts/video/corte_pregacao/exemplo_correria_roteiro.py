import json, re
P = json.load(open('/tmp/work/c1/prep/pecas.json')); DUR = P['dur']; pecas = P['pecas']
NOMES = {'deus': 'Deus', 'senhor': 'Senhor', 'criador': 'Criador'}
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
blocos = []; lados = ['centro', 'centro', 'centro', 'centro']; nb = 0
for p in pecas:
    L = linhas_de(p['ws_o'])
    y = 0.36 if p['quadro'] == 'aberto' else 0.45
    n = len(L); ng = -(-n // 3); tamanhos = [n // ng + (1 if i < n % ng else 0) for i in range(ng)]
    grupos, k = [], 0
    for t_ in tamanhos: grupos.append(L[k:k + t_]); k += t_
    for gi, g in enumerate(grupos):
        lado = 'centro' if (len(g) == 1) else lados[nb % 4]
        blocos.append({'lado': lado, 'y': y, 'amarelo': p['pb'], 'linhas': g}); nb += 1
for b, c in zip(blocos, blocos[1:]): b['fim'] = c['linhas'][0][0][1] - 0.03
blocos[-1]['fim'] = DUR
# transições: queima ao entrar no P&B, flash ao sair; nas outras trocas, alterna, uma a cada ~6 s
ini = [p['o0'] for p in pecas]
tr, ultimo = [], -10
for k, p in enumerate(pecas):
    if k == 0: continue
    t = p['o0']
    if p['pb'] and not pecas[k-1]['pb']: tipo = 'queima'; tr.append({'t': round(t, 3), 'tipo': tipo}); ultimo = t; continue
    elif pecas[k-1]['pb'] and not p['pb']: tipo = 'flash'; tr.append({'t': round(t, 3), 'tipo': tipo}); ultimo = t; continue
    elif t - ultimo >= 6.0 and (k + 1 >= len(pecas) or not pecas[k+1]['pb'] or pecas[k+1]['o0'] - t > 3): tipo = 'flash' if len(tr) % 2 == 0 else 'queima'
    else: continue
    if t - ultimo < 2.0 and tipo not in ('queima',): continue
    tr.append({'t': round(t, 3), 'tipo': tipo}); ultimo = t
tr.append({'t': round(DUR, 3), 'tipo': 'queima'})
r = {'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'dur': round(DUR, 3), 'musica': 'kit/musica_correria.wav', 'musica_abaixo_db': 2.5,
     'sfx': {'queima': 'kit/sfx_queima.wav', 'flash': 'kit/sfx_flash.wav'}, 'sfx_vol': 0.6,
     'fontes': {'legenda': 'kit/NimbusSansNarrow-Regular.otf', 'assinatura': 'kit/MrsSaintDelafield-Regular.ttf'},
     'sombra': '0 0 34px rgba(0,0,0,.75), 0 0 12px rgba(0,0,0,.55), 0 2px 4px rgba(0,0,0,.5)', 'legenda_tam': 96,
     'handle': '@alexandrealmeida.ofc', 'handle_y': 0.905,
     'blocos': blocos, 'transicoes': tr, 'assinatura': {'texto': 'Alexandre Almeida', 'sub': '@alexandrealmeida.ofc', 'dur': 5.0}}
json.dump(r, open('/tmp/work/c1/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(len(blocos), 'blocos;', len(tr), 'transições:', ' '.join(f"{t['t']:.1f}{t['tipo'][0]}" for t in tr))
for b in blocos[:12]: print(b['lado'], b['y'], ' / '.join(' '.join(w for w, t in l) for l in b['linhas']))
