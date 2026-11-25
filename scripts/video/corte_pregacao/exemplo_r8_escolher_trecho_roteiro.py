import json, re
P = json.load(open('/tmp/work/e9/prep/pecas.json')); DUR = P['dur']; pecas = P['pecas']
T = {}
for p in pecas:
    for w, t, k in p['ws_o']: T[k] = (w, t)
FIX = {'gravatar': 'Gravataí'}
def d(k):
    c = re.sub(r'[^\wÀ-ú?\-]', '', T[k][0]); c = FIX.get(c.lower(), c)
    return c if c in ('Gravataí',) else c.lower()
def t(k): return T[k][1]
FR = {'o', 'a', 'os', 'de', 'do', 'um', 'uma', 'e', 'que', 'eu', 'com', 'pra', 'mas', 'no', 'na', 'se', 'é', 'sem', 'tá', 'ter', 'tem', 'nesse', 'quando', 'porque', 'então', 'aí'}
def caps(ks):
    out, cur = [], []
    for k in ks:
        if k not in T: continue
        cur.append(k)
        if d(k) not in FR or len(cur) >= 2:
            out.append({'tipo': 'cap', 'w': [[' '.join(d(x) for x in cur), t(cur[0])]]}); cur = []
    if cur: out.append({'tipo': 'cap', 'w': [[' '.join(d(x) for x in cur), t(cur[0])]]})
    return out
R = lambda a, b: [k for k in range(a, b + 1) if k in T]
ev = []
ev += caps(R(104, 114)); ev.append({'tipo': 'digita', 'texto': 'NÃO DESISTA', 't': t(115), 'dur_digita': 0.7})
ev += caps(R(17, 25))
ev.append({'tipo': 'pilha', 'w': [['tem os colegas', t(26)], ['tem os amigos', t(29)], ['que não apoiam', t(32)]]})
ev.append({'tipo': 'combo', 'forte': ['família', t(36)], 'serif': ['também', t(37)], 'cor': 'quente'})
ev += caps(R(38, 42)); ev.append({'tipo': 'grande', 'w': [['MUDAR', t(43)]]})
ev.append({'tipo': 'serif', 'lado': 'esq', 'y': 0.46, 'linhas': [[['mudar', t(45)]], [['isso aí', t(46)]]]})
ev.append({'tipo': 'zoom', 't': pecas[5]['o0'] - 0.03})
ev += caps(R(48, 53)); ev.append({'tipo': 'grande', 'w': [['CANTO', t(54)]]})
ev.append({'tipo': 'cap', 'w': [['e não decidir', t(55)]]}); ev.append({'tipo': 'cap', 'w': [['mudar', t(58)]]})
ev += caps(R(59, 60))
ev.append({'tipo': 'serif', 'lado': 'dir', 'y': 0.55, 'linhas': [[['daquele', t(61)]], [['mesmo jeito', t(62)]]]})
ev += caps(R(76, 80)); ev.append({'tipo': 'brilho', 'w': [['DECIDI MUDAR', t(81)]], 'grande': True}); ev += caps(R(83, 84))
ev += caps(R(118, 125))
ev.append({'tipo': 'citacao', 'cor': 'quente', 'x': 0.08, 'y': 0.47, 'linhas': [[['“a gente quer', t(126)]], [['conseguir', t(129)]], [['um resultado', t(130)]], [['muito rápido”', t(132)]]]})
ev += caps(R(134, 137))
ev.append({'tipo': 'zoom', 't': pecas[8]['o0'] - 0.03})
ev += caps(R(139, 142)); ev.append({'tipo': 'combo', 'forte': ['estudar', t(143)], 'serif': ['direitinho', t(144)], 'cor': 'quente'})
ev.append({'tipo': 'brilho', 'w': [['aguentar o processo', t(145)]]})
ev.append({'tipo': 'pilha', 'w': [['a gente', t(148)], ['consegue', t(150)], ['chegar', t(151)]]})
r = {'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'dur': round(DUR + 0.5, 3), 'musica': 'kit/musica.wav', 'musica_abaixo_db': 30,
     'sfx': {k: f'kit/{k}.wav' for k in ('clique', 'whoosh', 'glitch', 'cartao', 'fim')},
     'fontes': {'cond': 'kit/Archivo.ttf', 'serif': 'kit/DMSerifDisplay-Italic.ttf'},
     'cores': {'destaque': '#4CD28A', 'quente': '#F2C35B', 'forte': '#3FBF7A'}, 'cor_luz': '#ffd27a',
     'cap_tam': 68, 'sombra_forte': True, 'fim': {'texto': '', 'dur': 2.4}, 'eventos': ev}
json.dump(r, open('/tmp/work/e9/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(len(ev), 'eventos')
