"""Gera os tempos de cada palavra de uma narração, para sincronizar legendas.

Uso: python3 palavras.py narracao.mp3 palavras.json [deslocamento_em_segundos]
Requer: pip install faster-whisper  e  FFmpeg no PATH.
Saída: lista JSON de [inicio_em_segundos, "palavra"].
"""
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel


def main():
    audio, out = sys.argv[1], sys.argv[2]
    offset = float(sys.argv[3]) if len(sys.argv) > 3 else 0.12  # o Whisper tende a marcar um pouco antes
    # Decodifica com FFmpeg para PCM 16 kHz mono (evita incompatibilidades do decodificador interno).
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(samples, language="pt", word_timestamps=True)
    words = [[round(float(w.start) + offset, 2), w.word.strip()] for s in segments for w in s.words]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
    print(f"{len(words)} palavras salvas em {out}")


if __name__ == "__main__":
    main()
