"""Converte documentos Markdown do curso em páginas com a identidade FREMEX.

    python3 FREMEX-COURSE/_build/md_to_page.py SAIDA.html "Título" "Etapa" doc1.md [doc2.md ...]
Requer: pip install markdown
"""
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[2]
BASE_CSS = re.search(r"<style>(.*?)</style>",
                     (ROOT / "brand/_build/etapa-1.template.html").read_text(encoding="utf-8"), re.S).group(1)
SYMBOL = (ROOT / "brand/logos/fremex/02-simbolo.svg").read_text(encoding="utf-8")
SYMBOL = re.sub(r"<title>.*?</title>", "", SYMBOL).replace("<svg ", '<svg class="mark" ', 1)

DOC_CSS = """
.doc { padding-block: clamp(32px, 6vw, 72px); }
.doc > * + * { margin-top: 1rem; }
.doc h1 { font-size: clamp(1.9rem, 4.5vw, 3.2rem); margin-bottom: 1.5rem; }
.doc h1:not(:first-child) { margin-top: 6rem; padding-top: 3rem; border-top: 2px solid var(--blue); }
.doc h2 { font-size: var(--s2); margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--line); }
.doc h3 { margin-top: 2.5rem; color: var(--ice); }
.doc p, .doc li { max-width: 72ch; }
.doc strong { color: var(--ice); font-weight: 600; }
.doc ul, .doc ol { padding-left: 1.2em; display: grid; gap: 6px; }
.doc li::marker { color: var(--blue-dig); }
.doc hr { border: 0; height: 1px; background: var(--line); margin-block: 2.5rem; }
.doc code { font-family: var(--f-mono); font-size: .88em; background: var(--navy); padding: 1px 6px; border-radius: 3px; color: var(--ice); }
.doc em { color: var(--mute); }
.doc a { word-break: break-word; }
.tbl { overflow-x: auto; margin-block: 1.5rem; border: 1px solid var(--line); }
.doc table { border-collapse: collapse; width: 100%; min-width: 640px; font-size: .9rem; }
.doc th, .doc td { text-align: left; vertical-align: top; padding: 11px 14px; border-bottom: 1px solid var(--line); }
.doc thead th { font-family: var(--f-mono); font-weight: 500; font-size: .75rem; letter-spacing: .06em; text-transform: uppercase; color: var(--blue-dig); background: var(--navy); }
.doc tbody tr:last-child td { border-bottom: 0; }
.doc td:first-child { white-space: nowrap; }
.doc h2 + p strong:first-child { color: var(--blue-dig); }
.mark { width: 28px; height: 28px; }
.bar .brand { display: flex; align-items: center; gap: 10px; }
.toc { display: flex; flex-wrap: wrap; gap: 6px 18px; font-family: var(--f-mono); font-size: var(--s-1); padding-block: 14px; border-bottom: 1px solid var(--line); }
.toc a { color: var(--mute); text-decoration: none; }
.toc a:hover { color: var(--ice); }
.docsep { margin-top: 5rem !important; }
"""


def slug(text):
    t = re.sub(r"<[^>]+>", "", text).lower()
    t = re.sub(r"[^\w\s-]", "", t)
    return "s-" + re.sub(r"\s+", "-", t).strip("-")


def convert(md_text):
    html = markdown.markdown(md_text, extensions=["tables", "sane_lists"])
    html = html.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    toc = []

    def h2(m):
        s = slug(m.group(1))
        toc.append((s, re.sub(r"<[^>]+>", "", m.group(1))))
        return f'<h2 id="{s}">{m.group(1)}</h2>'
    html = re.sub(r"<h2>(.*?)</h2>", h2, html)

    def h1(m):
        s = slug(m.group(1))
        toc.append((s, "§" + re.sub(r"<[^>]+>", "", m.group(1))))
        return f'<h1 id="{s}">{m.group(1)}</h1>'
    html = re.sub(r"<h1>(.*?)</h1>", h1, html)
    return html, toc


def main():
    out, title, stage, *docs = sys.argv[1:]
    bodies, toc = [], []
    for i, d in enumerate(docs):
        h, t = convert(Path(d).read_text(encoding="utf-8"))
        bodies.append(h if i == 0 else f'<div class="docsep"></div>{h}')
        toc += t
    import os
    lvl = os.environ.get("TOC", "h2")
    pick = (lambda n: n.startswith("§")) if lvl == "h1" else (lambda n: re.match(r"^\d", n))
    toc_html = "".join(f'<a href="#{s}">{n.lstrip("§").split(" — ")[0]}</a>' for s, n in toc if pick(n))
    page = f"""<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{BASE_CSS}{DOC_CSS}</style>
<div class="wrap">
  <div class="bar"><span class="brand">{SYMBOL}<strong>FREMEX ACADEMY</strong></span><span>{stage}</span><span>Documento de trabalho</span></div>
  <nav class="toc" aria-label="Seções">{toc_html}</nav>
  <article class="doc">{"".join(bodies)}</article>
</div>
"""
    Path(out).write_text(page, encoding="utf-8")
    print("Página gerada em", out)


if __name__ == "__main__":
    main()
