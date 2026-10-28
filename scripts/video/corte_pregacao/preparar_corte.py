#!/usr/bin/env python3
"""Prepara um corte de pregação: recorte vertical que segue o pregador, pausas cortadas e voz limpa.

Entra um vídeo horizontal (a pregação inteira) e uma lista de trechos; sai uma pasta com
    base.mp4       vídeo vertical (sem som), já com os trechos colados e as pausas longas tiradas
    voz.wav        a voz do pregador (isolada, se --isolar-voz) normalizada em -16 LUFS
    palavras.json  transcrição com o tempo de cada palavra (tempo do vídeo original)
    info.json      duração, trechos e mapa de tempo (usado por gerar_projeto.py)

Uso:
    uv run scripts/video/corte_pregacao/preparar_corte.py pregacao.mp4 04-projetos/AAAA-MM-DD-corte1/preparo \
        --trechos "940.4:953.8,954.1:958.8,959.2:963.0" --isolar-voz
    uv run scripts/video/corte_pregacao/preparar_corte.py --autoteste

Pontos:
  - Os trechos vêm em segundos do vídeo original, "início:fim". Escolha o início na primeira palavra e o
    fim logo depois da última (a transcrição de --transcrever ajuda a achar os tempos).
  - O recorte 9:16 segue o centro do pregador (média de brilho da parte de cima do quadro) com suavização.
  - --isolar-voz usa o audio-separator (modelo UVR-MDX-NET-Voc_FT.onnx em --modelo-voz).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

KEEP = 0.17          # som mantido de cada lado de uma pausa cortada (s)
PAUSA_MIN = 0.55     # pausa mínima para cortar (s)


def rodar(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"erro em {cmd[0]}:\n{r.stderr[-2500:]}")
    return r


def duracao(arq: Path) -> float:
    return float(rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq]).stdout)


def trechos_de_texto(txt: str) -> list[tuple[float, float]]:
    saida = []
    for par in txt.split(","):
        a, b = par.split(":")
        saida.append((float(a), float(b)))
    if any(b <= a for a, b in saida):
        sys.exit("cada trecho precisa ter fim maior que o início")
    return saida


def rastrear_cor(video: Path, t0: float, t1: float) -> list[float]:
    """Câmera aberta (pregador pequeno, músicos no palco): segue a cor azul do paletó, só na parte de cima do quadro
    (o telão azul-claro fica embaixo). Sem azul no quadro, mantém a última posição."""
    W, H = 480, 270
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", str(video), "-vf",
                          f"fps=2,scale={W}:{H},format=rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
    quadros = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(int)
    masc = []
    for f in quadros:
        reg = f[int(H * 0.15):int(H * 0.64)]
        r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
        masc.append((b > 45) & (b < 210) & (b - g > 15) & (b - r > 20))
    masc = np.array(masc)
    parado = masc.mean(0) > 0.55  # azul que fica no mesmo lugar (guitarra, telão): não é o pregador
    xs, ult = [], 0.5
    for m in masc:
        m = m & ~parado
        col = m.sum(0)
        if col.sum() >= 12:
            ult = float((col * np.arange(W)).sum() / col.sum() / W)
        xs.append(ult)
    return xs


def rastrear_centro(video: Path, t0: float, t1: float) -> list[float]:
    """Posição horizontal (0 a 1) do pregador a cada 0,5 s: centro de massa do brilho da parte de cima do quadro."""
    W, H = 480, 270
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", str(video), "-vf",
                          f"fps=2,scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    quadros = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)
    xs = []
    for f in quadros:
        reg = f[0:int(H * 0.42), int(W * 0.28):int(W * 0.66)]
        m = np.clip(reg - np.median(reg) - 25, 0, None)
        col = m.sum(0)
        xs.append(((col * np.arange(len(col))).sum() / col.sum() + int(W * 0.28)) / W if col.sum() > 0 else 0.5)
    return xs


def expressao_x(xs: list[float], largura_fonte: int, largura_corte: int) -> str:
    k = np.exp(-0.5 * (np.arange(-12, 13) / 4.0) ** 2)
    k /= k.sum()
    suave = np.convolve(np.pad(xs, 12, mode="edge"), k, mode="valid")
    pts = []
    passo = 2 * max(1, -(-len(suave) // 2 // 60))  # um ponto por segundo; no máx. ~60 pontos (o ffmpeg falha com expressões muito aninhadas)
    for i in list(range(0, len(suave), passo)) + ([len(suave) - 1] if (len(suave) - 1) % passo else []):
        cx = suave[i] * largura_fonte
        pts.append((i / 2.0, float(min(max(cx - largura_corte / 2, 0), largura_fonte - largura_corte))))
    expr = f"{pts[-1][1]:.1f}"
    for (ta, xa), (tb, xb) in reversed(list(zip(pts[:-1], pts[1:]))):
        expr = f"if(lt(t,{tb:.1f}),{xa:.1f}+({xb - xa:.1f})*(t-{ta:.1f}),{expr})"
    return expr


def silencios(audio: Path, t0: float, t1: float) -> list[tuple[float, float]]:
    r = rodar(["ffmpeg", "-v", "info", "-ss", t0, "-t", t1 - t0, "-i", audio, "-af",
               f"silencedetect=noise=-38dB:d={PAUSA_MIN}", "-f", "null", "-"])
    sil, ini = [], None
    for linha in r.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", linha)
        if m:
            ini = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", linha)
        if m and ini is not None:
            sil.append((ini + t0, float(m.group(1)) + t0))
            ini = None
    return sil


def montar_trechos(trechos, sil):
    segs = []
    for sa, sb in trechos:
        pos = sa
        for a, b in sil:
            if b - a > PAUSA_MIN and a > sa + 0.3 and b < sb - 0.3 and a >= pos and b <= sb:
                segs.append((pos, a + KEEP))
                pos = b - KEEP
        segs.append((pos, sb))
    return segs


def preparar(video: Path, saida: Path, trechos, largura: int, altura: int, isolar: bool, modelo: Path | None,
             transcrever: bool, modelo_whisper: str, idioma: str, rastreio: str = "brilho", zoom: float = 1.0, ypos: float = 0.0) -> dict:
    saida.mkdir(parents=True, exist_ok=True)
    t_ini, t_fim = min(a for a, _ in trechos), max(b for _, b in trechos)
    crop0 = max(0.0, t_ini - 6.0)
    dur_video = duracao(video)
    t_fim_rastro = min(dur_video, t_fim + 2)
    tmp = Path(tempfile.mkdtemp(prefix="corte_"))
    try:
        audio16 = tmp / "audio16k.wav"
        rodar(["ffmpeg", "-v", "error", "-y", "-ss", crop0, "-t", t_fim_rastro - crop0, "-i", video, "-vn", "-ac", "1", "-ar", 16000, audio16])
        # as funções de silêncio usam tempo absoluto: o áudio extraído começa em crop0
        sil = [(a, b) for a, b in silencios(audio16, t_ini - crop0, t_fim - crop0)]
        sil = [(a + crop0, b + crop0) for a, b in sil]
        segs = montar_trechos(trechos, sil)
        cum, o = [], 0.0
        for a, b in segs:
            cum.append(o)
            o += b - a
        dur = o
        print(f"{len(segs)} trechos, {dur:.1f} s depois de tirar as pausas")

        xs = (rastrear_cor if rastreio == "cor" else rastrear_centro)(video, crop0, t_fim_rastro)
        # largura da fonte e do recorte 9:16 (a altura da fonte vira a altura do vídeo)
        info_v = json.loads(rodar(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", video]).stdout)["streams"][0]
        wf, hf = int(info_v["width"]), int(info_v["height"])
        hc = int(round(hf / zoom / 2)) * 2
        wc = int(round(hc * largura / altura / 2)) * 2
        yc = int(round((hf - hc) * ypos))
        expr = expressao_x(xs, wf, wc)

        n = len(segs)
        partes_v = [f"[cv{i}]trim={s - crop0:.3f}:{e - crop0:.3f},setpts=PTS-STARTPTS[v{i}]" for i, (s, e) in enumerate(segs)]
        fc = (f"[0:v]fps=30,crop={wc}:{hc}:x='{expr}':y={yc},scale={largura}:{altura}:flags=lanczos[cv];"
              f"[cv]split={n}" + "".join(f"[cv{i}]" for i in range(n)) + ";" + ";".join(partes_v) + ";"
              + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vo]")
        if rastreio == "cor":
            # pregador pequeno e rápido: uma curva por trecho (tempo local), pontos de 0,5 s e pouca suavização
            # câmera parada: só desliza quando o pregador chega perto da borda do recorte (zona morta), depois suaviza
            folga = 0.5 * (wc / wf) * 0.4
            c, cam_x = xs[0], []
            for x in xs:
                if x > c + folga:
                    c = x - folga
                elif x < c - folga:
                    c = x + folga
                cam_x.append(c)
            k = np.exp(-0.5 * (np.arange(-6, 7) / 1.6) ** 2); k /= k.sum()
            suave = np.convolve(np.pad(cam_x, 6, mode="edge"), k, mode="valid")
            partes = []
            for i, (s_, e_) in enumerate(segs):
                i0, i1 = int((s_ - crop0) * 2), min(len(suave) - 1, int((e_ - crop0) * 2) + 1)
                pts = [(idx / 2.0 - (s_ - crop0), float(min(max(suave[idx] * wf - wc / 2, 0), wf - wc))) for idx in range(i0, i1 + 1)]
                ex = f"{pts[-1][1]:.1f}"
                for (ta, xa), (tb, xb) in reversed(list(zip(pts[:-1], pts[1:]))):
                    ex = f"if(lt(t,{tb:.2f}),{xa:.1f}+({xb - xa:.1f})*(t-{ta:.2f})/{max(tb - ta, 0.01):.2f},{ex})"
                partes.append(f"[fps]trim={s_ - crop0:.3f}:{e_ - crop0:.3f},setpts=PTS-STARTPTS,crop={wc}:{hc}:x='{ex}':y={yc},"
                              f"scale={largura}:{altura}:flags=lanczos[v{i}]")
            fc = ("[0:v]fps=30[fps0];[fps0]split=" + str(n) + "".join(f"[fps{i}]" for i in range(n)) + ";"
                  + ";".join(pp.replace("[fps]", f"[fps{i}]") for i, pp in enumerate(partes)) + ";"
                  + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vo]")
        fcarq = tmp / "fc.txt"
        fcarq.write_text(fc)
        rodar(["ffmpeg", "-v", "error", "-y", "-ss", crop0, "-t", t_fim_rastro - crop0, "-i", video,
               "-filter_complex_script", fcarq, "-map", "[vo]", "-an", "-c:v", "libx264", "-crf", 17, "-preset", "fast",
               "-pix_fmt", "yuv420p", saida / "base.mp4"])

        # voz: do áudio original ou isolada
        fonte_voz = tmp / "voz_origem.wav"
        rodar(["ffmpeg", "-v", "error", "-y", "-ss", crop0, "-t", t_fim_rastro - crop0, "-i", video, "-vn", "-ac", 2, "-ar", 44100, fonte_voz])
        if isolar:
            sep = shutil.which("audio-separator")
            if not sep or not modelo or not modelo.exists():
                sys.exit("para --isolar-voz preciso do audio-separator instalado e do --modelo-voz (UVR-MDX-NET-Voc_FT.onnx)")
            rodar([sep, fonte_voz, "--model_filename", modelo.name, "--model_file_dir", modelo.parent, "--output_format", "WAV",
                   "--output_dir", tmp / "sep", "--single_stem", "Vocals"])
            fonte_voz = next((tmp / "sep").glob("*Vocals*.wav"))
        m = len(segs)
        fa = (f"[0:a]asplit={m}" + "".join(f"[a{i}]" for i in range(m)) + ";"
              + ";".join(f"[a{i}]atrim={s - crop0:.3f}:{e - crop0:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={e - s - 0.015:.3f}:d=0.015[t{i}]" for i, (s, e) in enumerate(segs)) + ";"
              + "".join(f"[t{i}]" for i in range(m)) + f"concat=n={m}:v=0:a=1[o]")
        farq = tmp / "fa.txt"
        farq.write_text(fa)
        voz_bruta = tmp / "voz_colada.wav"
        rodar(["ffmpeg", "-v", "error", "-y", "-i", fonte_voz, "-filter_complex_script", farq, "-map", "[o]", "-ac", 2, "-ar", 48000, voz_bruta])
        rodar(["ffmpeg", "-v", "error", "-y", "-i", voz_bruta, "-af", "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", 48000, saida / "voz.wav"])

        if transcrever:
            from faster_whisper import WhisperModel
            wm = WhisperModel(modelo_whisper, device="cpu", compute_type="int8")
            seg, _ = wm.transcribe(str(audio16), language=idioma, word_timestamps=True, beam_size=5)
            palavras = []
            for s in seg:
                for w in s.words:
                    palavras.append({"w": w.word.strip(), "s": round(w.start + crop0, 2), "e": round(w.end + crop0, 2)})
            (saida / "palavras.json").write_text(json.dumps(palavras, ensure_ascii=False))
            print(f"{len(palavras)} palavras transcritas em palavras.json (confira e corrija os erros antes de legendar)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    info = {"dur": dur, "segs": segs, "crop0": crop0, "largura": largura, "altura": altura}
    (saida / "info.json").write_text(json.dumps(info))
    print(f"pronto em {saida}: base.mp4, voz.wav, info.json")
    return info


def autoteste() -> None:
    """Fabrica um vídeo de 20 s (barra clara que anda sobre fundo escuro, com tom e pausa) e confere a saída."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        rodar(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x101830:s=1280x720:r=30:d=20",
               "-f", "lavfi", "-i", "sine=f=300:d=20", "-filter_complex",
               "[0:v]drawbox=x='400+t*10':y=0:w=160:h=300:color=white:t=fill[v];[1:a]volume='if(between(t,8,10),0,0.5)':eval=frame[a]",
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", d / "fonte.mp4"])
        info = preparar(d / "fonte.mp4", d / "saida", [(1.0, 7.5), (10.5, 18.0)], 540, 960, False, None, False, "small", "pt")
        assert (d / "saida" / "base.mp4").exists() and (d / "saida" / "voz.wav").exists()
        v = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(d / "saida" / "base.mp4")], capture_output=True, text=True).stdout.strip()
        assert v == "540,960", v
        assert abs(duracao(d / "saida" / "base.mp4") - info["dur"]) < 0.15
        print("autoteste ok")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", nargs="?", type=Path)
    p.add_argument("saida", nargs="?", type=Path)
    p.add_argument("--trechos", help='"início:fim,início:fim" em segundos do vídeo original')
    p.add_argument("--largura", type=int, default=1080)
    p.add_argument("--altura", type=int, default=1920)
    p.add_argument("--rastreio", choices=["brilho", "cor"], default="brilho", help="cor = segue o paletó azul (câmera aberta)")
    p.add_argument("--zoom", type=float, default=1.0, help="ampliação do recorte (1,5 = recorte de 2/3 da altura)")
    p.add_argument("--ypos", type=float, default=0.0, help="0 = recorte colado no alto, 1 = embaixo")
    p.add_argument("--isolar-voz", action="store_true")
    p.add_argument("--modelo-voz", type=Path, default=None, help="UVR-MDX-NET-Voc_FT.onnx")
    p.add_argument("--transcrever", action="store_true", help="grava palavras.json (faster-whisper)")
    p.add_argument("--modelo-whisper", default="small")
    p.add_argument("--idioma", default="pt")
    p.add_argument("--autoteste", action="store_true")
    a = p.parse_args()
    if a.autoteste:
        return autoteste()
    if not (a.video and a.saida and a.trechos):
        p.error("preciso do vídeo, da pasta de saída e de --trechos")
    preparar(a.video, a.saida, trechos_de_texto(a.trechos), a.largura, a.altura, a.isolar_voz, a.modelo_voz,
             a.transcrever, a.modelo_whisper, a.idioma, a.rastreio, a.zoom, a.ypos)


if __name__ == "__main__":
    main()
