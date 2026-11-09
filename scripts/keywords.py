#!/usr/bin/env python3
"""Agrupa els CSV del Keyword Planner per pàgina i detecta canibalitzacions.

Ús:
    python3 keywords.py [carpeta-projecte]

Llegeix:  keywords/csv/*.csv  (exports del Keyword Planner, UTF-16 amb tabuladors o UTF-8)
          keywords/mapa.yaml  (quines paraules van a cada pàgina; veure l'exemple de sota)
Escriu:   keywords/keywords.csv     totes les paraules, sense duplicats, amb la pàgina assignada
          keywords/per_pagina.md    resum per pàgina: volum total, paraula principal, estacionalitat,
                                    paraules sense pàgina i paraules que encaixen en dues pàgines

Exemple de mapa.yaml:
    excloure: [gratis, pdf, curso, wikipedia]       # paraules que no volem enlloc
    pagines:
      - clau: preu
        inclou: [preu, precio, cuanto cuesta, quant costa]
        exclou: [conductos]
      - clau: sabadell
        inclou: [sabadell]
Els patrons són fragments de text (sense accents ni majúscules) o expressions regulars si comencen amb "re:".
"""
import csv
import io
import os
import re
import sys
import unicodedata
from collections import defaultdict

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML: pip install -r requirements.txt")

MESOS = ["gen", "feb", "mar", "abr", "mai", "jun", "jul", "ago", "set", "oct", "nov", "des"]
MES_EN = {"Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "Jun": 5, "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11,
          "ene": 0, "abr": 3, "ago": 7, "dic": 11}


def normal(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t.replace("·", "").replace("l l", "ll")).strip()


def numero(v):
    if v is None:
        return 0
    v = str(v).strip().replace(" ", "").replace('"', "")
    m = re.match(r"^([\d.,]+)\s*([KkM]?)", v)
    if not m:
        return 0
    n = m.group(1)
    n = n.replace(".", "").replace(",", ".") if re.search(r",\d{1,2}$", n) or n.count(".") > 1 else n.replace(",", "")
    try:
        x = float(n)
    except ValueError:
        return 0
    return x * (1000 if m.group(2) in "Kk" and m.group(2) else 1_000_000 if m.group(2) == "M" else 1)


def llegir_csv(ruta):
    b = open(ruta, "rb").read()
    for enc in ("utf-16", "utf-8-sig", "latin-1"):
        try:
            text = b.decode(enc)
            break
        except UnicodeError:
            continue
    linies = text.splitlines()
    inici = next((i for i, l in enumerate(linies) if l.lower().startswith(("keyword\t", "keyword,", "palabra clave\t", "palabra clave,"))), None)
    if inici is None:
        print(f"  ⚠ {os.path.basename(ruta)}: no trobo la capçalera «Keyword»")
        return []
    sep = "\t" if "\t" in linies[inici] else ","
    files = list(csv.DictReader(io.StringIO("\n".join(linies[inici:])), delimiter=sep))
    out = []
    for f in files:
        kw = (f.get("Keyword") or f.get("Palabra clave") or "").strip()
        if not kw:
            continue
        mesos = [0] * 12
        for k, v in f.items():
            m = re.match(r"(?:Searches|Búsquedas):\s*(\w+)", k or "")
            if m and m.group(1)[:3] in MES_EN:
                mesos[MES_EN[m.group(1)[:3]]] = numero(v)
        vol = f.get("Avg. monthly searches") or f.get("Promedio de búsquedas mensuales") or 0
        out.append({"keyword": kw, "volum": int(numero(vol)), "competencia": f.get("Competition") or f.get("Competencia") or "",
                    "cpc_baix": numero(f.get("Top of page bid (low range)") or f.get("Puja por la parte superior de la página (intervalo bajo)")),
                    "cpc_alt": numero(f.get("Top of page bid (high range)") or f.get("Puja por la parte superior de la página (intervalo alto)")),
                    "mesos": mesos, "font": os.path.basename(ruta)})
    return out


def coincideix(patro, kwn):
    if patro.startswith("re:"):
        return re.search(patro[3:], kwn) is not None
    return normal(patro) in kwn


