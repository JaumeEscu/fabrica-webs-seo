#!/usr/bin/env python3
"""Comprovació SEO de la web generada (web/) abans de publicar.

Ús:
    python3 comprovar.py [carpeta-projecte] [--sortida informes/comprovacio.md]

Mira, per a cada pàgina HTML: title, meta description, H1, canonical, hreflang recíproc,
robots, JSON-LD vàlid, FAQ visibles = schema, imatges sense alt, enllaços interns trencats,
paraules (contingut prim), títols i descripcions duplicats, marques [VERIFICAR] i
coherència amb el sitemap. Escriu un informe en Markdown i surt amb codi 1 si hi ha errors.
"""
import json
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin

LIMITS = {"titol": (30, 60), "descripcio": (70, 160), "paraules_min": 300}


class Analitzador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titol, self.desc, self.canonical, self.robots = "", None, None, ""
        self.h1, self.hreflang, self.enllacos, self.imatges_sense_alt = [], {}, [], 0
        self.jsonld, self.text, self.faq_visibles = [], [], 0
        self._pila, self._dins_script, self._buf = [], None, ""
        self._en_main = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")
        elif tag == "meta" and a.get("name") == "robots":
            self.robots = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.hreflang[a["hreflang"]] = a.get("href")
        elif tag == "a" and a.get("href"):
            self.enllacos.append(a["href"])
        elif tag == "img" and not a.get("alt") and a.get("alt") != "":
            self.imatges_sense_alt += 1
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._dins_script, self._buf = "ld", ""
        elif tag == "script":
            self._dins_script = "js"
        elif tag == "main":
            self._en_main += 1
        elif tag == "details" and self._en_main:
            self.faq_visibles += 1
        if tag in ("title", "h1"):
            self._pila.append(tag)
            self._buf = ""

    def handle_endtag(self, tag):
        if tag == "script":
            if self._dins_script == "ld":
                self.jsonld.append(self._buf)
            self._dins_script, self._buf = None, ""
        elif tag == "main":
            self._en_main -= 1
        if self._pila and tag == self._pila[-1]:
            t = self._pila.pop()
            if t == "title":
                self.titol = self._buf.strip()
            else:
                self.h1.append(self._buf.strip())

    def handle_data(self, data):
        if self._dins_script:
            self._buf += data
            return
        if self._pila:
            self._buf += data
        if self._en_main:
            self.text.append(data)


