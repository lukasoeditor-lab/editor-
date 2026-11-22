import json, re
P = json.load(open('/tmp/work/j1/prep/pecas.json')); DUR = P['dur']; pecas = P['pecas']
# fonte → (texto, hora no vídeo final)
T = {}
for p in pecas:
    i0 = [k for k, w in enumerate(json.load(open('/tmp/work/j1/words.json'))) if w[1] == p['ws'][0][1] and w[0] == p['ws'][0][0]][0]
    for k, (w, t) in enumerate(p['ws_o']):
        T[i0 + k] = (w, t)
NOMES = {'deus': 'Deus', 'ezequiel': 'Ezequiel', 'jeremias': 'Jeremias'}
def d(k, manter=True):
    w = T[k][0]; c = re.sub(r'[^\wÀ-ú?\-]', '', w)
    b = c.rstrip('?').lower()
    return NOMES.get(b, b) + ('?' if c.endswith('?') and manter else '')
def t(k): return T[k][1]
FRACAS = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'um', 'uma', 'e', 'que', 'no', 'na', 'ao', 'te', 'me', 'eu', 'é', 'para', 'seu', 'seus', 'teu', 'tua', 'mas', 'se'}
def caps(ks):
    out, cur = [], []
    for k in ks:
        cur.append(k)
        txt = ' '.join(d(x) for x in cur)
        if (d(k) not in FRACAS and len(cur) >= 1) or len(cur) >= 2 or len(txt) > 12:
            out.append({'tipo': 'cap', 'w': [[' '.join(d(x) for x in cur), t(cur[0])]]}); cur = []
    if cur: out.append({'tipo': 'cap', 'w': [[' '.join(d(x) for x in cur), t(cur[0])]]})
    for e in out:
        e['w'][0][0] = e['w'][0][0][0].upper() + e['w'][0][0][1:] if e['w'][0][0] in ('Deus',) else e['w'][0][0]
    return out
def rng(a, b): return [k for k in range(a, b + 1) if k in T]
ev = []
def resto(a, b, usados):
    return [k for k in rng(a, b) if k not in usados]
def seg(a, b, especiais):
    """caps para o que não for especial, na ordem"""
    usados = set()
    for e, ks in especiais: usados |= set(ks)
    pend = []
    lista = []
    for k in rng(a, b):
        esp = [e for e, ks in especiais if ks and ks[0] == k]
        if esp:
            if pend: lista += caps(pend); pend = []
            lista += esp
        elif k not in usados:
            pend.append(k)
    if pend: lista += caps(pend)
    ev.extend(lista)

def cit(linhas, cor='quente', y=0.50, aspas=True):
    L = []
    for li, ks in enumerate(linhas):
        txt = ' '.join(d(k) for k in ks)
        if aspas and li == 0: txt = '“' + txt
        if aspas and li == len(linhas) - 1: txt = txt + '”'
        L.append([[txt, t(ks[0])]])
    return {'tipo': 'citacao', 'linhas': L, 'cor': cor, 'x': 0.08, 'y': y}

seg(8, 14, [({'tipo': 'digita', 'texto': 'SONHO', 't': t(12), 'sat': [['foi', t(13), 'se'], ['frustrado', t(14), 'sd']]}, [12, 13, 14])])
seg(15, 23, [({'tipo': 'combo', 'forte': ['jogado', t(22)], 'serif': ['abaixo', t(23)], 'cor': 'quente'}, [22, 23])])
seg(24, 29, [])
ev.append({'tipo': 'luz', 't': t(30)})
for a, b, corte in ((30, 35, 33), (36, 41, 39), (42, 46, 45), (47, 50, 49), (51, 54, 53)):
    ev.append(cit([rng(a, corte - 1), rng(corte, b)]))
