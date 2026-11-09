#!/usr/bin/env python3
"""Dashboard de tots els projectes de la Fàbrica de webs SEO.

Ús:
    python3 dashboard.py <carpeta-arrel> [<carpeta-arrel> ...] [--sortida dashboard.html]

Busca fitxers projecte.yaml fins a 3 nivells per sota de cada arrel (per exemple ~/Projectes)
i genera una pàgina HTML autònoma amb l'estat de cada projecte, i un dashboard.json amb les mateixes dades.
"""
import datetime as dt
import html
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML: pip install -r requirements.txt")

FASES = [("f0_brief", "Brief"), ("f1_estrategia", "Estrat."), ("f2_keywords", "Paraules"), ("f2b_disseny", "Disseny"),
         ("f3_pagines", "Pàgines"), ("f4_construir", "Web"), ("f5_mesurar", "Mesura")]
ESTATS_PAGINA = ["idea", "keywords", "competencia", "estructura", "text", "revisio", "publicada"]
RE_MARCA = re.compile(r"\[(?:VERIFICAR|PENDENT|DATA)[^\]]*\]")
IGNORAR = {"web", "node_modules", ".git", "__pycache__", "csv"}


def trobar(arrels):
    trobats = []
    for arrel in arrels:
        arrel = os.path.expanduser(arrel)
        for dirpath, dirnames, fitxers in os.walk(arrel):
            prof = dirpath[len(arrel):].count(os.sep)
            dirnames[:] = [d for d in dirnames if d not in IGNORAR and not d.startswith(".")]
            if prof >= 3:
                dirnames[:] = []
            if "projecte.yaml" in fitxers:
                trobats.append(dirpath)
                dirnames[:] = []
    return sorted(set(trobats))


def estat_projecte(d):
    cfg = yaml.safe_load(open(os.path.join(d, "projecte.yaml"), encoding="utf-8")) or {}
    marques, darrer, n_contingut = 0, 0, 0
    for dirpath, dirnames, fitxers in os.walk(d):
        dirnames[:] = [x for x in dirnames if x not in IGNORAR and not x.startswith(".")]
        for f in fitxers:
            ruta = os.path.join(dirpath, f)
            try:
                darrer = max(darrer, os.path.getmtime(ruta))
            except OSError:
                pass
            if f.endswith(".md") and os.sep + "contingut" + os.sep in ruta:
                n_contingut += 1
                marques += len(RE_MARCA.findall(open(ruta, encoding="utf-8", errors="replace").read()))
    fases = cfg.get("fases") or {}
    fets = sum(1 for k, _ in FASES if (fases.get(k) or {}).get("estat") == "fet")
    actual = next((nom for k, nom in FASES if (fases.get(k) or {}).get("estat") == "en-curs"), None) \
        or next((nom for k, nom in FASES if (fases.get(k) or {}).get("estat") != "fet"), "Fet")
    pagines = cfg.get("pagines") or []
    per_estat = {e: sum(1 for p in pagines if p.get("estat") == e) for e in ESTATS_PAGINA}
    web = os.path.join(d, "web", "_pagines.json")
    generades = len(json.load(open(web, encoding="utf-8")).get("pagines", [])) if os.path.exists(web) else 0
    return {
        "carpeta": d, "nom": cfg.get("nom") or os.path.basename(d), "descripcio": cfg.get("descripcio", ""),
        "tipus": cfg.get("tipus", ""), "mode": cfg.get("mode", ""), "domini": cfg.get("domini", ""), "estat": cfg.get("estat", "actiu"),
        "idiomes": cfg.get("idiomes") or [], "fases": [{"clau": k, "nom": n, "estat": (fases.get(k) or {}).get("estat", "pendent")} for k, n in FASES],
        "fets": fets, "fase_actual": actual, "pagines": pagines, "per_estat": per_estat, "volum": sum(int(p.get("volum") or 0) for p in pagines),
        "pendents": cfg.get("pendents") or [], "bloquejos": cfg.get("bloquejos") or [], "seguent": cfg.get("seguent", ""),
        "metriques": cfg.get("metriques") or {}, "enllacos": cfg.get("enllacos") or {}, "marques": marques,
        "fitxers_contingut": n_contingut, "pagines_generades": generades,
        "actualitzat": dt.datetime.fromtimestamp(darrer).strftime("%Y-%m-%d") if darrer else "",
    }


