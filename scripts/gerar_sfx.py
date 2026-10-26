"""Synthesizes the sound effects used in the edit into public/sfx/."""
import wave
from pathlib import Path

import numpy as np

SR = 48000
OUT = Path(__file__).resolve().parent.parent / "public" / "sfx"
rng = np.random.default_rng(7)


def save(name, x):
    x = x / np.max(np.abs(x)) * 0.9
    data = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def lowpass(x, alpha):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha[i] * (v - acc) if np.ndim(alpha) else alpha * (v - acc)
        y[i] = acc
    return y


# Impact: pitch-dropping sub boom + short noise crack
t = np.arange(int(SR * 1.2)) / SR
freq = 40 + 90 * np.exp(-t * 18)
boom = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 3.5)
crack = lowpass(rng.standard_normal(t.size), 0.35) * np.exp(-t * 40)
save("impacto.wav", np.tanh(2.2 * boom + 0.6 * crack))

# Whoosh: noise swept from dark to bright, swelling into the hit
t = np.arange(int(SR * 0.45)) / SR
p = t / t[-1]
env = p**2.5 * (1 - np.clip((p - 0.92) / 0.08, 0, 1))
save("whoosh.wav", lowpass(rng.standard_normal(t.size), 0.02 + 0.5 * p**2) * env)

# Snap for the white flash: very short bright click
t = np.arange(int(SR * 0.12)) / SR
snap = rng.standard_normal(t.size) * np.exp(-t * 90)
save("estalo.wav", snap - lowpass(snap, 0.15))
