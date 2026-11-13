# SEO per a cercadors amb IA (Google AI Overviews, Mode IA, ChatGPT, Claude, Perplexity)

Idea principal: **el 80 % del SEO per a IA és el SEO de sempre**. Una web rastrejable, ràpida, clara i amb
contingut propi serveix tant per a Google com per a les IA. El que canvia és l'objectiu: ja no n'hi ha
prou amb sortir a la primera pàgina; cal **ser citat i recomanat** a les respostes.

## Com busquen les IA
- **Corpus**: el que el model va aprendre en l'entrenament (sobretot de Common Crawl).
- **RAG / cerca en viu**: quan necessita dades actuals, busca a la web, llegeix resultats i redacta.
- **Query fan-out**: una pregunta es desplega en moltes subconsultes («millor X», «X per a Y», «X vs Z»,
  «preu de X a [ciutat]»). Per això una pàgina que respon bé una subconsulta concreta pot ser citada encara
  que no sigui al top 10 per a la paraula genèrica (aprox. el 62 % de les cites dels AI Overviews vénen de
  fora del top 10, març 2026).
- Les consultes són més llargues i conversacionals, i hi ha menys clics directes: amb AI Overview el primer
  resultat perd una part gran del CTR. El valor és la cita (marca, confiança), no només el clic.

## Els quatre passos (i on els cobreix la fàbrica)
| Pas | Què vol dir | On |
|---|---|---|
| 1. Que et trobin | rastrejable, indexada, sitemap, robots.txt que no bloqueja bots de cerca, servidor que no els respon 403 | `construir.py` (robots, sitemap), `comprovar.py`, `auditar_viu.py` |
| 2. Que t'entenguin | arquitectura clara (una URL per servei/categoria), H1 descriptiu, jerarquia d'encapçalaments, schema, entitat amb `sameAs` | fases 1 i 3, `comprovar.py` |
| 3. Que et valorin | resposta directa al principi, dades pròpies, experiència real, autor amb nom i cara, FAQ, mencions fora de la web | fase 3, fase 4 §4 |
| 4. Que puguin interactuar | agents que fan accions (consultar disponibilitat, reservar). Tecnologia emergent (WebMCP) | opcional, veure al final |

## Rastrejadors
Llista completa i política a `scripts/bots_ia.py`. Tres tipus:
- **Cerca** (Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot…): mai no s'han de bloquejar.
- **Usuari** (ChatGPT-User, Claude-User, Perplexity-User): entren quan algú enganxa una URL a l'assistent. Tampoc.
- **Entrenament** (GPTBot, ClaudeBot, Google-Extended, CCBot…): decisió del propietari. Bloquejar-los no treu
  de la cerca, però sense CCBot la marca no entra al corpus que fan servir molts models.

`lloc.yaml`:
```yaml
bots_ia: permetre           # permetre | sense-entrenament (CCBot permès) | nomes-cerca
robots_bloquejar: [/privat/] # opcional: carpetes que no ha de rastrejar ningú
```
Compte: el robots.txt és una petició. Cloudflare («Block AI bots», AI Crawl Control), un WAF o un plugin de
seguretat poden respondre 403 als bots encara que el robots.txt els deixi. `auditar_viu.py` ho detecta.

## Què ajuda a sortir citat
1. **Entitat clara**: qui ets, què fas, on. Organization/LocalBusiness/Person amb `sameAs` als perfils oficials.
2. **Fonts de tercers**: mencions de marca en altres webs (correlació molt més alta que els enllaços:
   0,66 vs 0,22 segons Ahrefs), ressenyes, directoris del sector, premsa, blogs especialitzats.
3. **Resposta directa** (piràmide invertida): la resposta a les primeres línies de cada secció. Les IA extreuen
   fragments.
4. **Contingut propi** (non-commodity): preus reals, casos, dades pròpies, opinió argumentada («jo no faria X
   perquè…»), fotos de feina real.
5. **Dades estructurades** coherents amb el que es veu.
6. **Google Business Profile** si és negoci local: l'ús de la IA per trobar negocis locals ha crescut molt.

## Prioritzar
Una eina detecta desenes d'errors en segons; el criteri és decidir quins arreglar primer. Ordre habitual:
1. Bloquejos d'accés (robots, 403, noindex, canonical), pàgines que falten per a serveis o categories clau.
2. Primera pantalla clara (H1 que diu què fas, acció visible), contacte sense fricció, velocitat (imatges i vídeos).
3. Schema, autor, contingut prim o genèric, canibalització.
4. Open Graph, Twitter Cards, llargades de title/description, llms.txt.

Errors típics vistos en auditories reals: catàleg sense categories, H1 = nom de la marca, encapçalaments que
són xifres, imatge de portada de 2 MB, vídeo de YouTube a la portada (9 s de càrrega), dues pàgines amb el 76 %
del text igual, articles sense autor, bots d'IA bloquejats amb 403, botó de contacte que passa per una pàgina
d'espera i substitueix la pestanya.

## Comprovacions manuals de visibilitat
- `site:domini.com` a Google: quantes pàgines té indexades.
- Search Console: Indexació → Pàgines; Sitemaps.
- Common Crawl: https://index.commoncrawl.org/ → darrer índex → domini (ho fa `auditar_viu.py`).
- Prova de recomanació a ChatGPT, Gemini i Mode IA de Google (des de la ubicació del client):
  > Estoy en [ciudad] y busco [servicio]. ¿Qué opciones me recomiendas y por qué? Indica de dónde sacas la información.

  Apunta si surt la marca, en quina posició i quines fonts cita. Repeteix-ho cada mes (fase 5).

## Interacció amb agents (WebMCP) — opcional
Permet que un agent faci accions a la web (consultar disponibilitat, cercar productes) sense navegar com una
persona. És emergent i depèn del navegador. No és prioritari; té sentit per a reserves, botigues o
disponibilitat. Si el propietari ho vol, documenta-ho a `brief/decisions.md` abans d'implementar-ho.
