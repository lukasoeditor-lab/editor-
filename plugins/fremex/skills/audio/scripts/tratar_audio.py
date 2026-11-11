"""Trata o áudio de um vídeo: limpa a voz, adiciona música com ducking e normaliza o volume.

Uso:
  python3 tratar_audio.py entrada.mp4 saida.mp4 [--limpar] [--musica trilha.mp3] [--volume-musica 0.25]
                          [--ducking] [--lufs -14]

--limpar         redução de ruído leve + corte de graves (ar-condicionado, ventilador)
--musica         trilha de fundo (repetida até o fim do vídeo)
--volume-musica  volume da trilha antes do ducking (0.0 a 1.0)
--ducking        abaixa a música automaticamente quando há fala
--lufs           volume final integrado. Redes sociais: -14
Requer FFmpeg no PATH.
"""
import argparse
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada"); p.add_argument("saida")
    p.add_argument("--limpar", action="store_true")
    p.add_argument("--musica")
    p.add_argument("--volume-musica", type=float, default=0.25)
    p.add_argument("--ducking", action="store_true")
    p.add_argument("--lufs", type=float, default=-14)
    a = p.parse_args()

    voz = "[0:a]" + ("highpass=f=80,afftdn=nf=-25," if a.limpar else "") + "aresample=48000[voz]"
    final = f"loudnorm=I={a.lufs}:TP=-1:LRA=11"
    if a.musica:
        musica = f"[1:a]volume={a.volume_musica},aresample=48000[mus]"
        if a.ducking:
            grafo = (f"{voz};{musica};[voz]asplit=2[v1][v2];"
                     f"[mus][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[mduck];"
                     f"[v1][mduck]amix=inputs=2:duration=first:normalize=0,{final}[a]")
        else:
            grafo = f"{voz};{musica};[voz][mus]amix=inputs=2:duration=first:normalize=0,{final}[a]"
        entradas = ["-i", a.entrada, "-stream_loop", "-1", "-i", a.musica]
    else:
        grafo = f"{voz};[voz]{final}[a]"
        entradas = ["-i", a.entrada]
    subprocess.run(["ffmpeg", "-y", "-v", "error", *entradas, "-filter_complex", grafo,
                    "-map", "0:v?", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", a.saida], check=True)
    print(f"Salvo em {a.saida}")


if __name__ == "__main__":
    main()
