---
name: f3-pagina
description: Fase 3 de la Fàbrica de webs SEO (passos 5–11 del playbook). Crea una pàgina de principi a fi: anàlisi del top de Google, jerarquia d'encapçalaments, maquetació amb components, text SEO, versió en l'altre idioma, FAQ, schema, E-E-A-T, enllaçat intern i optimització per a cercadors amb IA. Fes-la servir per a cada pàgina del mapa paraula→URL, per ordre de prioritat.
---

# Fase 3 — Una pàgina, de l'anàlisi al text final

Treball a `pagines/<clau>/`. Resultat publicable a `contingut/<idioma>/<clau>.md` (format a `../fabrica-seo/referencies/format-contingut.md`).
Cada pas es valida amb el propietari. Per a pàgines secundàries (ciutats, variants), es poden condensar 5–7 en un sol document i 8–10 en un altre.
Actualitza `pagines[].estat` a `projecte.yaml` a cada pas: competencia → estructura → text → revisio.

## Pas 5 — Anàlisi del top de Google (`05_competencia.md`)
- Demana al propietari una **captura de Google** de la paraula principal des de la seva ubicació (la cerca des d'aquí no és la de l'usuari). Mentrestant, fes la cerca i avisa que l'ordre pot canviar.
- Llegeix els 5 primers resultats orgànics. Per a cadascun: tipus de web, H2 principals, longitud, què fan bé, què els falta.
- Anota els **elements de la SERP**: fragment destacat, «Altres preguntes», mapa, vídeos, IA Overview. Defineixen el format (taula, llista, pas a pas, vídeo).
- Conclusió: **l'oportunitat** — què podem fer millor o diferent (dades pròpies, resposta directa, eina, qui contractar).

## Pas 6 — Jerarquia d'encapçalaments (`06_encapcalaments.md`)
- H1 amb la paraula clau exacta (o gairebé). Cada H2/H3 amb una variant real del cluster (de `keywords/keywords.csv`), sense repetir la principal.
- Ordre = el recorregut de l'usuari: primer la pregunta que porta a Google, després les objeccions, després a qui contractar / com fer el pas.
- Cap encapçalament genèric sense cerca («Introducció», «Conclusió»), excepte els de conversió. Cap encapçalament que sigui només una xifra («+25», «90 %»).
- **Subconsultes (query fan-out)**: llista les 5–10 preguntes en què una IA desplegaria la consulta principal (per a qui, quant costa, comparativa, a [ciutat], alternatives) i comprova que cadascuna té una secció o una FAQ que la respon.
- Llista d'encapçalaments descartats i per què.
- Si hi ha dos idiomes: encapçalaments en l'idioma amb més volum i, a sota, la versió de l'altre.

## Pas 7 — Maquetació (`07_disseny.md`)
Taula bloc a bloc: bloc, què conté, **component del sistema de disseny** (fase 2b), per què aquí. No dissenyis de nou: reutilitza. Si cal un component nou, afegeix-lo al sistema. Hi ha d'haver:
- un `resum` amb la resposta directa al principi;
- una taula o llista que Google pugui extreure, si la consulta ho demana;
- l'acció principal al primer pantallàs i al final;
- un bloc de confiança (dades pròpies, com verifiquem, autor/revisor).

## Pas 8 — Text SEO (`08_text_<idioma>.md`)
- Text complet bloc a bloc, en l'idioma amb més volum.
- **Primera frase de cada secció = resposta directa** (40–60 paraules autònomes que una IA pugui citar sense context).
- Xifres amb font i data al costat. Si falta: `[VERIFICAR]`. Cap dada inventada.
- **Informació pròpia** (information gain): almenys un element que no tinguin els competidors (dada, taula, experiència, eina). El que només pot aportar el propietari: experiència real (casos, fotos, errors que veu cada dia), dades pròpies (preus, terminis, nombre de clients), opinió («jo no faria X, i t'explico per què») i una persona amb nom i cara.
- **Title**: fórmula «Què fas + On + Per què tu» dins 30–60 caràcters (p. ex. «Reparació de calderes a Badalona en 24 h | Marca»). La description, com un anunci: benefici concret i acció.
- Enllaços interns segons el pla de la fase 1: 2–4 cap a germanes, 1 cap al hub, text descriptiu.
- Checklist final de paraules del cluster incloses (✓) i no incloses (per què).

## Pas 9 — Text final i altres idiomes (`09_copy_<idioma>.md`)
- Repassa to i claredat: frases curtes, sense farciment, com parlaria el públic.
- Adapta (no tradueixis) a l'altre idioma: paraules que diria una persona d'aquí, slugs propis, mateixes xifres.

## Pas 10 — FAQ
8–10 preguntes reals (de «Altres preguntes», autocompletat i preguntes a les IA del pas 2). Respostes de 40–100 paraules, autònomes, en to de conversa, amb la zona si és local, i amb les mateixes xifres que la pàgina. Van a la capçalera `faq:` del Markdown (el generador les mostra i en fa el schema).

## Pas 11 — Schema
El generador ja crea Organization, WebSite, WebPage, BreadcrumbList, Article (guies amb autor), FAQPage, ItemList/LocalBusiness (directori). Revisa només si cal un tipus extra (Service, Product, HowTo, Event, Person per a una marca personal…) i posa'l a `schema:` de la capçalera. No marquis valoracions que no siguin pròpies.

## Muntar la pàgina
1. Escriu `contingut/<idioma>/<clau>.md` per a cada idioma: capçalera (titol 30–60, descripcio 70–160, clau, slug, tipus, pare, autor, revisor, actualitzat, relacionades, faq) + cos amb components.
2. Construeix i comprova:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/construir.py" <carpeta-projecte>
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/comprovar.py" <carpeta-projecte>
   ```
3. Revisa l'informe per prioritat (taula «Què arreglar primer»): 🔴 abans de seguir; 🟠 abans de publicar; 🟡 quan es pugui.
4. Fes una captura (mòbil i escriptori) de la pàgina i ensenya-la al propietari. Comprova també la primera pantalla: H1 que diu què fas, acció principal visible i contacte sense passos intermedis (WhatsApp o telèfon directes, sense pàgines d'espera).
5. `estat: revisio` a `projecte.yaml`; quan el propietari dona l'ok i no queden `[VERIFICAR]` a la pàgina, està llesta per publicar.
