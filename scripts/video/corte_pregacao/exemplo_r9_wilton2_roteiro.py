"""Pr. Wilton, "Quanto mais impossível for, maior será o milagre" no estilo 9, com "I Know I'm God Son" em loop."""
import json
P = json.load(open('/tmp/work/w2/prep/pecas.json'))
FIX = {117: 'homens,', 118: 'é', 228: 'página?', 289: 'porta-voz', 290: '', 110: 'diz:'}
ws = [[FIX.get(k, w), t, k] for p in P['pecas'] for w, t, k in p['ws_o']]
tk = {k: [w, round(t, 3)] for w, t, k in ws}
PAG = """23 24 | 25* 26
27 28 | 29 30*
94-99 | 100 101
102 103 | 104-106
107-110
111-114* | 115-117
118 119 | 120 121*
155-159 | 160* 161-163
164-166
167-169 | 170 171*
188-192 | 193 194*
195-198 | 199 200
201-204*
205-208 | 209 210*
211-214 | 215-217
218-220 | 221 222
223-225 | 226-228*
229-231 | 232 233*
266-269 | 270 271
272-274 | 275-279*
280-282 | 283-285*
286-289 | 291-293
294-296*
297-300*
301-304*
309-312*
313-315
316 317 | 318-321*"""
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
            ks = [k for k in ks if tk[k][0]]
            for i, k in enumerate(ks):
                p = list(tk[k])
                if serif and i == len(ks) - 1: p.append('s')
                l.append(p)
        ls.append(l)
    out.append({'linhas': ls})
pb0, pb1 = P['pecas'][1]['o0'], P['pecas'][2]['o0']
for o in out:
    if pb0 <= o['linhas'][0][0][1] < pb1: o['estilo'] = 'grande'
o0 = [p['o0'] for p in P['pecas']]
r = {'dur': P['dur'], 'base': 'prep/base.mp4', 'voz': 'prep/voz.wav',
     'musica': '/tmp/work/mus2/godson.mp3', 'musica_abaixo_db': 7,
     'handle': {'nome': 'PR. WILTON SANTOS', 'arroba': '@prwiltonsantos', 'foto': 'foto.jpg', 'verificado': True},
     'abre': 0.8,
     'escuro': [[o0[1] - 0.4, o0[1], o0[1] + 0.5], [o0[2] - 0.5, o0[2], o0[2] + 1.0], [o0[3] - 0.4, o0[3], o0[3] + 0.6],
                [o0[6] - 1.3, o0[6], o0[6] + 1.4], [o0[7] - 1.2, o0[7], o0[7] + 1.3]],
     'fecha': 1.2,
     'paginas': out}
json.dump(r, open('/tmp/work/w2/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print('o0', o0)
for o in out: print(o.get('estilo', ''), ' / '.join(' '.join(p[0] + ('*' if len(p) > 2 else '') for p in l) for l in o['linhas']))
