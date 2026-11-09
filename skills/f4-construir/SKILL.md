---
name: f4-construir
description: Fase 4 de la Fàbrica de webs SEO (pas 12 del playbook ampliat). Genera la web estàtica completa, passa la comprovació SEO tècnica, prepara el llançament (domini, allotjament, redireccions, Search Console, Bing, Google Business) i el pla de SEO fora de la web. Fes-la servir per previsualitzar, publicar o republicar una web de la fàbrica.
---

# Fase 4 — Construir i publicar

## 1. Construir
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/construir.py" <carpeta-projecte>            # previsualització
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/construir.py" <carpeta-projecte> --estricte # per publicar: falla si queden [VERIFICAR]
```
Genera `web/` amb HTML per pàgina, `assets/`, `sitemap.xml` (amb hreflang), `robots.txt`, `llms.txt`, `404.html` i `_pagines.json`.
Previsualització local: `cd web && python3 -m http.server 8000` → http://localhost:8000

## 2. Comprovar
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/comprovar.py" <carpeta-projecte>
```
Informe a `informes/comprovacio.md`. Errors que bloquegen: sense title, H1 ≠ 1, sense canonical, hreflang no recíproc, enllaços trencats, JSON-LD invàlid, FAQ del schema que no es veuen, noindex al sitemap, titles duplicats. Els avisos (longituds, contingut prim) es revisen un a un.
Revisa també: [Rich Results Test](https://search.google.com/test/rich-results) per a 2–3 pàgines i PageSpeed Insights (objectiu: LCP < 2,5 s, CLS < 0,1, INP < 200 ms).

## 3. Llista de llançament (`informes/llancament.md`)
- [ ] `--estricte` passa (0 marques pendents) i `comprovar.py` sense errors.
- [ ] Avís legal, privacitat i galetes amb les dades reals (i revisats si el sector ho demana).
- [ ] Imatges OG i logo; favicon.
- [ ] Allotjament estàtic (Cloudflare Pages, Netlify, GitHub Pages o el servidor propi) amb HTTPS i redirecció www/sense www a una sola versió.
- [ ] Si la web ja existia: **redireccions 301** de totes les URL antigues amb valor (de l'auditoria de la fase 0). Fitxer `_redirects` o configuració del servidor. Comprova-les després de publicar.
- [ ] Formularis connectats (endpoint, correu o n8n) i provats.
- [ ] Analítica respectuosa (Plausible, Umami o GA4 amb consentiment) i esdeveniments de conversió.
- [ ] Search Console: verificar el domini, enviar `sitemap.xml`, inspeccionar la portada i 2–3 pàgines clau.
- [ ] Bing Webmaster Tools (importar des de Search Console). Bing alimenta ChatGPT i Copilot.
- [ ] Google Business Profile si és un negoci local o té seu.

## 4. SEO fora de la web (millora sobre el PDF)
Pla dels primers 90 dies a `informes/fora-de-la-web.md`:
- Perfils coherents (mateix nom, descripció i URL): Google Business, LinkedIn, xarxes, directoris del sector.
- 3–5 enllaços de qualitat: associacions i gremis, premsa local, proveïdors, col·laboracions.
- Una **peça enllaçable**: dades pròpies (estudi, rànquing, mapa), eina o guia de referència que altres vulguin citar.
- Marca personal: articles com a convidat, podcasts, xerrades; enllaç a la web a cada bio.

## 5. Tancar
`fases.f4_construir.estat: fet`, `estat: publicat` i `enllacos.web` a `projecte.yaml`; les pàgines publicades a `estat: publicada`. `seguent`: primera revisió de la fase 5 d'aquí a 4 setmanes.
