"""Remove silêncios e pausas longas de um vídeo falado (corte seco, estilo reels).

Uso:
  python3 cortar_silencios.py entrada.mp4 saida.mp4 [--limiar -35] [--min 0.45] [--margem 0.12] [--plano]

--limiar  volume (dB) abaixo do qual é silêncio. Ambientes ruidosos: -30. Estúdio: -40.
--min     duração mínima (s) de uma pausa para ser cortada.
--margem  respiro (s) mantido antes e depois de cada fala, para não cortar sílabas.
--plano   só mostra os trechos que seriam mantidos, sem gerar vídeo.
Requer FFmpeg no PATH.
"""
import argparse
import json
import re
import subprocess
import sys


def duracao(arquivo):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arquivo],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def silencios(arquivo, limiar, minimo):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", arquivo, "-vn", "-af",
                          f"silencedetect=n={limiar}dB:d={minimo}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    inicios = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    fins = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(inicios, fins + [None] * (len(inicios) - len(fins))))


def trechos_mantidos(total, sil, margem):
    trechos, cursor = [], 0.0
    for ini, fim in sil:
        fim = total if fim is None else fim
        a, b = cursor, min(total, ini + margem)
        if b - a > 0.08:
            trechos.append((round(a, 3), round(b, 3)))
        cursor = max(0.0, fim - margem)
    if total - cursor > 0.08:
        trechos.append((round(cursor, 3), round(total, 3)))
    return trechos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada"); p.add_argument("saida")
    p.add_argument("--limiar", type=float, default=-35)
    p.add_argument("--min", type=float, default=0.45)
    p.add_argument("--margem", type=float, default=0.12)
    p.add_argument("--plano", action="store_true")
    a = p.parse_args()

    total = duracao(a.entrada)
    t = trechos_mantidos(total, silencios(a.entrada, a.limiar, a.min), a.margem)
    novo = sum(b - x for x, b in t)
    print(json.dumps({"duracao_original": round(total, 2), "duracao_final": round(novo, 2),
                      "trechos": len(t), "mantidos": t}, ensure_ascii=False))
    if a.plano:
        return
    if not t:
        sys.exit("Nenhuma fala detectada. Tente um --limiar mais baixo (ex.: -45).")

    tem_video = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=index",
                                "-of", "csv=p=0", a.entrada], capture_output=True, text=True).stdout.strip() != ""
    partes, rotulos = [], []
    for i, (x, b) in enumerate(t):
        if tem_video:
            partes.append(f"[0:v]trim=start={x}:end={b},setpts=PTS-STARTPTS[v{i}]")
        partes.append(f"[0:a]atrim=start={x}:end={b},asetpts=PTS-STARTPTS[a{i}]")
        rotulos.append(f"[v{i}][a{i}]" if tem_video else f"[a{i}]")
    v = 1 if tem_video else 0
    partes.append("".join(rotulos) + f"concat=n={len(t)}:v={v}:a=1" + ("[v][a]" if tem_video else "[a]"))
    grafo = ";".join(partes)
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.entrada, "-filter_complex", grafo]
    cmd += (["-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"] if tem_video else [])
    cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.saida]
    subprocess.run(cmd, check=True)
    print(f"Salvo em {a.saida}")


if __name__ == "__main__":
    main()
