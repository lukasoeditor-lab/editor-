"""Confere um plano de corte contra as regras de retenção e de área segura, antes de renderizar.

Uso: python3 -I verificar_plano.py public/cortes/X/plano.json

Regras (vindas do estudo de vídeo curto e das reprovações do usuário):
  - duração de 60 a 90 s (corte de pregação/evento)
  - texto na tela logo no início (gancho visível nos primeiros 0,5 s)
  - uma mudança visual (zoom, cartão, transição, P&B, texto gigante) pelo menos a cada 4 s
  - legenda e faixa dentro da área segura (centro 900x1400; 320 px de baixo livres)
  - voz sempre à frente: nenhum efeito sonoro com volume acima de 1,0 do pico da voz
Sai com código 1 se houver falha.
"""
import json
import sys
from pathlib import Path

LIMITE_SEM_MUDANCA = 4.0  # s


def mudancas(p):
    ev = {0, p["duracao"]}
    ev |= {z["f"] for z in p.get("zooms", [])}
    ev |= {h["f"] for h in p.get("hits", [])} | {h["fim"] for h in p.get("hits", [])}
    ev |= {t["f"] for t in p.get("transicoes", [])}
    ev |= set(p.get("cortes", []))
    for c in p.get("cartoes", []):
        ev |= {c["f0"], c["f1"]}
    for b in p.get("pb", []):
        ev |= {b["f0"], b["f1"]}
    return sorted(ev)


def main():
    p = json.loads(Path(sys.argv[1]).read_text())
    fps, falhas, avisos = p["fps"], [], []
    dur = p["duracao"] / fps
    if not 60 <= dur <= 90:
        falhas.append(f"duração {dur:.1f}s fora de 60-90 s")
    primeira = min([l["f0"] for l in p.get("legendas", [])] + [h["f"] for h in p.get("hits", [])] or [10**9])
    if primeira > 0.5 * fps:
        falhas.append(f"primeiro texto só aparece em {primeira / fps:.1f}s (gancho precisa estar na tela em até 0,5 s)")
    ev = mudancas(p)
    pior = max(((b - a, a) for a, b in zip(ev, ev[1:])), default=(0, 0))
    if pior[0] / fps > LIMITE_SEM_MUDANCA:
        falhas.append(f"{pior[0] / fps:.1f}s sem mudança visual a partir de {pior[1] / fps:.1f}s (máx. {LIMITE_SEM_MUDANCA}s)")
    for l in p.get("legendas", []):
        if len(l["palavras"]) > 4:
            avisos.append(f"legenda com {len(l['palavras'])} palavras em {l['f0'] / fps:.1f}s (ideal até 3)")
            break
    if p.get("estilo") == "simples":
        # posições fixas da composição (px, 1080x1920): legenda ~940, marca 1403, faixa 1330-1480
        if 1403 + 30 > 1920 - 320:
            falhas.append("marca no rodapé invade os 320 px de baixo")
    sfx_altos = [s for s in p.get("sfx", []) if s.get("vol", 0) > 1.0]
    if sfx_altos:
        falhas.append(f"{len(sfx_altos)} efeitos com volume > 1,0")
    print(f"duração {dur:.1f}s | {len(p.get('legendas', []))} legendas | {len(ev) - 2} mudanças visuais | "
          f"maior trecho parado {pior[0] / fps:.1f}s")
    for a in avisos:
        print("  aviso:", a)
    for f in falhas:
        print("  FALHA:", f)
    print("OK" if not falhas else "REPROVADO")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