def e(s):
    return html.escape(str(s or ""))


NOMS_FASE = {"f0_brief": ("Brief", "Brief"), "f1_estrategia": ("Estratègia", "Estrat."), "f2_keywords": ("Paraules clau", "Paraules"),
             "f2b_disseny": ("Disseny", "Disseny"), "f3_pagines": ("Pàgines", "Pàgines"), "f4_construir": ("Web", "Web"),
             "f5_mesurar": ("Mesura", "Mesura")}
NOMS_ESTAT = {"idea": "idea", "keywords": "paraules clau", "competencia": "competència", "estructura": "estructura",
              "text": "text", "revisio": "en revisió", "publicada": "publicades"}
MESOS_CA = ["de gener", "de febrer", "de març", "d'abril", "de maig", "de juny", "de juliol", "d'agost", "de setembre",
            "d'octubre", "de novembre", "de desembre"]

CSS = """
:root{--fons:#F4F5F7;--sup:#FFFFFF;--tinta:#161A23;--gris:#626A78;--linia:#E2E5EB;--fet:#3A3FB8;--fet-suau:#E6E7F7;
--torn:#E59E2E;--torn-fons:#FDF3E1;--torn-text:#6E4300;--bloq:#C2413A;--bloq-fons:#FBEAE8;--r:10px}
*{box-sizing:border-box}
body{margin:0;background:var(--fons);color:var(--tinta);font:15px/1.5 Geist,system-ui,sans-serif;font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
.pg{max-width:1120px;margin:0 auto;padding:3rem 1.5rem 4rem}
a{color:inherit;text-decoration-color:var(--linia);text-underline-offset:.2em}a:hover{text-decoration-color:var(--fet)}
:focus-visible{outline:2px solid var(--fet);outline-offset:2px}
.cap{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:.5rem 2rem;margin-bottom:.4rem}
h1{font-size:clamp(2rem,1.5rem + 2vw,2.75rem);line-height:1;letter-spacing:-.035em;font-weight:650;margin:0}
.data{color:var(--gris);font-size:.88rem}
.resum{font-size:1.15rem;color:var(--gris);margin:0 0 2.25rem;max-width:44rem}.resum b{color:var(--tinta);font-weight:600}
h2{font-size:1rem;font-weight:600;letter-spacing:-.01em;margin:0 0 .9rem}
.torn{background:var(--torn-fons);border-radius:var(--r);padding:1.25rem 1.4rem 1.1rem;margin-bottom:2.5rem}
.torn h2{color:var(--torn-text);display:flex;align-items:center;gap:.55rem}
.torn h2::before{content:"";width:.6rem;height:.6rem;border-radius:50%;background:var(--torn)}
.torn ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,22rem),1fr));gap:.1rem 2rem}
.torn li{padding:.5rem 0;border-top:1px solid color-mix(in srgb,var(--torn) 25%,transparent);display:grid;grid-template-columns:7.5rem 1fr;gap:1rem}
.torn .qui{color:var(--torn-text);font-weight:500;font-size:.85rem;padding-top:.08rem}
.torn li.bloq .qui{color:var(--bloq)}
.llista{display:grid;gap:1rem}
.proj{background:var(--sup);border:1px solid var(--linia);border-radius:var(--r);padding:1.5rem 1.6rem 1.25rem}
.proj__cap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem 1.5rem;align-items:baseline}
.proj h3{font-size:1.45rem;letter-spacing:-.025em;font-weight:650;margin:0}
.meta{color:var(--gris);font-size:.88rem;margin:.15rem 0 0}
.estat{font-size:.8rem;font-weight:500;color:var(--gris);border:1px solid var(--linia);border-radius:99px;padding:.1rem .65rem}
.desc{color:var(--gris);margin:.6rem 0 0;max-width:46rem}
/* Línia de fases: l'element memorable */
.linia{list-style:none;display:grid;grid-template-columns:repeat(7,1fr);margin:1.6rem 0 1.4rem;padding:0;position:relative}
.linia li{position:relative;padding-top:1.5rem;font-size:.8rem;color:var(--gris);text-align:center;line-height:1.25}
.linia li::before,.linia li::after{content:"";position:absolute;top:.42rem;height:3px;width:50%;background:var(--linia)}
.linia li::before{left:0}.linia li::after{right:0}
.linia li:first-child::before,.linia li:last-child::after{display:none}
.linia li.fet::before,.linia li.fet::after,.linia li.en-curs::before{background:var(--fet)}
.linia li.en-curs+li.en-curs::before{background:var(--torn)}
.linia li.en-curs:has(+li.en-curs)::after{background:var(--torn)}
.linia i{position:absolute;top:0;left:50%;width:1rem;height:1rem;margin-left:-.5rem;border-radius:50%;background:var(--sup);border:3px solid var(--linia);z-index:1}
.linia li.fet i{background:var(--fet);border-color:var(--fet)}
.linia li.en-curs i{border-color:var(--torn);box-shadow:0 0 0 4px var(--torn-fons)}
.linia li.fet{color:var(--tinta)}.linia li.en-curs{color:var(--tinta);font-weight:600}
.linia .curt{display:none}
.cos{display:grid;grid-template-columns:1.3fr 1fr 1.3fr;gap:1.5rem 2.25rem;padding-top:1.2rem;border-top:1px solid var(--linia)}
.etq{display:block;color:var(--gris);font-size:.82rem;margin-bottom:.4rem}
.barra{display:flex;height:.55rem;border-radius:99px;overflow:hidden;background:var(--fons);gap:2px;margin:.35rem 0 .55rem}
.barra span{display:block}
.llegenda{display:flex;flex-wrap:wrap;gap:.2rem .9rem;font-size:.82rem;color:var(--gris);margin:0;padding:0;list-style:none}
.llegenda i{display:inline-block;width:.55rem;height:.55rem;border-radius:2px;margin-right:.35rem}
.gran{font-size:1.6rem;font-weight:600;letter-spacing:-.03em;line-height:1.1}
.xif{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.xif .alerta{color:var(--torn-text)}
.seguent p{margin:0;font-size:1rem;line-height:1.45}
.peu{margin-top:1.1rem;display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem 1.5rem;font-size:.85rem;color:var(--gris)}
.peu nav{display:flex;gap:1rem}
details summary{cursor:pointer;color:var(--fet);font-weight:500;list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::after{content:" +";}details[open] summary::after{content:" –"}
table{width:100%;border-collapse:collapse;margin-top:.8rem;font-size:.88rem}
th,td{text-align:left;padding:.45rem .8rem .45rem 0;border-bottom:1px solid var(--linia)}
th{color:var(--gris);font-weight:500}td.n,th.n{text-align:right;padding-right:1.5rem}
.peu details[open]{flex-basis:100%;order:2}
.taula{overflow-x:auto}
.pt{display:inline-block;width:.55rem;height:.55rem;border-radius:2px;margin-right:.4rem}
.altres{margin-top:2rem;color:var(--gris)}
@media (max-width:860px){.cos{grid-template-columns:1fr}.pg{padding-top:2rem}}
@media (max-width:560px){.linia span{display:none!important}.linia{margin:1.25rem 0 1rem}.linia li{padding-top:1rem}.proj{padding:1.2rem 1.1rem}.torn li{grid-template-columns:1fr;gap:.1rem}}
"""
COLORS_ESTAT = {"idea": "#CDD1D9", "keywords": "#A9AEE6", "competencia": "#8D93DE", "estructura": "#7178D4",
                "text": "#555CC9", "revisio": "#E59E2E", "publicada": "#2E8A5E"}