def analitzar(dir_projecte):
    web = os.path.join(dir_projecte, "web")
    if not os.path.isdir(web):
        sys.exit("No hi ha web/. Executa primer construir.py")
    manifest = {}
    if os.path.exists(os.path.join(web, "_pagines.json")):
        manifest = json.load(open(os.path.join(web, "_pagines.json"), encoding="utf-8"))
    sitemap = set()
    if os.path.exists(os.path.join(web, "sitemap.xml")):
        sitemap = set(re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(web, "sitemap.xml"), encoding="utf-8").read()))
    pagines = {}
    for arrel, _, fitxers in os.walk(web):
        for f in fitxers:
            if f != "index.html" or arrel == web:
                continue
            ruta = "/" + os.path.relpath(arrel, web).replace(os.sep, "/") + "/"
            a = Analitzador()
            a.feed(open(os.path.join(arrel, f), encoding="utf-8").read())
            pagines[ruta] = a
    errors, avisos = defaultdict(list), defaultdict(list)
    titols, descs = defaultdict(list), defaultdict(list)
    domini = ""
    for ruta, a in pagines.items():
        if a.canonical:
            domini = "{0.scheme}://{0.netloc}".format(urlparse(a.canonical))
            break
    for ruta, a in sorted(pagines.items()):
        noindex = "noindex" in a.robots
        E, W = errors[ruta], avisos[ruta]
        lt = len(a.titol)
        if not a.titol:
            E.append("Sense <title>")
        elif not (LIMITS["titol"][0] <= lt <= LIMITS["titol"][1]):
            W.append(f"Title de {lt} caràcters (ideal {LIMITS['titol'][0]}–{LIMITS['titol'][1]})")
        if not a.desc:
            (W if noindex else E).append("Sense meta description")
        elif not (LIMITS["descripcio"][0] <= len(a.desc) <= LIMITS["descripcio"][1]):
            W.append(f"Meta description de {len(a.desc)} caràcters (ideal {LIMITS['descripcio'][0]}–{LIMITS['descripcio'][1]})")
        if len(a.h1) != 1:
            E.append(f"{len(a.h1)} H1 (n'hi ha d'haver exactament 1)")
        if not a.canonical:
            E.append("Sense canonical")
        elif urlparse(a.canonical).path != ruta:
            W.append(f"Canonical apunta a una altra URL: {a.canonical}")
        for idioma, url in a.hreflang.items():
            desti = pagines.get(urlparse(url).path)
            if not desti:
                E.append(f"hreflang {idioma} apunta a una pàgina que no existeix: {url}")
            elif a.canonical and a.canonical not in desti.hreflang.values():
                E.append(f"hreflang {idioma} no és recíproc ({url} no torna a aquesta pàgina)")
        faq_schema = 0
        for bloc in a.jsonld:
            try:
                d = json.loads(bloc)
                for g in d.get("@graph", [d]):
                    if g.get("@type") == "FAQPage":
                        faq_schema = len(g.get("mainEntity", []))
            except json.JSONDecodeError as e:
                E.append(f"JSON-LD no vàlid: {e}")
        if not a.jsonld:
            W.append("Sense dades estructurades (JSON-LD)")
        if faq_schema and faq_schema > a.faq_visibles:
            E.append(f"El schema FAQ té {faq_schema} preguntes però només se'n veuen {a.faq_visibles}")
        if a.imatges_sense_alt:
            W.append(f"{a.imatges_sense_alt} imatges sense alt")
        paraules = len(re.findall(r"\w+", " ".join(a.text)))
        if not noindex and paraules < LIMITS["paraules_min"]:
            W.append(f"Contingut prim: {paraules} paraules (mínim recomanat {LIMITS['paraules_min']})")
        for h in a.enllacos:
            u = urlparse(urljoin(domini + ruta, h))
            if u.netloc and domini and u.netloc != urlparse(domini).netloc:
                continue
            if h.startswith(("#", "mailto:", "tel:")) or u.path.startswith("/assets/"):
                continue
            if u.path not in pagines and u.path not in ("/",) and not os.path.exists(os.path.join(web, u.path.lstrip("/"))):
                E.append(f"Enllaç intern trencat: {h}")
        if a.canonical and not noindex and a.canonical not in sitemap:
            W.append("Indexable però no és al sitemap")
        if noindex and a.canonical in sitemap:
            E.append("És noindex però és al sitemap")
        if not noindex:
            idioma = ruta.strip("/").split("/")[0] if a.hreflang else ""
            titols[(idioma, a.titol)].append(ruta)
            descs[(idioma, a.desc)].append(ruta)
    for (_, t), rutes in titols.items():
        if t and len(rutes) > 1:
            for r in rutes:
                errors[r].append(f"Title duplicat amb {', '.join(x for x in rutes if x != r)}")
    for (_, t), rutes in descs.items():
        if t and len(rutes) > 1:
            for r in rutes:
                avisos[r].append(f"Description duplicada amb {', '.join(x for x in rutes if x != r)}")
    marques = manifest.get("marques", [])
    return pagines, errors, avisos, marques


def informe(dir_projecte, pagines, errors, avisos, marques):
    ne, na = sum(len(v) for v in errors.values()), sum(len(v) for v in avisos.values())
    L = [f"# Comprovació SEO", "", f"- Pàgines: **{len(pagines)}**", f"- Errors: **{ne}**", f"- Avisos: **{na}**",
         f"- Marques pendents ([VERIFICAR], [DATA]…): **{len(marques)}**", ""]
    for ruta in sorted(pagines):
        if errors.get(ruta) or avisos.get(ruta):
            L.append(f"## {ruta}")
            L += [f"- ✗ {e}" for e in errors.get(ruta, [])]
            L += [f"- ⚠ {w}" for w in avisos.get(ruta, [])]
            L.append("")
    if marques:
        L.append("## Marques pendents")
        per = defaultdict(list)
        for m in marques:
            per[m["url"]].append(m["text"])
        for u, ts in per.items():
            L.append(f"- {u}: " + "; ".join(sorted(set(ts))))
    return "\n".join(L) + "\n", ne


def main():
    args = sys.argv[1:]
    sortida = None
    if "--sortida" in args:
        i = args.index("--sortida")
        sortida = args[i + 1]
        del args[i:i + 2]
    dir_projecte = args[0] if args else os.getcwd()
    text, ne = informe(dir_projecte, *analitzar(dir_projecte))
    sortida = sortida or os.path.join(dir_projecte, "informes", "comprovacio.md")
    os.makedirs(os.path.dirname(sortida), exist_ok=True)
    open(sortida, "w", encoding="utf-8").write(text)
    print(text.split("\n## ")[0])
    print(f"Informe complet: {sortida}")
    sys.exit(1 if ne else 0)


if __name__ == "__main__":
    main()
