"""Depoimento "estourei minha bolha": gancho no começo, voz sem pausas, quadro vertical aberto/fechado, P&B na dúvida."""
import json, subprocess
import numpy as np
from pathlib import Path
G = Path('/tmp/work/s6'); OUT = G / 'prep'; OUT.mkdir(exist_ok=True)
W = json.load(open(G / 'words.json')); idx = dict(enumerate(W))
# (primeira palavra, última, efeito) na ordem do vídeo final
T = [((0, 3), (4, 7)), ((8, 21),), ((22, 26),), ((27, 47), 'pb'), ((48, 58), 'pb'), ((59, 63),), ((64, 69),), ((70, 84),),
     ((85, 98),), ((99, 109),), ((110, 119),), ((122, 128),), ((129, 135),), ((136, 139),), ((143, 150),),
     ((151, 163),), ((164, 168),), ((175, 176),), ((177, 183),)]
SR = 44100
V = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(G / 'sep/voz_Vocals.wav'), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                                 capture_output=True).stdout, np.float32).reshape(-1, 2)
mono = np.abs(V).mean(1); hop = SR // 100
rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, 'same'))[::hop]
THR = np.percentile(rms, 95) * 0.12
voz = rms > THR
def q(t): return not voz[min(len(voz) - 1, max(0, int(t * 100)))]
def limites(i, j):
    a, b = idx[i][1], idx[j][2]
    ant = idx[i - 1][2] if i > 0 else 0
    prox = idx[j + 1][1] if j + 1 in idx else b + 1.0
    t = a + 0.04
    while t > max(ant, a - 0.5) and not all(q(t - k / 100) for k in range(1, 7)): t -= 0.01
    s = max(t - 0.02, ant - 0.0)
    t = b - 0.05
    while t < min(prox, b + 0.6) and not all(q(t + k / 100) for k in range(6)): t += 0.01
    e = min(t + 0.04, prox - 0.02)
    return round(s, 3), round(e, 3)
# rosto (x, fração da largura) segundo a segundo, medido nos quadros
FACE = [0.62]*3 + [0.58]*3 + [0.58]*3 + [0.54]*3 + [0.54]*3 + [0.58]*3 + [0.54]*3 + [0.54]*3 + [0.58]*12 + [0.5]*9 + [0.46]*3 + [0.54]*3 + [0.58]*3 + [0.45]*3
def fx(a, b): return float(np.median([FACE[min(len(FACE) - 1, int(x))] for x in np.arange(a, max(b, a + 0.6), 0.5)]))
def sem_pausas(a, b, minimo=0.24, margem=0.07):
    """tira os silêncios internos de 0,24 s ou mais (fica 0,07 s de cada lado)"""
    i0, i1 = int(a * 100), int(b * 100); v = voz[i0:i1]
    out, ini, k = [], a, 0
    while k < len(v):
        if not v[k]:
            k2 = k
            while k2 < len(v) and not v[k2]: k2 += 1
            if (k2 - k) / 100 >= minimo:
                if k == 0: ini = (i0 + k2) / 100 - margem          # silêncio no começo
                elif k2 >= len(v): b = (i0 + k) / 100 + margem + 0.05  # silêncio no fim (rabo curto)
                else: out.append([ini, (i0 + k) / 100 + margem]); ini = (i0 + k2) / 100 - margem
            k = k2
        else: k += 1
    out.append([ini, b])
    return [[round(x, 3), round(y, 3)] for x, y in out if y - x > 0.08]
OVS = {(143, 150): (43.70, None), (175, 176): (54.55, None), (177, 183): (None, 57.10), (110, 119): (None, 35.34)}  # conferidos na energia
pecas, out = [], 0.0
for n, tr in enumerate(T):
    ef = tr[-1] if isinstance(tr[-1], str) else ''
    faixas = [x for x in tr if not isinstance(x, str)]
    quadro = 'fechado' if n % 2 == 1 else 'aberto'
    subs, ws = [], []
    for (i, j) in faixas:
        s_, e_ = limites(i, j)
        o_ = OVS.get((i, j), (None, None)); s_ = o_[0] or s_; e_ = o_[1] or e_
        partes_ = sem_pausas(s_, e_)
        for k in range(i, j + 1):
            tw = idx[k][1]; base = out + sum(b - a for a, b in subs); acc = 0.0; tt = None
            for a, b in partes_:
                if tw < b: tt = base + acc + max(tw - a, 0.0); break
                acc += b - a
            if tt is None: tt = base + acc - 0.05
            ws.append([idx[k][0], round(max(tt, out + 0.02), 3), k])
        subs += partes_
    pecas.append({'n': n, 'pb': ef, 'quadro': quadro, 'subs': subs, 'o0': round(out, 3), 'ws_o': ws, 'x': fx(subs[0][0], subs[-1][1])})
    print(f"{n:2} {quadro:7} {ef:3} {subs} out {out:6.2f} | " + ' '.join(w[0] for w in ws))
    out += sum(b - a for a, b in subs)
DUR = out; print('duração', round(DUR, 2))
partes = []; f = int(0.012 * SR)
for p in pecas:
  for a_, b_ in p['subs']:
    seg = V[int(a_ * SR):int(b_ * SR)].copy()
    seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]; partes.append(seg)
(OUT / 'voz.f32').write_bytes(np.concatenate(partes).astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(OUT / 'voz.f32'), '-af',
                'highpass=f=80,afftdn=nf=-30:nr=8,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=8',
                '-ar', '48000', str(OUT / 'voz.wav')], check=True)
segs = [(a_, b_, p) for p in pecas for a_, b_ in p['subs']]
fc = ['[0:v]fps=30,split=%d%s' % (len(segs), ''.join(f'[s{k}]' for k in range(len(segs))))]
for k, (a_, b_, p) in enumerate(segs):
    if p['quadro'] == 'aberto':
        cr = 'scale=1080:1920:flags=lanczos'
    else:
        cw, ch = 1556, 2766
        cx = int(min(max(p['x'] * 2160 - cw / 2, 0), 2160 - cw))
        cr = f'crop={cw}:{ch}:{cx}:728,scale=1080:1920:flags=lanczos'
    pb = ',hue=s=0' if p['pb'] == 'pb' else ''
    fc.append(f"[s{k}]trim={a_:.3f}:{b_:.3f},setpts=PTS-STARTPTS,{cr}{pb},setsar=1[v{k}]")
fc.append(''.join(f'[v{k}]' for k in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0[vo]')
(OUT / 'fc.txt').write_text(';'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(G / 'src.mp4'), '-filter_complex_script', str(OUT / 'fc.txt'), '-map', '[vo]', '-an',
                '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / 'base.mp4')], check=True)
json.dump({'dur': DUR, 'pecas': pecas}, open(OUT / 'pecas.json', 'w'), ensure_ascii=False)
print('ok')