def data_ca(d):
    return f"{d.day} {MESOS_CA[d.month - 1]} de {d.year}, {d:%H:%M}"


def num(n):
    return f"{n:,}".replace(",", ".")


def pagina(projectes):
    actius = [p for p in projectes if p["estat"] in ("actiu", "publicat")]
    altres = [p for p in projectes if p not in actius]
    n_pag = sum(len(p["pagines"]) for p in actius)
    n_pub = sum(p["per_estat"].get("publicada", 0) for p in actius)
    n_ver = sum(p["marques"] for p in actius)
    frase = (f"<b>{len(actius)}</b> {'projecte actiu' if len(actius) == 1 else 'projectes actius'}, <b>{n_pag}</b> pàgines planificades i "
             + (f"<b>{n_pub}</b> publicades" if n_pub else "cap de publicada encara")
             + (f". Queden <b>{n_ver}</b> dades per verificar." if n_ver else "."))
    torn = []
    for p in actius:
        torn += [f'<li class="bloq"><span class="qui">{e(p["nom"])} · bloquejat</span><span>{e(x)}</span></li>' for x in p["bloquejos"]]
        torn += [f'<li><span class="qui">{e(p["nom"])}</span><span>{e(x)}</span></li>' for x in p["pendents"]]
    torn_html = (f'<section class="torn" aria-labelledby="t-torn"><h2 id="t-torn">Et toca a tu ({len(torn)})</h2><ul>{"".join(torn)}</ul></section>'
                 if torn else "")
    ordre = {"actiu": 0, "publicat": 1}
    cos = "".join(render(p) for p in sorted(actius, key=lambda p: (ordre.get(p["estat"], 9), -p["fets"], p["nom"])))
    altres_html = ""
    if altres:
        altres_html = '<details class="altres"><summary>Projectes en pausa o arxivats (%d)</summary><div class="llista" style="margin-top:1rem">%s</div></details>' % (
            len(altres), "".join(render(p) for p in altres))
    return f"""<!DOCTYPE html><html lang="ca"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Projectes web · Dashboard</title><meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="pg">
<header class="cap"><h1>Projectes</h1><span class="data">Actualitzat el {data_ca(dt.datetime.now())}</span></header>
<p class="resum">{frase}</p>
{torn_html}
<main class="llista" aria-label="Projectes actius">{cos or '<p>No he trobat cap projecte.yaml.</p>'}</main>
{altres_html}
</div></body></html>"""


