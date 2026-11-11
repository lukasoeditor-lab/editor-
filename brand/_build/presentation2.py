"""Monta a apresentação da Etapa 2 (logotipo).

    python3 brand/_build/presentation2.py
"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).parent))
import logo as L  # noqa: E402
import concepts as C  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE.parent / "apresentacao" / "etapa-2-logotipo.html"


def svg(w, h, body, label, cls="", x=0, y=0):
    return (f'<svg class="{cls}" viewBox="{L.f(x)} {L.f(y)} {L.f(w)} {L.f(h)}" role="img" '
            f'aria-label="{label}">{body}</svg>')


def construction():
    F, X = L.symbol_shapes()
    grid = "".join(f'<path d="M{i} 0V100M0 {i}H100" stroke="#2459A6" stroke-opacity=".28" stroke-width=".25"/>'
                   for i in range(0, 101, 10))
    shapes = (f'<path fill="#F3F4F6" fill-opacity=".1" stroke="#F3F4F6" stroke-width=".5" d="{"".join(L.poly(q) for q in F)}"/>'
              f'<path fill="#2459A6" fill-opacity=".35" stroke="#6A96DE" stroke-width=".5" d="{"".join(L.poly(q) for q in X)}"/>')
    x_top = 100 - L.S * 0.62
    x_bot = 34 + L.S * 0.62
    t = 'font-family="IBM Plex Mono, monospace" font-size="4" fill="#9BA6BA"'
    ann = (
        # eixo da diagonal e ângulo
        f'<path d="M{L.f(x_top)} -8 L{L.f(x_bot)} 108" stroke="#6A96DE" stroke-width=".4" stroke-dasharray="1.5 1"/>'
        f'<path d="M{L.f(x_bot)} 108 V70" stroke="#9BA6BA" stroke-width=".4" stroke-dasharray="1 1"/>'
        f'<path d="M{L.f(x_bot)} 84 A24 24 0 0 0 {L.f(x_bot + 24 * 0.41)} {L.f(108 - 24 * 0.912)}" fill="none" stroke="#6A96DE" stroke-width=".5"/>'
        f'<text x="{L.f(x_bot - 22)}" y="80" {t}>24,2°</text>'
        # espessura do traço
        f'<path d="M0 108H{L.f(L.S)}M0 106V110M{L.f(L.S)} 106V110" stroke="#F3F4F6" stroke-width=".5"/>'
        f'<text x="0" y="116" {t}>S = 17 u</text>'
        # eixo central
        f'<path d="M-6 50H106" stroke="#F3F4F6" stroke-opacity=".5" stroke-width=".3" stroke-dasharray="2 1.5"/>'
        f'<text x="-30" y="51.4" {t}>eixo 50</text>'
        # respiro
        f'<circle cx="60.5" cy="50" r="5.5" fill="none" stroke="#F0C77A" stroke-width=".5"/>'
        f'<path d="M57 54 L40 72" stroke="#F0C77A" stroke-width=".4"/>'
        f'<text x="20" y="77" {t} fill="#F0C77A">respiro 6 u</text>'
        f'<text x="102" y="4" {t}>100 u</text>'
    )
    return svg(160, 136, grid + shapes + ann, "Construção do símbolo sobre grade de 10 unidades",
               "diagram", x=-32, y=-12)


def clearspace():
    w, h, body = L.horizontal()
    p = 2 * L.S
    t = 'font-family="IBM Plex Mono, monospace" font-size="9" fill="#F0C77A"'
    box = (f'<rect x="{-p}" y="{-p}" width="{L.f(w + 2 * p)}" height="{L.f(h + 2 * p)}" fill="none" '
           f'stroke="#F0C77A" stroke-width="1.2" stroke-dasharray="5 4"/>'
           f'<rect x="{-p}" y="{-p}" width="{p}" height="{p}" fill="#F0C77A" fill-opacity=".18"/>'
           f'<text x="{-p + 4}" y="{-p + 22}" {t}>2S</text>'
           f'<rect x="0" y="0" width="{L.f(w)}" height="{h}" fill="none" stroke="#9BA6BA" stroke-width=".6" stroke-opacity=".5"/>')
    return svg(w + 2 * p + 4, h + 2 * p + 4, box + body, "Área de proteção do logotipo", "diagram",
               x=-p - 2, y=-p - 2)


def motion():
    F, X = L.symbol_shapes()
    sl = L.slash_slices()
    s = "".join(f'<path class="sl sl{i}" fill="#2459A6" d="{L.poly(q)}"/>' for i, q in enumerate(sl))
    return svg(100, 100,
               f'<path class="mF" fill="#F3F4F6" d="{"".join(L.poly(q) for q in F)}"/>' + s +
               f'<path class="mX" fill="#2459A6" d="{L.poly(X[0])}"/>'
               f'<path class="mA" fill="#2459A6" d="{L.poly(X[1])}"/>',
               "Animação de abertura do símbolo", "sym motion")


def main():
    L.build()
    base_css = re.search(r"<style>(.*?)</style>", (HERE / "etapa-1.template.html").read_text(encoding="utf-8"), re.S).group(1)
    ww, wm = L.wordmark()
    _, wm_x = L.wordmark(L.WHITE, L.BLUE)
    old_w, old_wm = C.wordmark("A")
    tok = {
        "base_css": base_css,
        "symbol": svg(100, 100, L.symbol(), "Símbolo FREMEX", "sym"),
        "symbol_light": svg(100, 100, L.symbol(L.INK, L.BLUE), "Símbolo FREMEX", "sym"),
        "symbol_reduced": svg(100, 100, L.symbol(reduced=True), "Símbolo FREMEX reduzido", "sym"),
        "symbol_mono_w": svg(100, 100, L.symbol(L.WHITE, L.WHITE), "Símbolo FREMEX branco", "sym"),
        "symbol_mono_w_reduced": svg(100, 100, L.symbol(L.WHITE, L.WHITE, reduced=True), "Símbolo FREMEX branco", "sym"),
        "word": svg(ww, L.H, wm, "FREMEX", "word"),
        "word_x": svg(ww, L.H, wm_x, "FREMEX", "word"),
        "word_old": svg(old_w, C.H, old_wm, "FREMEX, versão da Etapa 1", "word"),
        "monogram": svg(100, 100, L.monogram(), "Monograma FREMEX", "sym"),
        "construction": construction(),
        "clearspace": clearspace(),
        "motion": motion(),
    }
    for key, args in {"h": L.horizontal(), "h_light": L.horizontal(L.INK, L.BLUE),
                      "h_mono_w": L.horizontal(L.WHITE, L.WHITE), "h_mono_k": L.horizontal(L.INK, L.INK),
                      "h_xblue": L.horizontal(L.WHITE, L.BLUE, L.BLUE)}.items():
        tok[key] = svg(*args, "Assinatura horizontal FREMEX", "lock")
    vw, vh, vb = L.vertical()
    tok["v"] = svg(vw, vh, vb, "Assinatura vertical FREMEX", "vlock")
    html = (HERE / "etapa-2.template.html").read_text(encoding="utf-8")
    for k, v in tok.items():
        html = html.replace("{{" + k + "}}", v)
    assert "{{" not in html, html[html.index("{{"):html.index("{{") + 40]
    OUT.write_text(html, encoding="utf-8")
    print("Apresentação gerada em", OUT)


if __name__ == "__main__":
    main()
