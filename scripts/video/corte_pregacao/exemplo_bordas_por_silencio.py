"""EXEMPLO (corte Cuidado, Pr. Alexandre): bordas pelo silêncio real da voz isolada, sem pausa de leitura, emendas contínuas no meio, crop vertical leve. Adapte os caminhos e a lista PECAS."""
import json, subprocess, glob
import numpy as np
from pathlib import Path
G = Path('/tmp/work/p1'); OUT = G / 'prep'; OUT.mkdir(exist_ok=True)
W = json.load(open(G / 'words.json'))
FIX = {"sopremos": "sofremos", "para": "para", "-brisa.": "-brisa."}

# (nome, tipo, início da 1ª palavra, início da última)
PECAS = [
    ("H", "v", 0.0, 5.44),      # Cuidado em passar 3 horas ao lado de alguém...
    ("A", "v", 16.62, 20.0),    # ...almoçando com a família e não estar olhando no celular.
    ("B", "c", 20.68, 23.98),   # ...conversando com o cônjuge, mas pensando no trabalho.
    ("C", "v", 24.78, 28.72),   # ...brincando com os filhos, mas preocupado com as contas.
    ("D", "v", 29.04, 32.96),   # Cuidado, cuidado de estar descansando, mas pensando nas tarefas de amanhã
    ("E", "c", 33.22, 38.92),   # Cuidado em estar diante de Deus, mas a mente ocupada com dezenas de preocupações
    ("F", "v", 39.66, 44.0),    # Cuidado, você está aqui dentro da igreja, mas com o seu pensamento lá fora
    ("G", "v", 44.32, 59.68),   # Passamos aqui duas horas ... em espírito. Aleluia, cuidado
    ("I", "c", 63.76, 67.0),    # Cuidado: ter uma Bíblia em casa, conhecer os versículos
    ("J", "v", 67.7, 68.76),    # frequentar a igreja
    ("K", "c", 69.3, 73.6),     # mas não desenvolver um tempo de qualidade para estar ouvindo a Deus.
    ("L", "c", 89.5, 89.5),     # Cuidado. (fecho)
]
voz = glob.glob(str(G / 'sep/*Vocals*.wav'))[0]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', voz, '-f', 'f32le', '-ac', '2', '-ar', '44100', '-'], capture_output=True).stdout
V = np.frombuffer(raw, np.float32).reshape(-1, 2); SR = 44100
mono = np.abs(V).mean(1); hop = int(SR * 0.01)
rms = np.sqrt(np.convolve(mono ** 2, np.ones(hop) / hop, 'same'))[::hop]
THR = np.percentile(rms, 95) * 0.07
def R(t): return rms[min(len(rms) - 1, max(0, int(t * 100)))]
def palavras(a, b): return [w for w in W if a - 0.001 <= w[1] <= b + 0.001]
def vale(a, b):
    idx = np.arange(int(a * 100), int(b * 100))
    v = np.convolve(rms[idx], np.ones(3) / 3, 'same'); j = int(np.argmin(v))
    return idx[j] / 100, v[j]
def silencio(t, n=12):
    return all(R(t + k * 0.01) < THR for k in range(n))
def achar_ini(p):
    """começo: o fim do silêncio antes da 1ª palavra (a voz entra inteira)"""
    t = p[1] + 0.05
    while t > p[1] - 0.8:
        if silencio(t - 0.10, 10): return t - 0.04
        t -= 0.01
    return vale(p[1] - 0.35, p[1] + 0.03)[0]
def achar_fim(u):
    """fim: o começo do silêncio depois da última palavra + o rabinho natural da voz"""
    prox = [w for w in W if w[1] > u[1]]
    lim = (prox[0][1] - 0.02) if prox else 1e9
    t = u[1] + 0.15
    while t < min(u[2] + 1.0, lim):
        if silencio(t): return min(t + 0.12, lim)
        t += 0.01
    return vale(max(u[2] - 0.1, u[1] + 0.1), min(u[2] + 0.4, lim + 0.12))[0] + 0.01

