#!/usr/bin/env python3
"""Comprovació SEO de la web generada (web/) abans de publicar.

Ús:
    python3 comprovar.py [carpeta-projecte] [--sortida informes/comprovacio.md]

Segueix els quatre passos «que et trobin, que t'entenguin, que et valorin, que puguin interactuar»:

- Trobar:   robots.txt (cercadors i rastrejadors d'IA), sitemap, noindex, canonical, hreflang,
            enllaços interns trencats, viewport.
- Entendre: title, description, un sol H1 descriptiu (no només la marca), jerarquia d'encapçalaments,
            JSON-LD vàlid i sense camps buits, entitat (Organization/Person amb sameAs), FAQ = schema,
            idioma, Open Graph.
- Valorar:  contingut prim, sobreoptimització de la paraula clau, canibalització (text compartit entre
            pàgines), autor als articles, marques [VERIFICAR].
- Rendiment: pes i mides de les imatges, formats moderns, vídeos incrustats sense càrrega diferida.

Cada problema té una prioritat (1 crític, 2 important, 3 menor) segons l'impacte en el negoci, no segons
com de «tècnic» sembla: una Twitter Card que falta no és tan greu com un robots.txt que bloqueja ChatGPT.
Escriu un informe en Markdown i surt amb codi 1 si hi ha errors (prioritat 1 que bloqueja la publicació).
"""
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bots_ia  # noqa: E402

LIMITS = {"titol": (30, 60), "descripcio": (70, 160), "paraules_min": 300,
          "img_kb_avis": 300, "img_kb_greu": 1000, "imatges_pagina_kb": 2000,
          "canibal_avis": 0.5, "canibal_greu": 0.7}