ev.append({'tipo': 'zoom', 't': t(55) - 0.05})
seg(55, 66, [])
seg(67, 77, [({'tipo': 'pilha', 'w': [['é', t(75)], ['muito', t(76)], ['maior', t(77)]]}, [75, 76, 77])])
seg(78, 84, [({'tipo': 'serif', 'lado': 'esq', 'y': 0.45, 'linhas': [[['os seus olhos', t(80)]], [['não viram', t(83)]]]}, rng(80, 84))])
seg(85, 91, [({'tipo': 'serif', 'lado': 'dir', 'y': 0.55, 'linhas': [[['os seus ouvidos', t(87)]], [['não ouviram', t(90)]]]}, rng(87, 91))])
seg(92, 99, [({'tipo': 'grande', 'w': [['CORAÇÃO', t(99)]]}, [99])])
seg(100, 108, [])
seg(109, 119, [({'tipo': 'brilho', 'w': [['ALÉM', t(119)]], 'grande': True}, [119])])
for a in (120, 125, 130):
    seg(a, a + 4, [({'tipo': 'brilho', 'w': [['além', t(a)]], 'som': False}, [a])])
seg(135, 142, [])
ev.append({'tipo': 'cartao', 't0': t(151) - 0.06, 't1': t(157) + 0.55})
seg(151, 165, [])
seg(166, 178, [({'tipo': 'combo', 'forte': ['vale', t(175)], 'serif': ['de ossos', t(176)], 'cor': 'quente'}, [175, 176, 177]),
               ({'tipo': 'grande', 'w': [['SEQUÍSSIMO', t(178)]]}, [178])])
seg(179, 189, [({'tipo': 'grande', 'w': [['FUTURO', t(189)]]}, [188, 189])])
seg(190, 200, [({'tipo': 'serif', 'lado': 'esq', 'y': 0.44, 'linhas': [[['o mês', t(193)]], [['que vem', t(195)]]]}, rng(193, 196)),
               ({'tipo': 'serif', 'lado': 'dir', 'y': 0.56, 'junto': True, 'linhas': [[['o ano', t(197)]], [['que vem', t(199)]]]}, rng(197, 200))])
seg(201, 207, [])
seg(208, 226, [({'tipo': 'grande', 'w': [['TEU SONHO', t(213)]]}, [213, 214])])
seg(227, 238, [({'tipo': 'pilha', 'w': [['aceite', t(231)], ['o lugar', t(232)]]}, [231, 232, 233])])
seg(239, 258, [])
seg(259, 261, [({'tipo': 'digita', 'texto': 'AMANHÃ', 't': t(260), 'sat': [['mas', t(259), 'ne']]}, [259, 260, 261])])
seg(269, 279, [])
seg(280, 285, [({'tipo': 'combo', 'forte': ['espírito', t(282)], 'serif': ['vai te conduzir', t(283)], 'cor': 'quente'}, rng(282, 285))])
seg(286, 292, [])
seg(293, 296, [({'tipo': 'brilho', 'w': [['PROFETIZAR', t(296)]], 'grande': True}, [295, 296])])
for a, b in ((297, 301), (302, 305), (306, 309)):
    ks = [k for k in rng(a, b) if d(k) != 'e']
    ev.append(cit([ks[:2], ks[2:]], cor='branco', y=0.47, aspas=False))
seg(310, 320, [])
seg(321, 332, [({'tipo': 'pilha', 'w': [['eu', t(321)], ['preciso de', t(322)], ['um profeta', t(324)]]}, rng(321, 325))])

r = {'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'dur': round(DUR + 0.6, 3), 'musica': 'kit/musica.wav', 'musica_abaixo_db': 12,
     'sfx': {k: f'kit/{k}.wav' for k in ('clique', 'whoosh', 'glitch', 'cartao', 'fim')},
     'fontes': {'cond': 'kit/Archivo.ttf', 'serif': 'kit/DMSerifDisplay-Italic.ttf'},
     'cores': {'destaque': '#F6C453', 'quente': '#E8963F', 'forte': '#D9672B'}, 'cor_luz': '#ffb347',
     'handle': '@alexandrealmeida.ofc', 'handle_y': 0.79, 'cap_tam': 68, 'cartao_inset': 34.6, 'fim': {'texto': '@alexandrealmeida.ofc', 'dur': 2.8}, 'eventos': ev}
json.dump(r, open('/tmp/work/j1/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(len(ev), 'eventos')
