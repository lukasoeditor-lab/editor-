"""Monta o plano de edição de um corte: corta pausas, refaz os tempos, legendas, textos gigantes,
zooms e a lista de efeitos sonoros.

Uso: python3 -I montar_plano.py X pasta_trabalho pasta_saida
  pasta_trabalho tem raw_X.mp4 e tr_X.json (transcrever.py)
  pasta_saida (public/cortes/X) recebe plano.json; pasta_trabalho recebe ed_X.mp4 e voz_X.wav
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cortes_config import CORTES, COMUM  # noqa: E402

FPS = 30
PAUSA_MAX = 1.2           # só pausas longas viram corte; o ritmo vem de zoom e texto, sem comer fala
FOLGA_ANTES, FOLGA_DEPOIS = 0.12, 0.34
PROPRIOS = {"deus", "jeremias", "senhor", "jesus", "ele"}
# instante do pico de cada efeito sonoro dentro do arquivo (medido), em segundos
PICO = {"whoosh": 0.25, "whoosh2": 1.14, "impacto": 0.09, "impacto2": 0.02, "estalo": 0.13, "riser": 1.62}
CICLO_ZOOM = [1.0, 1.2, 1.0, 1.34, 1.08, 1.26, 1.0, 1.42]


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def limpa(s):
    return re.sub(r"[.,;:!…]", "", s).strip()


def frame(t):
    return int(round(t * FPS))


def carregar_palavras(tr, correcoes=None):
    segs = json.load(open(tr))
    c = {norm(k): v for k, v in (correcoes or {}).items()}
    out = []
    for s in segs:
        for w in s["words"]:
            raw = w["word"].strip()
            n = norm(raw)
            if n in c:
                raw = re.sub(r"[A-Za-zÀ-ÿ]+", c[n], raw, count=1)
            out.append({"t0": w["start"], "t1": w["end"], "raw": raw})
    return out


def ajustar_limite(palavras, t, lado):
    """Se t cair no meio de uma palavra, leva para a lacuna mais próxima; senão mantém."""
    if not any(w["t0"] < t < w["t1"] for w in palavras):
        return t
    melhor, dist = t, 1e9
    for a, b in zip(palavras, palavras[1:]):
        meio = (a["t1"] + b["t0"]) / 2
        if abs(meio - t) < dist:
            melhor, dist = meio, abs(meio - t)
    return melhor if dist < 0.6 else t


def spans_de_corte(palavras, trechos):
    spans = []
    for a, b in trechos:
        a, b = ajustar_limite(palavras, a, "ini"), ajustar_limite(palavras, b, "fim")
        ws = [w for w in palavras if w["t0"] >= a - 0.01 and w["t1"] <= b + 0.05]
        if not ws:
            continue
        i0 = palavras.index(ws[0])
        ant = palavras[i0 - 1]["t1"] + 0.02 if i0 > 0 else 0.0
        ini = max(ant, ws[0]["t0"] - FOLGA_ANTES)
        for prev, w in zip(ws, ws[1:]):
            if w["t0"] - prev["t1"] > PAUSA_MAX:
                spans.append((ini, prev["t1"] + 0.45))
                ini = w["t0"] - 0.45
        j = palavras.index(ws[-1])
        prox = palavras[j + 1]["t0"] - 0.03 if j + 1 < len(palavras) else 1e9
        spans.append((ini, min(ws[-1]["t1"] + FOLGA_DEPOIS, max(prox, ws[-1]["t1"] + 0.04))))
    # alinha ao quadro para que áudio e vídeo tenham exatamente a mesma duração
    out = []
    for a, b in spans:
        fa, fb = frame(a), frame(b)
        if fb - fa >= 6:
            out.append((fa / FPS, fb / FPS))
    return out


def remapear(palavras, spans):
    novos, acum = [], 0.0
    for a, b in spans:
        for w in palavras:
            if a - 0.001 <= w["t0"] and w["t1"] <= b + 0.08:
                novos.append({**w, "n0": acum + (w["t0"] - a), "n1": min(acum + (w["t1"] - a), acum + (b - a))})
        acum += b - a
    cortes, ac = [], 0.0
    for a, b in spans[:-1]:
        ac += b - a
        cortes.append(ac)
    return novos, cortes, sum(b - a for a, b in spans)


def montar_edicao(raw, saida, spans):
    f = []
    for i, (a, b) in enumerate(spans):
        d = b - a
        f.append(f"[0:v]trim=start_frame={frame(a)}:end_frame={frame(b)},setpts=PTS-STARTPTS[v{i}]")
        f.append(f"[0:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:st=0:d=0.03,afade=t=out:st={d - 0.03:.4f}:d=0.03[a{i}]")
    ins = "".join(f"[v{i}][a{i}]" for i in range(len(spans)))
    f.append(f"{ins}concat=n={len(spans)}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-filter_complex", ";".join(f),
                    "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "14",
                    "-preset", "fast", "-c:a", "aac", "-b:a", "192k", str(saida)], check=True)


def fatiar_iso_antigo(palavras, cfg, spans, origem, destino):
    """Reaproveita a voz isolada de uma edição anterior: corta, na mesma sequência, os trechos novos."""
    antigos = spans_de_corte(palavras, cfg["iso_antigo"]["trechos"])
    acum, mapa = 0.0, []
    for a, b in antigos:
        mapa.append((a, b, acum))
        acum += b - a
    partes = []
    for a, b in spans:
        for oa, ob, off in mapa:
            if a >= oa - 0.04 and b <= ob + 0.04:
                partes.append((off + max(a - oa, 0.0), off + max(a - oa, 0.0) + (b - a)))
                break
        else:
            raise SystemExit(f"trecho {a:.2f}-{b:.2f} não está dentro da edição antiga da voz isolada")
    f = []
    for i, (a, b) in enumerate(partes):
        f.append(f"[0:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:st=0:d=0.02,afade=t=out:st={b - a - 0.02:.4f}:d=0.02[a{i}]")
    f.append("".join(f"[a{i}]" for i in range(len(partes))) + f"concat=n={len(partes)}:v=0:a=1[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(origem), "-filter_complex", ";".join(f),
                    "-map", "[a]", "-c:a", "libmp3lame", "-b:a", "192k", str(destino)], check=True)


def achar_sequencia(palavras, tokens, a_partir):
    alvo = [norm(t) for t in tokens]
    for i in range(a_partir, len(palavras) - len(alvo) + 1):
        if all(norm(palavras[i + k]["raw"]) == alvo[k] for k in range(len(alvo))):
            return i
    return -1


def legendas(palavras, enfase_set):
    chunks, atual = [], []
    for i, w in enumerate(palavras):
        atual.append(i)
        fim = (re.search(r"[.,;:!?…]$", w["raw"]) is not None or len(atual) >= 3
               or sum(len(limpa(palavras[j]["raw"])) for j in atual) > 20
               or (i + 1 < len(palavras) and palavras[i + 1]["n0"] - w["n1"] > 0.3))
        if fim:
            chunks.append(atual)
            atual = []
    if atual:
        chunks.append(atual)
    saida = []
    for k, idx in enumerate(chunks):
        f0 = frame(palavras[idx[0]]["n0"])
        f1 = frame(palavras[idx[-1]]["n1"]) + 6
        if k + 1 < len(chunks):
            f1 = min(f1, frame(palavras[chunks[k + 1][0]]["n0"]))
        f1 = max(f1, f0 + 6)
        usou = False
        ps = []
        for j in idx:
            w = palavras[j]
            e = (not usou) and norm(w["raw"]) in enfase_set
            usou = usou or e
            ps.append({"f0": frame(w["n0"]), "f1": frame(w["n1"]), "txt": (limpa(w["raw"]).capitalize() if norm(w["raw"]) in PROPRIOS else limpa(w["raw"]).lower()),
                       "enfase": e})
        saida.append({"f0": f0, "f1": f1, "palavras": ps})
    return saida


def main():
    cid, trab, saida = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    cfg = CORTES[cid]
    saida.mkdir(parents=True, exist_ok=True)
    palavras = carregar_palavras(trab / f"tr_{cid}.json", cfg.get("correcoes"))
    spans = spans_de_corte(palavras, cfg["trechos"])
    novas, cortes_t, total = remapear(palavras, spans)
    if "--reusar" not in sys.argv or not (trab / f"ed_{cid}.mp4").exists():
        montar_edicao(trab / f"raw_{cid}.mp4", trab / f"ed_{cid}.mp4", spans)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(trab / f"ed_{cid}.mp4"), "-vn", "-ac", "2",
                        "-ar", "48000", str(trab / f"voz_{cid}.wav")], check=True)
    duracao = frame(total)
    antigo = trab / f"iso_antigo_{cid}.mp3"
    if cfg.get("iso_antigo") and antigo.exists():
        fatiar_iso_antigo(palavras, cfg, spans, antigo, trab / f"iso_{cid}.mp3")
        print("  voz isolada fatiada a partir da edição antiga")

    # textos gigantes
    hits, cursor = [], 0
    for h in cfg["hits"]:
        i = achar_sequencia(novas, h["fala"], cursor)
        if i < 0:
            print("  ! hit não encontrado:", h["fala"])
            continue
        cursor = i + 1
        f0 = max(0, frame(novas[i]["n0"]) - 2)
        fim = min(duracao, f0 + frame(h["dur"]))
        hits.append({"f": f0, "fim": fim, "linhas": h["texto"].split("/"), "modo": h["modo"],
                     "recorte": bool(h.get("recorte")), "riser": bool(h.get("riser"))})
    # evita sobreposição de textos gigantes
    for a, b in zip(hits, hits[1:]):
        a["fim"] = min(a["fim"], b["f"] - 1)

    # zooms: a cada corte seco, a cada texto gigante e quando passa muito tempo sem mudança
    eventos = [(frame(t), "corte") for t in cortes_t] + [(h["f"], "hit") for h in hits]
    eventos.sort()
    legs = legendas(novas, {norm(e) for e in cfg["enfase"]})
    zooms, ciclo, ult, par = [{"f": 0, "escala": 1.0, "seco": False}], 1, 0, 0
    cand = sorted(set(eventos + [(c["f0"], "frase") for c in legs]))
    for f, tipo in cand:
        if f - ult < 12:
            continue
        if tipo == "frase" and f - ult < 100:
            continue
        if tipo == "hit":
            esc = 1.5 if par % 2 else 1.34
            par += 1
        else:
            esc = CICLO_ZOOM[ciclo % len(CICLO_ZOOM)]
            ciclo += 1
            if esc == zooms[-1]["escala"]:
                esc = CICLO_ZOOM[ciclo % len(CICLO_ZOOM)]
                ciclo += 1
        zooms.append({"f": f, "escala": esc, "seco": tipo != "frase"})
        ult = f

    # efeitos sonoros (tempo = quando o arquivo começa a tocar, já com o pico alinhado ao evento)
    sfx = []
    ult_hit = -10.0
    for k, h in enumerate(hits):
        t = h["f"] / FPS
        if t - ult_hit > 2.0:
            sfx.append({"t": t - PICO["whoosh2"], "arq": "whoosh2", "vol": 0.5})
        elif t - ult_hit > 0.9:
            sfx.append({"t": t - PICO["whoosh"], "arq": "whoosh", "vol": 0.55})
        imp = "impacto" if k % 2 == 0 else "impacto2"
        sfx.append({"t": t - PICO[imp], "arq": imp, "vol": 0.9})
        sfx.append({"t": t - PICO["estalo"], "arq": "estalo", "vol": 0.4})
        if h["riser"]:
            sfx.append({"t": t - PICO["riser"], "arq": "riser", "vol": 0.7})
        ult_hit = t
    hit_frames = {h["f"] for h in hits}
    for z in zooms[1:]:
        if z["f"] not in hit_frames and z["seco"]:
            sfx.append({"t": z["f"] / FPS - PICO["whoosh"], "arq": "whoosh", "vol": 0.22})
    sfx = [s for s in sfx if s["t"] > -0.2]
    sfx.sort(key=lambda s: s["t"])

    plano = {
        "fps": FPS, "duracao": duracao, "base": f"cortes/{cid}",
        "paleta": cfg["paleta"],
        "rotulo": {"topo": COMUM["rotulo_topo"], "sub": COMUM["rotulo_sub"]},
        "marquee": cfg["marquee_padrao"],
        "zooms": zooms, "hits": hits, "legendas": legs, "sfx": sfx,
        "cortes": [frame(t) for t in cortes_t],
        "musica": cfg["musica"],
    }
    (saida / "plano.json").write_text(json.dumps(plano, ensure_ascii=False))
    print(f"{cid}: {len(spans)} trechos, {duracao} quadros ({duracao / FPS:.1f}s), {len(hits)} textos, "
          f"{len(zooms)} zooms, {len(legs)} legendas, {len(sfx)} sons")


if __name__ == "__main__":
    main()
