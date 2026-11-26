"""Corte "Se Ele faz, eu adoro" (Pr. Alexandre, João 4) no estilo 9."""
import json, re
P = json.load(open('/tmp/work/t9/prep/pecas.json'))
FIX = {390: 'e', 379: 'nem'}
S = {'adoro', 'glorificando', 'milagre', 'passageiro', 'benefícios', 'eternidade', 'ouro', 'cristais', 'vê',
     'primordial', 'salvação', 'outra', 'separará', 'amor', 'ninguém'}
ws = [[FIX.get(k, w), t, k] for p in P['pecas'] for w, t, k in p['ws_o']]
inicio_peca = {p['ws_o'][0][2] for p in P['pecas']}
tk = {k: [w, round(t, 3)] for w, t, k in ws}
# páginas à mão: linhas por faixa de índice de palavra; * = serifa
PAG = """296-299 | 300*
301-304 | 305 306*
307-309 | 310 311
312-315 | 316 317
318 | 319-321
30 31* | 32-34
35 36 37*
38-40 | 41 42
43-45 46*
47 48 49*
50-52 | 53-55
56 57
58-60 | 61 62
63-65 66*
67 68 | 69*
184-186 | 187 188
189-192 | 193 194 195*
196-197 | 198 199*
200-203 | 204 205*
206-209 | 210 211*
235-238 | 239-241*
242 243 244* | 245-248
249-251 | 252-254
255-256 | 257 258
259-261 262* | 263
372-373 374* | 375-378
379 380 | 381 382*
383 384 | 385 386
387 388 | 389-390 391*
392-393 | 394 395* 396 397"""
def faixa(tok):
    serif = tok.endswith('*'); tok = tok.rstrip('*')
    a, _, b = tok.partition('-'); ks = list(range(int(a), int(b or a) + 1))
    return ks, serif
out = []
for linha in PAG.splitlines():
    ls = []
    for parte in linha.split('|'):
        l = []
        for tok in parte.split():
            ks, serif = faixa(tok)
            for i, k in enumerate(ks):
                p = list(tk[k])
                if serif and i == len(ks) - 1: p.append('s')
                l.append(p)
        ls.append(l)
    out.append({'linhas': ls})
pb = P['pecas'][1]
for o in out:
    if pb['o0'] <= o['linhas'][0][0][1] < P['pecas'][2]['o0']: o['estilo'] = 'grande'
o0 = [p['o0'] for p in P['pecas']]
r = {'dur': P['dur'], 'base': 'prep/base.mp4', 'voz': 'prep/voz.wav',
     'handle': {'nome': 'PR. ALEXANDRE ALMEIDA', 'arroba': '@alexandrealmeida.ofc', },
     'abre': 1.6,
     'escuro': [[o0[1] - 0.45, o0[1], o0[1] + 0.9]] + [[o0[k] - 1.5, o0[k], o0[k] + 1.6] for k in range(2, len(o0))],
     'paginas': out}
json.dump(r, open('/tmp/work/t9/roteiro.json', 'w'), ensure_ascii=False, indent=1)
for o in out: print(o.get('estilo', ''), ' / '.join(' '.join(p[0] + ('*' if len(p) > 2 else '') for p in l) for l in o['linhas']))
