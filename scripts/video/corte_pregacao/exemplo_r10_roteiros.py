"""Roteiros dos 3 cortes da pregação de 2 Reis 5 (Pr. Alexandre) no estilo 10 (estilo 9 + imagens de apoio,
cartão digitado, clarão, sépia e chamada final). Uso: python3 roteiro10.py k1|k2|k3"""
import json, subprocess, sys
from pathlib import Path

K = sys.argv[1]
G = Path(f'/tmp/work/{K}')
P = json.load(open(G / 'prep/pecas.json'))
BR = Path('/tmp/work/broll/hd')

CFG = {
 'k1': dict(
  FIX={},
  PAG="""1529-1531 | 1532 1533 1534*
1535 1536 | 1537 1538*
1539 1540 | 1541 1542
1246-1249 | 1250-1254
1255-1257 | 1258* 1259 1260
1261-1264 | 1265-1268*
1293-1296 | 1297*
1298-1300
1301-1305 | 1306-1308*
1342-1344 | 1345-1347*
1348-1350 | 1351-1355
1356-1359 | 1360-1365*
1366-1369*
1381-1383*
1384-1387 | 1388 1389*
1390-1392 | 1393 1394*
1762-1765 | 1766 1767* 1768
1769-1774
1775-1778 | 1779-1782*
1783-1787*
1788-1792 | 1793-1796
1400-1403 | 1404-1407*""",
  CARD=[dict(linhas=["1797-1800", "1801-1802", "1803-1805"], ate=1811)],
  BROLL=[(25586, 1344, 1365, False, 0.33), (32056, 1384, 1394, True, 0.55), (4701, 1775, 1787, False, 0.40)],
  ESCURO=[1, 5], CLARAO=[2, 'card', 'card_fim'], ),
 'k2': dict(
  FIX={4518: 'realidade,', 4528: 'algo,', 4738: 'Senhor,', 4960: 'certo,'},
  PAG="""4500-4503 4504 4505* | 4506-4508
4509-4513 | 4514 4515
4516-4521 | 4522 4523 4524*
4525-4528 | 4529-4535
4536-4539 4540*
4560-4564 | 4565-4567*
4568-4570 | 4571 4572*
4573-4575 | 4576-4578
4579-4582 | 4583*
4738-4741 | 4742-4747 4748*
4749-4752 | 4753-4755*
4756-4759 | 4760-4762*
4763-4768 | 4769 4770 4771* 4772 4773
4840 4841* | 4842-4844
4845-4847 | 4848-4852
4853-4856 | 4857-4859*
4860-4863 | 4864-4866
4867-4869
4870-4874 | 4875-4877*
4878-4880 | 4881 4882*
4957-4960 | 4961-4963*
4964* 4965 | 4966-4969
4995-4997 | 4998 4999*
5000-5003 5004* | 5005 5006
5007-5011
5012-5014 | 5015 5016*""",
  CARD=[dict(linhas=["4584-4588", "4589-4592", "4593-4595"], ate=4595)],
  BROLL=[(28729, 4525, 4540, False, 0.50), (25575, 4560, 4578, True, 0.45), (6734, 4875, 4882, False, 0.50), (25896, 5007, 5016, False, 0.55)],
  ESCURO=[1, 6], CLARAO=['card', 4, 5], ),
 'k3': dict(
  FIX={5713: 'assim:', 6125: 'assim:'},
  PAG="""6013-6015 | 6016-6018*
6019 6020* | 6021-6024
5679-5681* | 5682-5685
5686-5690
5691-5693 | 5694-5696*
5697-5702 | 5703-5706*
5707-5710 | 5711-5713
5714-5718*
5719-5725 | 5726 5727* 5728-5731
5732 5733 | 5734 5735 5736*
5737-5739 | 5740-5743
6058-6062*
6120-6122 | 6123-6125
6126-6128*
6129-6132* | 6133-6136
6137 6138 | 6139-6141*
6142 6143 | 6144*
6145 6146 | 6147 6148
6149-6152*
6153 6154*
6155 6156 | 6157 6158*
6159-6161 | 6162*""",
  CARD=[dict(linhas=["6051-6053", "6054-6057"], ate=6057)],
  BROLL=[(48610, 5691, 5706, False, 0.66), (45982, 5719, 5743, True, 0.50), (46448, 6126, 6136, False, 0.50), (4397, 6155, 6162, False, 0.50)],
  ESCURO=[2, 4], CLARAO=['card', 'card_fim', 5], ),
}[K]

ws = [[CFG['FIX'].get(k, w), t, k] for p in P['pecas'] for w, t, k in p['ws_o']]
tk = {k: [w, round(t, 3)] for w, t, k in ws}
W = json.load(open(G / 'words.json'))
def fim(k):  # fim da palavra k no vídeo final
    return tk[k][1] + (W[k][2] - W[k][1])
