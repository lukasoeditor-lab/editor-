"""Depoimento "estourei minha bolha": gancho no começo, voz sem pausas, quadro vertical aberto/fechado, P&B na dúvida."""
import json, subprocess
import numpy as np
from pathlib import Path
G = Path('/tmp/work/b1'); OUT = G / 'prep'; OUT.mkdir(exist_ok=True)
W = json.load(open(G / 'words.json')); idx = dict(enumerate(W))
# (primeira palavra, última, efeito) na ordem do vídeo final
T = [(26, 38, ''),            # GANCHO: mas tudo isso foi capaz quando eu tomei a decisão, estourei minha bolha
     (0, 5, ''),              # e ali estava com um sonho
     (10, 19, 'pb'),          # pô, será que um dia eu vou ter uma barbearia
     (20, 24, 'pb'),          # será que eu vou conseguir
     (39, 42, ''),            # e vou fazer acontecer
     (48, 50, ''),            # vendi a moto
     (51, 57, ''),            # minha noiva ali trabalhando, lixou lá tudinho
     (58, 63, ''),            # fez o espaço para conseguir chegar
     (64, 68, '')]            # conhecer esses caras aqui, ó
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
FACE = [0.78, 0.62, 0.60, 0.77, 0.80, 0.75, 0.72, 0.73, 0.77, 0.71, 0.75, 0.72, 0.73, 0.81, 0.72, 0.66, 0.60, 0.48, 0.52, 0.66, 0.66, 0.47, 0.48, 0.49, 0.62]
def fx(a, b): return float(np.median([FACE[min(len(FACE) - 1, int(x))] for x in np.arange(a, b, 0.5)]))
pecas, out = [], 0.0
for n, (i, j, ef) in enumerate(T):
    s, e = limites(i, j)
    if i == 26: s = max(s, idx[25][2] + 0.03); e = 11.20  # "bolha" vai até 11,1 (o "e" do Whisper só começa em 11,9)
    if i == 39: s = 11.84
    quadro = 'fechado' if n % 2 == 0 else 'aberto'
    ws = [[idx[k][0], round(out + idx[k][1] - s, 3)] for k in range(i, j + 1)]
    pecas.append({'n': n, 'pb': ef, 'quadro': quadro, 's': s, 'e': e, 'o0': round(out, 3), 'ws_o': ws, 'x': fx(s, e), 'i': i, 'j': j})
    print(f"{n} {quadro:7} {ef:3} {s:6.2f}-{e:6.2f} out {out:6.2f} | " + ' '.join(idx[k][0] for k in range(i, j + 1)))
    out += e - s
DUR = out; print('duração', round(DUR, 2))
partes = []; f = int(0.012 * SR)
for p in pecas:
    seg = V[int(p['s'] * SR):int(p['e'] * SR)].copy()
    seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]; partes.append(seg)
(OUT / 'voz.f32').write_bytes(np.concatenate(partes).astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(OUT / 'voz.f32'), '-af',
                'highpass=f=80,afftdn=nf=-30:nr=8,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=8',
                '-ar', '48000', str(OUT / 'voz.wav')], check=True)
fc = ['[0:v]fps=30,split=%d%s' % (len(pecas), ''.join(f'[s{k}]' for k in range(len(pecas))))]
for k, p in enumerate(pecas):
    if p['quadro'] == 'aberto':
        cr = 'scale=1080:1920:flags=lanczos'
    else:
        cw, ch = 1556, 2766
        cx = int(min(max(p['x'] * 2160 - cw / 2, 0), 2160 - cw))
        cr = f'crop={cw}:{ch}:{cx}:0,scale=1080:1920:flags=lanczos'
    pb = ',hue=s=0' if p['pb'] == 'pb' else ''
    fc.append(f"[s{k}]trim={p['s']:.3f}:{p['e']:.3f},setpts=PTS-STARTPTS,{cr}{pb},setsar=1[v{k}]")
fc.append(''.join(f'[v{k}]' for k in range(len(pecas))) + f'concat=n={len(pecas)}:v=1:a=0[vo]')
(OUT / 'fc.txt').write_text(';'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(G / 'src.mp4'), '-filter_complex_script', str(OUT / 'fc.txt'), '-map', '[vo]', '-an',
                '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / 'base.mp4')], check=True)
json.dump({'dur': DUR, 'pecas': pecas}, open(OUT / 'pecas.json', 'w'), ensure_ascii=False)
print('ok')
