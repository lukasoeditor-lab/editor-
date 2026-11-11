"""Muda o formato de um vídeo (ex.: horizontal 16:9 para vertical 9:16).

Uso:
  python3 reenquadrar.py entrada.mp4 saida.mp4 --formato 9:16 [--modo desfoque|corte|barras] [--foco 0.5]

Formatos: 9:16 (1080x1920, Reels/TikTok/Shorts) · 4:5 (1080x1350, feed) · 1:1 (1080x1080) · 16:9 (1920x1080)
Modos:
  desfoque  vídeo inteiro no centro, com o próprio vídeo desfocado preenchendo o fundo (padrão)
  corte     preenche a tela cortando as laterais; --foco escolhe a posição horizontal (0 = esquerda, 1 = direita)
  barras    vídeo inteiro com barras pretas
Requer FFmpeg no PATH.
"""
import argparse
import subprocess

FORMATOS = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080), "16:9": (1920, 1080)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada"); p.add_argument("saida")
    p.add_argument("--formato", default="9:16", choices=FORMATOS)
    p.add_argument("--modo", default="desfoque", choices=["desfoque", "corte", "barras"])
    p.add_argument("--foco", type=float, default=0.5)
    a = p.parse_args()
    W, H = FORMATOS[a.formato]

    if a.modo == "corte":
        f = min(max(a.foco, 0), 1)
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H}:(in_w-{W})*{f}:(in_h-{H})/2,setsar=1")
        cmd = ["-vf", vf]
    elif a.modo == "barras":
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x080A0F,setsar=1"
        cmd = ["-vf", vf]
    else:
        grafo = (f"[0:v]split=2[f][b];"
                 f"[b]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40,eq=brightness=-0.12[fundo];"
                 f"[f]scale={W}:{H}:force_original_aspect_ratio=decrease[frente];"
                 f"[fundo][frente]overlay=(W-w)/2:(H-h)/2,setsar=1[v]")
        cmd = ["-filter_complex", grafo, "-map", "[v]", "-map", "0:a?"]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.entrada, *cmd,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.saida], check=True)
    print(f"Salvo em {a.saida} ({W}x{H}, modo {a.modo})")


if __name__ == "__main__":
    main()
