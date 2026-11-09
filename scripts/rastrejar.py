#!/usr/bin/env python3
"""Rastreja una web existent i en fa l'inventari (fase 0, mode «existent»).

Ús:
    python3 rastrejar.py https://www.exemple.com [carpeta-projecte] [--max 300] [--sense-sitemap]

Primer prova el sitemap.xml (i els sitemaps que enllaci); si no n'hi ha, segueix els enllaços
interns. Per a cada URL desa: estat HTTP, redirecció, title, description, H1, nombre d'H2,
paraules, canonical, robots, idioma, hreflang, enllaços interns sortints i entrants, tipus de schema.

Escriu brief/inventari.csv i brief/inventari_resum.md
"""
import csv
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from collections import Counter, deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag

AGENT = "Mozilla/5.0 (compatible; FabricaWebsSEO/0.1; inventari)"


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.d = {"title": "", "description": "", "h1": [], "h2": 0, "canonical": "", "robots": "", "lang": "",
                  "hreflang": [], "schema": []}
        self.enllacos, self.text = [], []
        self._t, self._buf, self._skip, self._ld = None, "", 0, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.d["lang"] = a.get("lang", "")
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.d["description"] = a.get("content", "")
        elif tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.d["robots"] = a.get("content", "")
        elif tag == "link" and "canonical" in (a.get("rel") or ""):
            self.d["canonical"] = a.get("href", "")
        elif tag == "link" and a.get("hreflang"):
            self.d["hreflang"].append(a["hreflang"])
        elif tag == "a" and a.get("href"):
            self.enllacos.append(a["href"])
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._ld, self._buf = True, ""
        elif tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag == "h2":
            self.d["h2"] += 1
        if tag in ("title", "h1"):
            self._t, self._buf = tag, ""

    def handle_endtag(self, tag):
        if tag == "script" and self._ld:
            self._ld = False
            try:
                j = json.loads(self._buf)
                for g in (j.get("@graph", [j]) if isinstance(j, dict) else j):
                    t = g.get("@type") if isinstance(g, dict) else None
                    self.d["schema"] += t if isinstance(t, list) else [t] if t else []
            except Exception:
                self.d["schema"].append("JSON-LD-invalid")
        elif tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        if tag == self._t:
            if tag == "title":
                self.d["title"] = self._buf.strip()
            else:
                self.d["h1"].append(re.sub(r"\s+", " ", self._buf).strip())
            self._t = None

    def handle_data(self, data):
        if self._ld or self._t:
            self._buf += data
        if not self._skip and not self._ld:
            self.text.append(data)


