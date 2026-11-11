"""FREMEX — logotipo (Etapa 2). Direção aprovada: A · Vetor.

Geometria construída sobre uma caixa de 100 unidades. Regras:
  * traço do símbolo: S = 17 u; traço do lettering: 20 u (caixa-alta 100 u)
  * ângulo do vetor: a diagonal "/" desloca 0,449 u na horizontal por 1 u na
    vertical (~24,2° da vertical). Todo corte diagonal da marca usa esse ângulo.
  * respiro entre F e X: GAP = 6 u (versão reduzida: 10 u)

    python3 brand/_build/logo.py
"""
from pathlib import Path
import math

OUT = Path(__file__).resolve().parents[1] / "logos" / "fremex"
INK, WHITE, BLUE, NAVY = "#080A0F", "#F3F4F6", "#2459A6", "#101D35"
H = 100.0
S = 17.0
SLOPE = ((100 - S * 0.62) - (34 + S * 0.62)) / 100  # 0.449
ANGLE = math.degrees(math.atan(SLOPE))


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def poly(pts, dx=0.0, dy=0.0):
    return "M" + " L".join(f"{f(x + dx)} {f(y + dy)}" for x, y in pts) + "Z"


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def diag(x0, y0, x1, y1, w):
    ang = math.atan2(abs(y1 - y0), abs(x1 - x0))
    k = w / math.sin(ang)
    return [(x0 - k / 2, y0), (x0 + k / 2, y0), (x1 + k / 2, y1), (x1 - k / 2, y1)]


# ------------------------------------------------------------------ símbolo
def symbol_shapes(s=S, gap=6.0):
    """Retorna (formas do F, formas do X). Caixa 100x100."""
    x_top, x_bot = 100 - s * 0.62, 34 + s * 0.62
    slope = (x_top - x_bot) / 100
    k = (s * 1.04) * (1 + slope ** 2) ** 0.5

    def f_bar(y):
        xr = x_top - slope * y - k / 2 - gap
        return [(0, y), (xr, y), (xr - slope * s, y + s), (0, y + s)]

    F = [rect(0, 0, s, 100), f_bar(0), f_bar(50 - s / 2)]
    X = [diag(x_top, 0, x_bot, 100, s * 1.04),
         diag(x_top - slope * 50, 50, 100 - s * 0.62, 100, s * 1.04)]
    return F, X


def symbol(color=WHITE, accent=BLUE, reduced=False):
    F, X = symbol_shapes(20.0, 10.0) if reduced else symbol_shapes()
    return (f'<path fill="{color}" d="{"".join(poly(q) for q in F)}"/>'
            f'<path fill="{accent}" d="{"".join(poly(q) for q in X)}"/>')


def slash_slices(s=S):
    """A diagonal "/" dividida em 3 faixas (linguagem de movimento herdada da C)."""
    x_top, x_bot = 100 - s * 0.62, 34 + s * 0.62
    w = s * 1.04
    k = w / math.sin(math.atan2(100, x_top - x_bot))
    parts, gap = [0.44, 0.26, 0.16], 0.07
    out, cur = [], -k / 2
    for p in parts:
        a, b = cur, cur + p * k
        out.append([(x_top + a, 0), (x_top + b, 0), (x_bot + b, 100), (x_bot + a, 100)])
        cur = b + gap * k
    return out


# ------------------------------------------------------------------ lettering
LS = 20.0  # traço do lettering


def cut_bar(x, y, w):
    """Barra com terminal direito cortado no ângulo do vetor."""
    c = LS * SLOPE
    return [(x, y), (x + w, y), (x + w - c, y + LS), (x, y + LS)]


def glyph(ch):
    s = LS
    if ch == "F":
        w = 76
        return w, [rect(0, 0, s, H), cut_bar(0, 0, w), cut_bar(0, (H - s) / 2, w * 0.84)]
    if ch == "E":
        w = 76
        return w, [rect(0, 0, s, H), cut_bar(0, 0, w), cut_bar(0, (H - s) / 2, w * 0.84), cut_bar(0, H - s, w)]
    if ch == "R":
        w, b = 84, 62.0
        c = s * 0.9                          # chanfro do bojo, no ângulo de 45°
        ci = max(c - s * 0.414, 0.01)
        outer = [(0, 0), (w - c, 0), (w, c), (w, b), (0, b)]
        inner = [(s, s), (w - s - ci, s), (w - s, s + ci), (w - s, b - s), (s, b - s)]
        bowl = poly(outer) + poly(inner[::-1])
        k = s * 1.06 * (1 + SLOPE ** 2) ** 0.5
        x_end = w - k / 2
        y0 = b - s
        x_start = x_end - SLOPE * (H - y0)
        leg = [(x_start - k / 2, y0), (x_start + k / 2, y0), (x_end + k / 2, H), (x_end - k / 2, H)]
        return w, [rect(0, 0, s, H), leg], bowl
    if ch == "M":
        w, v = 106, 74.0
        return w, [rect(0, 0, s, H), rect(w - s, 0, s, H),
                   diag(s * 0.55, 0, w / 2, v, s * 1.02), diag(w - s * 0.55, 0, w / 2, v, s * 1.02)]
    if ch == "X":
        w = 90
        return w, [diag(s * 0.62, 0, w - s * 0.62, H, s * 1.05), diag(w - s * 0.62, 0, s * 0.62, H, s * 1.05)]
    raise KeyError(ch)


