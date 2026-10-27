#!/usr/bin/env python3
"""Monta as frases da legenda dinâmica (eventos `frase`) a partir de palavras.json.

Quebra a fala em frases (pausa entre palavras, pontuação ou limite de palavras) e escolhe a palavra-chave de
cada frase (a mais longa que não é palavra comum), ou as que você indicar. Grava um roteiro.json pronto para
o gerar_projeto.py; depois você edita à mão (corrigir texto, trocar palavra-chave, pôr efeitos).

Uso:
    uv run scripts/video/corte_pregacao/roteirizar.py palavras.json roteiro.json --ini 940.4 --fim 1016 \
        --logo @.png [--destaques "crente,rejeitando"] [--musica musica.mp3]
    uv run scripts/video/corte_pregacao/roteirizar.py --autoteste
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

COMUNS = set("""a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre e ou mas que se
já não é eu tu ele ela nós vocês você me te lhe nos lhes meu minha teu tua seu sua isso isto aquilo esse essa este esta
aquele aquela ao aos à às pra pro como quando onde mais muito pouco também só aí lá aqui foi ser está estão estar tem
têm ter vai vão ir era são sou eram há então porque pois cada todo toda todos todas""".split())


def limpar(txt: str) -> str:
    return re.sub(r"[,.?!;:]+$", "", txt.strip()).lower()


def frases(palavras: list[dict], ini: float, fim: float, pausa: float, maximo: int, destaques: set[str]):
    ps = [p for p in palavras if ini - 0.05 <= p["s"] <= fim]
    grupos, atual = [], []
    for i, p in enumerate(ps):
        atual.append(p)
        prox = ps[i + 1] if i + 1 < len(ps) else None
        fecha = prox is None or prox["s"] - p["e"] >= pausa or re.search(r"[.?!;:]$", p["w"]) or len(atual) >= maximo
        if fecha:
            grupos.append(atual)
            atual = []
    saida = []
    for g in grupos:
        # palavra-chave: indicada, senão a mais longa que não é comum (no máximo 1 por frase de até 6 palavras, 2 acima)
        cand = [i for i, p in enumerate(g) if limpar(p["w"]) in destaques]
        if not cand:
            cand = sorted((i for i, p in enumerate(g) if limpar(p["w"]) not in COMUNS and len(limpar(p["w"])) >= 6),
                          key=lambda i: -len(limpar(g[i]["w"])))[: (1 if len(g) <= 6 else 2)]
        w = []
        for i, p in enumerate(g):
            item = [re.sub(r"[,.?!;:]+$", "", p["w"]).strip() + ("," if p["w"].rstrip().endswith(",") else ""), round(p["s"], 2)]
            if i in cand:
                item.append("s")
            w.append(item)
        saida.append({"tipo": "frase", "w": w})
    return saida


def roteiro(palavras, ini, fim, pausa, maximo, destaques, logo, musica, estilo):
    ev = frases(palavras, ini, fim, pausa, maximo, destaques)
    r = {"estilo": estilo, "rotulo_topo": "ALÉM DO PÚLPITO", "logo": logo, "cauda": 1.5, "eventos": ev}
    if musica:
        r["musica"] = {"arquivo": musica, "inicio": 0, "abaixo_da_voz_db": 14}
    return r


def autoteste():
    ps = [{"w": "Deus", "s": 1.0, "e": 1.3}, {"w": "não", "s": 1.35, "e": 1.5}, {"w": "quer", "s": 1.55, "e": 1.8},
          {"w": "sacrifício.", "s": 1.9, "e": 2.6}, {"w": "Quer", "s": 3.4, "e": 3.6}, {"w": "obediência", "s": 3.65, "e": 4.3}]
    r = roteiro(ps, 0.9, 5.0, 0.5, 7, set(), "logo.png", None, "A")
    assert len(r["eventos"]) == 2, r
    assert r["eventos"][0]["w"][3][2] == "s" and r["eventos"][1]["w"][1][2] == "s", r
    print("autoteste ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("palavras", nargs="?", type=Path)
    p.add_argument("saida", nargs="?", type=Path)
    p.add_argument("--ini", type=float, default=0.0)
    p.add_argument("--fim", type=float, default=1e9)
    p.add_argument("--pausa", type=float, default=0.45, help="pausa (s) que fecha a frase")
    p.add_argument("--maximo", type=int, default=7, help="palavras por frase")
    p.add_argument("--destaques", default="", help="palavras-chave, separadas por vírgula")
    p.add_argument("--logo", default="CAMINHO/DO/PNG-DO-@.png")
    p.add_argument("--musica")
    p.add_argument("--estilo", default="A", choices=["A", "B"])
    p.add_argument("--autoteste", action="store_true")
    a = p.parse_args()
    if a.autoteste:
        return autoteste()
    if not (a.palavras and a.saida):
        p.error("preciso do palavras.json e do arquivo de saída")
    ps = json.loads(a.palavras.read_text(encoding="utf-8"))
    r = roteiro(ps, a.ini, a.fim, a.pausa, a.maximo, {limpar(x) for x in a.destaques.split(",") if x.strip()}, a.logo, a.musica, a.estilo)
    a.saida.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(r['eventos'])} frases em {a.saida}; confira o texto e as palavras-chave antes de gerar")


if __name__ == "__main__":
    main()
