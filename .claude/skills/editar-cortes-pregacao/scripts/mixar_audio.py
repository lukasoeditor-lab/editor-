"""Mixa o áudio de um corte: voz + música de fundo + efeitos sonoros, e junta ao vídeo renderizado.

Uso: python3 -I mixar_audio.py X pasta_trabalho pasta_musicas pasta_sfx video_mudo.mp4 saida.mp4

- voz: pasta_trabalho/iso_X.mp3 (voz isolada, preferida) ou voz_X.wav (áudio do trecho já sem pausas)
- música: segundo plano["musica"]: arquivo, início (s), modo "continuo" ou "loop" (+ corte_em)
    loop: toca de `inicio` até `inicio+corte_em`, volta ao começo e repete até o fim do vídeo,
    com crossfade curto na emenda (a música tem uma batida forte depois do ponto de corte).
    continuo: toca a partir de `inicio`; se acabar antes do vídeo, repete com crossfade.
- a música desce sozinha quando o pastor fala (ducking) e a voz dá um recuo curto em cada impacto
- no final o volume é padronizado em -14 LUFS (loudnorm em duas passadas)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
ARQ_SFX = {"whoosh": "el_whoosh.mp3", "whoosh2": "el_whoosh2.mp3", "impacto": "el_impacto.mp3",
           "impacto2": "el_impacto2.mp3", "estalo": "el_estalo.mp3", "riser": "el_riser.mp3", "clique": "el_clique.mp3"}
MUSICA_ABAIXO_DA_VOZ_DB = 9.0   # antes do ducking
DUCK_FALA = 0.5                 # ganho da música enquanto o pastor fala
RECUO_VOZ_IMPACTO = 0.6         # ganho da voz logo após um impacto
GANHO_EFEITOS = 0.45            # efeitos são acentos: ficam abaixo da voz
XFADE = 0.45                    # emenda do laço da música, segundos


def decodificar(arq, inicio=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(inicio)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-i", str(arq), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    b = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(b, np.float32).reshape(-1, 2).copy()


def lufs(x):
    p = subprocess.run(["ffmpeg", "-v", "info", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                        "-af", "ebur128", "-f", "null", "-"], input=x.tobytes(), capture_output=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr.decode())
    return float(m[-1]) if m else -23.0


def laco(seg, total):
    """Repete `seg` com crossfade de potência constante até ter `total` amostras."""
    n_x = int(XFADE * SR)
    if len(seg) >= total:
        return seg[:total]
    out = seg.copy()
    sobe = np.sin(np.linspace(0, np.pi / 2, n_x))[:, None]
    desce = np.cos(np.linspace(0, np.pi / 2, n_x))[:, None]
    while len(out) < total:
        cauda = out[-n_x:] * desce + seg[:n_x] * sobe
        out = np.concatenate([out[:-n_x], cauda, seg[n_x:]])
    return out[:total]


def suavizar(env, ataque, soltura):
    out = np.empty_like(env)
    a = np.exp(-1.0 / (ataque * SR))
    r = np.exp(-1.0 / (soltura * SR))
    v = env[0]
    for i, e in enumerate(env):
        k = a if e < v else r  # ganho cai rápido (ataque) e volta devagar (soltura)
        v = k * v + (1 - k) * e
        out[i] = v
    return out


def main():
    cid = sys.argv[1]
    trab, musicas, sfx_dir = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    video, saida = Path(sys.argv[5]), Path(sys.argv[6])
    plano = json.load(open(Path(sys.argv[7]) if len(sys.argv) > 7 else f"public/cortes/{cid}/plano.json"))
    dur = plano["duracao"] / plano["fps"]
    n = int(round(dur * SR))

    # prefere a voz isolada (sem banda, bateria, guitarra e ruído) quando existir: iso_X.mp3
    iso = trab / f"iso_{cid}.mp3"
    voz = decodificar(iso if iso.exists() else trab / f"voz_{cid}.wav")[:n]
    print(f"{cid}: voz {'isolada' if iso.exists() else 'ORIGINAL (sem isolamento)'}")
    voz = np.pad(voz, ((0, n - len(voz)), (0, 0)))
    # a gravação ao vivo vem muito alta (perto de 0 dBFS): baixa a voz para sobrar espaço aos efeitos
    voz *= 10 ** ((-20.0 - lufs(voz)) / 20)

    sem_musica = "--sem-musica" in sys.argv
    # música
    m = plano["musica"]
    ini = float(m.get("inicio", 0))
    if sem_musica:
        mus = np.zeros((n, 2), np.float32)
    else:
        if m["modo"] == "loop":
            seg = decodificar(musicas / m["arquivo"], ini, float(m["corte_em"]))
        else:
            seg = decodificar(musicas / m["arquivo"], ini, dur + 3)
        mus = laco(seg, n)
    f_in, f_out = int(1.0 * SR), int(2.6 * SR)
    mus[:f_in] *= np.linspace(0, 1, f_in)[:, None]
    mus[-f_out:] *= np.linspace(1, 0, f_out)[:, None]

    # nível da música em relação à voz + ducking pela fala
    alvo = lufs(voz) - MUSICA_ABAIXO_DA_VOZ_DB
    if not sem_musica:
        mus *= 10 ** ((alvo - lufs(mus)) / 20)
    envv = np.sqrt(np.convolve((voz.mean(1)) ** 2, np.ones(int(0.05 * SR)) / int(0.05 * SR), "same"))
    fala = np.clip(envv / (np.percentile(envv, 90) * 0.35 + 1e-9), 0, 1)
    ganho = suavizar(1.0 - (1.0 - DUCK_FALA) * fala, 0.04, 0.35)
    mus *= ganho[:, None]

    # recuo da voz nos impactos
    g_voz = np.ones(n, np.float32)
    for s in plano["sfx"]:
        if s["arq"].startswith("impacto"):
            t = s["t"] + 0.09
            a, b = int(max(0, (t - 0.04)) * SR), int(min(dur, t + 0.42) * SR)
            g_voz[a:b] = RECUO_VOZ_IMPACTO
    g_voz = suavizar(g_voz.astype(np.float64), 0.008, 0.12).astype(np.float32)
    voz *= g_voz[:, None]

    # efeitos
    efx = np.zeros((n, 2), np.float32)
    cache = {}
    pico_voz = float(np.percentile(np.abs(voz), 99.5))
    for s in plano["sfx"]:
        if s["arq"] not in cache:
            cache[s["arq"]] = decodificar(sfx_dir / ARQ_SFX[s["arq"]])
        # o pico do efeito fica na altura do pico da voz (vol = fração disso), nunca muito acima dela
        x = cache[s["arq"]] / max(float(np.abs(cache[s["arq"]]).max()), 1e-6) * s["vol"] * pico_voz * GANHO_EFEITOS
        i0 = int(round(s["t"] * SR))
        if i0 < 0:
            x, i0 = x[-i0:], 0
        j = min(n, i0 + len(x))
        if j > i0:
            efx[i0:j] += x[: j - i0]

    mix = voz + mus + efx
    rms = lambda x: float(np.sqrt((x ** 2).mean()) + 1e-12)
    razao = 20 * np.log10(rms(voz) / rms(mus + efx))
    print(f"{cid}: voz está {razao:.1f} dB acima de música+efeitos (precisa ser >= 6)")
    if razao < 6:
        raise SystemExit("a voz está coberta pela música/efeitos: reduza os volumes")
    pico = float(np.abs(mix).max())
    if pico > 0.97:
        mix *= 0.97 / pico

    # padroniza em -14 LUFS (duas passadas) e junta ao vídeo
    tmp = saida.with_suffix(".mix.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", str(tmp)],
                   input=mix.astype(np.float32).tobytes(), check=True)
    alvo_ln = "I=-14:TP=-1.0:LRA=9"
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", str(tmp), "-af", f"loudnorm={alvo_ln}:print_format=json",
                        "-f", "null", "-"], capture_output=True)
    j = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr.decode(), re.S).group(0))
    filtro = (f"loudnorm={alvo_ln}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
              f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(tmp), "-map", "0:v", "-map", "1:a",
                    "-af", filtro, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(saida)], check=True)
    tmp.unlink()
    print(f"{cid}: áudio mixado ({dur:.1f}s) -> {saida}")


if __name__ == "__main__":
    main()
