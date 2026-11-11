"""Gera os SVGs das três direções conceituais da FREMEX (Etapa 1).

Toda a geometria é construída por código: letras e símbolos são polígonos
sobre uma grade de altura de caixa-alta H = 100. Execute:
    python3 brand/_build/concepts.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "logos" / "concepts"
INK, WHITE, BLUE, NAVY = "#080A0F", "#F3F4F6", "#2459A6", "#101D35"
H = 100.0


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def poly(pts, dx=0.0, dy=0.0):
    return "M" + " L".join(f"{f(x + dx)} {f(y + dy)}" for x, y in pts) + "Z"


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def diag(x0, y0, x1, y1, w):
    """Haste diagonal com terminais horizontais e espessura óptica w."""
    import math
    ang = math.atan2(abs(y1 - y0), abs(x1 - x0))
    k = w / math.sin(ang)  # largura horizontal da haste
    return [(x0 - k / 2, y0), (x0 + k / 2, y0), (x1 + k / 2, y1), (x1 - k / 2, y1)]


def bar_cut(x, y, w, h, cut):
    """Barra com terminal direito cortado em diagonal (assinatura da direção A)."""
    return [(x, y), (x + w, y), (x + w - cut, y + h), (x, y + h)]


# ---------------------------------------------------------------- letras
def letters(style):
    s = {"A": 19, "B": 15, "C": 11}[style]
    cut = s * 0.55 if style == "A" else 0
    wide = {"A": 1.0, "B": 0.78, "C": 0.74}[style]

    def bar(x, y, w):
        return bar_cut(x, y, w, s, cut) if cut else rect(x, y, w, s)

    def F():
        w = 74 * wide
        return w, [rect(0, 0, s, H), bar(0, 0, w), bar(0, (H - s) / 2, w * 0.82)]

    def E():
        w = 74 * wide
        return w, [rect(0, 0, s, H), bar(0, 0, w), bar(0, (H - s) / 2, w * 0.82), bar(0, H - s, w)]

    def R():
        w = 80 * wide
        bowl = H * 0.56
        shapes = [rect(0, 0, s, H), rect(0, 0, w, s), rect(w - s, 0, s, bowl), rect(0, bowl - s, w, s)]
        shapes.append(diag(w * 0.55, bowl - s / 2, w - s * 0.55, H, s * 1.02))
        if style == "B":  # bojo aberto: um corte de "frame" no canto superior direito
            shapes[1] = rect(0, 0, w - s * 1.6, s)
        return w, shapes

    def M():
        w = 104 * wide
        v = H * (0.62 if style != "C" else 0.7)
        return w, [rect(0, 0, s, H), rect(w - s, 0, s, H),
                   diag(s * 0.55, 0, w / 2, v, s), diag(w - s * 0.55, 0, w / 2, v, s)]

    def X():
        w = 86 * wide
        a = diag(s * 0.62, 0, w - s * 0.62, H, s * 1.05)
        b = diag(w - s * 0.62, 0, s * 0.62, H, s * 1.05)
        return w, [a, b]

    return {"F": F, "R": R, "E": E, "M": M, "X": X}, s


def c_slices(x0, y0, x1, y1, w):
    """Divide uma haste diagonal em 3 faixas paralelas (rastro / iteração)."""
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    k = w / math.sin(ang)
    parts = [0.44, 0.26, 0.16]  # espessuras relativas
    gap = (1 - sum(parts)) / 2
    out, cur = [], -k / 2
    for p in parts:
        a, b = cur, cur + p * k
        out.append([(x0 + a, y0), (x0 + b, y0), (x1 + b, y1), (x1 + a, y1)])
        cur = b + gap * k
    return out


def wordmark(style, color=WHITE, accent=None):
    glyphs, s = letters(style)
    track = {"A": 15, "B": 13, "C": 22}[style]
    x, paths = 0.0, []
    for i, ch in enumerate("FREMEX"):
        w, shapes = glyphs[ch]()
        fill = accent if (accent and ch == "X") else color
        d = "".join(poly(p, dx=x) for p in shapes)
        paths.append(f'<path fill="{fill}" d="{d}"/>')
        x += w + track
    return x - track, "".join(paths)


# ---------------------------------------------------------------- símbolos
def symbol(style, color=WHITE, accent=BLUE):
    """Retorna o conteúdo de um símbolo numa caixa 100x100."""
    if style == "A":
        # VETOR — ligadura F+X. A barra média do F aponta para o cruzamento do X:
        # o traço que nasce no F e se torna vetor. Os terminais do F são cortados
        # no mesmo ângulo da diagonal "/", com um respiro constante entre as partes.
        s, gap = 17, 5.5
        x_top, x_bot = 100 - s * 0.62, 34 + s * 0.62
        slope = (x_top - x_bot) / 100
        k = (s * 1.04) * (1 + slope ** 2) ** 0.5

        def f_bar(y):
            xr = x_top - slope * y - k / 2 - gap
            return [(0, y), (xr, y), (xr - slope * s, y + s), (0, y + s)]

        p = [rect(0, 0, s, 100), f_bar(0), f_bar(50 - s / 2)]
        d1 = diag(x_top, 0, x_bot, 100, s * 1.04)
        d2 = diag(x_top - slope * 50, 50, 100 - s * 0.62, 100, s * 1.04)
        return (f'<path fill="{color}" d="{"".join(poly(q) for q in p)}"/>'
                f'<path fill="{accent}" d="{poly(d1)}{poly(d2)}"/>')
    if style == "B":
        # FRAME — o F é o canto de um quadro (haste + topo); o X, no mesmo peso,
        # fecha o canto oposto. Juntos desenham a moldura sem fechá-la.
        s = 14
        p = [rect(0, 0, s, 100), rect(0, 0, 100, s), rect(0, 43, 40, s)]
        xs = [diag(52 + s * 0.6, 52, 100 - s * 0.6, 100, s),
              diag(100 - s * 0.6, 52, 52 + s * 0.6, 100, s)]
        return (f'<path fill="{color}" d="{"".join(poly(q) for q in p)}"/>'
                f'<path fill="{accent}" d="{"".join(poly(q) for q in xs)}"/>')
    # C — ITERAÇÃO: um X onde a haste descendente é decomposta em faixas,
    # como quadros de um movimento. Constante + variável = evolução.
    s = 22
    solid = diag(100 - s * 0.6, 0, s * 0.6, 100, s * 1.0)
    sl = c_slices(s * 0.6, 0, 100 - s * 0.6, 100, s * 1.0)
    return (f'<path fill="{accent}" d="{"".join(poly(q) for q in sl)}"/>'
            f'<path fill="{color}" d="{poly(solid)}"/>')


def svg(view_w, view_h, body, title, bg=None, pad=0):
    bgr = f'<rect x="{-pad}" y="{-pad}" width="{view_w + 2*pad}" height="{view_h + 2*pad}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(-pad)} {f(-pad)} {f(view_w + 2*pad)} {f(view_h + 2*pad)}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{bgr}{body}</svg>')


def horizontal(style, color=WHITE, accent=BLUE, xaccent=None):
    ww, wm = wordmark(style, color, xaccent)
    scale = 0.62
    gap = 46
    sym = f'<g>{symbol(style, color, accent)}</g>'
    word = f'<g transform="translate({f(100 + gap)} {f((100 - H*scale)/2)}) scale({scale})">{wm}</g>'
    return 100 + gap + ww * scale, 100, sym + word


def vertical(style, color=WHITE, accent=BLUE):
    ww, wm = wordmark(style, color)
    scale = 0.36
    tw = ww * scale
    total_w = max(tw, 100)
    sym = f'<g transform="translate({f((total_w-100)/2)} 0)">{symbol(style, color, accent)}</g>'
    word = f'<g transform="translate({f((total_w-tw)/2)} 140) scale({scale})">{wm}</g>'
    return total_w, 140 + H * scale, sym + word


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    names = {"A": "vetor", "B": "frame", "C": "iteracao"}
    parts = {}
    for st, nm in names.items():
        ww, wm = wordmark(st)
        files = {
            f"{st}-{nm}-simbolo.svg": svg(100, 100, symbol(st), f"FREMEX símbolo — direção {st}"),
            f"{st}-{nm}-logotipo.svg": svg(ww, H, wm, f"FREMEX logotipo — direção {st}"),
            f"{st}-{nm}-horizontal.svg": svg(*horizontal(st), f"FREMEX horizontal — direção {st}"),
            f"{st}-{nm}-vertical.svg": svg(*vertical(st), f"FREMEX vertical — direção {st}"),
            f"{st}-{nm}-icone-app.svg": svg(100, 100, f'<g transform="translate(26 26) scale(.48)">{symbol(st)}</g>',
                                           f"FREMEX ícone — direção {st}", bg=INK),
        }
        for fn, content in files.items():
            (OUT / fn).write_text(content + "\n", encoding="utf-8")
        parts[st] = {
            "symbol": symbol(st), "symbol_dark": symbol(st, INK, BLUE),
            "symbol_mono_w": symbol(st, WHITE, WHITE), "symbol_mono_k": symbol(st, INK, INK),
            "word": (ww, wm), "word_dark": wordmark(st, INK),
            "horizontal": horizontal(st), "horizontal_dark": horizontal(st, INK, BLUE),
            "vertical": vertical(st),
        }
    return parts


if __name__ == "__main__":
    build()
    print("SVGs gerados em", OUT)
