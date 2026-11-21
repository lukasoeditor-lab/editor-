"""Corte 'O que é fé' (Pr. Alexandre Almeida) no estilo correria: voz sem pausas, quadro vertical que
alterna aberto/fechado, P&B nas citações, roteiro para gerar_correria.py."""
import json, subprocess
import numpy as np
from pathlib import Path
G = Path('/tmp/work/c1'); OUT = G / 'prep'; OUT.mkdir(exist_ok=True)
W = json.load(open(G / 'words.json'))
W = [w for i, w in enumerate(W) if not (226 <= i <= 231)]  # o Whisper duplicou "eu creio que Deus vai fazer"
W0 = json.load(open(G / 'words.json'))
idx = {i: w for i, w in enumerate(W0)}

# trechos por índice de palavra (da transcrição original); pb = citação (P&B + legenda amarela)
T = [(0, 7), (8, 12), (13, 17), (18, 26), (27, 40), (41, 48), (49, 53), (54, 70), (71, 76), (77, 80), (81, 86),
     (87, 101, 'pb'), (102, 110), (112, 115), (116, 124), (125, 140, 'pb'), (141, 144), (145, 156), (157, 157),
     (158, 165), (166, 189), (190, 199), (200, 205), (206, 219), (220, 225, 'pb'), (232, 243), (244, 244),
     (245, 254), (255, 259), (260, 263), (264, 283, 'pb')]

SR = 44100
V = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(G / 'sep/voz_Vocals.wav'), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                                 capture_output=True).stdout, np.float32).reshape(-1, 2)
mono = np.abs(V).mean(1); hop = SR // 100
rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, 'same'))[::hop]
THR = np.percentile(rms, 95) * 0.15
voz = rms > THR


def regioes(a, b):
    """trechos com voz entre a e b; silêncios internos de 0,2 s ou mais saem (fica 0,06 s de cada lado)"""
    i0, i1 = int(a * 100), int(b * 100)
    v = voz[i0:i1].copy()
    segs, s, quieto = [], None, 0
    for k, on in enumerate(v):
        if on:
            if s is None: s = k
            quieto = 0
        elif s is not None:
            quieto += 1
            if quieto >= 16:
                segs.append([s, k - quieto + 1]); s = None; quieto = 0
    if s is not None: segs.append([s, len(v)])
    out = []
    for s, e in segs:
        if e - s < 5: continue  # estalo
        out.append([(i0 + s) / 100 - 0.06, (i0 + e) / 100 + 0.10])
    for p, q in zip(out, out[1:]):  # sem sobrepor
        if q[0] < p[1]: m = (p[1] + q[0]) / 2; p[1] = m; q[0] = m
    return out


def limites(i, j):
    """da 1ª à última palavra do trecho, procurando o silêncio real em volta"""
    a = idx[i][1]; b = idx[j][2]
    prox = idx[j + 1][1] if j + 1 in idx else b + 1.0
    if j + 1 in idx and 226 <= j + 1 <= 231: prox = idx[232][1]
    ant = idx[i - 1][2] if i > 0 else 0
    # recua até achar 80 ms de silêncio (sem passar do fim da palavra anterior)
    t = a + 0.05
    while t > max(ant, a - 0.6) and not all(not voz[int(t * 100) - k] for k in range(1, 9)): t -= 0.01
    s = max(t - 0.03, ant)
    t = b - 0.05
    while t < min(prox, b + 0.8) and not all(not voz[int(t * 100) + k] for k in range(8)): t += 0.01
    e = min(t + 0.02, prox - 0.02)
    return s, e


# enquadramento: x do pregador (4 qps), recorte 9:16
xs = np.load(G / 'xs.npy')
def x_med(a, b):
    v = xs[int(a * 4):max(int(a * 4) + 1, int(b * 4))]
    return float(np.median(v))
QUADROS = {'aberto': (608, 1080, 0), 'fechado': (468, 832, 0)}

pecas, out_t = [], 0.0
for n, tr in enumerate(T):
    i, j = tr[0], tr[1]; pb = len(tr) > 2
    s, e = limites(i, j)
    subs = regioes(s, e)
    subs[0][0] = max(subs[0][0], s); subs[-1][1] = min(subs[-1][1], e) if subs[-1][1] > e else subs[-1][1]
    ws = [idx[k] for k in range(i, j + 1) if not (226 <= k <= 231)]
    quadro = 'aberto' if n % 2 == 0 else 'fechado'
    pecas.append({'n': n, 'pb': pb, 'quadro': quadro, 'subs': subs, 'ws': ws, 'x': x_med(s, e)})