def main():
    dir_p = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    dir_kw = os.path.join(dir_p, "keywords")
    dir_csv = os.path.join(dir_kw, "csv")
    fitxers = sorted(f for f in os.listdir(dir_csv) if f.lower().endswith(".csv")) if os.path.isdir(dir_csv) else []
    if not fitxers:
        sys.exit("No hi ha CSV a keywords/csv/")
    totes = {}
    for f in fitxers:
        for k in llegir_csv(os.path.join(dir_csv, f)):
            n = normal(k["keyword"])
            if n not in totes or k["volum"] > totes[n]["volum"]:
                totes[n] = k
    mapa = yaml.safe_load(open(os.path.join(dir_kw, "mapa.yaml"), encoding="utf-8")) if os.path.exists(os.path.join(dir_kw, "mapa.yaml")) else {}
    mapa = mapa or {}
    excloure = mapa.get("excloure") or []
    pagines = mapa.get("pagines") or []
    per_pagina, sense, conflictes, excloses = defaultdict(list), [], [], 0
    for n, k in sorted(totes.items(), key=lambda x: -x[1]["volum"]):
        if any(coincideix(p, n) for p in excloure):
            k["pagina"] = "(exclosa)"
            excloses += 1
            continue
        cands = []
        for p in pagines:
            hits = [pt for pt in p.get("inclou", []) if coincideix(pt, n)]
            if hits and not any(coincideix(pt, n) for pt in p.get("exclou", [])):
                cands.append((max(len(h) for h in hits), p["clau"]))
        if not cands:
            k["pagina"] = ""
            sense.append(k)
            continue
        cands.sort(reverse=True)
        k["pagina"] = cands[0][1]
        if len(cands) > 1:
            k["conflicte"] = ", ".join(c for _, c in cands[1:])
            conflictes.append(k)
        per_pagina[k["pagina"]].append(k)
    # keywords.csv
    with open(os.path.join(dir_kw, "keywords.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "volum", "competencia", "cpc_baix", "cpc_alt", "pagina", "tambe_encaixa_a", "mes_pic", "font"])
        for k in sorted(totes.values(), key=lambda x: -x["volum"]):
            pic = MESOS[k["mesos"].index(max(k["mesos"]))] if any(k["mesos"]) else ""
            w.writerow([k["keyword"], k["volum"], k["competencia"], f"{k['cpc_baix']:.2f}", f"{k['cpc_alt']:.2f}",
                        k.get("pagina", ""), k.get("conflicte", ""), pic, k["font"]])
    # per_pagina.md
    L = ["# Paraules clau per pàgina", "", f"{len(totes)} paraules úniques de {len(fitxers)} CSV · {excloses} excloses · "
         f"{len(sense)} sense pàgina · {len(conflictes)} amb conflicte", "",
         "| Pàgina | Paraula principal | Volum principal | Volum total | Paraules | Mesos forts |", "|---|---|---|---|---|---|"]
    resum = []
    for p in pagines:
        ks = per_pagina.get(p["clau"], [])
        total = sum(k["volum"] for k in ks)
        mesos = [sum(k["mesos"][i] for k in ks) for i in range(12)]
        forts = ", ".join(MESOS[i] for i in sorted(range(12), key=lambda i: -mesos[i])[:3]) if any(mesos) else "–"
        principal = ks[0] if ks else None
        resum.append((total, p["clau"]))
        L.append(f"| {p['clau']} | {principal['keyword'] if principal else '–'} | {principal['volum'] if principal else 0} | {total} | {len(ks)} | {forts} |")
    for p in pagines:
        ks = per_pagina.get(p["clau"], [])
        L += ["", f"## {p['clau']}", ""]
        if not ks:
            L.append("Cap paraula. Revisa els patrons o si la pàgina té sentit.")
            continue
        L += ["| Paraula | Volum | Competència | CPC alt |", "|---|---|---|---|"]
        L += [f"| {k['keyword']} | {k['volum']} | {k['competencia']} | {k['cpc_alt']:.2f} |" for k in ks[:25]]
        if len(ks) > 25:
            L.append(f"| … {len(ks) - 25} més a keywords.csv | | | |")
    if conflictes:
        L += ["", "## Possibles canibalitzacions", "", "Paraules que encaixen en més d'una pàgina. Decideix-ne una i ajusta `mapa.yaml`.", "",
              "| Paraula | Volum | Assignada a | També encaixa a |", "|---|---|---|---|"]
        L += [f"| {k['keyword']} | {k['volum']} | {k['pagina']} | {k['conflicte']} |" for k in conflictes[:60]]
    if sense:
        L += ["", "## Sense pàgina (les 40 amb més volum)", "", "Poden ser idees de pàgines noves o soroll per excloure.", "",
              "| Paraula | Volum |", "|---|---|"]
        L += [f"| {k['keyword']} | {k['volum']} |" for k in sense[:40]]
    open(os.path.join(dir_kw, "per_pagina.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"✓ {len(totes)} paraules · {len(sense)} sense pàgina · {len(conflictes)} conflictes")
    print("  keywords/keywords.csv i keywords/per_pagina.md")


if __name__ == "__main__":
    main()
