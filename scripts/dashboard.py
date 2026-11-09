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


CSS = """
:root{--t:#1d2021;--f:#f6f4ef;--b:#fff;--l:#e3ded4;--p:#1f5f5b;--a:#d9643a;--s:#6b6a66}
*{box-sizing:border-box}body{margin:0;background:var(--f);color:var(--t);font:15px/1.5 Inter,system-ui,sans-serif}
.cap{padding:2rem 2rem 1rem;max-width:1400px;margin:auto}h1{font:650 2rem/1.1 Fraunces,Georgia,serif;margin:0 0 .3rem}
.cap p{color:var(--s);margin:0}.totals{display:flex;flex-wrap:wrap;gap:.8rem;margin:1.2rem 0 0}
.totals div{background:var(--b);border:1px solid var(--l);border-radius:12px;padding:.7rem 1rem;min-width:9rem}
.totals b{display:block;font:650 1.6rem Fraunces,Georgia,serif;color:var(--p)}.totals span{font-size:.82rem;color:var(--s)}
.filtres{display:flex;gap:.4rem;margin-top:1rem}.filtres button{border:1px solid var(--l);background:var(--b);border-radius:99px;padding:.3rem .8rem;cursor:pointer}
.filtres button[aria-pressed=true]{background:var(--t);color:#fff;border-color:var(--t)}
.graella{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:1rem;padding:1rem 2rem 3rem;max-width:1400px;margin:auto}
.proj{background:var(--b);border:1px solid var(--l);border-radius:16px;padding:1.2rem 1.3rem;display:flex;flex-direction:column;gap:.8rem}
.proj header{display:flex;justify-content:space-between;gap:1rem;align-items:start}.proj h2{margin:0;font:650 1.3rem Fraunces,Georgia,serif}
.meta,.desc,footer{color:var(--s);font-size:.85rem;margin:0}.meta a{color:inherit}
.xip{font-size:.75rem;border-radius:99px;padding:.15rem .6rem;background:#e7f1ef;color:var(--p);font-weight:600;white-space:nowrap}
.xip--pausa{background:#f1eee8;color:var(--s)}.xip--publicat{background:#e8eefc;color:#2c4fa0}
.fases{display:flex;list-style:none;padding:0;margin:0;gap:3px}.f{flex:1;height:30px;border-radius:6px;background:#eeebe5;position:relative;display:grid;place-items:center}
.f span{font-size:.68rem;color:var(--s);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 2px}
.f--fet{background:var(--p)}.f--fet span{color:#fff}.f--en-curs{background:#f6dccf;outline:2px solid var(--a)}.f--en-curs span{color:#7a3115;font-weight:600}
.nums{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem}.nums div{background:var(--f);border-radius:10px;padding:.5rem .6rem}
.nums b{display:block;font-size:1.15rem}.nums span{font-size:.72rem;color:var(--s);line-height:1.2;display:block}.nums .alerta{background:#fff3c4}
.barra{display:flex;height:8px;border-radius:99px;overflow:hidden;background:#eeebe5}.seg--idea{background:#d8d3c9}.seg--keywords{background:#c2cfcb}
.seg--competencia{background:#9fbcb6}.seg--estructura{background:#7aa59d}.seg--text{background:#4f8a80}.seg--revisio{background:#e2a27f}.seg--publicada{background:var(--p)}
.gsc{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;border:1px dashed var(--l);border-radius:10px;padding:.6rem}.gsc b{display:block;font-size:1.1rem}
.gsc span{font-size:.72rem;color:var(--s)}.gsc p{grid-column:1/-1;margin:0;font-size:.72rem;color:var(--s)}
.bloc h3{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;margin:0 0 .3rem;color:var(--s)}.bloc ul{margin:0;padding-left:1.1rem}
.bloc--bloq{background:#fdeee6;border-radius:10px;padding:.6rem .8rem}.bloc--bloq h3{color:#a3401c}
.seg-pas{margin:0;background:#eef5f3;border-radius:10px;padding:.55rem .8rem}footer{margin-top:auto}
.llegenda{display:flex;flex-wrap:wrap;gap:.8rem;font-size:.78rem;color:var(--s);margin-top:.8rem}.llegenda i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:4px;vertical-align:-1px}
"""

JS = """
document.querySelectorAll('.filtres button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('.filtres button').forEach(x=>x.setAttribute('aria-pressed',x===b));
 document.querySelectorAll('.proj').forEach(p=>p.hidden=b.dataset.f!=='tots'&&p.dataset.estat!==b.dataset.f);});
"""


