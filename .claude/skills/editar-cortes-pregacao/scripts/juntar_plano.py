"""Junta plano.json (montar_plano.py) com camera.json (preparar_pessoa.py) em plano_final.json,
que é o arquivo passado ao Remotion: npx remotion render Corte out/X.mp4 --props=public/cortes/X/plano_final.json
Uso: python3 -I juntar_plano.py public/cortes/X
"""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
plano = json.loads((d / "plano.json").read_text())
plano["camera"] = json.loads((d / "camera.json").read_text())
(d / "plano_final.json").write_text(json.dumps({"plano": plano}, ensure_ascii=False))
print(d.name, "ok:", len(plano["camera"]["frames"]), "quadros de câmera,", plano["duracao"], "do plano")