def obtenir(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept": "text/html,application/xml"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            cos = r.read(3_000_000)
            ct = r.headers.get("Content-Type", "")
            enc = re.search(r"charset=([\w-]+)", ct)
            return r.status, r.geturl(), ct, cos.decode(enc.group(1) if enc else "utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, "", ""
    except Exception as e:
        return 0, url, str(e), ""


def urls_sitemap(base):
    vistes, cua, urls = set(), deque([urljoin(base, "/sitemap.xml"), urljoin(base, "/sitemap_index.xml")]), []
    estat, _, _, robots = obtenir(urljoin(base, "/robots.txt"))
    if estat == 200:
        cua.extendleft(re.findall(r"(?im)^sitemap:\s*(\S+)", robots))
    while cua:
        u = cua.popleft()
        if u in vistes:
            continue
        vistes.add(u)
        estat, _, _, xml = obtenir(u)
        if estat != 200 or "<" not in xml:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
        if "<sitemapindex" in xml:
            cua.extend(locs)
        else:
            urls += locs
    return list(dict.fromkeys(urls))


def normalitzar(u):
    u, _ = urldefrag(u)
    return u


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    inici = args[0].rstrip("/") + "/"
    dir_p = args[1] if len(args) > 1 else os.getcwd()
    maxim = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 300
    host = urlparse(inici).netloc.replace("www.", "")
    desde_sitemap = [] if "--sense-sitemap" in sys.argv else [
        u for u in urls_sitemap(inici) if urlparse(u).netloc.replace("www.", "") == host]
    cua = deque(desde_sitemap or [inici])
    print(f"Sitemap: {len(desde_sitemap)} URL" if desde_sitemap else "Sense sitemap: segueixo enllaços")
    vistes, files, entrants = set(), [], Counter()
    while cua and len(files) < maxim:
        u = normalitzar(cua.popleft())
        if u in vistes:
            continue
        vistes.add(u)
        estat, final, ct, cos = obtenir(u)
        fila = {"url": u, "estat": estat, "redirigeix_a": final if final != u else ""}
        if estat == 200 and "html" in ct:
            p = Pagina()
            try:
                p.feed(cos)
            except Exception:
                pass
            paraules = len(re.findall(r"\w+", " ".join(p.text)))
            interns = set()
            for h in p.enllacos:
                a = normalitzar(urljoin(final, h))
                if urlparse(a).netloc.replace("www.", "") == host and a.startswith("http") and not re.search(r"\.(jpg|jpeg|png|gif|pdf|zip|svg|webp|mp4)$", a, re.I):
                    interns.add(a)
            for a in interns:
                entrants[a] += 1
                if not desde_sitemap and a not in vistes:
                    cua.append(a)
            d = p.d
            fila.update(title=d["title"], len_title=len(d["title"]), description=d["description"], len_description=len(d["description"]),
                        h1=" | ".join(d["h1"]), num_h1=len(d["h1"]), num_h2=d["h2"], paraules=paraules, canonical=d["canonical"],
                        robots=d["robots"], lang=d["lang"], hreflang=",".join(d["hreflang"]), schema=",".join(dict.fromkeys(d["schema"])),
                        enllacos_interns=len(interns))
        files.append(fila)
        print(f"  {estat} {u}")
        time.sleep(0.3)
    for f in files:
        f["enllacos_entrants"] = entrants.get(f["url"], 0)
    os.makedirs(os.path.join(dir_p, "brief"), exist_ok=True)
    camps = ["url", "estat", "redirigeix_a", "title", "len_title", "description", "len_description", "h1", "num_h1", "num_h2",
             "paraules", "canonical", "robots", "lang", "hreflang", "schema", "enllacos_interns", "enllacos_entrants"]
    with open(os.path.join(dir_p, "brief", "inventari.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=camps, extrasaction="ignore")
        w.writeheader()
        w.writerows(files)
    ok = [f for f in files if f["estat"] == 200 and "title" in f]
    prims = [f for f in ok if f["paraules"] < 300]
    L = ["# Inventari de la web", "", f"Web: {inici} · {len(files)} URL rastrejades · {len(ok)} pàgines HTML vàlides", "",
         "| Problema | Pàgines |", "|---|---|",
         f"| Errors (4xx/5xx/sense resposta) | {sum(1 for f in files if f['estat'] != 200)} |",
         f"| Sense title | {sum(1 for f in ok if not f['title'])} |",
         f"| Title > 60 caràcters | {sum(1 for f in ok if f['len_title'] > 60)} |",
         f"| Sense meta description | {sum(1 for f in ok if not f['description'])} |",
         f"| Sense H1 o amb més d'un | {sum(1 for f in ok if f['num_h1'] != 1)} |",
         f"| Menys de 300 paraules | {len(prims)} |",
         f"| Sense canonical | {sum(1 for f in ok if not f['canonical'])} |",
         f"| Noindex | {sum(1 for f in ok if 'noindex' in (f['robots'] or ''))} |",
         f"| Sense schema | {sum(1 for f in ok if not f['schema'])} |",
         f"| Òrfenes (cap enllaç intern entrant) | {sum(1 for f in ok if not f['enllacos_entrants'])} |",
         f"| Titles duplicats | {sum(c for t, c in Counter(f['title'] for f in ok if f['title']).items() if c > 1)} |", "",
         "Detall a `inventari.csv`. Fes servir la skill f0-brief per decidir què es manté, es millora, es fusiona o es redirigeix."]
    open(os.path.join(dir_p, "brief", "inventari_resum.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"✓ {len(files)} URL → brief/inventari.csv i brief/inventari_resum.md")


if __name__ == "__main__":
    main()