# codi: (prioritat, bloqueja la publicació, per què importa)
CODIS = {
    "robots_bloqueja": (1, True, "Si un cercador o un assistent no pot entrar, la pàgina no surt ni la poden citar."),
    "sense_sitemap": (1, True, "El sitemap és el plànol que fan servir Google i Bing per descobrir les pàgines."),
    "noindex_sitemap": (1, True, "Senyals contradictoris: el sitemap demana indexar una pàgina que diu que no s'indexi."),
    "sense_title": (1, True, "Sense title Google s'inventa el text del resultat."),
    "h1": (1, True, "L'H1 diu de què va la pàgina; n'hi ha d'haver un i només un."),
    "sense_canonical": (1, True, "Sense canonical, Google pot triar una altra URL com a principal."),
    "hreflang": (1, True, "Un hreflang trencat fa que Google ignori la relació entre idiomes."),
    "enllac_trencat": (1, True, "Un enllaç trencat talla el rastreig i l'experiència de l'usuari."),
    "jsonld_invalid": (1, True, "Un JSON-LD mal format s'ignora sencer."),
    "faq_schema": (1, True, "Google penalitza el marcatge que no es veu a la pàgina."),
    "title_duplicat": (1, True, "Dos titles iguals: Google no sap quina pàgina mostrar."),
    "sense_viewport": (1, True, "Sense viewport la pàgina no és apta per a mòbil (indexació mobile-first)."),
    "canibal_greu": (1, False, "Dues pàgines amb el mateix text competeixen per la mateixa cerca (canibalització)."),
    "sense_descripcio": (2, False, "La description és l'anunci del resultat: sense ella baixa el CTR."),
    "prim": (2, False, "Poc text útil: poques respostes per a les subconsultes que generen Google i les IA."),
    "sense_jsonld": (2, False, "Les dades estructurades són la fitxa tècnica de l'entitat per a Google i les IA."),
    "entitat": (2, False, "Ser una entitat clara (qui, què, on, perfils oficials) és un dels factors per sortir citat."),
    "h1_marca": (2, False, "Un H1 que només és el nom de la marca no explica què oferiu."),
    "salt_encap": (2, False, "Els encapçalaments són l'índex de la pàgina; les IA n'extreuen fragments per seccions."),
    "sobreopt": (2, False, "Repetir la paraula clau de manera poc natural no ajuda i fa el text pitjor."),
    "canibal": (2, False, "Molt text compartit entre pàgines: revisa que cada una respongui una intenció diferent."),
    "sense_autor": (2, False, "Un article sense autor identificat té menys senyals d'experiència (E-E-A-T)."),
    "img_greu": (2, False, "Una imatge de més d'1 MB alenteix la càrrega, sobretot al mòbil."),
    "pes_pagina": (2, False, "Massa pes d'imatges a la mateixa pàgina."),
    "iframe": (2, False, "Un vídeo o mapa incrustat sense càrrega diferida alenteix molt la primera càrrega."),
    "sense_alt": (2, False, "Sense alt, ni Google ni els lectors de pantalla saben què mostra la imatge."),
    "sense_lang": (2, False, "L'atribut lang diu l'idioma als cercadors i als lectors de pantalla."),
    "llargada": (3, False, "Fora de mida, el text es talla o es desaprofita espai al resultat."),
    "desc_duplicada": (3, False, "Descriptions iguals: cada resultat hauria de vendre la seva pàgina."),
    "img_pes": (3, False, "Imatge pesada: comprimeix-la o passa-la a WebP/AVIF."),
    "img_mida": (3, False, "Sense width i height la pàgina «salta» mentre carrega (CLS)."),
    "img_format": (3, False, "WebP o AVIF pesen molt menys que JPG/PNG amb la mateixa qualitat."),
    "encap_buit": (3, False, "Un encapçalament buit o només amb xifres no descriu la secció."),
    "encap_duplicat": (3, False, "Dos H2 iguals a la mateixa pàgina no ajuden a navegar."),
    "schema_buit": (3, False, "Camps buits al schema: millor treure'ls que deixar-los en blanc."),
    "og_trencada": (2, False, "La imatge per compartir no existeix: a xarxes i missatgeria l'enllaç surt sense imatge o trencat."),
    "og": (3, False, "Sense Open Graph, l'enllaç compartit a xarxes i missatgeria es veu pobre."),
    "sense_llms": (3, False, "llms.txt és un resum opcional per a assistents d'IA."),
    "entrenament": (3, False, "Informatiu: bloquejar l'entrenament no treu de la cerca, però CCBot alimenta el corpus de molts models."),
    "canonical_altra": (3, False, "El canonical apunta a una altra URL: comprova que sigui intencionat."),
    "fora_sitemap": (3, False, "Pàgina indexable que no és al sitemap."),
}
PRIO = {1: "🔴 Crític", 2: "🟠 Important", 3: "🟡 Menor"}
LLOC = "(tot el lloc)"


