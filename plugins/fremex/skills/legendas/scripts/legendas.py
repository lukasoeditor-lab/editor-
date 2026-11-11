"""Gera legendas palavra por palavra (estilo reels) e, opcionalmente, grava no vídeo.

Uso:
  python3 legendas.py video.mp4 [--saida video-legendado.mp4] [--palavras 3] [--idioma pt]
                      [--fonte "Arial Black"] [--tamanho 78] [--posicao 0.72]
                      [--cor-destaque 6A96DE] [--maiusculas] [--so-arquivos]

Gera sempre video.ass (legenda animada) e video.srt (legenda simples para as plataformas).
Sem --so-arquivos, grava a legenda no vídeo (--saida).
Requer: FFmpeg com libass e  pip install faster-whisper
"""
import argparse
import os
import subprocess

import numpy as np


def transcrever(arquivo, idioma, modelo):
    from faster_whisper import WhisperModel
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", arquivo, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    amostras = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(amostras, language=idioma, word_timestamps=True, vad_filter=True)
    return [(float(w.start), float(w.end), w.word.strip()) for s in segs for w in s.words if w.word.strip()]


def blocos(palavras, por_bloco):
    """Agrupa até N palavras, quebrando em pontuação ou em pausas maiores que 0,6 s."""
    out, atual = [], []
    for i, w in enumerate(palavras):
        atual.append(w)
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        quebra = w[2][-1:] in ".,?!:;" or len(atual) >= por_bloco or prox is None or prox[0] - w[1] > 0.6
        if quebra:
            out.append(atual); atual = []
    return out


def ts_ass(t):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ts_srt(t):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def bgr(hexcor):
    hexcor = hexcor.lstrip("#")
    return f"&H00{hexcor[4:6]}{hexcor[2:4]}{hexcor[0:2]}&"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video"); p.add_argument("--saida")
    p.add_argument("--palavras", type=int, default=3)
    p.add_argument("--idioma", default="pt")
    p.add_argument("--modelo", default="small")
    p.add_argument("--fonte", default="Arial Black")
    p.add_argument("--tamanho", type=int, default=78, help="tamanho em px para vídeo de 1920 de altura")
    p.add_argument("--posicao", type=float, default=0.72, help="altura da legenda (0 = topo, 1 = base)")
    p.add_argument("--cor-destaque", default="6A96DE")
    p.add_argument("--maiusculas", action="store_true")
    p.add_argument("--so-arquivos", action="store_true")
    p.add_argument("--sem-pulo", dest="pulo", action="store_false", help="desliga o pulo de escala da palavra falada")
    a = p.parse_args()

    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0:s=x", a.video],
                                   capture_output=True, text=True, check=True).stdout.strip().split("x"))
    escala = h / 1920
    palavras = transcrever(a.video, a.idioma, a.modelo)
    if a.maiusculas:
        palavras = [(x, y, t.upper()) for x, y, t in palavras]
    base = os.path.splitext(a.video)[0]

    destaque, branco, apagado = bgr(a.cor_destaque), "&H00F6F4F3&", "&H80F6F4F3&"
    tam = int(a.tamanho * escala); y = int(h * a.posicao)
    ass = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: FREMEX,{a.fonte},{tam},{branco},{branco},&H00080A0F&,&H64080A0F&,-1,0,0,0,100,100,0,0,1,"
        f"{max(2, int(5 * escala))},{max(1, int(3 * escala))},5,60,60,0,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    srt, n = [], 1
    lista = blocos(palavras, a.palavras)
    for k, bloco in enumerate(lista):
        fim_bloco = bloco[-1][1] + 0.15
        if k + 1 < len(lista):  # nunca invade o bloco seguinte (evita duas legendas sobrepostas)
            fim_bloco = min(fim_bloco, lista[k + 1][0][0])
        for i, (ini, fim, _) in enumerate(bloco):
            ate = bloco[i + 1][0] if i + 1 < len(bloco) else fim_bloco
            partes = []
            for j, (_, _, txt) in enumerate(bloco):
                cor = destaque if j == i else (branco if j < i else apagado)
                if j == i and a.pulo:  # a palavra falada "pula": cresce e volta ao tamanho normal
                    partes.append("{\\c" + cor + "\\fscx114\\fscy114\\t(0,120,\\fscx100\\fscy100)}" + txt + "{\\fscx100\\fscy100}")
                else:
                    partes.append("{\\c" + cor + "}" + txt)
            pop = "{\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}" if i == 0 else ""
            ass.append(f"Dialogue: 0,{ts_ass(ini)},{ts_ass(ate)},FREMEX,,0,0,0,,{{\\pos({w // 2},{y})}}{pop}" + " ".join(partes))
        srt += [str(n), f"{ts_srt(bloco[0][0])} --> {ts_srt(fim_bloco)}", " ".join(t for _, _, t in bloco), ""]
        n += 1
    open(base + ".ass", "w", encoding="utf-8").write("\n".join(ass) + "\n")
    open(base + ".srt", "w", encoding="utf-8").write("\n".join(srt))
    print(f"{len(palavras)} palavras · legendas em {base}.ass e {base}.srt")

    if not a.so_arquivos:
        saida = a.saida or base + "-legendado.mp4"
        caminho_ass = (base + ".ass").replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-vf", f"ass='{caminho_ass}'",
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "copy", "-movflags", "+faststart", saida], check=True)
        print(f"Vídeo legendado: {saida}")


if __name__ == "__main__":
    main()
