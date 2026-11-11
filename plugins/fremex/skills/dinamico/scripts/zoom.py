"""Zoom dinâmico: alterna o enquadramento a cada corte (jump cut) e dá "punch" nas palavras fortes.

Uso: python3 zoom.py entrada.mp4 edicao.json saida.mp4

Lê de edicao.json:
  "zoom": {
    "cortes":   [3.2, 7.9, ...],               # tempos dos cortes; os trechos alternam entre normal e aproximado
    "alternar": 0.08,                          # quanto aproxima nos trechos alternados (0.08 = 8%)
    "punches":  [{"t": 2.1, "forca": 0.12}],   # aproximação rápida que volta sozinha, nas palavras fortes
    "centro":   [0.5, 0.42]                    # ponto de foco (x, y de 0 a 1); 0.42 favorece o rosto
  }
Requer FFmpeg no PATH. Mantém o áudio original.
"""
import json
import subprocess
import sys


def main():
    entrada, cfg, saida = sys.argv[1:4]
    z = json.load(open(cfg, encoding="utf-8")).get("zoom", {})
    w, h, fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height,r_frame_rate", "-of", "csv=p=0", entrada],
                               capture_output=True, text=True, check=True).stdout.strip().split(",")
    num, den = fps.split("/")
    fps = round(int(num) / int(den), 3)

    termos = ["1"]
    cortes = sorted(z.get("cortes", []))
    alt = float(z.get("alternar", 0.08))
    if cortes and alt:
        limites = cortes + [99999]
        trechos = [f"between(in_time,{limites[i]},{limites[i + 1]})" for i in range(0, len(limites) - 1, 2)]
        termos.append(f"{alt}*({'+'.join(trechos)})")
    for p in z.get("punches", []):
        t, f = float(p["t"]), float(p.get("forca", 0.12))
        # sobe rápido (0,08 s) e volta suave (0,35 s)
        termos.append(f"{f}*if(lt(in_time,{t}),exp(-pow((in_time-{t})/0.08,2)),exp(-pow((in_time-{t})/0.35,2)))")
    expr = "+".join(termos)
    cx, cy = z.get("centro", [0.5, 0.42])
    vf = (f"zoompan=z='{expr}':d=1:x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':s={w}x{h}:fps={fps},setsar=1")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", entrada, "-vf", vf, "-map", "0:v", "-map", "0:a?",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "-movflags", "+faststart", saida], check=True)
    print(f"Zoom aplicado: {len(cortes)} cortes, {len(z.get('punches', []))} punches → {saida}")


if __name__ == "__main__":
    main()
