#!/usr/bin/env python3
"""Converteix un document de text final (pas 9, format «BLOC») en una pàgina per al generador.

Ús:
    python3 doc_a_contingut.py 09_copy_preu_ca.md --clau preu --slug preu-aerotermia --idioma ca \
        [--faq 10_faq_preu.md] [--pare aerotermia] [--tipus guia] [--autor jaume] [--sortida contingut/ca/preu.md]

Entén aquestes marques del document:
    ## BLOC n · NOM                → s'ignora (separador)
    **H1: text** / **H2: text** / **H3: text**
    **Xifres:** + llista           → ::: xifres
    **Caixa destacada: títol** + llista/paràgrafs → ::: avis
    **Targeta n:** text            → ::: targetes (una targeta per línia)
    **Calculadora:** ... / *[...]* → ::: avis amb [PENDENT] (component per fer)
    Botó: **text**                 → ::: cta
    → text                         → enllaç pendent [PENDENT enllaç]
La FAQ es llegeix de la secció de l'idioma («Versió catalana» / «Versió castellana») del document del pas 10.
El title i la description s'han de revisar: es proposen a partir de l'H1 i del primer paràgraf.
"""
import argparse
import re
import sys

import yaml

SECCIO_IDIOMA = {"ca": "catalana", "es": "castellana", "en": "anglesa"}


def llegir_faq(ruta, idioma):
    text = open(ruta, encoding="utf-8").read()
    nom = SECCIO_IDIOMA.get(idioma, idioma)
    m = re.search(rf"^## Versió {nom}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        # document d'un sol idioma
        bloc = text
    else:
        bloc = m.group(1)
    faq, actual = [], None
    for linia in bloc.splitlines():
        l = linia.strip()
        q = re.match(r"^\*\*(.+\?)\*\*$", l)
        if q:
            actual = {"p": q.group(1).strip(), "r": ""}
            faq.append(actual)
        elif actual is not None and l and not l.startswith(("**H2", "---", "#", ">")):
            actual["r"] = (actual["r"] + " " + l).strip()
        elif l.startswith("---") or l.startswith("## "):
            actual = None
    return [f for f in faq if f["r"]]


def convertir(text):
    linies = text.splitlines()
    inici = next((i for i, l in enumerate(linies) if l.startswith("## BLOC")), 0)
    out, i, h1, primer_par = [], inici, None, None

    def bloc_llista(j):
        items = []
        while j < len(linies) and (linies[j].strip().startswith(("-", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9")) and linies[j].strip()):
            items.append(linies[j])
            j += 1
        return items, j

    while i < len(linies):
        l = linies[i].rstrip()
        s = l.strip()
        if s.startswith("## BLOC") or s == "---" or re.match(r"^\*\(.*\)\*$", s):
            i += 1
            continue
        m = re.match(r"^\*\*H([123]):\s*(.+?)\*\*$", s)
        if m:
            if m.group(1) == "1":
                h1 = m.group(2)
                out.append(f"# {h1}")
            else:
                out.append("#" * int(m.group(1)) + " " + m.group(2))
            i += 1
            continue
        if re.match(r"^\*Actualitzat|^\*Actualizado|^\*Updated", s):
            i += 1
            continue
        if s.startswith("**Xifres:**") or s.startswith("**Cifras:**"):
            items, i = bloc_llista(i + 1)
            out += ["::: xifres"] + items + [":::"]
            continue
        m = re.match(r"^\*\*Caixa destacada:\s*(.+?)\*\*$|^\*\*Caja destacada:\s*(.+?)\*\*$", s)
        if m:
            titol = m.group(1) or m.group(2)
            items, i = bloc_llista(i + 1)
            out += ["::: avis", f"**{titol}**", ""] + items + [":::"]
            continue
        if re.match(r"^\*\*(Targeta|Tarjeta) \d+:\*\*", s):
            targetes = []
            while i < len(linies) and (re.match(r"^\*\*(Targeta|Tarjeta) \d+:\*\*", linies[i].strip()) or not linies[i].strip()):
                t = linies[i].strip()
                if t:
                    cos = re.sub(r"^\*\*(Targeta|Tarjeta) \d+:\*\*\s*", "", t)
                    titol, _, resta = cos.partition(":")
                    targetes += [f"### {titol.strip()}", resta.strip() or cos]
                i += 1
            out += ["::: targetes columnes=2"] + targetes + [":::", ""]
            continue
        if s.startswith("**Calculadora:**") or re.match(r"^\*\[.*\]\*$", s):
            bloc = [s]
            i += 1
            while i < len(linies) and linies[i].strip() and not linies[i].startswith("**H"):
                bloc.append(linies[i].strip())
                i += 1
            out += ["::: avis", "[PENDENT component] " + " ".join(bloc).replace("*", ""), ":::"]
            continue
        m = re.match(r"^(Botó|Botón):\s*\*\*(.+?)\*\*(.*)$", s)
        if m:
            nota = re.sub(r"^\s*·\s*", "", m.group(3)).strip()
            out += [f'::: cta text="{m.group(2)}" enllac="@pressupost"' + (f' nota="{nota}"' if nota else ""), ":::"]
            i += 1
            continue
        if s.startswith("→"):
            out.append(f"{s[1:].strip()} [PENDENT enllaç]")
            i += 1
            continue
        if s and primer_par is None and h1 and not s.startswith(("#", "::", "-", "|", "*")):
            primer_par = s
        out.append(l)
        i += 1
    cos = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
    return cos, h1, primer_par


def retallar(t, n):
    t = re.sub(r"\*|\[.*?\]", "", t or "").strip()
    return t if len(t) <= n else t[: t.rfind(" ", 0, n - 1)].rstrip(",;:") + "…"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    ap.add_argument("--clau", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--idioma", default="ca")
    ap.add_argument("--faq")
    ap.add_argument("--pare")
    ap.add_argument("--tipus", default="guia")
    ap.add_argument("--autor")
    ap.add_argument("--keyword")
    ap.add_argument("--sortida")
    a = ap.parse_args()
    cos, h1, primer = convertir(open(a.doc, encoding="utf-8").read())
    cap = {"clau": a.clau, "slug": a.slug, "titol": retallar(h1, 60), "descripcio": retallar(primer, 158), "tipus": a.tipus}
    for k in ("pare", "autor", "keyword"):
        if getattr(a, k):
            cap[k] = getattr(a, k)
    if a.faq:
        cap["faq"] = llegir_faq(a.faq, a.idioma)
    text = "---\n" + yaml.safe_dump(cap, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + cos
    if a.sortida:
        open(a.sortida, "w", encoding="utf-8").write(text)
        print(f"✓ {a.sortida} ({len(cap.get('faq', []))} FAQ). Revisa titol i descripcio.")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
