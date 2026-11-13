#!/usr/bin/env python3
"""Auditoria d'una web publicada: que te trobin els cercadors i les IA.

Ús:
    python3 auditar_viu.py https://www.exemple.com [carpeta-projecte] [--max 30]

Mira el que només es pot veure amb la web en línia (complementa comprovar.py, que mira web/):

1. robots.txt real del servidor: què pot fer cada rastrejador de cerca, d'assistent i d'entrenament.
2. Bloqueigs per user-agent: demana la portada fent-se passar per cada bot. Un 403/429/503 vol dir que
   el servidor, el CDN o el tallafoc (Cloudflare, WAF, plugin de seguretat) els barra el pas encara que
   el robots.txt ho permeti.
3. Sitemap: cada URL respon 200, sense redirecció, sense noindex i amb canonical a si mateixa.
4. Redirecció www / sense www i http → https cap a una sola versió.
5. Pes de la portada: HTML i imatges (HEAD) per detectar fitxers massa pesats.
6. Common Crawl: si el domini és al darrer índex (corpus d'entrenament de molts models).

Escriu informes/auditoria_viva.md (o a la carpeta actual si no hi ha projecte).
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from urllib.robotparser import RobotFileParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bots_ia  # noqa: E402

AGENT = "Mozilla/5.0 (compatible; FabricaWebsSEO/0.2; auditoria)"
TIMEOUT = 20


class SenseRedireccio(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OBRIDOR = urllib.request.build_opener(SenseRedireccio)


def demana(url, agent=AGENT, metode="GET", seguir=False, maxim=600_000):
    """Retorna (estat, capçaleres, cos) sense excepcions."""
    req = urllib.request.Request(url, method=metode, headers={"User-Agent": agent, "Accept": "text/html,*/*"})
    try:
        obr = urllib.request.urlopen if seguir else OBRIDOR.open
        with obr(req, timeout=TIMEOUT) as r:
            cos = r.read(maxim) if metode == "GET" else b""
            return r.status, dict(r.headers), cos.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), ""
    except (urllib.error.URLError, ssl.SSLError, TimeoutError, ConnectionError, OSError) as e:
        return 0, {}, str(getattr(e, "reason", e))


class Cap(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.robots, self.canonical, self.imatges = "", "", []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.robots = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href", "")
        elif tag == "img" and a.get("src"):
            self.imatges.append(a["src"])


def urls_sitemap(base, robots_txt, maxim):
    llocs = re.findall(r"(?im)^sitemap:\s*(\S+)", robots_txt) or [urllib.parse.urljoin(base, "/sitemap.xml")]
    vistos, urls = set(), []
    while llocs and len(urls) < maxim:
        sm = llocs.pop(0)
        if sm in vistos:
            continue
        vistos.add(sm)
        estat, _, cos = demana(sm, seguir=True, maxim=5_000_000)
        if estat != 200:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", cos)
        if "<sitemapindex" in cos:
            llocs += locs
        else:
            urls += [u for u in locs if u not in urls]
    return urls[:maxim], sorted(vistos)


def main():
    brut, args, maxim = sys.argv[1:], [], 30
    while brut:
        a = brut.pop(0)
        if a == "--max" and brut:
            maxim = int(brut.pop(0))
        elif not a.startswith("--"):
            args.append(a)
    if not args:
        sys.exit(__doc__)
    base = args[0].rstrip("/") + "/"
    dir_projecte = args[1] if len(args) > 1 else None
    domini = urllib.parse.urlparse(base).netloc
    L = [f"# Auditoria en viu · {domini}", "", f"Data: {time.strftime('%Y-%m-%d %H:%M')}", ""]
    critics, avisos = [], []

    # 1. robots.txt
    estat, _, robots_txt = demana(urllib.parse.urljoin(base, "/robots.txt"), seguir=True)
    L += ["## 1. robots.txt", ""]
    if estat != 200:
        L.append(f"- No es pot llegir /robots.txt (estat {estat}). Sense robots.txt tothom pot entrar, però cal per declarar el sitemap.")
        avisos.append("Sense robots.txt accessible")
        robots_txt = ""
    rp = RobotFileParser()
    rp.parse(robots_txt.splitlines())
    L += ["| Rastrejador | Tipus | Pot entrar a la portada? |", "|---|---|---|"]
    for bot, (grup, desc) in bots_ia.tots().items():
        pot = rp.can_fetch(bot, base)
        L.append(f"| {bot} — {desc} | {grup} | {'sí' if pot else '**no**'} |")
        if not pot and grup != "entrenament":
            critics.append(f"robots.txt bloqueja {bot} ({desc})")
    L.append("")

    # 2. Bloqueig per user-agent (servidor/CDN)
    L += ["## 2. Resposta del servidor a cada bot", "",
          "El robots.txt és una petició; el servidor o el CDN poden barrar el pas igualment.", "",
          "| User-agent | Estat |", "|---|---|"]
    ref, _, _ = demana(base, seguir=True)
    for bot, ua in bots_ia.UA.items():
        e, _, _ = demana(base, agent=ua, seguir=True)
        nota = "" if e == ref else f" (el navegador rep {ref})"
        L.append(f"| {bot} | {e or 'sense resposta'}{nota} |")
        if e in (401, 403, 406, 429, 503) and ref == 200:
            grup = bots_ia.tots().get(bot, ("cerca",))[0]
            (critics if grup != "entrenament" else avisos).append(f"El servidor respon {e} a {bot}")
    L += ["", "_Si algun bot de cerca rep 403, revisa Cloudflare (Bots / AI Crawl Control), el WAF o el plugin de seguretat._", ""]

    # 3. www / https
    L += ["## 3. Versió única del domini", ""]
    net = domini[4:] if domini.startswith("www.") else domini
    for variant in (f"http://{net}/", f"http://www.{net}/", f"https://{net}/", f"https://www.{net}/"):
        e, cap, _ = demana(variant)
        desti = cap.get("Location", "")
        L.append(f"- `{variant}` → {e or 'sense resposta'}{' → ' + desti if desti else ''}")
        if e in (302, 307):
            avisos.append(f"{variant} redirigeix amb {e} (temporal): millor 301")
    L.append("")

    # 4. Sitemap
    urls, sitemaps = urls_sitemap(base, robots_txt, maxim)
    L += ["## 4. Sitemap", "", f"Sitemaps llegits: {', '.join(sitemaps) or 'cap'}", f"URLs revisades: {len(urls)} (màxim {maxim})", ""]
    if not urls:
        critics.append("No s'ha trobat cap URL al sitemap")
    problemes = []
    for u in urls:
        e, cap, cos = demana(u)
        if e in (301, 302, 307, 308):
            problemes.append(f"- {u} → {e} redirecció a {cap.get('Location', '')} (al sitemap només hi ha d'haver URLs finals)")
            continue
        if e != 200:
            problemes.append(f"- {u} → estat {e}")
            continue
        c = Cap()
        c.feed(cos)
        if "noindex" in c.robots.lower() or "noindex" in cap.get("X-Robots-Tag", "").lower():
            problemes.append(f"- {u} → noindex però és al sitemap")
        if c.canonical and c.canonical.rstrip("/") != u.rstrip("/"):
            problemes.append(f"- {u} → canonical a {c.canonical}")
    L += problemes or ["- Totes les URLs revisades responen 200, sense redirecció ni noindex."]
    if problemes:
        avisos.append(f"{len(problemes)} URLs del sitemap amb problemes")
    L.append("")

    # 5. Pes de la portada
    e, cap, cos = demana(base, seguir=True, maxim=5_000_000)
    L += ["## 5. Pes de la portada", ""]
    if e == 200:
        c = Cap()
        c.feed(cos)
        L.append(f"- HTML: {len(cos.encode()) / 1024:.0f} KB")
        pesades = []
        for src in dict.fromkeys(c.imatges):
            u = urllib.parse.urljoin(base, src)
            ei, ci, _ = demana(u, metode="HEAD", seguir=True)
            kb = int(ci.get("Content-Length") or 0) / 1024
            if kb > 300:
                pesades.append(f"- {u}: {kb:.0f} KB")
        L += pesades or ["- Cap imatge de més de 300 KB."]
        if pesades:
            avisos.append(f"{len(pesades)} imatges de més de 300 KB a la portada")
        L.append(f"- Per a Core Web Vitals: https://pagespeed.web.dev/analysis?url={urllib.parse.quote(base)}")
    L.append("")

    # 6. Common Crawl
    L += ["## 6. Common Crawl (corpus d'entrenament de molts models)", ""]
    e, _, cos = demana("https://index.commoncrawl.org/collinfo.json", seguir=True)
    try:
        index = json.loads(cos)[0]
        e2, _, cos2 = demana(f"{index['cdx-api']}?url={urllib.parse.quote(net)}/*&output=json&limit=5", seguir=True)
        n = len([x for x in cos2.splitlines() if x.strip().startswith("{")]) if e2 == 200 else 0
        if n:
            L.append(f"- El domini és a l'índex {index['id']} ({n}+ captures). Ja forma part del corpus.")
        else:
            L.append(f"- No apareix a l'índex {index['id']}. Les IA només el coneixeran per cerca en viu (RAG) fins al proper rastreig.")
    except (ValueError, KeyError, IndexError):
        L.append(f"- No s'ha pogut consultar Common Crawl ({e}). Comprova-ho a mà a https://index.commoncrawl.org/")
    L.append("")

    # 7. Proves manuals
    L += ["## 7. Proves manuals recomanades", "",
          f"- Google: `site:{net}` → quantes pàgines té indexades. 0 o només URLs antigues = problema de rastreig.",
          "- Search Console: Indexació → Pàgines, i Sitemaps (enviat i llegit).",
          "- Pregunta a ChatGPT, Gemini i al Mode IA de Google: «Estoy en [ciutat] y busco [servei]. ¿Qué opciones me "
          "recomiendas y por qué? Indica de dónde sacas la información.» Apunta si et citen i de quines fonts treuen les dades.",
          "- Comparteix una URL per WhatsApp o LinkedIn i mira la vista prèvia (Open Graph).", ""]

    resum = ["## Resum", ""]
    resum += [f"- 🔴 {c}" for c in critics] + [f"- 🟠 {a}" for a in avisos]
    if not critics and not avisos:
        resum.append("- Cap problema detectat.")
    text = "\n".join(L[:4] + resum + [""] + L[4:]) + "\n"
    desti = os.path.join(dir_projecte or ".", "informes", "auditoria_viva.md") if dir_projecte else "auditoria_viva.md"
    os.makedirs(os.path.dirname(desti) or ".", exist_ok=True)
    open(desti, "w", encoding="utf-8").write(text)
    print("\n".join(resum))
    print(f"\nInforme complet: {desti}")
    sys.exit(1 if critics else 0)


if __name__ == "__main__":
    main()