def normal(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


class Analitzador(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titol, self.desc, self.canonical, self.robots, self.lang = "", None, None, "", ""
        self.viewport, self.og, self.twitter = False, {}, {}
        self.h1, self.hreflang, self.enllacos = [], {}, []
        self.imatges, self.iframes, self.encap = [], [], []
        self.jsonld, self.text, self.faq_visibles = [], [], 0
        self._pila, self._dins_script, self._buf = [], None, ""
        self._en_main = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "meta":
            nom, prop = (a.get("name") or "").lower(), (a.get("property") or "").lower()
            if nom == "description":
                self.desc = a.get("content", "")
            elif nom == "robots":
                self.robots = a.get("content", "")
            elif nom == "viewport":
                self.viewport = True
            elif prop.startswith("og:"):
                self.og[prop] = a.get("content", "")
            elif nom.startswith("twitter:"):
                self.twitter[nom] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.hreflang[a["hreflang"]] = a.get("href")
        elif tag == "a" and a.get("href"):
            self.enllacos.append(a["href"])
        elif tag == "img":
            self.imatges.append(a)
        elif tag == "iframe":
            self.iframes.append(a)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._dins_script, self._buf = "ld", ""
        elif tag in ("script", "style"):
            self._dins_script = "js"
        elif tag == "main":
            self._en_main += 1
        elif tag == "details" and self._en_main:
            self.faq_visibles += 1
        if tag == "title" or re.fullmatch(r"h[1-6]", tag):
            self._pila.append(tag)
            self._buf = ""

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            if self._dins_script == "ld":
                self.jsonld.append(self._buf)
            self._dins_script, self._buf = None, ""
        elif tag == "main":
            self._en_main -= 1
        if self._pila and tag == self._pila[-1]:
            t = self._pila.pop()
            text = re.sub(r"\s+", " ", self._buf).strip()
            if t == "title":
                self.titol = text
            else:
                if t == "h1":
                    self.h1.append(text)
                if self._en_main or t == "h1":
                    self.encap.append((int(t[1]), text))

    def handle_data(self, data):
        if self._dins_script:
            self._buf += data
            return
        if self._pila:
            self._buf += data
        if self._en_main:
            self.text.append(data)


def recorre(node, cami=""):
    """Camps buits dins un JSON-LD."""
    if isinstance(node, dict):
        for k, v in node.items():
            if v in ("", None, [], {}):
                yield f"{cami}{k}"
            else:
                yield from recorre(v, f"{cami}{k}.")
    elif isinstance(node, list):
        for v in node:
            yield from recorre(v, cami)


def nodes(d):
    for g in (d.get("@graph") or [d]) if isinstance(d, dict) else d:
        if isinstance(g, dict):
            yield g


def tipus(g):
    t = g.get("@type")
    return t if isinstance(t, list) else [t]


def shingles(text, n=5):
    p = re.findall(r"\w+", normal(text))
    return {" ".join(p[i:i + n]) for i in range(max(0, len(p) - n + 1))}


def analitzar(dir_projecte):
    web = os.path.join(dir_projecte, "web")
    if not os.path.isdir(web):
        sys.exit("No hi ha web/. Executa primer construir.py")
    manifest = {}
    if os.path.exists(os.path.join(web, "_pagines.json")):
        manifest = json.load(open(os.path.join(web, "_pagines.json"), encoding="utf-8"))
    keywords = {p["url"]: p.get("keyword") for p in manifest.get("pagines", [])}
    troballes = defaultdict(list)  # ruta -> [(codi, missatge)]

    def afegeix(ruta, codi, msg):
        troballes[ruta].append((codi, msg))

    # ---- Fitxers del lloc
    sitemap = set()
    ruta_sitemap = os.path.join(web, "sitemap.xml")
    if os.path.exists(ruta_sitemap):
        sitemap = set(re.findall(r"<loc>([^<]+)</loc>", open(ruta_sitemap, encoding="utf-8").read()))
    else:
        afegeix(LLOC, "sense_sitemap", "No hi ha sitemap.xml")
    ruta_robots = os.path.join(web, "robots.txt")
    if os.path.exists(ruta_robots):
        rp = RobotFileParser()
        rp.parse(open(ruta_robots, encoding="utf-8").read().splitlines())
        for bot, (grup, desc) in bots_ia.tots().items():
            if rp.can_fetch(bot, "/"):
                continue
            if grup in ("cerca", "usuari"):
                afegeix(LLOC, "robots_bloqueja", f"robots.txt bloqueja {bot} ({desc})")
            else:
                afegeix(LLOC, "entrenament", f"robots.txt bloqueja {bot} ({desc})")
        if rp.can_fetch("*", "/") is False:
            afegeix(LLOC, "robots_bloqueja", "robots.txt bloqueja tots els rastrejadors (User-agent: * / Disallow: /)")
    if not os.path.exists(os.path.join(web, "llms.txt")):
        afegeix(LLOC, "sense_llms", "No hi ha llms.txt")

    # ---- Pàgines
    pagines = {}
    for arrel, _, fitxers in os.walk(web):
        for f in fitxers:
            if f != "index.html":
                continue
            html = open(os.path.join(arrel, f), encoding="utf-8").read()
            if arrel == web:
                # A una web multiidioma, l'arrel només redirigeix a /ca/; a una d'un sol idioma és la portada
                if re.search(r'http-equiv=["\']?refresh', html, re.I):
                    continue
                ruta = "/"
            else:
                ruta = "/" + os.path.relpath(arrel, web).replace(os.sep, "/") + "/"
            a = Analitzador()
            a.feed(html)
            pagines[ruta] = a
    domini = ""
    for a in pagines.values():
        if a.canonical:
            domini = "{0.scheme}://{0.netloc}".format(urlparse(a.canonical))
            break
    titols, descs = defaultdict(list), defaultdict(list)
    entitats, amb_sameas = 0, 0
    textos = {}
    for ruta, a in sorted(pagines.items()):
        noindex = "noindex" in a.robots
        F = lambda codi, msg: afegeix(ruta, codi, msg)  # noqa: E731
        # Trobar
        if not a.viewport:
            F("sense_viewport", "Sense <meta name=viewport>")
        if not a.canonical:
            F("sense_canonical", "Sense canonical")
        elif urlparse(a.canonical).path != ruta:
            F("canonical_altra", f"Canonical apunta a una altra URL: {a.canonical}")
        for idioma, url in a.hreflang.items():
            desti = pagines.get(urlparse(url).path)
            if not desti:
                F("hreflang", f"hreflang {idioma} apunta a una pàgina que no existeix: {url}")
            elif a.canonical and a.canonical not in desti.hreflang.values():
                F("hreflang", f"hreflang {idioma} no és recíproc ({url} no torna a aquesta pàgina)")
        for h in a.enllacos:
            u = urlparse(urljoin(domini + ruta, h))
            if u.netloc and domini and u.netloc != urlparse(domini).netloc:
                continue
            if h.startswith(("#", "mailto:", "tel:")) or u.path.startswith("/assets/"):
                continue
            if u.path not in pagines and u.path not in ("/",) and not os.path.exists(os.path.join(web, u.path.lstrip("/"))):
                F("enllac_trencat", f"Enllaç intern trencat: {h}")
        if a.canonical and not noindex and sitemap and a.canonical not in sitemap:
            F("fora_sitemap", "Indexable però no és al sitemap")
        if noindex and a.canonical in sitemap:
            F("noindex_sitemap", "És noindex però és al sitemap")
        # Entendre
        lt = len(a.titol)
        if not a.titol:
            F("sense_title", "Sense <title>")
        elif not (LIMITS["titol"][0] <= lt <= LIMITS["titol"][1]):
            F("llargada", f"Title de {lt} caràcters (ideal {LIMITS['titol'][0]}–{LIMITS['titol'][1]})")
        if not a.desc:
            F("llargada" if noindex else "sense_descripcio", "Sense meta description")
        elif not (LIMITS["descripcio"][0] <= len(a.desc) <= LIMITS["descripcio"][1]):
            F("llargada", f"Meta description de {len(a.desc)} caràcters (ideal {LIMITS['descripcio'][0]}–{LIMITS['descripcio'][1]})")
        if len(a.h1) != 1:
            F("h1", f"{len(a.h1)} H1 (n'hi ha d'haver exactament 1)")
        marca = normal(a.og.get("og:site_name", ""))
        if marca and a.h1 and normal(a.h1[0]).strip(" .") in (marca, f"{marca}.", ""):
            F("h1_marca", f"L'H1 és només el nom de la marca («{a.h1[0]}»): digues què oferiu")
        if not a.lang:
            F("sense_lang", "<html> sense atribut lang")
        anterior, vistos = 0, defaultdict(int)
        for nivell, text in a.encap:
            if anterior and nivell > anterior + 1:
                F("salt_encap", f"Salt d'encapçalament H{anterior} → H{nivell} («{text[:50]}»)")
            anterior = nivell
            if not re.search(r"[^\W\d_]{3,}", text):
                F("encap_buit", f"H{nivell} buit o sense paraules: «{text}»")
            if nivell == 2:
                vistos[normal(text)] += 1
        for t, n in vistos.items():
            if n > 1 and t:
                F("encap_duplicat", f"H2 repetit {n} vegades: «{t[:50]}»")
        faq_schema = 0
        for bloc in a.jsonld:
            try:
                d = json.loads(bloc)
            except json.JSONDecodeError as e:
                F("jsonld_invalid", f"JSON-LD no vàlid: {e}")
                continue
            buits = sorted(set(recorre(d)))
            if buits:
                F("schema_buit", "Camps buits al JSON-LD: " + ", ".join(buits[:6]))
            for g in nodes(d):
                t = tipus(g)
                if "FAQPage" in t:
                    faq_schema = len(g.get("mainEntity", []))
                if set(t) & {"Organization", "LocalBusiness", "ProfessionalService", "Person"}:
                    entitats += 1
                    amb_sameas += bool(g.get("sameAs"))
                if set(t) & {"Article", "BlogPosting", "NewsArticle"} and not g.get("author"):
                    F("sense_autor", f"{t[0]} sense author al schema")
        if not a.jsonld:
            F("sense_jsonld", "Sense dades estructurades (JSON-LD)")
        if faq_schema and faq_schema > a.faq_visibles:
            F("faq_schema", f"El schema FAQ té {faq_schema} preguntes però només se'n veuen {a.faq_visibles}")
        if a.og.get("og:type") == "article" and not any("author" in b for b in a.jsonld) \
                and not any(c == "sense_autor" for c, _ in troballes[ruta]):
            F("sense_autor", "Article sense autor identificat")
        og_img = a.og.get("og:image", "")
        if og_img and domini and og_img.startswith(domini):
            if not os.path.isfile(os.path.join(web, urlparse(og_img).path.lstrip("/"))):
                F("og_trencada", f"og:image apunta a un fitxer que no existeix: {urlparse(og_img).path}")
        falten = [k for k in ("og:title", "og:description", "og:image") if not a.og.get(k)]
        if falten and not noindex:
            F("og", "Falta " + ", ".join(falten) + ("" if a.twitter.get("twitter:card") else " i twitter:card"))
        # Valorar
        text = " ".join(a.text)
        paraules = len(re.findall(r"\w+", text))
        if not noindex and paraules < LIMITS["paraules_min"]:
            F("prim", f"Contingut prim: {paraules} paraules (mínim recomanat {LIMITS['paraules_min']})")
        kw = keywords.get(ruta)
        if kw and paraules and not noindex:
            n = len(re.findall(r"\b" + re.escape(normal(kw)) + r"\b", normal(text)))
            per100 = n / paraules * 100
            if n >= 5 and per100 > 2.5:
                F("sobreopt", f"«{kw}» surt {n} vegades ({per100:.1f} per cada 100 paraules): escriu-ho de manera més natural")
        if not noindex and paraules >= 80:
            textos[ruta] = shingles(text)
        # Rendiment
        total_kb, sense_alt = 0, 0
        for img in a.imatges:
            src = img.get("src") or ""
            if "alt" not in img:
                sense_alt += 1
            if src.startswith("/") and not src.startswith("//"):
                fitxer = os.path.join(web, urlparse(src).path.lstrip("/"))
                if os.path.exists(fitxer):
                    kb = os.path.getsize(fitxer) / 1024
                    total_kb += kb
                    if kb > LIMITS["img_kb_greu"]:
                        F("img_greu", f"{src} pesa {kb / 1024:.1f} MB")
                    elif kb > LIMITS["img_kb_avis"]:
                        F("img_pes", f"{src} pesa {kb:.0f} KB")
                    if src.lower().endswith((".jpg", ".jpeg", ".png")) and kb > 100:
                        F("img_format", f"{src}: prova WebP/AVIF")
            if not src.lower().endswith(".svg") and not (img.get("width") and img.get("height")):
                F("img_mida", f"Imatge sense width/height: {src[:60]}")
        if sense_alt:
            F("sense_alt", f"{sense_alt} imatges sense alt")
        if total_kb > LIMITS["imatges_pagina_kb"]:
            F("pes_pagina", f"{total_kb / 1024:.1f} MB d'imatges en aquesta pàgina")
        for fr in a.iframes:
            if (fr.get("loading") or "").lower() != "lazy" and not (fr.get("src") or "").startswith("about:"):
                F("iframe", f"iframe sense loading=lazy: {(fr.get('src') or fr.get('data-src') or '')[:60]}")
        if not noindex:
            idioma = ruta.strip("/").split("/")[0] if a.hreflang else ""
            titols[(idioma, a.titol)].append(ruta)
            descs[(idioma, a.desc)].append(ruta)
    for (_, t), rutes in titols.items():
        if t and len(rutes) > 1:
            for r in rutes:
                afegeix(r, "title_duplicat", f"Title duplicat amb {', '.join(x for x in rutes if x != r)}")
    for (_, t), rutes in descs.items():
        if t and len(rutes) > 1:
            for r in rutes:
                afegeix(r, "desc_duplicada", f"Description duplicada amb {', '.join(x for x in rutes if x != r)}")
    # Entitat
    if not entitats:
        afegeix(LLOC, "entitat", "Cap pàgina declara Organization, LocalBusiness o Person al schema")
    elif not amb_sameas:
        afegeix(LLOC, "entitat", "L'entitat no té sameAs (perfils oficials: LinkedIn, Google Business, xarxes)")
    # Canibalització: text compartit entre pàgines del mateix idioma
    rutes = sorted(textos)
    for i, r1 in enumerate(rutes):
        for r2 in rutes[i + 1:]:
            if pagines[r1].lang != pagines[r2].lang:
                continue
            s1, s2 = textos[r1], textos[r2]
            comu = len(s1 & s2) / max(1, min(len(s1), len(s2)))
            if comu >= LIMITS["canibal_greu"]:
                afegeix(r1, "canibal_greu", f"Comparteix el {comu:.0%} del text amb {r2}")
            elif comu >= LIMITS["canibal_avis"]:
                afegeix(r1, "canibal", f"Comparteix el {comu:.0%} del text amb {r2}")
    marques = manifest.get("marques", [])
    return pagines, troballes, marques


def informe(dir_projecte, pagines, troballes, marques):
    tot = [(r, c, m) for r, ll in troballes.items() for c, m in ll]
    ne = sum(1 for _, c, _ in tot if CODIS[c][1])
    per_prio = defaultdict(int)
    for _, c, _ in tot:
        per_prio[CODIS[c][0]] += 1
    L = ["# Comprovació SEO", "", f"- Pàgines: **{len(pagines)}**", f"- Errors que bloquegen la publicació: **{ne}**"]
    L += [f"- {PRIO[p]}: **{per_prio.get(p, 0)}**" for p in (1, 2, 3)]
    L += [f"- Marques pendents ([VERIFICAR], [DATA]…): **{len(marques)}**", ""]
    # Què arreglar primer: per tipus de problema, ordenat per prioritat i abast
    per_codi = defaultdict(set)
    for r, c, _ in tot:
        per_codi[c].add(r)
    if per_codi:
        L += ["## Què arreglar primer", "", "| Prioritat | Problema | Pàgines | Per què importa |", "|---|---|---|---|"]
        for c in sorted(per_codi, key=lambda c: (CODIS[c][0], -len(per_codi[c]))):
            p, _, perque = CODIS[c]
            exemple = next(m for r, cc, m in tot if cc == c)
            n = len(per_codi[c])
            abast = "tot el lloc" if per_codi[c] == {LLOC} else f"{n}"
            L.append(f"| {PRIO[p]} | {exemple}{' (i més)' if n > 1 else ''} | {abast} | {perque} |")
        L += ["", "_La prioritat és per impacte en el negoci. Revisa-la amb criteri: un avís tècnic no sempre és el més urgent._", ""]
    L.append("## Detall per pàgina")
    L.append("")
    for ruta in sorted(troballes, key=lambda r: (r != LLOC, r)):
        L.append(f"### {ruta}")
        for c, m in sorted(troballes[ruta], key=lambda x: CODIS[x[0]][0]):
            L.append(f"- {PRIO[CODIS[c][0]][:1]} {m}{'  **(bloqueja)**' if CODIS[c][1] else ''}")
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
    print(text.split("\n## Detall")[0])
    print(f"Informe complet: {sortida}")
    sys.exit(1 if ne else 0)


if __name__ == "__main__":
    main()
