"""Exporta um vídeo nas especificações de cada plataforma e confere o resultado.

Uso:
  python3 exportar.py entrada.mp4 --plataforma reels [--nome cliente-campanha-v1] [--pasta entregas]

Plataformas: reels · tiktok · shorts (1080x1920) · feed (1080x1350) · youtube (1920x1080) · quadrado (1080x1080)
O vídeo precisa já estar no formato certo (use a skill reenquadrar antes, se não estiver).
Requer FFmpeg no PATH.
"""
import argparse
import json
import os
import subprocess

PRESETS = {
    "reels": (1080, 1920), "tiktok": (1080, 1920), "shorts": (1080, 1920),
    "feed": (1080, 1350), "quadrado": (1080, 1080), "youtube": (1920, 1080),
}


def sonda(arq):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                   "stream=codec_type,width,height,r_frame_rate:format=duration",
                                   "-of", "json", arq], capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    return v["width"], v["height"], float(j["format"]["duration"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada")
    p.add_argument("--plataforma", required=True, choices=PRESETS)
    p.add_argument("--nome")
    p.add_argument("--pasta", default="entregas")
    a = p.parse_args()
    W, H = PRESETS[a.plataforma]
    w, h, dur = sonda(a.entrada)
    if abs(w / h - W / H) > 0.01:
        raise SystemExit(f"O vídeo é {w}x{h}, mas {a.plataforma} pede {W}x{H}. Reenquadre antes de exportar.")
    os.makedirs(a.pasta, exist_ok=True)
    nome = a.nome or os.path.splitext(os.path.basename(a.entrada))[0]
    saida = os.path.join(a.pasta, f"{nome}_{a.plataforma}_{W}x{H}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.entrada,
                    "-vf", f"scale={W}:{H}:flags=lanczos,fps=30,setsar=1",
                    "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", saida], check=True)
    lufs = subprocess.run(["ffmpeg", "-hide_banner", "-i", saida, "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    integrado = [l for l in lufs.splitlines() if l.strip().startswith("I:")]
    w2, h2, d2 = sonda(saida)
    print(json.dumps({"arquivo": saida, "resolucao": f"{w2}x{h2}", "duracao_s": round(d2, 2),
                      "tamanho_mb": round(os.path.getsize(saida) / 1e6, 1),
                      "volume": integrado[-1].strip() if integrado else "sem áudio"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
