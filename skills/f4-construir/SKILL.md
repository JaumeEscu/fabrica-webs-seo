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
Genera `web/` amb HTML per pàgina, `assets/`, `sitemap.xml` (amb hreflang), `robots.txt` (amb els rastrejadors de cerca, d'assistents i d'entrenament explícits segons `bots_ia` de `lloc.yaml`; veure `../fabrica-seo/referencies/seo-ia.md`), `llms.txt`, `404.html` i `_pagines.json`.
Previsualització local: `cd web && python3 -m http.server 8000` → http://localhost:8000

## 2. Comprovar
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/comprovar.py" <carpeta-projecte>
```
Informe a `informes/comprovacio.md`, amb una taula **«Què arreglar primer»** ordenada per prioritat d'impacte:
- 🔴 **Crític** (la majoria bloquegen la publicació): robots.txt que bloqueja cercadors o assistents d'IA, sense sitemap, noindex al sitemap, sense title, H1 ≠ 1, sense canonical, hreflang no recíproc, enllaços trencats, JSON-LD invàlid, FAQ del schema que no es veuen, titles duplicats, sense viewport, dues pàgines amb ≥ 70 % del text igual.
- 🟠 **Important**: sense description, contingut prim, sense schema o entitat sense `sameAs`, H1 que és només la marca, salts d'encapçalament, sobreoptimització de la paraula clau, canibalització 50–70 %, articles sense autor, imatges > 1 MB o > 2 MB per pàgina, iframes (YouTube, mapes) sense `loading=lazy`, imatges sense alt.
- 🟡 **Menor**: llargades de title/description, imatges > 300 KB o en JPG/PNG grans, imatges sense width/height (CLS), encapçalaments buits o repetits, camps buits al schema, Open Graph i Twitter Cards, llms.txt.

La prioritat orienta; no substitueix el criteri. Comenta-la amb el propietari pensant en el negoci.
Revisa també: [Rich Results Test](https://search.google.com/test/rich-results) per a 2–3 pàgines i PageSpeed Insights (objectiu: LCP < 2,5 s, CLS < 0,1, INP < 200 ms).

## 3. Llista de llançament (`informes/llancament.md`)
- [ ] `--estricte` passa (0 marques pendents) i `comprovar.py` sense errors.
- [ ] Avís legal, privacitat i galetes amb les dades reals (i revisats si el sector ho demana).
- [ ] Imatge OG (`og_imatge` a `lloc.yaml`, 1200×630, < 300 KB), logo i favicon. Prova la vista prèvia compartint un enllaç per WhatsApp o LinkedIn.
- [ ] Política de rastrejadors d'IA decidida amb el propietari (`bots_ia`). Si hi ha Cloudflare o un WAF, comprova que no bloqueja els bots de cerca.
- [ ] Allotjament estàtic (Cloudflare Pages, Netlify, GitHub Pages o el servidor propi) amb HTTPS i redirecció www/sense www a una sola versió.
- [ ] Si la web ja existia: **redireccions 301** de totes les URL antigues amb valor (de l'auditoria de la fase 0). Fitxer `_redirects` o configuració del servidor. Comprova-les després de publicar.
- [ ] Formularis connectats (endpoint, correu o n8n) i provats.
- [ ] Analítica respectuosa (Plausible, Umami o GA4 amb consentiment) i esdeveniments de conversió.
- [ ] Search Console: verificar el domini, enviar `sitemap.xml`, inspeccionar la portada i 2–3 pàgines clau.
- [ ] Bing Webmaster Tools (importar des de Search Console). Bing alimenta ChatGPT i Copilot.
- [ ] Google Business Profile si és un negoci local o té seu.
- [ ] **Auditoria en viu** després de publicar:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/auditar_viu.py" https://www.domini.com <carpeta-projecte>
  ```
  robots.txt real, resposta del servidor a cada bot (detecta 403 de Cloudflare/WAF), sitemap (200, sense redirecció ni noindex), www/https a una sola versió amb 301, pes de la portada i presència a Common Crawl. Informe a `informes/auditoria_viva.md`.
- [ ] `site:domini.com` a Google al cap d'uns dies per confirmar la indexació.

## 4. SEO fora de la web (millora sobre el PDF)
Pla dels primers 90 dies a `informes/fora-de-la-web.md`:
- Perfils coherents (mateix nom, descripció i URL): Google Business, LinkedIn, xarxes, directoris del sector. Afegeix-los tots a `sameAs` de l'entitat.
- **Mencions de marca** en altres webs (pesen més que els enllaços per sortir citat a les IA): ressenyes, directoris, notes de premsa, entrevistes, clients que expliquen el projecte.
- 3–5 enllaços de qualitat: associacions i gremis, premsa local, proveïdors, col·laboracions.
- Una **peça enllaçable**: dades pròpies (estudi, rànquing, mapa), eina o guia de referència que altres vulguin citar.
- Marca personal: articles com a convidat, podcasts, xerrades; enllaç a la web a cada bio.

## 5. Tancar
`fases.f4_construir.estat: fet`, `estat: publicat` i `enllacos.web` a `projecte.yaml`; les pàgines publicades a `estat: publicada`. `seguent`: primera revisió de la fase 5 d'aquí a 4 setmanes.