KERN = {"FR": 12, "RE": 16, "EM": 15, "ME": 15, "EX": 9}


def wordmark(color=WHITE, x_color=None):
    x, out, word = 0.0, [], "FREMEX"
    for i, ch in enumerate(word):
        g = glyph(ch)
        w, shapes = g[0], g[1]
        extra = g[2] if len(g) > 2 else ""
        fill = x_color if (x_color and ch == "X") else color
        d = "".join(poly(p, dx=x) for p in shapes)
        if extra:  # bojo do R com contraforma (regra evenodd)
            out.append(f'<path fill="{fill}" fill-rule="evenodd" transform="translate({f(x)} 0)" d="{extra}"/>')
        out.append(f'<path fill="{fill}" d="{d}"/>')
        if i < len(word) - 1:
            x += w + KERN[word[i:i + 2]]
        else:
            x += w
    return x, "".join(out)


# ------------------------------------------------------------------ assinaturas
WM_SCALE = 0.58     # altura do lettering = 58% do símbolo
LOCK_GAP = 40


def horizontal(color=WHITE, accent=BLUE, x_color=None):
    ww, wm = wordmark(color, x_color)
    y = (100 - H * WM_SCALE) / 2
    body = (symbol(color, accent) +
            f'<g transform="translate({f(100 + LOCK_GAP)} {f(y)}) scale({WM_SCALE})">{wm}</g>')
    return 100 + LOCK_GAP + ww * WM_SCALE, 100, body


def vertical(color=WHITE, accent=BLUE):
    ww, wm = wordmark(color)
    sc = 0.34
    tw = ww * sc
    W = max(tw, 100)
    body = (f'<g transform="translate({f((W - 100) / 2)} 0)">{symbol(color, accent)}</g>'
            f'<g transform="translate({f((W - tw) / 2)} 136) scale({sc})">{wm}</g>')
    return W, 136 + H * sc, body


def monogram(tile=BLUE, color=WHITE, accent=INK):
    c = 22  # selo com o canto superior direito chanfrado (mesmo chanfro do R)
    seal = [(0, 0), (100 - c, 0), (100, c), (100, 100), (0, 100)]
    return (f'<path fill="{tile}" d="{poly(seal)}"/>'
            f'<g transform="translate(22 22) scale(.56)">{symbol(color, accent)}</g>')


def svg(w, h, body, title, pad=0, bg=None, radius=0):
    vb = f"{f(-pad)} {f(-pad)} {f(w + 2 * pad)} {f(h + 2 * pad)}"
    bgr = (f'<rect x="{f(-pad)}" y="{f(-pad)}" width="{f(w + 2 * pad)}" height="{f(h + 2 * pad)}" '
           f'rx="{f(radius)}" fill="{bg}"/>') if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{bgr}{body}</svg>\n')


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    ww, wm = wordmark()
    _, wm_k = wordmark(INK)
    _, wm_x = wordmark(WHITE, BLUE)
    hw, hh, hb = horizontal()
    files = {
        "01-logotipo.svg": svg(ww, H, wm, "FREMEX"),
        "01-logotipo-preto.svg": svg(ww, H, wm_k, "FREMEX"),
        "02-simbolo.svg": svg(100, 100, symbol(), "FREMEX símbolo"),
        "02-simbolo-fundo-claro.svg": svg(100, 100, symbol(INK, BLUE), "FREMEX símbolo"),
        "03-monograma.svg": svg(100, 100, monogram(), "FREMEX monograma"),
        "04-horizontal.svg": svg(hw, hh, hb, "FREMEX"),
        "04-horizontal-fundo-claro.svg": svg(*horizontal(INK, BLUE), "FREMEX"),
        "05-vertical.svg": svg(*vertical(), "FREMEX"),
        "05-vertical-fundo-claro.svg": svg(*vertical(INK, BLUE), "FREMEX"),
        "06-mono-branca.svg": svg(*horizontal(WHITE, WHITE), "FREMEX"),
        "07-mono-preta.svg": svg(*horizontal(INK, INK), "FREMEX"),
        "08-destaque-azul.svg": svg(*horizontal(WHITE, BLUE, BLUE), "FREMEX"),
        "08-sobre-azul.svg": svg(*horizontal(WHITE, WHITE), "FREMEX", pad=30, bg=BLUE),
        "09-icone-app.svg": svg(100, 100, f'<g transform="translate(24 24) scale(.52)">{symbol()}</g>',
                                "FREMEX", bg=INK, radius=22),
        "09-favicon.svg": svg(100, 100, f'<g transform="translate(18 18) scale(.64)">{symbol(WHITE, WHITE, reduced=True)}</g>',
                              "FREMEX", bg=BLUE, radius=20),
        "10-marca-dagua.svg": svg(100, 100, symbol(WHITE, WHITE, reduced=True), "FREMEX"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    return files


if __name__ == "__main__":
    build()
    print(f"ângulo do vetor: {ANGLE:.1f}° da vertical; SVGs em {OUT}")
