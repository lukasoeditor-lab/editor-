"""EXEMPLO (caminhos fixos do corte 3, Ana): bordas por palavra + vale de energia da voz, pausa de leitura nos cartões, nitidez, enquadramento. Adapte os caminhos e a lista PECAS."""
import json, subprocess, sys, glob, re
import numpy as np
from pathlib import Path
W0 = Path('/tmp/work/n2'); E1 = W0 / 'e1'
OUT = E1 / 'prep2'; OUT.mkdir(exist_ok=True)
W = json.load(open(W0 / 'story_flat.json'))          # [palavra, início, fim]
CROP0 = 44.45

# (nome, tipo v=vídeo c=cartão, início da 1ª palavra, início da última palavra)
PECAS = [
 ("H1", "v", 148.50, 152.55), ("H2a", "v", 154.60, 164.90), ("H2b", "c", 165.05, 169.00),
 ("C1a", "c", 50.60, 54.80), ("C1c", "v", 63.80, 80.50), ("Q1", "c", 80.55, 84.60),
 ("Q3", "v", 98.05, 102.85), ("N1", "c", 120.25, 123.20), ("N2", "v", 125.00, 128.55),
 ("A1", "c", 177.40, 183.50), ("A2b", "c", 198.10, 203.30),
 ("A2c", "v", 208.15, 212.20), ("A2d", "v", 212.50, 217.20),
 ("R1", "c", 297.40, 300.85), ("R3", "v", 314.30, 317.20),
 ("R4v", "v", 358.85, 360.50), ("R4", "c", 360.60, 363.80), ("R5", "c", 375.15, 376.95),
 ("R6v", "v", 389.00, 394.20), ("R6", "c", 394.20, 396.10),
]

# ---- voz isolada (tempo da fonte = CROP0 + t) ----
voz = glob.glob(str(W0 / 'sep/out/*Vocals*.wav'))[0]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', voz, '-f', 'f32le', '-ac', '2', '-ar', '44100', '-'], capture_output=True).stdout
V = np.frombuffer(raw, np.float32).reshape(-1, 2); SR = 44100
mono = np.abs(V).mean(1)
hop = int(SR * 0.01)
rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, 'same'))[::hop]   # 10 ms
THR = np.percentile(rms, 95) * 0.07
print('limiar de voz', THR)
def R(t): return rms[int((t - CROP0) * 100)]
def voz_em(t): return R(t) > THR

def palavras(a, b): return [w for w in W if a - 0.001 <= w[1] <= b + 0.001]

def achar_fim(ult):
    """ponto mais quieto perto do fim da última palavra (vale de energia): corta ali, nunca no meio da sílaba"""
    prox = [w for w in W if w[1] > ult[1]]
    a = ult[2] - 0.12
    b = min(ult[2] + 0.40, (prox[0][1] + 0.12) if prox else 1e9)
    b = max(b, a + 0.1)
    idx = np.arange(int((a - CROP0) * 100), int((b - CROP0) * 100))
    v = np.convolve(rms[idx], np.ones(3) / 3, 'same')
    j = int(np.argmin(v))
    if v[j] > THR * 4: print('   (sem vale claro depois de', ult[0], ')')
    return CROP0 + (idx[j] + 1) / 100

def achar_ini(prim):
    """começo do trecho: 0,12 s antes da 1ª palavra se ali já está quieto; senão o ponto mais quieto antes dela"""
    s0 = prim[1] - 0.12
    if all(R(s0 + k * 0.01) < THR * 2 for k in (-2, -1, 0, 1, 2)):
        return s0
    idx = np.arange(int((prim[1] - 0.30 - CROP0) * 100), int((prim[1] + 0.03 - CROP0) * 100))
    v = np.convolve(rms[idx], np.ones(3) / 3, 'same')
    j = int(np.argmin(v))
    if v[j] > THR * 4: print('   (sem vale claro antes de', prim[0], ')')
    return CROP0 + idx[j] / 100

def txt_len(ws): return len(' '.join(w[0] for w in ws))

pecas = []
for nome, kind, a, b in PECAS:
    ws = palavras(a, b)
    ini = achar_ini(ws[0])
    fim_fala = achar_fim(ws[-1])
    if fim_fala is None:
        print('!! sem silêncio depois de', nome, ws[-1]); fim_fala = ws[-1][2]
    seg = {'nome': nome, 'kind': kind, 'ws': ws, 's': round(ini, 3), 'fim_fala': round(fim_fala, 3)}
    pecas.append(seg)

# fim do trecho = fim da fala + folga; não passa do começo da próxima palavra da fonte
for i, p in enumerate(pecas):
    prox = [w for w in W if w[1] > p['ws'][-1][1]]
    lim = prox[0][1] - 0.03 if prox else p['fim_fala'] + 1
    folga = 0.30 if p['kind'] == 'c' else 0.55
    p['e'] = round(max(p['fim_fala'], min(p['fim_fala'] + folga, lim)), 3)