pecas = []
for nome, kind, a, b in PECAS:
    ws = palavras(a, b)
    p = {'nome': nome, 'kind': kind, 'ws': ws, 's': round(achar_ini(ws[0]), 3), 'fim_fala': round(achar_fim(ws[-1]), 3)}
    p['e'] = p['fim_fala']
    p['s'] = max(0.0, p['s'])
    txt = ' '.join(w[0] for w in ws)
    p['pausa'] = 0.0  # sem parada para ler: a voz segue natural
    if nome == 'P9': p['pausa'] = 3.4  # tempo para ler o versículo no cartão
    pecas.append(p)
for p in pecas:  # fins conferidos na energia da voz (o grito final de "cuidado" é longo)
    if p['nome'] == 'G': p['e'] = 61.25
    if p['nome'] == 'L': p['s'], p['e'] = 89.78, 91.15
for p, q in zip(pecas, pecas[1:]):
    if p['s'] < q['s'] < p['e']:  # trechos colados na fonte: emenda no meio, sem repetir áudio
        m = round((p['e'] + q['s']) / 2, 3); p['e'] = m; q['s'] = m
_px = [w for w in W if w[1] > pecas[-1]['ws'][-1][1]]

for p in pecas:
    print(f"{p['nome']:4} {p['kind']} {p['s']:6.2f}-{p['e']:6.2f} pausa {p['pausa']:.2f} | " + ' '.join(w[0] for w in p['ws']))
segs = [[p['s'], p['e']] for p in pecas]; pausas = [p['pausa'] for p in pecas]
dur = sum(b - a + q for (a, b), q in zip(segs, pausas)); print('duração', round(dur, 2))

# voz: trechos + silêncio das pausas; tira ruído e chiado, nível de rede social
partes = []
for (a, b), q in zip(segs, pausas):
    seg = V[int(a * SR):int(b * SR)].copy(); f = int(0.015 * SR)
    seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]
    partes.append(seg)
    if q > 0: partes.append(np.zeros((int(q * SR), 2), np.float32))
(OUT / 'voz.f32').write_bytes(np.concatenate(partes).astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '44100', '-ac', '2', '-i', str(OUT / 'voz.f32'), '-af',
                'highpass=f=80,afftdn=nf=-30:nr=10,equalizer=f=3000:t=q:w=1.2:g=2,equalizer=f=250:t=q:w=1:g=-1.5,'
                'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=8',
                '-ar', '48000', str(OUT / 'voz.wav')], check=True)

# vídeo: já é vertical; amplia para 1080x1920 com limpeza e nitidez; pausa = último quadro repetido
fc = []
n = len(segs)
fc.append('[0:v]fps=30,split=' + str(n) + ''.join(f'[f{i}]' for i in range(n)))
for i, ((a, b), q) in enumerate(zip(segs, pausas)):
    pad = f',tpad=stop_mode=clone:stop_duration={q:.2f}' if q > 0 else ''
    fc.append(f'[f{i}]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,crop=964:1714:58:0,scale=1080:1920:flags=lanczos,'
              f'unsharp=7:7:0.9:5:5:0.0,eq=contrast=1.04:saturation=1.06{pad}[v{i}]')
fc.append(''.join(f'[v{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=0[vo]')
(OUT / 'fc.txt').write_text(';'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(G / 'src.mp4'), '-filter_complex_script', str(OUT / 'fc.txt'), '-map', '[vo]', '-an',
                '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(OUT / 'base.mp4')], check=True)
json.dump({'dur': dur, 'segs': segs, 'pausas': pausas, 'crop0': 0, 'largura': 1080, 'altura': 1920}, open(OUT / 'info.json', 'w'))
json.dump(pecas, open(OUT / 'pecas.json', 'w'), ensure_ascii=False)
print('ok')
