"""Corte "Muda o teu ponto de vista" (Pr. Alexandre, Lagoinha Mauá): voz sem pausas, quadro vertical seguindo o pregador."""
import json, subprocess
import numpy as np
from pathlib import Path
G = Path('/tmp/work/a3'); OUT = G / 'prep'; OUT.mkdir(exist_ok=True)
W = json.load(open(G / 'words.json')); idx = dict(enumerate(W))
T = [((5517, 5539),),                                   # talvez do teu ponto de vista ... é o maior obstáculo
     ((5544, 5554),),                                   # eu quero te chamar atenção, muda o teu ponto de vista
     ((5094, 5121),),                                   # o exército de Saul ... como um gigante
     ((5139, 5173),),                                   # só que quando chega Davi ... oportunidade de Deus ser glorificado e exaltado
     ((5244, 5254), (5276, 5286)),                      # André ... cinco pães e dois peixes ... como é que vai sustentar 10 mil pessoas
     ((5305, 5330),),                                   # mas do ponto de vista de Jesus era matéria-prima ... milagre de Deus
     ((5343, 5356),),                                   # você lembra daqueles dez espias ... terra de Canaã
     ((5401, 5426), 'pb'),                              # Moisés, não dá para entrar ... somos como gafanhotos
     ((5445, 5457),),                                   # mas para Josué e Calebe ... era oportunidade
     ((5556, 5581),)]                                   # a maior oportunidade de Deus ser glorificado na tua vida ... sobrenatural existir, aleluia
SR = 44100
A0, A1 = 1880.0, 2080.0   # janela da fonte usada
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(A0), '-t', str(A1 - A0), '-i', str(G / 'src.mp4'), '-map', '0:a:0', '-vn', '-ac', '2', '-ar', str(SR), str(G / 'janela.wav')], check=True)
if not list((G / 'sepj').glob('*Vocals*.wav')):
    subprocess.run(['audio-separator', str(G / 'janela.wav'), '-m', 'UVR-MDX-NET-Voc_FT.onnx', '--model_file_dir', '/tmp/work/models', '--output_dir', str(G / 'sepj'),
                    '--single_stem', 'Vocals', '--output_format', 'WAV'], check=True, capture_output=True)
V = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(next((G / 'sepj').glob('*Vocals*.wav'))), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                                 capture_output=True).stdout, np.float32).reshape(-1, 2)
mono = np.abs(V).mean(1); hop = SR // 100
rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, 'same'))[::hop]
THR = np.percentile(rms, 95) * 0.12
voz = rms > np.percentile(rms, 95) * 0.05  # silêncio de verdade: abaixo de -26 dB
sm = np.convolve(rms, np.ones(5) / 5, 'same')
def q(t): return not voz[min(len(voz) - 1, max(0, int((t - A0) * 100)))]
def limites(i, j):
    """começo e fim pelo ponto mais quieto entre as palavras (o Whisper erra as bordas)"""
    a, b = idx[i][1], idx[j][2]
    ant = idx[i - 1][2]; prox = idx[j + 1][1]
    def vale(x0, x1):
        k0, k1 = int((x0 - A0) * 100), max(int((x0 - A0) * 100) + 1, int((x1 - A0) * 100))
        seg = sm[k0:k1]; return A0 + (k0 + int(np.argmin(seg))) / 100, seg.min()
    # fim: primeiro silêncio de verdade depois da última palavra; se ele emenda a próxima, o vale entre as duas
    t = b - 0.05; e = None
    while t < b + 0.7:
        if all(q(t + k / 100) for k in range(4)): e = t + 0.08; break
        t += 0.01
    if e is None: e = vale(b - 0.08, max(prox + 0.25, b + 0.15))[0] + 0.01
    t = a + 0.03; s = None
    while t > a - 0.6:
        if all(q(t - k / 100) for k in range(1, 5)): s = t - 0.06; break
        t -= 0.01
    if s is None: s = vale(min(ant - 0.2, a - 0.15), a + 0.05)[0]
    return round(s, 3), round(e, 3)
def sem_pausas(a, b, minimo=0.30, margem=0.12):
    i0, i1 = int((a - A0) * 100), int((b - A0) * 100); v = voz[i0:i1]
    out, ini, k = [], a, 0
    while k < len(v):
        if not v[k]:
            k2 = k
            while k2 < len(v) and not v[k2]: k2 += 1
            if (k2 - k) / 100 >= minimo:
                if k == 0: ini = A0 + (i0 + k2) / 100 - margem
                elif k2 >= len(v): b = A0 + (i0 + k) / 100 + margem + 0.05
                else: out.append([ini, A0 + (i0 + k) / 100 + margem]); ini = A0 + (i0 + k2) / 100 - margem
            k = k2
        else: k += 1
    out.append([ini, b])
    return [[round(x, 3), round(y, 3)] for x, y in out if y - x > 0.08]
