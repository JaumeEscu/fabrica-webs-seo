# Fàbrica de webs SEO

Plugin de Claude Code (i Cowork) per crear webs optimitzades per a SEO i continguts, de manera repetible:
- a partir d'una **web existent** (rastreig, inventari, auditoria i millora), o
- a partir d'una **idea** (brief, estratègia, paraules clau, pàgines i web).

Es basa en el playbook de 12 passos de SEO amb IA i en el que vam aprendre fent Bona Tria, amb millores: mapa paraula→URL i canibalitzacions, pla d'enllaçat intern, E-E-A-T i dades pròpies, cercadors amb IA (respostes directes, `llms.txt`), sistema de disseny abans de les pàgines, SEO fora de la web i mesura mensual.

## Instal·lació

A Claude Code:
```
/plugin marketplace add JaumeEscu/fabrica-webs-seo
/plugin install fabrica-webs-seo@fabrica-webs-seo
```
Python 3.10+ i les llibreries: `pip install -r requirements.txt`

## Com s'usa

Digues a Claude què vols fer, per exemple:
- «Vull treballar la meva marca personal, la web és jaumeesteban.com»
- «Tinc una idea: un directori de detectius privats a Catalunya»
- «Com van els projectes?» (dashboard)

La skill `fabrica-seo` crea el projecte (o el retroba pel seu `projecte.yaml`) i et porta fase per fase. Cada fase acaba amb la teva validació.

| Fase | Skill | Què fa |
|---|---|---|
| 0 | `f0-brief` | Brief; si la web existeix, rastreig, inventari i auditoria de continguts |
| 1 | `f1-estrategia` | Context, buyer personas, pàgines, arquitectura i pla d'enllaçat intern (passos 1–3) |
| 2 | `f2-keywords` | Keyword Planner i altres fonts, agrupació per pàgina, canibalitzacions (pas 4) |
| 2b | `f2b-disseny` | Sistema de disseny: tokens, components, conversió i accessibilitat |
| 3 | `f3-pagina` | Una pàgina de principi a fi: competència, encapçalaments, maquetació, text, idiomes, FAQ, schema (passos 5–11) |
| 4 | `f4-construir` | Web estàtica, comprovació SEO tècnica, llançament i SEO fora de la web (pas 12) |
| 5 | `f5-mesurar` | Revisió mensual amb Search Console i refresc de continguts |
| — | `directori` | Criteris, verificació d'empreses, fitxes i pàgines per zona |
| — | `dashboard` | Estat de tots els projectes en una pàgina |

## Eines (`scripts/`)

| Script | Per a què |
|---|---|
| `nou_projecte.py` | Crea un projecte a partir de `plantilla/` |
| `rastrejar.py` | Inventari d'una web existent (sitemap o enllaços) |
| `keywords.py` | Agrupa els CSV del Keyword Planner per pàgina i detecta canibalitzacions |
| `construir.py` | Genera la web: HTML, canonical, hreflang, Open Graph, JSON-LD, sitemap, robots, llms.txt |
| `comprovar.py` | Comprovació SEO de la web generada abans de publicar, amb prioritats (crític, important, menor) |
| `auditar_viu.py` | Auditoria de la web publicada: robots i 403 per a cada bot d'IA, sitemap, www/https, pes, Common Crawl |
| `bots_ia.py` | Llista de rastrejadors de cerca, d'assistents i d'entrenament (la fan servir els altres scripts) |
| `dashboard.py` | Dashboard de tots els projectes |

## Estructura d'un projecte

Veure `plantilla/ESTRUCTURA.md`. El contingut de cada pàgina és un fitxer Markdown amb capçalera YAML (`skills/fabrica-seo/referencies/format-contingut.md`); el disseny viu en un tema (`temes/base/`) i en els tokens de `lloc.yaml`. Canviar el disseny de tota la web = canviar els tokens o el tema, no les pàgines.

## Exemple

`exemples/demo/` és un projecte petit amb dos idiomes, un directori i tots els components:
```
python3 scripts/construir.py exemples/demo
python3 scripts/comprovar.py exemples/demo
cd exemples/demo/web && python3 -m http.server 8000
```

## Webs i eines d'interès

Recull d'eines per auditar i seguir una web. Les marcades amb † vénen del *Curso gratis de SEO con IA* de BIG school (novembre 2026).

### Oficials
| Eina | Per a què |
|---|---|
| [Google Search Console](https://search.google.com/search-console) | Indexació, consultes, clics i impressions; enviar el sitemap |
| [Bing Webmaster Tools](https://www.bing.com/webmasters) | El mateix per a Bing, que alimenta Copilot i part de ChatGPT |
| [Rich Results Test](https://search.google.com/test/rich-results) | Validar les dades estructurades que Google pot fer servir |
| [Schema Markup Validator](https://validator.schema.org/) | Validar qualsevol JSON-LD de Schema.org |
| [PageSpeed Insights](https://pagespeed.web.dev/) | Core Web Vitals (LCP, CLS, INP) amb dades reals |
| [Google Business Profile](https://www.google.com/business/) | Fitxa de negoci local |

### Rastreig i IA
| Eina | Per a què |
|---|---|
| [Common Crawl Index](https://index.commoncrawl.org/) † | Saber si el domini és al corpus d'entrenament de molts models (també ho fa `auditar_viu.py`) |
| [Robots.txt Tester](https://technicalseo.com/tools/robots-txt/) † | Provar què pot rastrejar cada bot amb el robots.txt |
| [WebMCP Inspector](https://carlosortega.page/herramientas/webmcp-inspector/) † | Veure i provar les eines WebMCP que ofereix una web als agents d'IA |

### Auditoria ràpida
| Eina | Per a què |
|---|---|
| [MicroAudit](https://auditoriaseo.thebigschool.com/) † | Primera revisió tècnica: 90 punts en 10 blocs. Detecta; no prioritza per negoci |
| [Visual Schema](https://carlosortega.page/herramientas/visual-schema/) † | Visualitzar i validar les dades estructurades d'una URL o d'un codi |
| [WPO Analyzer](https://carlosortega.page/herramientas/wpo-analyzer/) † | Recursos que alenteixen la pàgina (imatges pesades, scripts) |
| [SEO Meta in 1 Click](https://chromewebstore.google.com/detail/seo-meta-in-1-click/bjogjfinolnhfhkbipphpdlldadpnmhc) † | Extensió de Chrome: title, description, encapçalaments, imatges i enllaços d'una pàgina |
| [Social Share Preview](https://chromewebstore.google.com/detail/social-share-preview/ggnikicjfklimmffbkhknndafpdlabib) † | Extensió de Chrome: com es veu l'enllaç compartit (Open Graph) |

### Proves manuals
- `site:domini.com` a Google: quantes pàgines té indexades.
- Pregunta de recomanació a ChatGPT, Gemini i al Mode IA de Google (detall a `skills/fabrica-seo/referencies/seo-ia.md`).
