"""Corte "Não sonhe com a mente na sua limitação" (Pr. Wilton Santos) no estilo 9, com a música "Deep Pain" (enviada pelo Lukas) 6 dB abaixo da voz."""
import json
P = json.load(open('/tmp/work/c9/prep/pecas.json'))
FIX = {62: 'sublime', 69: 'palavra:', 70: 'Abra,', 71: 'pedi,', 72: 'pedi,', 73: 'dar-se-vos-á,', 74: '', 75: '', 76: '', 77: 'batei'}
ws = [[FIX.get(k, w), t, k] for p in P['pecas'] for w, t, k in p['ws_o']]
tk = {k: [w, round(t, 3)] for w, t, k in ws}
PAG = """0-4 | 5 6 7*
8-11 | 12 13* 14 15
16-18
19-21 | 22*
23 24*
36-38 | 39-41
42-45 | 46*
47-50 | 51*
52-56 | 57
58-60 | 61 62* 63
64-66 | 67 68 69*
70-72 | 73
77-80 | 81 82*
83 84 85* | 86-89
90-93 | 94 95 96*
97-99 | 100 101* 102
103-106 | 107 108*
109-112
113-116 | 117 118 119*
120-122 | 123 124* 125 126
127 128 | 129 130*"""
def faixa(tok):
    serif = tok.endswith('*'); tok = tok.rstrip('*')
    a, _, b = tok.partition('-'); return list(range(int(a), int(b or a) + 1)), serif
out = []
for linha in PAG.splitlines():
    ls = []
    for parte in linha.split('|'):
        l = []
        for tok in parte.split():
            ks, serif = faixa(tok)
            for i, k in enumerate(ks):
                if not tk[k][0]: continue
                p = list(tk[k])
                if serif and i == len(ks) - 1: p.append('s')
                l.append(p)
        ls.append(l)
    out.append({'linhas': ls})
pb0, pb1 = P['pecas'][2]['o0'], P['pecas'][3]['o0']
for o in out:
    if pb0 <= o['linhas'][0][0][1] < pb1: o['estilo'] = 'grande'
o0 = [p['o0'] for p in P['pecas']]
volta = tk[8][1] - 0.5          # ele volta ao palco em "Sonhe com a mente..."
r = {'dur': P['dur'], 'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'musica': 'musica.wav', 'musica_abaixo_db': 6,
     'handle': {'nome': 'PR. WILTON SANTOS', 'arroba': '@prwiltonsantos'},
     'abre': 0.8,
     'escuro': [[o0[2] - 0.35, o0[2], o0[2] + 0.45], [o0[3] - 0.6, o0[3], o0[3] + 1.4], [o0[4] - 1.5, o0[4], o0[4] + 1.6]],
     'paginas': out}
json.dump(r, open('/tmp/work/c9/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print('volta', round(volta, 2), 'o0', o0)
for o in out: print(o.get('estilo', ''), ' / '.join(' '.join(p[0] + ('*' if len(p) > 2 else '') for p in l) for l in o['linhas']))