# trechos colados na fonte: nunca sobrepor (senão o áudio repete)
for p, q in zip(pecas, pecas[1:]):
    if q['subs'][0][0] < p['subs'][-1][1]:
        m = round((p['subs'][-1][1] + q['subs'][0][0]) / 2, 3); p['subs'][-1][1] = m; q['subs'][0][0] = m
# mapa fonte → saída
def planos(a, b):
    """divide [a,b] quando o pregador se afasta do centro do quadro: corte seco para um quadro novo centrado nele"""
    k0, k1 = int(a * 4), max(int(a * 4) + 1, int(b * 4))
    v = xs[k0:k1]; cortes = [a]; ini = 0
    for k in range(2, len(v)):
        c = np.median(v[ini:k])
        if k - ini >= 4 and np.all(np.abs(v[k - 2:k + 1] - c) > 0.06): cortes.append(a + k / 4.0 - 0.5); ini = k - 2
    cortes.append(b)
    return [(cortes[i], cortes[i + 1], float(np.median(xs[int(cortes[i] * 4):max(int(cortes[i] * 4) + 1, int(cortes[i + 1] * 4))])))
            for i in range(len(cortes) - 1) if cortes[i + 1] - cortes[i] > 0.3]
segs = []
for p in pecas:
    for a, b in p['subs']:
        pl = planos(a, b) or [(a, b, p['x'])]
        pl[0] = (a, pl[0][1], pl[0][2]); pl[-1] = (pl[-1][0], b, pl[-1][2])
        for a2, b2, x2 in pl:
            segs.append({'a': a2, 'b': b2, 'pb': p['pb'], 'quadro': p['quadro'], 'x': x2, 'n': p['n'], 'o': out_t})
            out_t += b2 - a2
DUR = out_t
def mapa(t):
    for s in segs:
        if s['a'] - 0.001 <= t <= s['b'] + 0.001: return s['o'] + (t - s['a'])
    best = min(segs, key=lambda s: min(abs(t - s['a']), abs(t - s['b'])))
    return best['o'] if abs(t - best['a']) < abs(t - best['b']) else best['o'] + best['b'] - best['a']
for p in pecas:
    p['o0'] = segs[[k for k, s in enumerate(segs) if s['n'] == p['n']][0]]['o']
    p['ws_o'] = [[w[0], round(mapa(w[1]), 3)] for w in p['ws']]
    print(f"{p['n']:2} {p['quadro']:7} {'PB' if p['pb'] else '  '} {p['o0']:6.2f} x={p['x']:.2f} {len(p['subs'])} subs | " + ' '.join(w[0] for w in p['ws']))
print('duração', round(DUR, 2))

# voz
partes = []
f = int(0.012 * SR)
for a_, b_ in [ab for p in pecas for ab in p['subs']]:  # voz pelos trechos (os recortes de câmera não mexem no som)
    seg = V[int(a_ * SR):int(b_ * SR)].copy()
    seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]
    partes.append(seg)
(OUT / 'voz.f32').write_bytes(np.concatenate(partes).astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(OUT / 'voz.f32'), '-af',
                'highpass=f=80,afftdn=nf=-30:nr=8,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=8',
                '-ar', '48000', str(OUT / 'voz.wav')], check=True)

# vídeo: recorte fixo por trecho (centro no pregador), P&B nas citações, sem nitidez nem cor
fc = ['[0:v]fps=30,split=%d%s' % (len(segs), ''.join(f'[s{k}]' for k in range(len(segs))))]
for k, s in enumerate(segs):
    cw, ch, cy = QUADROS[s['quadro']]
    cx = int(min(max(s['x'] * 1920 - cw / 2, 0), 1920 - cw))
    pb = ',hue=s=0' if s['pb'] else ''
    fc.append(f"[s{k}]trim={s['a']:.3f}:{s['b']:.3f},setpts=PTS-STARTPTS,crop={cw}:{ch}:{cx}:{cy},scale=1080:1920:flags=lanczos{pb},setsar=1[v{k}]")
fc.append(''.join(f'[v{k}]' for k in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0[vo]')
(OUT / 'fc.txt').write_text(';'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(G / 'src.mp4'), '-filter_complex_script', str(OUT / 'fc.txt'), '-map', '[vo]', '-an',
                '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / 'base.mp4')], check=True)
json.dump({'dur': DUR, 'pecas': pecas}, open(OUT / 'pecas.json', 'w'), ensure_ascii=False)
print('ok')
