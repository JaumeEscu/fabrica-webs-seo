# Regles de la casa

Aprenentatges de Bona Tria que s'apliquen a tots els projectes.

## Dades i veracitat
- Cap xifra sense font. Cita la font i la data al costat («Font: Selectra, juliol 2026»).
- Si una dada falta o és dubtosa: `[VERIFICAR]`, `[VERIFICAR amb <qui>]`, `[DATA]` o `[PENDENT]`. Mai no l'omplis amb una estimació sense dir-ho.
- Les FAQ, les taules i el schema han de dir exactament el mateix (una xifra, un lloc).
- Valoracions i estrelles: no les marquis al schema si no són pròpies (Google no ho permet si vénen d'una altra plataforma).

## Treball amb el propietari
- El propietari valida cada pas. Presenta la sortida curta i clara i demana «ok» o canvis.
- El propietari exporta les dades que només ell pot treure (Keyword Planner, Search Console, captures de Google des de la seva ubicació). Dona-li instruccions pas a pas (veure `f2-keywords`).
- Si el model de negoci canvia, torna a la fase 1 i revisa què queda afectat. Anota la decisió amb data a `brief/decisions.md`.

## SEO
- Una paraula clau principal = una URL. Si dues pàgines volen la mateixa, se'n fusiona una o es canvia l'enfocament (canibalització).
- L'H1 porta la paraula clau principal; cada H2/H3 fa servir una variant real del cluster. Cap encapçalament sense cerca al darrere (excepte els de conversió).
- Cada secció important comença amb una resposta directa de 1–2 frases (bona per a fragments destacats i per a les IA).
- Cada pàgina indexable: title 30–60 caràcters, description 70–160, 1 H1, canonical, hreflang si hi ha idiomes, schema, i almenys 300 paraules útils.
- Enllaços interns: cada pàgina rep enllaços del seu hub i enllaça cap a 2–4 pàgines germanes amb text descriptiu (mai «clica aquí»).
- Pàgines programàtiques (ciutat, servei×ciutat): només s'indexen si tenen dades pròpies suficients (mínim de fitxes a `lloc.yaml`).
- E-E-A-T: autor real, revisor quan hi ha dades tècniques, data d'actualització, pàgina «com treballem / com verifiquem».

## SEO per a IA
Detall a `seo-ia.md`. Resum:
- Cap rastrejador de cerca ni d'assistent bloquejat (robots.txt ni servidor). Els d'entrenament, decisió del propietari (`bots_ia` a `lloc.yaml`).
- Entitat clara: Organization/LocalBusiness/Person amb `sameAs` a tots els perfils oficials.
- H1 descriptiu del que oferim, mai només el nom de la marca. Encapçalaments amb paraules, no xifres soles.
- Contingut propi i concret («reparem calderes a Badalona en menys de 24 h») en lloc de genèric («empresa líder amb anys d'experiència»).
- Cada pàgina respon la intenció principal i les subconsultes que se'n deriven (query fan-out).
- Prioritza per impacte en el negoci, no per gravetat tècnica: un bot bloquejat és més greu que una Twitter Card que falta.

## Idiomes
- Si el públic cerca en dos idiomes, fes les dues versions. Escriu primer en l'idioma amb més volum i adapta (no tradueixis literalment) a l'altre.
- Slugs en l'idioma de cada versió. La mateixa `clau` a les dues versions per enllaçar-les (hreflang).

## Disseny
- Primer el sistema de disseny (fase 2b), després les pàgines. Cada pàgina combina components existents; si en cal un de nou, s'afegeix al sistema.
- Mòbil primer. Contrast AA. La web ha de funcionar sense JavaScript.
- Una crida a l'acció principal per pàgina, repetida al final.
