import json, re
P = json.load(open('/tmp/work/b1/prep/pecas.json')); DUR = P['dur']; pecas = P['pecas']
T = {}
for p in pecas:
    for k, (w, t) in zip(range(p['i'], p['j'] + 1), p['ws_o']): T[k] = (w, max(t, p['o0'] + 0.02))
FIX = {'misturei': 'estourei'}
def d(k):
    c = re.sub(r'[^\wÀ-ú?\-]', '', T[k][0]).lower(); return FIX.get(c, c)
def t(k): return T[k][1]
FR = {'o', 'a', 'de', 'do', 'um', 'uma', 'e', 'que', 'eu', 'com', 'para', 'minha', 'mas', 'lá', 'ali', 'esses', 'vou'}
def caps(ks):
    out, cur = [], []
    for k in ks:
        cur.append(k)
        if d(k) not in FR or len(cur) >= 2:
            out.append({'tipo': 'cap', 'w': [[' '.join(d(x) for x in cur), t(cur[0])]]}); cur = []
    if cur: out.append({'tipo': 'cap', 'w': [[' '.join(d(x) for x in cur), t(cur[0])]]})
    return out
R = lambda a, b: list(range(a, b + 1))
ev = []
# gancho
ev += caps(R(26, 35))
ev.append({'tipo': 'digita', 'texto': 'BOLHA', 't': t(36), 'dur_digita': 0.55, 'sat': [['estourei', t(36), 'ne'], ['minha', t(37), 'nd']]})
# história
ev += caps(R(0, 4)); ev.append({'tipo': 'grande', 'w': [['SONHO', t(5)]]})
ev.append({'tipo': 'luz', 't': pecas[2]['o0']})
ev.append({'tipo': 'citacao', 'cor': 'quente', 'x': 0.08, 'y': 0.47, 'linhas': [[['“pô, será que', t(10)]], [['um dia eu vou ter', t(14)]], [['uma barbearia?', t(18)]]]})
ev.append({'tipo': 'citacao', 'cor': 'quente', 'x': 0.08, 'y': 0.47, 'linhas': [[['será que', t(20)]], [['eu vou conseguir?”', t(22)]]]})
ev.append({'tipo': 'zoom', 't': pecas[4]['o0'] - 0.03})
ev.append({'tipo': 'pilha', 'w': [['e vou', t(39) + 0.03], ['fazer', t(41)], ['acontecer', t(42)]]})
ev.append({'tipo': 'combo', 'forte': ['vendi', t(48)], 'serif': ['a moto', t(49)], 'cor': 'quente'})
ev += caps(R(51, 54))
ev.append({'tipo': 'serif', 'lado': 'esq', 'y': 0.46, 'linhas': [[['lixou lá', t(55)]], [['tudinho', t(57)]]]})
ev += caps(R(58, 62)); ev.append({'tipo': 'brilho', 'w': [['CHEGAR', t(63)]], 'grande': True})
ev += caps(R(64, 68))
r = {'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'dur': round(DUR + 0.5, 3), 'musica': 'kit/musica.wav', 'musica_abaixo_db': 5,
     'sfx': {k: f'kit/{k}.wav' for k in ('clique', 'whoosh', 'glitch', 'cartao', 'fim')},
     'fontes': {'cond': 'kit/Archivo.ttf', 'serif': 'kit/DMSerifDisplay-Italic.ttf'},
     'cores': {'destaque': '#3EC6E0', 'quente': '#D9B48A', 'forte': '#C08F5E'}, 'cor_luz': '#ffcf8a',
     'cap_tam': 68, 'sombra_forte': True, 'fim': {'texto': '', 'dur': 2.4}, 'eventos': ev}
json.dump(r, open('/tmp/work/b1/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(len(ev), 'eventos')
