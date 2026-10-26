"""Transcreve um .wav mono 16 kHz em português com tempo por palavra.
Uso: python3 -I transcrever.py audio.wav saida.json
O áudio é lido como array numpy porque o decodificador do PyAV (usado pelo
faster-whisper para ler arquivos) falha nesta imagem."""
import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
import wave, numpy as np
w = wave.open(sys.argv[1]); audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
segs, info = m.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False)
out = []
for s in segs:
    print(f"[{s.start:6.2f} - {s.end:6.2f}] {s.text.strip()}")
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"start": w.start, "end": w.end, "word": w.word} for w in s.words]})
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
