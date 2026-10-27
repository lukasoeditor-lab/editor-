#!/usr/bin/env python3
"""Mistura voz, música e efeitos de um projeto HyperFrames e cola no vídeo renderizado.

O render do HyperFrames já mistura o áudio, mas esta etapa deixa o resultado sob controle: limitador baixo
(sem estourar no AAC), níveis conferidos e o mesmo arquivo de vídeo, sem renderizar de novo. Lê as tags
<audio> do index.html do projeto (início, duração, volume, trecho, fades) e refaz a mistura.

Uso:
    uv run scripts/video/corte_pregacao/misturar_audio.py projeto/index.html render.mp4 final.mp4 [--teto 0.68]
    uv run scripts/video/corte_pregacao/misturar_audio.py --autoteste

Depois confira: `ffmpeg -i final.mp4 -af ebur128=peak=true -f null -` (alvo −14 a −16 LUFS, pico real ≤ −1 dBTP).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def rodar(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"erro em {cmd[0]}:\n{r.stderr[-2500:]}")
    return r


def misturar(index: Path, video: Path, saida: Path, teto: float) -> None:
    html = index.read_text(encoding="utf-8")
    total = float(re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"', html).group(1))
    tags = re.findall(r"<audio ([^>]*)>", html)
    if not tags:
        sys.exit("o index.html não tem nenhuma tag <audio>")
    base = index.parent
    entradas, cadeias, rotulos = [], [], []
    for i, t in enumerate(tags):
        def g(k, d=None):
            m = re.search(rf'{k}="([^"]*)"', t)
            return m.group(1) if m else d
        src, ini, dur, vol = g("src"), float(g("data-start", 0)), float(g("data-duration")), float(g("data-volume", 1))
        ms, fi, fo = float(g("data-media-start", 0)), float(g("data-fade-in", 0)), float(g("data-fade-out", 0))
        entradas += ["-i", base / src]
        f = f"[{i}:a]aformat=sample_fmts=fltp:channel_layouts=stereo,aresample=48000,atrim=start={ms}:end={ms + dur},asetpts=PTS-STARTPTS"
        if fi:
            f += f",afade=t=in:d={fi}"
        if fo:
            f += f",afade=t=out:st={max(dur - fo, 0):.3f}:d={fo}"
        f += f",volume={vol},adelay={int(ini * 1000)}|{int(ini * 1000)}[a{i}]"
        cadeias.append(f)
        rotulos.append(f"[a{i}]")
    fc = ";".join(cadeias) + ";" + "".join(rotulos) + (
        f"amix=inputs={len(tags)}:normalize=0:duration=longest,alimiter=limit={teto}:level=disabled,atrim=duration={total}[m]")
    rodar(["ffmpeg", "-v", "error", "-y", *entradas, "-i", video, "-filter_complex", fc, "-map", f"{len(tags)}:v", "-map", "[m]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", total, saida])
    print(f"{len(tags)} faixas misturadas em {saida} ({total:.1f} s)")


def autoteste() -> None:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=330:d=4", "-ac", "2", "-ar", "48000", d / "voz.wav"])
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=110:d=4", "-ac", "2", "-ar", "48000", d / "efeito.wav"])
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=160x90:r=30:d=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", d / "v.mp4"])
        (d / "index.html").write_text(
            '<div data-composition-id="main" data-start="0" data-duration="4">'
            '<audio id="voice" src="voz.wav" data-start="0" data-duration="4" data-volume="0.5"></audio>'
            '<audio id="fx" src="efeito.wav" data-start="1" data-duration="1" data-volume="0.8" data-fade-out="0.2"></audio></div>')
        misturar(d / "index.html", d / "v.mp4", d / "final.mp4", 0.68)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(d / "final.mp4")], capture_output=True, text=True).stdout
        assert "audio" in r and "video" in r, r
        print("autoteste ok")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("index", nargs="?", type=Path)
    p.add_argument("video", nargs="?", type=Path)
    p.add_argument("saida", nargs="?", type=Path)
    p.add_argument("--teto", type=float, default=0.68, help="teto do limitador (0,68 ≈ −3,3 dBFS)")
    p.add_argument("--autoteste", action="store_true")
    a = p.parse_args()
    if a.autoteste:
        return autoteste()
    if not (a.index and a.video and a.saida):
        p.error("preciso do index.html, do vídeo renderizado e do arquivo de saída")
    misturar(a.index, a.video, a.saida, a.teto)


if __name__ == "__main__":
    main()