# trechos que continuam um no outro na fonte (fim == começo da seguinte): emenda sem repetir nem pular áudio
for p, q in zip(pecas, pecas[1:]):
    if q['s'] < p['e'] and q['ws'][0][1] > p['ws'][-1][1] and q['ws'][0][1] - p['ws'][-1][2] < 1.0:
        meio = round((p['e'] + q['s']) / 2, 3)
        p['e'] = meio; q['s'] = meio
# pausa de leitura nos cartões: só texto na tela, a voz para (a música segue)
for p in pecas:
    p['pausa'] = 0.0
    if p['kind'] == 'c':
        txt = ' '.join(w[0] for w in p['ws'])
        precisa = 0.6 + len(txt) / 17.0
        falado = p['e'] - p['s']
        p['pausa'] = round(min(2.2, max(0.8, precisa - falado)), 2)
ult = pecas[-1]; ult['pausa'] = max(ult['pausa'], 1.2)
for p in pecas:
    print(f"  1a palavra {p['ws'][0][1]:.2f}", end=' ')
    print(f"{p['nome']:4} {p['kind']} {p['s']:7.2f}-{p['e']:7.2f} (fala até {p['fim_fala']:.2f}) pausa {p['pausa']:.2f} | " + ' '.join(w[0] for w in p['ws'])[:70])

segs = [[p['s'], p['e']] for p in pecas]
pausas = [p['pausa'] for p in pecas]
dur = sum(b - a + q for (a, b), q in zip(segs, pausas))
print('duração', round(dur, 1))

# ---- voz nova: trechos com fade de 15 ms + silêncio da pausa ----
partes = []
for (a, b), q in zip(segs, pausas):
    i0, i1 = int((a - CROP0) * SR), int((b - CROP0) * SR)
    seg = V[i0:i1].copy()
    f = int(0.015 * SR)
    seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]
    partes.append(seg)
    if q > 0: partes.append(np.zeros((int(q * SR), 2), np.float32))
cola = np.concatenate(partes)
(OUT / 'voz_colada.f32').write_bytes(cola.astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '44100', '-ac', '2', '-i', str(OUT / 'voz_colada.f32'),
                '-af', 'highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=9', '-ar', '48000', str(OUT / 'voz.wav')], check=True)

# ---- vídeo: câmera segue o paletó, enquadramento mais alto, nitidez ----
xs = list(np.load(E1 / 'xs.npy'))
WF, HF = 1280, 720
ZOOM, YPOS = 1.35, 0.40
hc = int(round(HF / ZOOM / 2)) * 2; wc = int(round(hc * 1080 / 1920 / 2)) * 2; yc = int(round((HF - hc) * YPOS))
folga = 0.5 * (wc / WF) * 0.28
c, cam_x = xs[0], []
for x in xs:
    if x > c + folga: c = x - folga
    elif x < c - folga: c = x + folga
    cam_x.append(c)
k = np.exp(-0.5 * (np.arange(-6, 7) / 1.2) ** 2); k /= k.sum()
suave = np.convolve(np.pad(cam_x, 6, mode='edge'), k, mode='valid')
n = len(segs); partes = []
for i, ((s_, e_), q) in enumerate(zip(segs, pausas)):
    i0, i1 = int((s_ - CROP0) * 2), min(len(suave) - 1, int((e_ - CROP0) * 2) + 1)
    pts = [(idx / 2.0 - (s_ - CROP0), float(min(max(suave[idx] * WF - wc / 2, 0), WF - wc))) for idx in range(i0, i1 + 1)]
    ex = f"{pts[-1][1]:.1f}"
    for (ta, xa), (tb, xb) in reversed(list(zip(pts[:-1], pts[1:]))):
        ex = f"if(lt(t,{tb:.2f}),{xa:.1f}+({xb - xa:.1f})*(t-{ta:.2f})/{max(tb - ta, 0.01):.2f},{ex})"
    pad = f",tpad=stop_mode=clone:stop_duration={q:.2f}" if q > 0 else ""
    partes.append(f"[fps{i}]trim={s_ - CROP0:.3f}:{e_ - CROP0:.3f},setpts=PTS-STARTPTS,crop={wc}:{hc}:x='{ex}':y={yc},"
                  f"hqdn3d=2:1.5:3:3,scale=1080:1920:flags=lanczos,unsharp=7:7:1.1:5:5:0.0,eq=contrast=1.05:saturation=1.08{pad}[v{i}]")
fc = ("[0:v]fps=30[fps0];[fps0]split=" + str(n) + "".join(f"[fps{i}]" for i in range(n)) + ";" + ";".join(partes) + ";"
      + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vo]")
(OUT / 'fc.txt').write_text(fc)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(CROP0), '-t', '360', '-i', str(W0 / 'src.mp4'), '-filter_complex_script', str(OUT / 'fc.txt'),
                '-map', '[vo]', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / 'base.mp4')], check=True)
json.dump({'dur': dur, 'segs': segs, 'pausas': pausas, 'crop0': CROP0, 'largura': 1080, 'altura': 1920}, open(OUT / 'info.json', 'w'))
json.dump([{k: v for k, v in p.items()} for p in pecas], open(OUT / 'pecas.json', 'w'), ensure_ascii=False)
print('ok', OUT)
