"""Monta a apresentação da Etapa 1 a partir dos SVGs gerados em concepts.py.

    python3 brand/_build/presentation.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import concepts as c  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TPL = Path(__file__).parent / "etapa-1.template.html"
OUT = ROOT / "apresentacao" / "etapa-1-direcao-criativa.html"


def svg(w, h, body, label, cls=""):
    return (f'<svg class="{cls}" viewBox="0 0 {c.f(w)} {c.f(h)}" role="img" aria-label="{label}">'
            f'{body}</svg>')


def main():
    parts = c.build()
    tokens = {}
    for st, p in parts.items():
        ww, wm = p["word"]
        _, wmd = p["word_dark"]
        tokens[f"{st}.symbol"] = svg(100, 100, p["symbol"], f"Símbolo da direção {st}", "sym")
        tokens[f"{st}.symbol_dark"] = svg(100, 100, p["symbol_dark"], f"Símbolo da direção {st} sobre fundo claro", "sym")
        tokens[f"{st}.symbol_mono_w"] = svg(100, 100, p["symbol_mono_w"], f"Símbolo {st} monocromático branco", "sym")
        tokens[f"{st}.symbol_mono_k"] = svg(100, 100, p["symbol_mono_k"], f"Símbolo {st} monocromático preto", "sym")
        tokens[f"{st}.word"] = svg(ww, c.H, wm, "FREMEX", "word")
        tokens[f"{st}.word_dark"] = svg(ww, c.H, wmd, "FREMEX", "word")
        hw, hh, hb = p["horizontal"]
        tokens[f"{st}.horizontal"] = svg(hw, hh, hb, f"Assinatura horizontal da direção {st}", "lock")
        hw, hh, hb = p["horizontal_dark"]
        tokens[f"{st}.horizontal_dark"] = svg(hw, hh, hb, f"Assinatura horizontal da direção {st} sobre fundo claro", "lock")
        vw, vh, vb = p["vertical"]
        tokens[f"{st}.vertical"] = svg(vw, vh, vb, f"Assinatura vertical da direção {st}", "vlock")
    html = TPL.read_text(encoding="utf-8")
    for k, v in tokens.items():
        html = html.replace("{{" + k + "}}", v)
    assert "{{" not in html, html[html.index("{{"):html.index("{{") + 40]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print("Apresentação gerada em", OUT)


if __name__ == "__main__":
    main()
