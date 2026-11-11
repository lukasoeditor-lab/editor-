"""Coloca efeitos sonoros nos tempos definidos em edicao.json e mistura com o áudio do vídeo.

Uso: python3 sfx.py entrada.mp4 edicao.json saida.mp4 [--pasta-sfx ../sfx]

Lê de edicao.json:
  "sfx": [{"t": 0.0, "tipo": "whoosh", "volume": 0.5}, {"t": 2.1, "tipo": "pop"}]
  tipo = nome de um arquivo da biblioteca (whoosh, swipe, pop, click, ding, riser, boom, glitch)
         ou um caminho para um .wav/.mp3 que o usuário tenha licença para usar.
  Para "riser", use o tempo em que ele deve TERMINAR (ex.: logo antes do corte); o script compensa a duração.
Requer FFmpeg no PATH. Gera a biblioteca automaticamente se ela não existir.
"""
import argparse
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def duracao(arq):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                                capture_output=True, text=True, check=True).stdout.strip())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada"); p.add_argument("edicao"); p.add_argument("saida")
    p.add_argument("--pasta-sfx", default=os.path.join(AQUI, "..", "sfx"))
    a = p.parse_args()
    efeitos = json.load(open(a.edicao, encoding="utf-8")).get("sfx", [])
    if not efeitos:
        sys.exit("Nenhum efeito em edicao.json (chave 'sfx').")
    if not os.path.exists(os.path.join(a.pasta_sfx, "whoosh.wav")):
        subprocess.run([sys.executable, os.path.join(AQUI, "gerar_sfx.py"), a.pasta_sfx], check=True)

    entradas, filtros, rotulos = ["-i", a.entrada], [], []
    for i, e in enumerate(efeitos, start=1):
        arq = e["tipo"] if os.path.isfile(e["tipo"]) else os.path.join(a.pasta_sfx, f"{e['tipo']}.wav")
        if not os.path.isfile(arq):
            sys.exit(f"Efeito não encontrado: {e['tipo']}")
        t = float(e["t"])
        if e["tipo"] == "riser":
            t = max(0.0, t - duracao(arq))
        entradas += ["-i", arq]
        atraso = int(t * 1000)
        filtros.append(f"[{i}:a]aresample=48000,volume={e.get('volume', 0.5)},adelay={atraso}|{atraso}[s{i}]")
        rotulos.append(f"[s{i}]")
    filtros.append(f"[0:a]aresample=48000[base]")
    filtros.append(f"[base]{''.join(rotulos)}amix=inputs={len(rotulos) + 1}:duration=first:normalize=0[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", ";".join(filtros),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", a.saida], check=True)
    print(f"{len(efeitos)} efeitos sonoros aplicados → {a.saida}")


if __name__ == "__main__":
    main()
