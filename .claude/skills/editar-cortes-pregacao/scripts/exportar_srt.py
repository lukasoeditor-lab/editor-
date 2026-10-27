"""Exporta as legendas de um plano (plano.json) como .srt na linha do tempo do vídeo final.

Uso: python3 -I exportar_srt.py public/cortes/X/plano.json saida.srt
Serve de legenda "fechada" (acessibilidade/SEO) ao lado da legenda queimada no vídeo.
"""
import json
import sys
from pathlib import Path


def ts(frames, fps):
    ms = round(frames / fps * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    plano = json.loads(Path(sys.argv[1]).read_text())
    fps = plano["fps"]
    linhas = []
    for i, leg in enumerate(plano["legendas"], 1):
        txt = " ".join(w["txt"] for w in leg["palavras"])
        linhas += [str(i), f"{ts(leg['f0'], fps)} --> {ts(leg['f1'], fps)}", txt, ""]
    Path(sys.argv[2]).write_text("\n".join(linhas), encoding="utf-8")
    print(f"{len(plano['legendas'])} legendas -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