OVS = json.load(open(G / 'ovs.json')) if (G / 'ovs.json').exists() else {}
# posição do pregador (camisa preta = parte mais escura da faixa do tronco), 4 quadros/s na janela
if not (G / 'xs.npy').exists():
    w, h = 480, 270
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(A0), '-t', str(A1 - A0), '-i', str(G / 'src.mp4'), '-map', '0:v:0', '-vf', f'fps=4,scale={w}:{h}',
                          '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)
    xs = [np.argmax(np.convolve((f[90:170] < 38).sum(0).astype(float), np.ones(30) / 30, 'same')) / w for f in F]
    np.save(G / 'xs.npy', np.array(xs))
xs = np.load(G / 'xs.npy')
def xm(a, b):
    v = xs[int((a - A0) * 4):max(int((a - A0) * 4) + 1, int((b - A0) * 4))]
    return float(np.median(v))
pecas, out = [], 0.0
for n, tr in enumerate(T):
    ef = tr[-1] if isinstance(tr[-1], str) else ''
    faixas = [x for x in tr if not isinstance(x, str)]
    quadro = 'aberto' if n % 2 == 0 else 'fechado'
    subs, ws = [], []
    for (i, j) in faixas:
        s_, e_ = limites(i, j)
        o_ = OVS.get(f'{i}-{j}', [None, None]); s_ = o_[0] or s_; e_ = o_[1] or e_
        partes_ = sem_pausas(s_, e_)
        for k in range(i, j + 1):
            tw = idx[k][1]; base = out + sum(b - a for a, b in subs); acc = 0.0; tt = None
            for a, b in partes_:
                if tw < b: tt = base + acc + max(tw - a, 0.0); break
                acc += b - a
            if tt is None: tt = base + acc - 0.05
            ws.append([idx[k][0], round(max(tt, out + 0.02), 3), k])
        subs += partes_
    pecas.append({'n': n, 'pb': ef, 'quadro': quadro, 'subs': subs, 'o0': round(out, 3), 'ws_o': ws})
    print(f"{n:2} {quadro:7} {ef:3} out {out:6.2f} | " + ' '.join(w[0] for w in ws))
    out += sum(b - a for a, b in subs)
DUR = out; print('duração', round(DUR, 2))
partes = []; f = int(0.012 * SR)
for p in pecas:
    for a_, b_ in p['subs']:
        seg = V[int((a_ - A0) * SR):int((b_ - A0) * SR)].copy()
        seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]; partes.append(seg)
(OUT / 'voz.f32').write_bytes(np.concatenate(partes).astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(OUT / 'voz.f32'), '-af',
                'highpass=f=80,afftdn=nf=-30:nr=8,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=8',
                '-ar', '48000', str(OUT / 'voz.wav')], check=True)
segs = [(a_, b_, p) for p in pecas for a_, b_ in p['subs']]
fc = ['[0:v:0]fps=30,split=%d%s' % (len(segs), ''.join(f'[s{k}]' for k in range(len(segs))))]
for k, (a_, b_, p) in enumerate(segs):
    cw, ch = (608, 1080) if p['quadro'] == 'aberto' else (500, 888)
    cx = int(min(max(xm(p['subs'][0][0], p['subs'][-1][1]) * 1920 - cw / 2, 0), 1920 - cw))
    pb = ',hue=s=0' if p['pb'] == 'pb' else ''
    fc.append(f"[s{k}]trim={a_ - A0:.3f}:{b_ - A0:.3f},setpts=PTS-STARTPTS,crop={cw}:{ch}:{cx}:0,scale=1080:1920:flags=lanczos{pb},setsar=1[v{k}]")
fc.append(''.join(f'[v{k}]' for k in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0[vo]')
(OUT / 'fc.txt').write_text(';'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(A0), '-t', str(A1 - A0), '-i', str(G / 'src.mp4'), '-filter_complex_script', str(OUT / 'fc.txt'),
                '-map', '[vo]', '-an', '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / 'base.mp4')], check=True)
json.dump({'dur': DUR, 'pecas': pecas}, open(OUT / 'pecas.json', 'w'), ensure_ascii=False)
print('ok')
