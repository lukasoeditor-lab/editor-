"""Monta o kit de som do estilo "correria" (R2) a partir do vídeo de referência.

Gera em <saida>/:
  musica_correria.wav  música da referência sem a voz e sem os efeitos das transições (36,9 s, ~125 BPM)
  sfx_queima.wav       efeito da "queima de filme" (estalo/chiado agudo de ~0,2 s), tirado de 18,98 s
  sfx_flash.wav        efeito do "flash branco" (chiado agudo um pouco mais longo), tirado de 9,55 s
Como: separa voz e instrumental (UVR-MDX-NET-Voc_FT); os efeitos são só agudos (>1,5 kHz) e a música é
quase toda grave (−23 dB acima de 1 kHz), então um passa-altas na janela de cada transição isola o efeito,
e o mesmo filtro, subtraído, limpa a música.

Uso: python3 preparar_kit_correria.py referencia.mp4 saida/ [--modelos /tmp/work/models]
O áudio não vai para o git (regra de 05-biblioteca/som); rode este script em cada máquina.
"""
import argparse, glob, subprocess, tempfile
from pathlib import Path
import numpy as np

SR = 44100
TRANSICOES = [6.72, 9.55, 14.31, 15.56, 18.98, 23.23, 32.12]  # medidas no vídeo de referência


def carregar(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def salvar(nome, y):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(nome)],
                   input=np.clip(y, -1, 1).astype(np.float32).tobytes(), check=True)


def passa_altas(seg, fc=1500):
    S = np.fft.rfft(seg, axis=0); f = np.fft.rfftfreq(len(seg), 1 / SR)
    S[f < fc] = 0; S[(f >= fc) & (f < fc * 1.3)] *= 0.5
    return np.fft.irfft(S, len(seg), axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"); ap.add_argument("saida"); ap.add_argument("--modelos", default="/tmp/work/models")
    a = ap.parse_args()
    out = Path(a.saida); out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        wav = Path(d) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.ref, "-vn", "-ac", "2", "-ar", str(SR), wav], check=True)
        subprocess.run(["audio-separator", str(wav), "-m", "UVR-MDX-NET-Voc_FT.onnx", "--model_file_dir", a.modelos,
                        "--output_dir", d, "--single_stem", "Instrumental"], check=True, capture_output=True)
        x = carregar(glob.glob(str(Path(d) / "*Instrumental*"))[0])
    n = int(0.48 * SR)

    def efeito(t):
        i = int((t - 0.06) * SR); s = passa_altas(x[i:i + n])
        env = np.ones(n); fi, fo = int(0.01 * SR), int(0.15 * SR)
        env[:fi] = np.linspace(0, 1, fi); env[-fo:] = np.linspace(1, 0, fo)
        s = s * env[:, None]
        return s / np.abs(s).max() * 0.5
    salvar(out / "sfx_queima.wav", efeito(18.98))
    salvar(out / "sfx_flash.wav", efeito(9.55))
    m = x.copy()
    for t in TRANSICOES:
        i0, i1 = int((t - 0.08) * SR), int((t + 0.45) * SR)
        seg = m[i0:i1]; h = passa_altas(seg)
        w = np.ones(i1 - i0); r = int(0.03 * SR); w[:r] = np.linspace(0, 1, r); w[-r:] = np.linspace(1, 0, r)
        m[i0:i1] = seg - h * w[:, None]
    salvar(out / "musica_correria.wav", m[:int(36.95 * SR)])
    print("kit pronto em", out)


if __name__ == "__main__":
    main()
