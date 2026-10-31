"""Monta a versão do app para publicar como Artifact do Claude.

Uso: python3 tools/build_artifact.py <pasta-de-saida>

O Artifact já fornece <!doctype>, <head> e <body>, então a página publicada
leva só o conteúdo do <body> do app, com título e estilos no topo.
Os arquivos de apoio (CSS, JS e imagens) são copiados ao lado.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'app'
ASSETS = ['styles.css', 'app.js', 'symbol.png', 'logo.png']

# Ajustes para o quadro do Artifact, que já protege as bordas do celular
FRAME_CSS = """<style>
  .topbar { top: env(safe-area-inset-top, 0px); padding-top: 12px; }
  body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }
</style>"""


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    title = re.search(r'<title>.*?</title>', html).group(0)
    fonts = '\n'.join(re.findall(r'<link [^>]*fonts\.g[^>]*>', html))
    body = re.search(r'<body>(.*)</body>', html, re.S).group(1).strip()
    page = '\n'.join([
        title,
        '<meta name="theme-color" content="#e5e1d9">',
        fonts,
        '<link rel="stylesheet" href="styles.css">',
        FRAME_CSS,
        body,
    ])
    (out / 'index.html').write_text(page + '\n', encoding='utf-8')
    for name in ASSETS:
        shutil.copy(ROOT / name, out / name)
    print(out / 'index.html')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'dist-artifact')
