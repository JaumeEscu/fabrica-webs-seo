---
name: f1-estrategia
description: Fase 1 de la Fàbrica de webs SEO (passos 1–3 del playbook). Document de context del negoci, buyer personas orientades a SEO i pluja d'idees de pàgines amb l'arquitectura web. Fes-la servir després del brief o quan cal replantejar l'estructura d'una web.
---

# Fase 1 — Estratègia (passos 1, 2 i 3)

Cada pas és un fitxer a `estrategia/` i es valida abans del següent.

## Pas 1 — Context (`estrategia/01_context.md`)
A partir del brief, omple:
- Dades del negoci (nom, web, activitat, ubicació, contacte que es mostrarà o no).
- Què fa exactament (serveis concrets, no categories).
- Diferenciació real, amb xifres si n'hi ha (ex.: «de 328 empreses revisades, només 81 passen el filtre»).
- Públic, zona, idiomes, to de veu (2–3 adjectius i exemples de frases sí/no).
- Prova d'expertesa: qui escriu i qui revisa, i per què se'ls ha de creure (E-E-A-T).
- Entitat: nom exacte de la marca, descripció d'una línia que es repetirà igual a tot arreu (web, schema, perfils), perfils `sameAs`.

## Pas 2 — Buyer personas (`estrategia/02_personas.md`)
2–4 perfils. Per a cadascun:
- Qui és (situació, no demografia de manual), què vol aconseguir, què el frena.
- **Com cerca a Google**: 8–12 cerques literals, com les escriuria (hipòtesis que es validaran al pas 4).
- **Què pregunta a una IA** (ChatGPT, Gemini): 3–5 preguntes llargues. Serveixen per a les FAQ i el contingut citable.
- Què necessita veure per confiar i fer el pas (prova, preu, garantia).
- Moment de compra i estacionalitat.

## Pas 3 — Pàgines i arquitectura (`estrategia/03_arquitectura.md`)
1. **Pluja d'idees de pàgines** en una taula: pàgina, paraula clau llavor, intenció (transaccional / comercial / informativa / navegacional), persona, per què té sentit.
   - El PDF prioritza les pàgines **transaccionals** (qui vol contractar). Comença per aquestes.
   - Afegeix-hi després les **informatives de suport** que alimenten les transaccionals (guies de preu, comparatives) i les de **confiança** (com treballem, sobre nosaltres, autor).
   - Directoris: pàgines per zona i per servei×zona, però només on hi haurà prou fitxes (veure `directori`).
2. **Arquitectura**: arbre d'URL amb hubs i pàgines filles. Regles:
   - Màxim 3 clics des de la portada a qualsevol pàgina important.
   - Cada hub enllaça totes les seves filles; cada filla enllaça el hub i 2–4 germanes.
   - URL curtes, en l'idioma de la versió, sense dates ni paraules buides.
3. **Pla d'enllaçat intern** (millora sobre el PDF): taula «des de → cap a → text de l'enllaç». Inclou-hi els enllaços del menú i del peu.
4. **Mapa preliminar paraula→URL**: una paraula clau llavor per URL. Si dues pàgines comparteixen llavor, fusiona-les o canvia l'enfocament ara.
5. Llista les **llavors per al Keyword Planner** (pas 4): una per pàgina i variants d'idioma i de ciutat.

En acabar cada pas, actualitza `projecte.yaml`. Al pas 3, omple `pagines:` amb `clau`, `slug` per idioma, `keyword` (llavor) i `estat: idea`.
