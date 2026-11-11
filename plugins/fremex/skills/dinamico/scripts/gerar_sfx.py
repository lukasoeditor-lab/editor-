"""Gera a biblioteca de efeitos sonoros FREMEX por síntese (sem direitos de terceiros).

Uso: python3 gerar_sfx.py [pasta]   (padrão: ../sfx ao lado desta pasta)
Cria: whoosh, swipe, pop, click, ding, riser, boom, glitch (.wav, 48 kHz, estéreo).
Os sons são gerados por fórmulas matemáticas: são da FREMEX e podem ser usados em qualquer trabalho.
"""
import os
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def env(n, ataque, queda):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-np.maximum(0, t - ataque) / queda)


def passa_baixa(x, corte):
    """Filtro passa-baixa de um polo com corte variável (array em Hz)."""
    a = np.exp(-2 * np.pi * np.asarray(corte) / SR) * np.ones_like(x)
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def seno_varrido(f0, f1, dur, curva=1.0):
    n = int(SR * dur); t = np.linspace(0, 1, n)
    f = f0 + (f1 - f0) * t ** curva
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def whoosh(dur=0.5):
    n = int(SR * dur); t = np.linspace(0, 1, n)
    ruido = rng.standard_normal(n)
    corte = 400 + 5000 * np.sin(np.pi * t) ** 2
    s = passa_baixa(ruido, corte) - passa_baixa(ruido, corte * 0.25)
    return s * np.sin(np.pi * t) ** 1.5


def swipe():
    n = int(SR * 0.28); t = np.linspace(0, 1, n)
    s = passa_baixa(rng.standard_normal(n), 800 + 7000 * t)
    return s * np.sin(np.pi * t) ** 2


def pop():
    s = seno_varrido(950, 280, 0.09, 0.6)
    return s * env(len(s), 0.002, 0.03)


def click():
    n = int(SR * 0.025)
    r = rng.standard_normal(n)
    s = r - passa_baixa(r, 2000 * np.ones(n))
    return s * env(n, 0.0005, 0.006)


def ding():
    n = int(SR * 1.1); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 1318.5 * t) + 0.45 * np.sin(2 * np.pi * 2637 * t) + 0.2 * np.sin(2 * np.pi * 3955 * t)
    return s * env(n, 0.003, 0.32)


def riser(dur=1.2):
    n = int(SR * dur); t = np.linspace(0, 1, n)
    tom = seno_varrido(180, 1400, dur, 2.0)
    ruido = passa_baixa(rng.standard_normal(n), 500 + 9000 * t ** 2)
    return (0.6 * tom + 0.5 * ruido) * t ** 2.2


def boom():
    s = seno_varrido(90, 38, 0.8, 0.5)
    n = len(s)
    cauda = passa_baixa(rng.standard_normal(n), 180 * np.ones(n))
    return (s + 0.6 * cauda) * env(n, 0.004, 0.22)


def glitch():
    n = int(SR * 0.22)
    blocos = np.repeat(rng.standard_normal(n // 240 + 1), 240)[:n]
    tom = np.sign(np.sin(2 * np.pi * 220 * np.arange(n) / SR))
    return (0.6 * blocos + 0.3 * tom) * env(n, 0.001, 0.12)


def salvar(caminho, s, pan=0.0):
    s = s / (np.max(np.abs(s)) + 1e-9) * 0.89
    esq, dir_ = s * (1 - max(0, pan)), s * (1 + min(0, pan))
    dados = (np.stack([esq, dir_], axis=1) * 32767).astype(np.int16)
    with wave.open(caminho, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(dados.tobytes())


def main():
    pasta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sfx")
    os.makedirs(pasta, exist_ok=True)
    for nome, fn in [("whoosh", whoosh), ("swipe", swipe), ("pop", pop), ("click", click), ("ding", ding),
                     ("riser", riser), ("boom", boom), ("glitch", glitch)]:
        salvar(os.path.join(pasta, f"{nome}.wav"), fn())
    print(f"Biblioteca de efeitos em {os.path.abspath(pasta)}")


if __name__ == "__main__":
    main()
