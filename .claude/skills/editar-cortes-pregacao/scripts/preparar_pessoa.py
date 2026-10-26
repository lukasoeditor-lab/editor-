"""Recorta o pastor de um vídeo horizontal e calcula a câmera virtual que o mantém centralizado.

Uso: python3 -I preparar_pessoa.py entrada.mp4 pasta_saida [modelo_rvm.onnx]

Gera em pasta_saida:
  pessoa.webm   janela móvel (JANELA_W x JANELA_H) com o pastor recortado (VP9 com alpha)
  camera.json   por quadro: [x0, y0, cx, yb] em pixels do vídeo original
                (x0,y0 = canto da janela; cx = centro horizontal do pastor; yb = linha da base do corpo)

Etapa 1: matting em baixa resolução no quadro inteiro, só para achar o pastor (a pessoa
com mais movimento, com bônus de continuidade) e suavizar o caminho da câmera.
Etapa 2: matting em alta resolução somente na janela em volta dele.
Modelo: Robust Video Matting (rvm_mobilenetv3_fp32.onnx, github.com/PeterL1n/RobustVideoMatting).
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

JANELA_W, JANELA_H = 700, 1000
SIGMA_X, SIGMA_Y = 7.0, 10.0  # suavização da câmera, em quadros


def sessao(modelo):
    return ort.InferenceSession(str(modelo), providers=["CPUExecutionProvider"])


class Rvm:
    def __init__(self, modelo, ratio):
        self.s = sessao(modelo)
        self.ratio = np.array([ratio], np.float32)
        self.rec = [np.zeros((1, 1, 1, 1), np.float32) for _ in range(4)]

    def __call__(self, bgr):
        x = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32).transpose(2, 0, 1)[None] / 255
        _, pha, *self.rec = self.s.run(
            None,
            {"src": x, "r1i": self.rec[0], "r2i": self.rec[1], "r3i": self.rec[2],
             "r4i": self.rec[3], "downsample_ratio": self.ratio},
        )
        return pha[0, 0]


def suavizar(v, sigma):
    v = np.asarray(v, np.float64)
    n = int(sigma * 4)
    k = np.exp(-0.5 * (np.arange(-n, n + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(v, n, mode="edge")
    return np.convolve(p, k, mode="valid")


def achar_pastor(entrada, modelo):
    """Etapa 1: devolve (cx, yb) por quadro, em pixels do vídeo original."""
    cap = cv2.VideoCapture(str(entrada))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    sw, sh = 480, int(round(480 * H / W))
    f = W / sw
    rvm = Rvm(modelo, 1.0)
    antes = []  # cinza dos últimos quadros, para medir movimento
    cx_l, yb_l = [], []
    prev = None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        pq = cv2.resize(fr, (sw, sh), interpolation=cv2.INTER_AREA)
        a = rvm(pq)
        cinza = cv2.GaussianBlur(cv2.cvtColor(pq, cv2.COLOR_BGR2GRAY), (5, 5), 0).astype(np.float32)
        antes.append(cinza)
        mov = np.abs(cinza - antes[max(0, len(antes) - 4)])
        n, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
        melhor, pontos = None, -1
        for i in range(1, n):
            area = st[i, cv2.CC_STAT_AREA]
            if area < 600:
                continue
            m = lab == i
            p = float(mov[m].sum()) + 0.5 * area
            if prev is not None and m[int(np.clip(prev[1], 0, sh - 1)), int(np.clip(prev[0], 0, sw - 1))]:
                p *= 1.6
            if p > pontos:
                melhor, pontos = i, p
        if melhor is None:
            cx_l.append(cx_l[-1] if cx_l else W / 2)
            yb_l.append(yb_l[-1] if yb_l else H * 0.8)
            continue
        m = (lab == melhor)
        massa = (a * m)
        linhas = massa.sum(1)
        acum = np.cumsum(linhas) / max(linhas.sum(), 1e-6)
        yb = int(np.searchsorted(acum, 0.97))
        ys, xs = np.nonzero(m)
        cx = float(np.average(xs, weights=a[ys, xs]))
        cy = float(np.average(ys, weights=a[ys, xs]))
        prev = (cx, cy)
        cx_l.append(cx * f)
        yb_l.append(yb * f)
    cap.release()
    cx_s = suavizar(cx_l, SIGMA_X)
    yb_s = suavizar(np.median(np.lib.stride_tricks.sliding_window_view(
        np.pad(yb_l, 7, mode="edge"), 15), axis=1), SIGMA_Y)
    return cx_s, yb_s, (W, H)


def recortar(entrada, saida, modelo, cx, yb, W, H, fps):
    """Etapa 2: matting na janela em volta do pastor e gravação do webm com alpha."""
    saida.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(entrada))
    rvm = Rvm(modelo, 0.55)
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{JANELA_W}x{JANELA_H}", "-r", str(fps), "-i", "-",
         "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24",
         "-row-mt", "1", "-deadline", "good", "-cpu-used", "5", "-auto-alt-ref", "0",
         str(saida / "pessoa.webm")],
        stdin=subprocess.PIPE)
    cam = []
    pad = 400
    i = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        x0 = int(round(cx[i] - JANELA_W / 2))
        y0 = int(round(yb[i] - 950))
        g = cv2.copyMakeBorder(fr, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
        janela = g[y0 + pad:y0 + pad + JANELA_H, x0 + pad:x0 + pad + JANELA_W]
        a = rvm(janela)
        a = np.clip((a - 0.06) / 0.88, 0, 1)
        a = cv2.erode(a, np.ones((2, 2), np.uint8))
        # zera o que veio da borda replicada (fora do vídeo original)
        yy = np.arange(y0, y0 + JANELA_H)[:, None]
        xx = np.arange(x0, x0 + JANELA_W)[None, :]
        a = a * ((yy >= 0) & (yy < H) & (xx >= 0) & (xx < W))
        rgba = np.dstack([janela, (a * 255).astype(np.uint8)])
        ff.stdin.write(rgba.tobytes())
        cam.append([x0, y0, round(float(cx[i]), 2), round(float(yb[i]), 2)])
        i += 1
    ff.stdin.close()
    ff.wait()
    (saida / "camera.json").write_text(json.dumps(
        {"fps": fps, "janela": [JANELA_W, JANELA_H], "fonte": [W, H], "frames": cam}))
    return len(cam)


if __name__ == "__main__":
    entrada = Path(sys.argv[1])
    saida = Path(sys.argv[2])
    modelo = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("rvm.onnx")
    cap = cv2.VideoCapture(str(entrada))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    cx, yb, (W, H) = achar_pastor(entrada, modelo)
    print("etapa 1 ok:", len(cx), "quadros", flush=True)
    n = recortar(entrada, saida, modelo, cx, yb, W, H, round(fps))
    print("etapa 2 ok:", n, "quadros", flush=True)