def faixa(tok):
    serif = tok.endswith('*'); tok = tok.rstrip('*')
    a, _, b = tok.partition('-'); return list(range(int(a), int(b or a) + 1)), serif

out = []
for linha in CFG['PAG'].splitlines():
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
o0 = [p['o0'] for p in P['pecas']] + [P['dur']]

# cartões digitados
cards = []
for c in CFG['CARD']:
    linhas = []
    for f in c['linhas']:
        ks, _ = faixa(f); linhas.append([[tk[k][0].strip(',.:;'), tk[k][1], fim(k)] for k in ks])
        # pontuação final da linha volta no último caractere
        last = tk[ks[-1]][0]
        if last[-1] in '.:,': linhas[-1][-1][0] += last[-1]
    t0 = round(linhas[0][0][1] - 0.30, 3); t1 = round(fim(c['ate']) + 0.55, 3)
    prox = [p['o0'] for p in P['pecas'] if p['o0'] > tk[c['ate']][1]]
    if prox: t1 = round(min(t1, prox[0]), 3)          # o cartão sai no corte para o trecho seguinte
    if c['ate'] + 1 in tk and tk[c['ate'] + 1][1] > tk[c['ate']][1]: t1 = round(min(t1, tk[c['ate'] + 1][1] - 0.08), 3)  # e antes da próxima fala
    cards.append({'t0': t0, 't1': t1, 'linhas': linhas})
# o cartão fica no lugar da legenda: tira páginas que começam dentro dele
for c in cards:
    out = [o for o in out if not (c['t0'] - 0.05 <= o['linhas'][0][0][1] < c['t1'])]

# trocas
clarao = []
for x in CFG['CLARAO']:
    if x == 'card': clarao.append(cards[0]['t0'])
    elif x == 'card_fim': clarao.append(cards[0]['t1'])
    else: clarao.append(o0[x])
escuro = [[o0[k] - 0.9, o0[k], o0[k] + 1.0] for k in CFG['ESCURO']]

# imagens de apoio: recorte 9:16, câmera lenta se for curta, P&B opcional
(G / 'broll').mkdir(exist_ok=True)
brolls = []
for n, (vid, ka, kb, pb, xc) in enumerate(CFG['BROLL']):
    t0 = round(tk[ka][1] - 0.5, 3); t1 = round(fim(kb) + 0.6, 3); need = t1 - t0
    src = BR / f'{vid}.mp4'
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(src)], capture_output=True, text=True).stdout)
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(src)],
                                   capture_output=True, text=True).stdout.strip().split(','))
    lento = max(1.0, min(1.6, (need + 0.3) / max(0.1, d - 0.4)))
    cw = int(h * 9 / 16) // 2 * 2; cx = int(min(max(xc * w - cw / 2, 0), w - cw))
    vf = f"crop={cw}:{h}:{cx}:0,scale=1080:1920:flags=lanczos,setpts={lento:.3f}*PTS,fps=30" + (",hue=s=0" if pb else "") + ",setsar=1"
    dst = G / 'broll' / f'b{n}_{vid}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-ss', '0.2', '-i', str(src), '-t', f'{need:.3f}', '-vf', vf, '-an',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(dst)], check=True)
    brolls.append({'arq': str(dst), 't0': t0, 't1': t1, 'entra': 1.0, 'sai': 1.0})

r = {'dur': P['dur'], 'base': 'prep/base.mp4', 'voz': 'prep/voz.wav',
     'musica': '/tmp/work/c9/musica.wav', 'musica_abaixo_db': 7,
     'handle': {'nome': 'ALEXANDRE ALMEIDA', 'arroba': '@alexandrealmeida.ofc', 'foto': 'foto_alexandre.jpg'},
     'abre': 1.2, 'escuro': escuro, 'clarao': clarao, 'broll': brolls, 'cartoes': cards,
     'cta': {'texto': 'COMENTE<br>EU CREIO', 'dur': 2.6, 'escurece': 1.6},
     'paginas': out}
json.dump(r, open(G / 'roteiro.json', 'w'), ensure_ascii=False, indent=1)
print(K, 'dur', round(P['dur'], 2), 'o0', [round(x, 2) for x in o0])
print('cartões', [(c['t0'], c['t1'], [' '.join(w[0] for w in l) for l in c['linhas']]) for c in cards])
print('clarões', [round(x, 2) for x in clarao], 'escuro', escuro)
print('apoio', [(b['arq'].split('/')[-1], b['t0'], b['t1']) for b in brolls])
for o in out: print('  ' + ' / '.join(' '.join(p[0] + ('*' if len(p) > 2 else '') for p in l) for l in o['linhas']))