def render(p):
    fases = ""
    for f in p["fases"]:
        llarg, curt = NOMS_FASE.get(f["clau"], (f["nom"], f["nom"]))
        estat = {"fet": "fet", "en-curs": "en-curs"}.get(f["estat"], "pendent")
        fases += f'<li class="{estat}" title="{e(llarg)}: {e(f["estat"])}"><i></i><span class="llarg">{e(llarg)}</span><span class="curt">{e(curt)}</span></li>'
    en_curs = [NOMS_FASE[f["clau"]][0] for f in p["fases"] if f["estat"] == "en-curs" and f["clau"] in NOMS_FASE]
    total = len(p["pagines"])
    if total:
        barra = "".join(f'<span style="flex:{n};background:{COLORS_ESTAT[k]}" title="{e(NOMS_ESTAT[k])}: {n}"></span>'
                        for k, n in p["per_estat"].items() if n)
        llegenda = "".join(f'<li><i style="background:{COLORS_ESTAT[k]}"></i>{n} {e(NOMS_ESTAT[k])}</li>' for k, n in p["per_estat"].items() if n)
        pag_html = f'<span class="etq">Pàgines</span><span class="gran">{total}</span><div class="barra">{barra}</div><ul class="llegenda">{llegenda}</ul>'
    else:
        pag_html = '<span class="etq">Pàgines</span><p style="margin:0;color:var(--gris)">Encara no hi ha mapa de pàgines. Surt de la fase de paraules clau.</p>'
    gsc = p["metriques"].get("gsc") or {}
    if gsc:
        xif = (f'<div><span class="etq">Clics · {e(gsc.get("periode", ""))}</span><span class="gran">{num(int(gsc.get("clics", 0)))}</span></div>'
               f'<div><span class="etq">Impressions</span><span class="gran">{num(int(gsc.get("impressions", 0)))}</span></div>')
    else:
        xif = (f'<div><span class="etq">Cerques/mes objectiu</span><span class="gran">{num(p["volum"]) if p["volum"] else "–"}</span></div>'
               f'<div><span class="etq">Per verificar</span><span class="gran{" alerta" if p["marques"] else ""}">{p["marques"]}</span></div>')
    files = "".join(
        f'<tr><td>{e(pg.get("clau"))}</td><td>{e(pg.get("keyword", ""))}</td><td class="n">{num(int(pg["volum"])) if pg.get("volum") else "–"}</td>'
        f'<td><span class="pt" style="background:{COLORS_ESTAT.get(pg.get("estat"), "#CDD1D9")}"></span>{e(NOMS_ESTAT.get(pg.get("estat"), pg.get("estat", "")))}</td></tr>'
        for pg in sorted(p["pagines"], key=lambda x: -int(x.get("volum") or 0)))
    detall = (f'<details><summary>Veure les {total} pàgines</summary><div class="taula"><table><thead><tr><th>Pàgina</th><th>Paraula clau</th>'
              f'<th class="n">Cerques/mes</th><th>Estat</th></tr></thead><tbody>{files}</tbody></table></div></details>') if total else "<span></span>"
    domini = f' · <a href="https://{e(p["domini"])}">{e(p["domini"])}</a>' if p["domini"] and "[" not in p["domini"] else ""
    enllacos = "".join(f'<a href="{e(v)}">{e(k.capitalize())}</a>' for k, v in p["enllacos"].items())
    tipus = {"directori": "Directori", "marca-personal": "Marca personal", "negoci-local": "Negoci local"}.get(p["tipus"], p["tipus"].capitalize())
    mode = "a partir d'una web" if p["mode"] == "existent" else "des de zero"
    return f"""
<article class="proj">
  <div class="proj__cap"><div><h3>{e(p["nom"])}</h3><p class="meta">{e(tipus)} {mode} · {" i ".join(map(e, p["idiomes"]))}{domini}</p></div>
  <span class="estat">{"En curs: " + e(" i ".join(en_curs)) if en_curs else e(p["estat"].capitalize())}</span></div>
  {f'<p class="desc">{e(p["descripcio"])}</p>' if p["descripcio"] else ""}
  <ol class="linia" aria-label="Fases del projecte">{fases}</ol>
  <div class="cos">
    <div>{pag_html}</div>
    <div class="xif">{xif}</div>
    <div class="seguent"><span class="etq">Següent pas</span><p>{e(p["seguent"]) or "–"}</p></div>
  </div>
  <div class="peu">{detall}<nav>{enllacos}</nav></div>
</article>"""


def main():
    args = sys.argv[1:]
    sortida = "dashboard.html"
    if "--sortida" in args:
        i = args.index("--sortida")
        sortida = args[i + 1]
        del args[i:i + 2]
    arrels = args or [os.getcwd()]
    projectes = [estat_projecte(d) for d in trobar(arrels)]
    with open(sortida, "w", encoding="utf-8") as f:
        f.write(pagina(projectes))
    with open(os.path.splitext(sortida)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(projectes, f, ensure_ascii=False, indent=1)
    print(f"✓ {len(projectes)} projectes → {sortida}")
    for p in projectes:
        print(f"  · {p['nom']}: fase {p['fase_actual']}, {len(p['pagines'])} pàgines, {p['marques']} [VERIFICAR]")


if __name__ == "__main__":
    main()