def pagina(projectes):
    actius = [p for p in projectes if p["estat"] in ("actiu", "publicat")]
    tot = {"Projectes actius": len(actius),
           "Pàgines planificades": sum(len(p["pagines"]) for p in projectes),
           "Pàgines publicades": sum(p["per_estat"].get("publicada", 0) for p in projectes),
           "Pendents teus": sum(len(p["pendents"]) for p in actius),
           "[VERIFICAR] oberts": sum(p["marques"] for p in actius)}
    totals = "".join(f"<div><b>{v}</b><span>{e(k)}</span></div>" for k, v in tot.items())
    estats = sorted({p["estat"] for p in projectes})
    filtres = '<button data-f="tots" aria-pressed="true">Tots</button>' + "".join(f'<button data-f="{e(s)}" aria-pressed="false">{e(s)}</button>' for s in estats)
    colors = {"idea": "#d8d3c9", "keywords": "#c2cfcb", "competencia": "#9fbcb6", "estructura": "#7aa59d", "text": "#4f8a80", "revisio": "#e2a27f", "publicada": "#1f5f5b"}
    llegenda = "".join(f'<span><i style="background:{c}"></i>{k}</span>' for k, c in colors.items())
    ordre = {"actiu": 0, "publicat": 1, "pausa": 2, "arxivat": 3}
    targetes = "".join(render(p) for p in sorted(projectes, key=lambda p: (ordre.get(p["estat"], 9), p["nom"])))
    ara = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html><html lang="ca"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Projectes web · Dashboard</title><meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,650&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<section class="cap"><h1>Projectes web</h1><p>Actualitzat el {ara} · {len(projectes)} projectes</p>
<div class="totals">{totals}</div><div class="filtres">{filtres}</div><div class="llegenda">Estat de les pàgines: {llegenda}</div></section>
<main class="graella">{targetes or '<p>No he trobat cap projecte.yaml.</p>'}</main><script>{JS}</script></body></html>"""


def render(p):
    barres = "".join(f'<span class="seg seg--{e(k)}" style="flex:{n}" title="{e(k)}: {n}"></span>' for k, n in p["per_estat"].items() if n)
    fases = "".join(f'<li class="f f--{e(f["estat"])}" title="{e(f["nom"])}: {e(f["estat"])}"><span>{e(f["nom"])}</span></li>' for f in p["fases"])
    gsc = p["metriques"].get("gsc") or {}
    gsc_html = ""
    if gsc:
        gsc_html = (f'<div class="gsc"><div><b>{e(gsc.get("clics", 0))}</b><span>clics</span></div><div><b>{e(gsc.get("impressions", 0))}</b>'
                    f'<span>impressions</span></div><div><b>{e(gsc.get("posicio", "–"))}</b><span>posició mitjana</span></div>'
                    f'<p>Search Console · {e(gsc.get("periode", ""))}</p></div>')
    pendents = "".join(f"<li>{e(x)}</li>" for x in p["pendents"][:5])
    bloquejos = "".join(f"<li>{e(x)}</li>" for x in p["bloquejos"][:3])
    enllacos = " · ".join(f'<a href="{e(v)}">{e(k)}</a>' for k, v in p["enllacos"].items())
    domini = f' · <a href="https://{e(p["domini"])}">{e(p["domini"])}</a>' if p["domini"] and "[" not in p["domini"] else ""
    volum = f'{p["volum"]:,}'.replace(",", ".")
    return f"""
<article class="proj" data-estat="{e(p["estat"])}">
  <header><div><h2>{e(p["nom"])}</h2><p class="meta">{e(p["tipus"])} · {e(p["mode"])} · {" / ".join(map(e, p["idiomes"]))}{domini}</p></div>
  <span class="xip xip--{e(p["estat"])}">{e(p["estat"])}</span></header>
  {f'<p class="desc">{e(p["descripcio"])}</p>' if p["descripcio"] else ""}
  <ol class="fases">{fases}</ol>
  <div class="nums"><div><b>{len(p["pagines"])}</b><span>pàgines planificades</span></div>
  <div><b>{p["per_estat"].get("publicada", 0)}</b><span>publicades</span></div>
  <div><b>{volum}</b><span>cerques/mes objectiu</span></div>
  <div class="{"alerta" if p["marques"] else ""}"><b>{p["marques"]}</b><span>[VERIFICAR] pendents</span></div></div>
  {f'<div class="barra">{barres}</div>' if barres else ""}
  {gsc_html}
  {f'<div class="bloc bloc--bloq"><h3>Bloquejat</h3><ul>{bloquejos}</ul></div>' if bloquejos else ""}
  {f'<div class="bloc"><h3>Pendents</h3><ul>{pendents}</ul></div>' if pendents else ""}
  <p class="seg-pas"><b>Següent:</b> {e(p["seguent"]) or "–"}</p>
  <footer>Fase actual: <b>{e(p["fase_actual"])}</b> · darrer canvi {e(p["actualitzat"])}{(" · " + enllacos) if enllacos else ""}</footer>
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
