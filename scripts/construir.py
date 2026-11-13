#!/usr/bin/env python3
"""Generador de la web d'un projecte de la Fàbrica de webs SEO.

Llegeix:  lloc.yaml, contingut/<idioma>/**/*.md, directori/fitxes.yaml (opcional)
Escriu:   web/  (HTML per pàgina, assets, sitemap.xml, robots.txt, llms.txt, 404.html)

Ús:
    python3 construir.py [carpeta-projecte] [--estricte]

  --estricte      surt amb error si queden marques [VERIFICAR]/[DATA]/... (per publicar)

Cada pàgina en Markdown porta una capçalera YAML. Camps principals:
    clau, slug, titol, descripcio, tipus, pare, keyword, noindex, actualitzat,
    autor, revisor, faq, relacionades, schema, og_imatge, plantilla
Al cos: "# H1", enllaços interns "[text](@clau)" i blocs "::: component ... :::".
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bots_ia  # noqa: E402

try:
    import yaml
    import markdown
    from markdown.extensions.toc import slugify_unicode
    import jinja2
except ImportError as e:  # pragma: no cover
    sys.exit(f"Falta una llibreria ({e.name}). Instal·la-les amb: pip install -r requirements.txt")

AQUI = os.path.dirname(os.path.abspath(__file__))
ARREL_PLUGIN = os.path.dirname(AQUI)

# [VERIFICAR], [VERIFICAR amb X], [DATA], [ID-3], [INSTAL·LADOR VERIFICAT]...
RE_MARCA = re.compile(r"\[(?:VERIFICAR|PENDENT|DATA|[A-ZÀ-ÚÇ][A-ZÀ-ÚÇ·\-]{2,}(?:[ \-][A-ZÀ-ÚÇ·\-0-9]+)*)(?:[^\]\[<>]*)\](?!\()")
RE_DIRECTIVA = re.compile(r"^:::\s*([a-z0-9_-]+)\s*(.*)$")
RE_ATTR = re.compile(r'([a-z_]+)=("([^"]*)"|\'([^\']*)\'|(\S+))')
RE_ENLLAC_CLAU = re.compile(r'(href|src)="@([a-z0-9_\-]+)(#[^"]*)?"')
RE_ENLLAC_MD = re.compile(r"\]\(@([a-z0-9_\-]+)(#[^)\s]*)?\)")


# ----------------------------------------------------------------------------- utilitats
def llegir_yaml(ruta, defecte=None):
    if not os.path.exists(ruta):
        return defecte
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f) or defecte


def tr(valor, idioma):
    """Valor traduïble: text pla o {ca: ..., es: ...}."""
    if isinstance(valor, dict):
        return valor.get(idioma) or next(iter(valor.values()), "")
    return valor if valor is not None else ""


def separar_capcalera(text):
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            cap = yaml.safe_load(parts[0][3:]) or {}
            return cap, parts[1].lstrip("\n")
    return {}, text


def attrs(cadena):
    out = {}
    for m in RE_ATTR.finditer(cadena or ""):
        out[m.group(1)] = m.group(3) if m.group(3) is not None else (m.group(4) if m.group(4) is not None else m.group(5))
    return out


def mida_imatge(ruta):
    """(amplada, alçada) d'una imatge PNG, JPEG, GIF o WebP sense llibreries externes; None si no es pot llegir."""
    import struct
    try:
        with open(ruta, "rb") as f:
            cap = f.read(32)
            if cap[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", cap[16:24])
            if cap[:6] in (b"GIF87a", b"GIF89a"):
                return struct.unpack("<HH", cap[6:10])
            if cap[:4] == b"RIFF" and cap[8:12] == b"WEBP":
                if cap[12:16] == b"VP8X":
                    return (int.from_bytes(cap[24:27], "little") + 1, int.from_bytes(cap[27:30], "little") + 1)
                if cap[12:16] == b"VP8 ":
                    f.seek(26)
                    w, h = struct.unpack("<HH", f.read(4))
                    return (w & 0x3FFF, h & 0x3FFF)
                if cap[12:16] == b"VP8L":
                    b = cap[21:25]
                    return (1 + (((b[1] & 0x3F) << 8) | b[0]), 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6)))
            if cap[:2] == b"\xff\xd8":
                f.seek(2)
                while True:
                    m = f.read(2)
                    if len(m) < 2 or m[0] != 0xFF:
                        return None
                    if m[1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        f.read(3)
                        h, w = struct.unpack(">HH", f.read(4))
                        return (w, h)
                    f.seek(struct.unpack(">H", f.read(2))[0] - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def text_pla(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


# ----------------------------------------------------------------------------- generador
class Lloc:
    def __init__(self, dir_projecte):
        self.dir = os.path.abspath(dir_projecte)
        self.cfg = llegir_yaml(os.path.join(self.dir, "lloc.yaml"), {})
        if not self.cfg:
            sys.exit(f"No trobo lloc.yaml a {self.dir}")
        self.idiomes = self.cfg.get("idiomes") or ["ca"]
        self.idioma_defecte = self.cfg.get("idioma_defecte") or self.idiomes[0]
        self.prefix = self.cfg.get("prefix_idioma", len(self.idiomes) > 1)
        self.domini_real = (self.cfg.get("domini") or "").rstrip("/")
        self.sortida = os.path.join(self.dir, "web")
        tema = self.cfg.get("tema", "base")
        self.dir_tema = os.path.join(self.dir, "tema") if tema == "tema" else os.path.join(ARREL_PLUGIN, "temes", tema)
        carregadors = [jinja2.FileSystemLoader(self.dir_tema)]
        if tema != "base":
            carregadors.append(jinja2.FileSystemLoader(os.path.join(ARREL_PLUGIN, "temes", "base")))
        self.env = jinja2.Environment(loader=jinja2.ChoiceLoader(carregadors), autoescape=False,
                                      trim_blocks=True, lstrip_blocks=True)
        self.env.filters["tr"] = tr
        self.env.filters["esc"] = lambda s: html.escape(str(s or ""), quote=True)
        self.dir_cfg = self.cfg.get("directori") or {}
        self.fitxes = llegir_yaml(os.path.join(self.dir, "directori", "fitxes.yaml"), []) or []
        self.pagines = []          # totes les pàgines (dict)
        self.per_clau = {}         # (clau, idioma) -> pàgina
        self.avisos = []
        self.marques = []          # (url, text)

    # --- rutes
    def base_idioma(self, idioma):
        return f"/{idioma}/" if self.prefix else "/"

    def ruta(self, idioma, slug):
        slug = (slug or "").strip("/")
        return self.base_idioma(idioma) + (slug + "/" if slug else "")

    def absoluta(self, ruta):
        return (self.domini_real or "") + ruta

    # --- lectura de continguts
    def llegir(self):
        for idioma in self.idiomes:
            base = os.path.join(self.dir, "contingut", idioma)
            if not os.path.isdir(base):
                self.avisos.append(f"No hi ha contingut per a l'idioma «{idioma}» (contingut/{idioma}/)")
                continue
            for arrel, _, fitxers in os.walk(base):
                for nom in sorted(fitxers):
                    if not nom.endswith(".md"):
                        continue
                    ruta = os.path.join(arrel, nom)
                    with open(ruta, encoding="utf-8") as f:
                        cap, cos = separar_capcalera(f.read())
                    rel = os.path.relpath(ruta, base)
                    clau = cap.get("clau") or os.path.splitext(rel)[0].replace(os.sep, "-")
                    if "slug" in cap:
                        slug = cap.get("slug") or ""
                    else:
                        slug = "" if rel in ("index.md", "inici.md") else os.path.splitext(rel)[0].replace(os.sep, "/")
                    p = dict(cap)
                    p.update(clau=clau, slug=slug, idioma=idioma, font=os.path.relpath(ruta, self.dir), cos_md=cos,
                             url=self.ruta(idioma, slug))
                    if (clau, idioma) in self.per_clau:
                        self.avisos.append(f"Clau repetida «{clau}» en {idioma}: {p['font']}")
                    self.per_clau[(clau, idioma)] = p
                    self.pagines.append(p)
        # pàgines de fitxa del directori
        if self.dir_cfg.get("actiu") and self.dir_cfg.get("pagina_fitxa"):
            for fx in self.fitxes:
                for idioma in self.idiomes:
                    ruta_fx = tr(self.dir_cfg.get("ruta_fitxa", "fitxa"), idioma)
                    slug = f"{ruta_fx}/{fx['slug']}"
                    clau = f"fitxa-{fx['slug']}"
                    p = {"clau": clau, "slug": slug, "idioma": idioma, "tipus": "fitxa", "fitxa": fx,
                         "titol": tr(fx.get("titol"), idioma) or tr(self.dir_cfg.get("titol_fitxa") or "{nom} · {municipi} | {lloc}", idioma).format(
                             nom=fx["nom"], municipi=fx.get("municipi", ""), comarca=fx.get("comarca", ""), lloc=self.cfg.get("nom", "")),
                         "descripcio": tr(fx.get("descripcio_meta") or fx.get("descripcio"), idioma),
                         "pare": fx.get("pare"), "cos_md": tr(fx.get("text"), idioma) or "", "plantilla": "fitxa.html",
                         "font": "directori/fitxes.yaml", "url": self.ruta(idioma, slug), "h1": fx["nom"]}
                    self.per_clau[(clau, idioma)] = p
                    self.pagines.append(p)

    def url_clau(self, clau, idioma, origen):
        p = self.per_clau.get((clau, idioma))
        if not p and self.per_clau.get((clau, self.idioma_defecte)):
            self.avisos.append(f"@{clau} no existeix en «{idioma}»: enllaço a la versió «{self.idioma_defecte}» (a {origen})")
            p = self.per_clau[(clau, self.idioma_defecte)]
        if not p:
            self.avisos.append(f"Enllaç a una clau que no existeix: @{clau} (a {origen})")
            return "#"
        return p["url"]

    # --- markdown i components
    def markdown(self, text, pagina):
        text = RE_ENLLAC_MD.sub(lambda m: "](" + self.url_clau(m.group(1), pagina["idioma"], pagina["font"]) + (m.group(2) or "") + ")", text)
        # una llista just després d'un paràgraf (sense línia en blanc) també ha de ser llista
        text = re.sub(r"(?m)^(?![ \t]*(?:[-*+]|\d+\.)\s)(?![ \t]*$)(?!\|)(.+)\n(?=[ \t]*(?:[-*+]|\d+\.)\s)", r"\1\n\n", text)
        md = markdown.Markdown(extensions=["tables", "attr_list", "md_in_html", "sane_lists", "toc"],
                               extension_configs={"toc": {"slugify": slugify_unicode, "permalink": False}})
        return md.convert(text)

    def cos(self, pagina):
        """Converteix el cos: separa l'H1, resol directives i enllaços."""
        linies = pagina["cos_md"].split("\n")
        h1 = pagina.get("h1")
        if not h1:
            for i, l in enumerate(linies):
                if l.startswith("# "):
                    h1 = l[2:].strip()
                    linies.pop(i)
                    break
        pagina["h1"] = h1 or pagina.get("titol", "")
        trossos, buffer, i = [], [], 0
        while i < len(linies):
            m = RE_DIRECTIVA.match(linies[i].strip())
            if m and m.group(1):
                if buffer:
                    trossos.append(self.markdown("\n".join(buffer), pagina))
                    buffer = []
                nom, at = m.group(1), attrs(m.group(2))
                interior, i = [], i + 1
                while i < len(linies) and linies[i].strip() != ":::":
                    interior.append(linies[i])
                    i += 1
                trossos.append(self.component(nom, at, "\n".join(interior), pagina, previ="".join(trossos)))
            else:
                buffer.append(linies[i])
            i += 1
        if buffer:
            trossos.append(self.markdown("\n".join(buffer), pagina))
        h = "\n".join(trossos)
        h = RE_ENLLAC_CLAU.sub(lambda m: f'{m.group(1)}="{self.url_clau(m.group(2), pagina["idioma"], pagina["font"])}{m.group(3) or ""}"', h)
        return h

    def component(self, nom, at, interior, pagina, previ=""):
        ctx = {"at": at, "idioma": pagina["idioma"], "pagina": pagina, "lloc": self.cfg}
        if nom == "targetes":
            targetes = []
            for bloc in re.split(r"^###\s+", interior, flags=re.M):
                if not bloc.strip():
                    continue
                titol, _, resta = bloc.partition("\n")
                enllac = None
                mt = re.match(r"\[(.+)\]\((.+)\)$", titol.strip())
                if mt:
                    titol, enllac = mt.group(1), mt.group(2)
                    if enllac.startswith("@"):
                        enllac = self.url_clau(enllac[1:], pagina["idioma"], pagina["font"])
                targetes.append({"titol": titol.strip(), "enllac": enllac, "html": self.markdown(resta, pagina)})
            ctx["targetes"] = targetes
        elif nom == "directori":
            fitxes = self.filtrar_fitxes(at)
            pagina.setdefault("fitxes_llistades", []).extend(fitxes)
            ctx["fitxes"] = fitxes
            # nivell dels noms: H3 si el directori és dins una secció (ja hi ha un H2 abans), H2 si va just després de l'H1
            nivell = str(at.get("nivell") or (3 if "<h2" in previ else 2))
            ctx["nivell"] = nivell if nivell in ("2", "3", "4") else "3"
            ctx["ruta_fitxa"] = (lambda fx: self.ruta(pagina["idioma"], f"{tr(self.dir_cfg.get('ruta_fitxa', 'fitxa'), pagina['idioma'])}/{fx['slug']}")) \
                if self.dir_cfg.get("pagina_fitxa") else (lambda fx: None)
            minim = int(pagina.get("min_fitxes") or self.dir_cfg.get("min_fitxes_indexar") or 0)
            if minim and len(fitxes) < minim and not pagina.get("noindex"):
                pagina["noindex"] = True
                self.avisos.append(f"{pagina['url']}: només {len(fitxes)} fitxes (mínim {minim}) → noindex automàtic")
        ctx["html"] = self.markdown(interior, pagina) if interior.strip() else ""
        try:
            plantilla = self.env.get_template(f"components/{nom}.html")
        except jinja2.TemplateNotFound:
            self.avisos.append(f"Component desconegut «{nom}» a {pagina['font']}")
            return ctx["html"]
        return plantilla.render(**ctx)

    def filtrar_fitxes(self, at):
        res = []
        for fx in self.fitxes:
            ok = True
            for k, v in at.items():
                if k in ("limit", "ordre", "titol"):
                    continue
                camp = fx.get(k) if k != "servei" else fx.get("serveis", [])
                if isinstance(camp, list):
                    ok &= v in camp
                else:
                    ok &= str(camp or "").lower() == v.lower()
            if ok:
                res.append(fx)
        res.sort(key=lambda f: (not f.get("destacat"), f.get("nom", "")))
        if at.get("limit"):
            res = res[: int(at["limit"])]
        return res

    # --- schema
    def schema(self, p):
        org_cfg = self.cfg.get("organitzacio") or {}
        org_id = self.absoluta("/#org")
        web_id = self.absoluta("/#web")
        grafs = [
            {"@type": org_cfg.get("tipus", "Organization"), "@id": org_id, "name": org_cfg.get("nom") or self.cfg.get("nom"),
             "url": self.absoluta("/"), "description": tr(org_cfg.get("descripcio"), p["idioma"]) or None,
             "logo": self.absoluta(self.cfg["logo"]) if self.cfg.get("logo") else None,
             "sameAs": org_cfg.get("perfils") or None},
            {"@type": "WebSite", "@id": web_id, "name": self.cfg.get("nom"), "url": self.absoluta("/"),
             "inLanguage": self.idiomes, "publisher": {"@id": org_id}},
        ]
        url = self.absoluta(p["url"])
        pagina = {"@type": "WebPage", "@id": url + "#pagina", "url": url, "name": p.get("titol"),
                  "description": p.get("descripcio"), "inLanguage": p["idioma"], "isPartOf": {"@id": web_id}}
        if p.get("actualitzat"):
            pagina["dateModified"] = str(p["actualitzat"])
        autors = self.cfg.get("autors") or {}

        def persona(idp):
            a = autors.get(idp)
            if not a:
                self.avisos.append(f"{p['font']}: autor/revisor «{idp}» no és a lloc.yaml → autors")
                return None
            d = {"@type": "Person", "name": a.get("nom"), "jobTitle": tr(a.get("carrec"), p["idioma"]) or None,
                 "sameAs": a.get("perfils") or None}
            if a.get("url"):
                d["url"] = self.absoluta(self.url_clau(a["url"][1:], p["idioma"], "lloc.yaml")) if a["url"].startswith("@") else a["url"]
            return {k: v for k, v in d.items() if v}
        if p.get("revisor") and persona(p["revisor"]):
            pagina["reviewedBy"] = persona(p["revisor"])
        bc = self.molles(p)
        if len(bc) > 1:
            pagina["breadcrumb"] = {"@id": url + "#molles"}
            grafs.append({"@type": "BreadcrumbList", "@id": url + "#molles", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": b["nom"], "item": self.absoluta(b["url"])} for i, b in enumerate(bc)]})
        grafs.append(pagina)
        if p.get("tipus") in ("guia", "article") and p.get("autor"):
            art = {"@type": "Article", "@id": url + "#article", "headline": p.get("h1"), "mainEntityOfPage": {"@id": url + "#pagina"},
                   "inLanguage": p["idioma"], "publisher": {"@id": org_id}, "author": persona(p["autor"])}
            if p.get("actualitzat"):
                art["dateModified"] = str(p["actualitzat"])
            if p.get("publicat"):
                art["datePublished"] = str(p["publicat"])
            grafs.append(art)
        if p.get("faq"):
            grafs.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
                {"@type": "Question", "name": text_pla(self.markdown(f["p"], p)),
                 "acceptedAnswer": {"@type": "Answer", "text": text_pla(self.markdown(f["r"], p))}} for f in p["faq"]]})
        fitxes = p.get("fitxes_llistades") or []
        if fitxes:
            grafs.append({"@type": "ItemList", "@id": url + "#llista", "numberOfItems": len(fitxes), "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": self.schema_fitxa(fx, p["idioma"])} for i, fx in enumerate(fitxes)]})
        if p.get("tipus") == "fitxa":
            grafs.append(self.schema_fitxa(p["fitxa"], p["idioma"]))
        for extra in p.get("schema") or []:
            grafs.append(extra)
        net = [{k: v for k, v in g.items() if v not in (None, [], "")} for g in grafs]
        return json.dumps({"@context": "https://schema.org", "@graph": net}, ensure_ascii=False, indent=1)

    def schema_fitxa(self, fx, idioma):
        d = {"@type": fx.get("schema_tipus") or self.dir_cfg.get("schema_tipus") or "LocalBusiness", "name": fx.get("nom"),
             "description": tr(fx.get("descripcio"), idioma) or None, "url": fx.get("web") or None,
             "telephone": fx.get("telefon") or None}
        if fx.get("municipi"):
            d["address"] = {"@type": "PostalAddress", "addressLocality": fx["municipi"], "addressRegion": fx.get("regio") or None}
            d["address"] = {k: v for k, v in d["address"].items() if v}
        if fx.get("zona"):
            d["areaServed"] = fx["zona"]
        return {k: v for k, v in d.items() if v}

    def molles(self, p):
        cadena, vist, actual = [], set(), p
        while actual and actual["clau"] not in vist:
            vist.add(actual["clau"])
            nom = actual.get("molla") or ({"ca": "Inici", "es": "Inicio", "en": "Home"}.get(p["idioma"], "Home")
                                          if actual.get("slug") == "" else actual.get("h1") or actual.get("titol"))
            cadena.insert(0, {"nom": nom, "url": actual["url"]})
            pare = actual.get("pare")
            if pare is None and actual.get("slug"):
                pare = next((x["clau"] for x in self.pagines if x["idioma"] == p["idioma"] and x.get("slug") == ""), None)
            actual = self.per_clau.get((pare, p["idioma"])) if pare else None
        return cadena

    # --- render
    def alternatives(self, p):
        alt = []
        for idioma in self.idiomes:
            q = self.per_clau.get((p["clau"], idioma))
            if q and not q.get("noindex"):
                alt.append({"idioma": idioma, "url": self.absoluta(q["url"])})
        if len(alt) > 1:
            defecte = next((a for a in alt if a["idioma"] == self.idioma_defecte), alt[0])
            alt.append({"idioma": "x-default", "url": defecte["url"]})
        return alt if len(alt) > 1 else []

    def menu(self, items, idioma):
        out = []
        for it in items or []:
            enllac = it.get("enllac", "#")
            if enllac.startswith("@"):
                clau, _, ancora = enllac[1:].partition("#")
                enllac = self.url_clau(clau, idioma, "lloc.yaml") + (f"#{ancora}" if ancora else "")
            out.append({"text": tr(it.get("text"), idioma), "url": enllac,
                        "fills": self.menu(it.get("fills"), idioma) if it.get("fills") else []})
        return out

    def construir(self, estricte=False):
        self.llegir()
        if os.path.exists(self.sortida):
            shutil.rmtree(self.sortida)
        os.makedirs(self.sortida)
        # assets: tema base → tema propi → assets del projecte
        for origen in [os.path.join(ARREL_PLUGIN, "temes", "base", "assets"), os.path.join(self.dir_tema, "assets"),
                       os.path.join(self.dir, "assets")]:
            if os.path.isdir(origen):
                shutil.copytree(origen, os.path.join(self.sortida, "assets"), dirs_exist_ok=True)
        self.escriure_tokens()
        # primer passada: cossos (cal per saber noindex i fitxes abans de les alternatives)
        for p in self.pagines:
            p["cos_html"] = self.cos(p)
        for p in self.pagines:
            self.render(p)
        self.sitemap()
        self.extres()
        self.avisos = list(dict.fromkeys(self.avisos))
        manifest = [{"url": p["url"], "clau": p["clau"], "idioma": p["idioma"], "titol": p.get("titol"),
                     "noindex": bool(p.get("noindex")), "font": p["font"], "tipus": p.get("tipus", "pagina"),
                     "keyword": p.get("keyword")} for p in self.pagines]
        with open(os.path.join(self.sortida, "_pagines.json"), "w", encoding="utf-8") as f:
            json.dump({"generat": dt.datetime.now().isoformat(timespec="seconds"), "pagines": manifest,
                       "marques": [{"url": u, "text": t} for u, t in self.marques], "avisos": self.avisos},
                      f, ensure_ascii=False, indent=1)
        print(f"✓ {len(self.pagines)} pàgines generades a {os.path.relpath(self.sortida)}")
        print(f"  {len(self.marques)} marques pendents ([VERIFICAR], [DATA]…)")
        self.avisos = list(dict.fromkeys(self.avisos))
        for a in self.avisos:
            print("  ⚠", a)
        if estricte and self.marques:
            print("✗ Mode estricte: queden marques pendents. No es pot publicar.")
            sys.exit(1)

    def escriure_tokens(self):
        d = self.cfg.get("disseny") or {}
        vars_css = "\n".join(f"  --{k.replace('_', '-')}: {v};" for k, v in d.items() if k != "google_fonts")
        with open(os.path.join(self.sortida, "assets", "tokens.css"), "w", encoding="utf-8") as f:
            f.write(f"/* Generat des de lloc.yaml → disseny */\n:root {{\n{vars_css}\n}}\n")

    def render(self, p):
        idioma = p["idioma"]

        def marca(m):
            self.marques.append((p["url"], m.group(0)))
            return f'<mark class="verificar">{m.group(0)}</mark>'
        cos = RE_MARCA.sub(marca, p["cos_html"])
        faq = [{"p": self.markdown(f["p"], p).removeprefix("<p>").removesuffix("</p>"), "r": RE_MARCA.sub(marca, self.markdown(f["r"], p))}
               for f in p.get("faq") or []]
        relacionades = []
        for c in p.get("relacionades") or []:
            q = self.per_clau.get((c, idioma))
            if q:
                relacionades.append({"titol": q.get("molla") or q.get("h1") or q.get("titol"), "url": q["url"],
                                     "descripcio": q.get("descripcio")})
            else:
                self.avisos.append(f"{p['font']}: relacionada «{c}» no existeix")
        autors = self.cfg.get("autors") or {}
        og, og_mida = self.imatge_og(tr(p.get("og_imatge") or self.cfg.get("og_imatge"), idioma), p)
        ctx = {
            "lloc": self.cfg, "p": p, "idioma": idioma, "cos": cos, "faq": faq, "relacionades": relacionades,
            "index": [] if p.get("index") is False else [
                {"id": m.group(1), "text": text_pla(m.group(2))} for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', cos, re.S)],
            "titol": p.get("titol") or p.get("h1"), "descripcio": p.get("descripcio", ""),
            "canonical": self.absoluta(p["url"]), "alternatives": self.alternatives(p),
            "schema": self.schema(p), "molles": self.molles(p), "menu": self.menu(self.cfg.get("menu"), idioma),
            "peu": self.menu(self.cfg.get("peu"), idioma), "idiomes": self.idiomes,
            "altres_idiomes": [{"idioma": i, "url": self.per_clau[(p["clau"], i)]["url"]} for i in self.idiomes
                               if i != idioma and (p["clau"], i) in self.per_clau],
            "cta": {"text": tr((self.cfg.get("cta_principal") or {}).get("text"), idioma),
                    "url": self.menu([self.cfg.get("cta_principal")], idioma)[0]["url"] if self.cfg.get("cta_principal") else None},
            "autor": autors.get(p.get("autor")), "revisor": autors.get(p.get("revisor")),
            "og_imatge": self.absoluta(og) if og else "",
            "og_mida": og_mida,
            "inici": self.ruta(idioma, ""), "any": dt.date.today().year,
            "og_locale": (self.cfg.get("locales") or {}).get(idioma) or bots_ia.LOCALES.get(idioma, idioma),
            "og_alternes": [(self.cfg.get("locales") or {}).get(i) or bots_ia.LOCALES.get(i, i) for i in self.idiomes
                            if i != idioma and (p["clau"], i) in self.per_clau],
        }
        if not p.get("descripcio"):
            self.avisos.append(f"{p['url']}: sense meta descripció")
        if not ctx["og_imatge"] and not p.get("noindex") and not getattr(self, "_avis_og", False):
            self._avis_og = True
            self.avisos.append("Sense imatge OG: afegeix og_imatge a lloc.yaml (1200×630, < 300 KB) o a la pàgina")
        plantilla = self.env.get_template(p.get("plantilla") or "pagina.html")
        sortida = RE_ENLLAC_CLAU.sub(lambda m: f'{m.group(1)}="{self.url_clau(m.group(2), idioma, p["font"])}{m.group(3) or ""}"',
                                     plantilla.render(**ctx))
        desti = os.path.join(self.sortida, p["url"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(desti), exist_ok=True)
        with open(desti, "w", encoding="utf-8") as f:
            f.write(sortida)

    def sitemap(self):
        files = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
        avui = dt.date.today().isoformat()
        for p in self.pagines:
            if p.get("noindex"):
                continue
            files.append(f"  <url><loc>{self.absoluta(p['url'])}</loc><lastmod>{p.get('actualitzat') or avui}</lastmod>")
            for a in self.alternatives(p):
                files.append(f'    <xhtml:link rel="alternate" hreflang="{a["idioma"]}" href="{a["url"]}"/>')
            files.append("  </url>")
        files.append("</urlset>")
        with open(os.path.join(self.sortida, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write("\n".join(files) + "\n")

    def imatge_og(self, ruta, p):
        """Comprova que la imatge OG local existeix i en llegeix la mida real (PNG, JPEG, WebP, GIF)."""
        if not ruta:
            return "", None
        if ruta.startswith(("http://", "https://")):
            return ruta, None
        local = None
        for base in (os.path.join(self.dir), os.path.join(self.dir_tema), os.path.join(ARREL_PLUGIN, "temes", "base")):
            c = os.path.join(base, ruta.lstrip("/"))
            if os.path.isfile(c):
                local = c
                break
        if not local:
            self.avisos.append(f"Imatge OG «{ruta}» no existeix (a {p['font']}): no la poso fins que hi sigui")
            return "", None
        return ruta, mida_imatge(local)

    def robots_txt(self):
        """robots.txt amb els rastrejadors d'IA explícits (veure scripts/bots_ia.py)."""
        politica = self.cfg.get("bots_ia") or "permetre"
        if politica not in bots_ia.POLITIQUES:
            self.avisos.append(f"lloc.yaml: bots_ia «{politica}» no és vàlid ({', '.join(bots_ia.POLITIQUES)}); faig servir «permetre»")
            politica = "permetre"
        privades = [r if r.endswith("/") else r + "/" for r in (self.cfg.get("robots_bloquejar") or [])]
        L = [f"# robots.txt · {self.cfg.get('nom', '')}", f"# Política de rastrejadors d'IA: {politica}", ""]
        L += ["User-agent: *", "Allow: /"] + [f"Disallow: {r}" for r in privades] + [""]
        # Cercadors i assistents: explícits, perquè quedi clar que poden entrar
        for grup in ("cerca", "usuari"):
            L.append("# Cerca (clàssica i amb IA)" if grup == "cerca" else "# Assistents a petició de l'usuari")
            for b in bots_ia.BOTS[grup]:
                L.append(f"User-agent: {b}")
            L += ["Allow: /"] + [f"Disallow: {r}" for r in privades] + [""]
        bloc = bots_ia.bloquejats(politica)
        permesos = [x for x in bots_ia.BOTS["entrenament"] if x not in bloc]
        if permesos:
            L.append("# Entrenament de models (permès)")
            L += [f"User-agent: {x}" for x in permesos] + ["Allow: /"] + [f"Disallow: {r}" for r in privades] + [""]
        if bloc:
            L.append("# Entrenament de models (bloquejat)")
            L += [f"User-agent: {x}" for x in bloc] + ["Disallow: /", ""]
        L.append(f"Sitemap: {self.absoluta('/sitemap.xml')}")
        return "\n".join(L) + "\n"

    def extres(self):
        s = self.sortida
        with open(os.path.join(s, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(self.robots_txt())
        # llms.txt: resum per a cercadors amb IA
        linies = [f"# {self.cfg.get('nom')}", "", f"> {tr(self.cfg.get('descripcio'), self.idioma_defecte)}", ""]
        for idioma in self.idiomes:
            linies.append(f"## Pàgines ({idioma})")
            for p in self.pagines:
                if p["idioma"] == idioma and not p.get("noindex") and p.get("tipus") != "fitxa":
                    linies.append(f"- [{p.get('titol') or p.get('h1')}]({self.absoluta(p['url'])}): {p.get('descripcio', '')}")
            linies.append("")
        with open(os.path.join(s, "llms.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(linies))
        # arrel: si hi ha prefix d'idioma, redirigeix a l'idioma per defecte
        if self.prefix:
            desti = self.ruta(self.idioma_defecte, "")
            with open(os.path.join(s, "index.html"), "w", encoding="utf-8") as f:
                f.write(f'<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={desti}">'
                        f'<link rel="canonical" href="{self.absoluta(desti)}"><meta name="robots" content="noindex">'
                        f'<title>{html.escape(self.cfg.get("nom", ""))}</title></head><body>'
                        + " · ".join(f'<a href="{self.ruta(i, "")}">{i}</a>' for i in self.idiomes) + "</body></html>")
        plantilla = self.env.get_template("404.html")
        with open(os.path.join(s, "404.html"), "w", encoding="utf-8") as f:
            f.write(plantilla.render(lloc=self.cfg, idioma=self.idioma_defecte, inici=self.ruta(self.idioma_defecte, ""),
                                     menu=self.menu(self.cfg.get("menu"), self.idioma_defecte), peu=[], cta={}, any=dt.date.today().year,
                                     p={"idioma": self.idioma_defecte}, titol="404", descripcio="", canonical="", alternatives=[],
                                     schema="{}", molles=[], idiomes=self.idiomes, altres_idiomes=[], og_imatge=""))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dir_projecte = args[0] if args else os.getcwd()
    Lloc(dir_projecte).construir(estricte="--estricte" in sys.argv)


if __name__ == "__main__":
    main()
