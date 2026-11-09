---
name: f2-keywords
description: Fase 2 de la Fàbrica de webs SEO (pas 4 del playbook ampliat). Instruccions per exportar el Keyword Planner, altres fonts de paraules clau, agrupació automàtica dels CSV per pàgina, detecció de canibalitzacions i mapa definitiu paraula clau → URL. Fes-la servir quan l'arquitectura està validada o quan arriben CSV nous.
---

# Fase 2 — Paraules clau i mapa paraula→URL

Sortida: `keywords/04_keyword_research.md` validat, `keywords/mapa.yaml`, `keywords/keywords.csv`, i `pagines:` de `projecte.yaml` amb volum i prioritat.

## 1. Instruccions per al propietari (`keywords/INSTRUCCIONS.md`)
Escriu-les adaptades al projecte, amb una taula de llavors (una per fila, amb el nom del CSV):
1. ads.google.com → si demana campanya, «Canviar al mode expert» → «Crear un compte sense campanya» (no cal targeta).
2. Eines → Planificació → Planificador de paraules clau → «Descobrir noves paraules clau» → «Començar amb paraules clau».
3. Configuració: ubicació = la zona del brief (ex.: Catalunya); idioma = tots; xarxa = Google; dates = últims 12 mesos.
4. **Una llavor cada vegada** → «Obtenir resultats» → baixada → «Idees de paraules clau (.csv)» → canviar el nom com a la taula.
5. Pujar els CSV a `keywords/csv/`. Amb 5–6 ja es pot començar.
Nota: sense campanya activa, Google dona volums en franges (50 = 10–100, 500 = 100–1.000, 5.000 = 1.000–10.000…). Serveixen per comparar; les sumes inflen el volum real.

## 2. Altres fonts (millora sobre el PDF)
El Keyword Planner es queda curt en català i en cerques de cua llarga. Complementa amb:
- **Autocompletat de Google** i **«Altres preguntes dels usuaris»** (People Also Ask): cerca les llavors i anota-ho, o demana captures al propietari.
- **Search Console** (si la web existeix): consultes amb impressions i posició 5–30 = oportunitats ràpides.
- **Competència**: quines pàgines tenen els 3 primers resultats que nosaltres no (gap de contingut).
- **Preguntes a les IA** del pas 2: són les consultes llargues que les FAQ han de respondre.
Marca aquestes paraules com a «sense volum» però no les descartis: alimenten H2, H3 i FAQ.

## 3. Agrupació automàtica
1. Escriu `keywords/mapa.yaml` a partir de l'arquitectura (format a la capçalera de l'script): una entrada per pàgina amb patrons `inclou`/`exclou`, i `excloure` global per a soroll (marques, productes que no toquen, altres països, «gratis», «pdf», «curso»…).
2. Executa:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/keywords.py" <carpeta-projecte>
   ```
3. Llegeix `keywords/per_pagina.md` i itera el `mapa.yaml` fins que:
   - les paraules **sense pàgina** amb volum són soroll o idees de pàgina noves (proposa-les);
   - les **canibalitzacions** estan resoltes (cada paraula a una sola pàgina; si n'hi ha moltes entre dues pàgines, potser és una sola pàgina).

## 4. Anàlisi (`keywords/04_keyword_research.md`)
- **Què diuen les dades** (5–6 punts): idioma dominant, volum per tipus de pàgina, CPC (indica intenció de compra), estacionalitat i quan publicar, cerques que no podem guanyar (botigues, marques).
- **Neteja aplicada**: què s'ha exclòs i per què.
- **Taula de pàgines** ordenada per volum: pàgina, URL per idioma, paraula principal, volum del cluster, nombre de variants.
- **Canvis respecte de l'arquitectura** del pas 3 (pàgines noves, fusionades, eliminades).
- **Tipus de resultat a Google** per a les 5 pàgines principals (millora): què surt (mapa local, vídeos, fragments, botigues, IA Overview) i què implica per al format.
- **Ordre de producció**: primer la pàgina amb més volum *on podem guanyar* (feina d'especialista, poca competència de grans marques, diferenciació clara).

## 5. Tancar la fase
Actualitza `projecte.yaml` → `pagines:` amb `keyword` definitiva, `volum`, `prioritat` (1 = primera) i `estat: keywords`. `seguent`: fase 2b si encara no hi ha sistema de disseny, si no, fase 3 amb la pàgina de prioritat 1.
