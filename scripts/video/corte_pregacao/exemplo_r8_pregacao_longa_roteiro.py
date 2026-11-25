import json, re
P = json.load(open('/tmp/work/a3/prep/pecas.json')); DUR = P['dur']; pecas = P['pecas']
T = {}
for p in pecas:
    for w, t, k in p['ws_o']: T[k] = (w, t)
FIX = {'saúde': 'Saul', 'caleb': 'Calebe', 'deus': 'Deus', 'jesus': 'Jesus', 'davi': 'Davi', 'andré': 'André', 'moisés': 'Moisés', 'canaã': 'Canaã', 'josué': 'Josué', 'ele': 'Ele'}
def d(k):
    c = re.sub(r'[^\wÀ-ú?\-]', '', T[k][0]); return FIX.get(c.lower(), c.lower())
def t(k): return T[k][1]
FR = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'um', 'uma', 'e', 'que', 'eu', 'com', 'pra', 'para', 'mas', 'no', 'na', 'se', 'é', 'te', 'era', 'ser', 'como', 'teu', 'tua', 'ao', 'só', 'nós', 'eles', 'ele', 'Ele', 'aquele', 'está', 'vai', 'quando', 'nosso'}
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
ev += caps(R(5517, 5528))
ev.append({'tipo': 'pilha', 'w': [['a maior dificuldade', t(5529)], ['a maior luta', t(5533)], ['o maior obstáculo', t(5537)]]})
ev += caps(R(5544, 5548))
ev.append({'tipo': 'digita', 'texto': 'PONTO DE VISTA', 't': t(5552), 'dur_digita': 0.6, 'sat': [['muda o teu', t(5549), 'ne']]})
ev.append({'tipo': 'zoom', 't': pecas[2]['o0'] - 0.03})
ev += caps(R(5094, 5120)); ev.append({'tipo': 'grande', 'w': [['GIGANTE', t(5121)]]})
ev += caps(R(5139, 5142)); ev.append({'tipo': 'combo', 'forte': ['Davi', t(5143)], 'serif': ['o menino de 17 anos', t(5147)], 'cor': 'quente'})
ev += caps(R(5152, 5166)); ev.append({'tipo': 'brilho', 'w': [['OPORTUNIDADE', t(5167)]], 'grande': True}); ev += caps(R(5168, 5173))
ev += caps(R(5244, 5247)); ev.append({'tipo': 'combo', 'forte': ['cinco pães', t(5248)], 'serif': ['e dois peixes', t(5250)], 'cor': 'quente'}); ev += caps(R(5253, 5254))
ev.append({'tipo': 'citacao', 'cor': 'quente', 'x': 0.08, 'y': 0.47, 'linhas': [[['“como é que vai', t(5276)]], [['sustentar', t(5280)]], [['uma multidão', t(5281)]], [['de dez mil?”', t(5283)]]]})
ev += caps(R(5305, 5312)); ev.append({'tipo': 'grande', 'w': [['MATÉRIA-PRIMA', t(5313)]]}); ev += caps(R(5315, 5321))
ev.append({'tipo': 'serif', 'lado': 'esq', 'y': 0.45, 'linhas': [[['uma oportunidade', t(5323)]], [['de ver o milagre', t(5325)]]]})
ev += caps(R(5343, 5345)); ev.append({'tipo': 'combo', 'forte': ['dez espias', t(5346)], 'serif': ['terra de Canaã', t(5354)], 'cor': 'quente'})
ev.append({'tipo': 'luz', 't': pecas[7]['o0']})
ev.append({'tipo': 'citacao', 'cor': 'quente', 'x': 0.08, 'y': 0.46, 'linhas': [[['“Moisés,', t(5401)]], [['não dá pra entrar', t(5402)]], [['naquela terra”', t(5406)]]]})
ev.append({'tipo': 'citacao', 'cor': 'quente', 'x': 0.08, 'y': 0.46, 'linhas': [[['“aqueles homens', t(5418)]], [['são gigantes', t(5420)]], [['e nós somos', t(5422)]], [['como gafanhotos”', t(5425)]]]})
ev.append({'tipo': 'zoom', 't': pecas[8]['o0'] - 0.03})
ev += caps(R(5445, 5446)); ev.append({'tipo': 'combo', 'forte': ['Josué', t(5447)], 'serif': ['e Calebe', t(5448)], 'cor': 'quente'})
ev += caps(R(5450, 5456)); ev.append({'tipo': 'brilho', 'w': [['oportunidade', t(5457)]], 'som': False})
ev += caps(R(5556, 5560)); ev.append({'tipo': 'brilho', 'w': [['GLORIFICADO', t(5562)]], 'grande': True}); ev += caps(R(5563, 5565))
ev.append({'tipo': 'serif', 'lado': 'esq', 'y': 0.44, 'linhas': [[['Ele te honrar', t(5566)]], [['Ele te exaltar', t(5570)]]]})
ev.append({'tipo': 'serif', 'lado': 'dir', 'y': 0.56, 'junto': True, 'linhas': [[['o milagre acontecer', t(5573)]], [['o sobrenatural existir', t(5576)]]]})
ev.append({'tipo': 'grande', 'w': [['ALELUIA', t(5581)]]})
r = {'base': 'prep/base.mp4', 'voz': 'prep/voz.wav', 'dur': round(DUR + 0.5, 3), 'musica': 'kit/musica.wav', 'musica_abaixo_db': 5,
     'sfx': {k: f'kit/{k}.wav' for k in ('clique', 'whoosh', 'glitch', 'cartao', 'fim')},
     'fontes': {'cond': 'kit/Archivo.ttf', 'serif': 'kit/DMSerifDisplay-Italic.ttf'},
     'cores': {'destaque': '#A6D86A', 'quente': '#E6C48F', 'forte': '#D99A4E'}, 'cor_luz': '#ffd08a',
     'cap_tam': 68, 'sombra_forte': True, 'handle': '@alexandrealmeida.ofc', 'handle_y': 0.79,
     'fim': {'texto': '@alexandrealmeida.ofc', 'dur': 2.8}, 'eventos': ev}
json.dump(r, open('/tmp/work/a3/roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(len(ev), 'eventos')
