---
name: fabrica-seo
description: Punt d'entrada de la Fàbrica de webs SEO. Fes-la servir quan algú vulgui crear o millorar una web pensada per a SEO i continguts (marca personal, negoci, directori, idea nova), continuar un projecte web existent de la fàbrica, o saber en quina fase és un projecte. Decideix la fase i carrega la skill que toca.
---

# Fàbrica de webs SEO

Sistema per crear webs que guanyin trànsit orgànic amb contingut útil, des de zero o a partir d'una web que ja existeix. Es basa en el playbook de 12 passos (Dani Llamazares) i en el que vam aprendre fent Bona Tria, amb les millores que el PDF no cobria (mapa paraula→URL, enllaçat intern, E-E-A-T, cercadors amb IA, sistema de disseny, SEO fora de la web i mesura).

## Com començar

1. **Busca `projecte.yaml`** a la carpeta de treball o a les subcarpetes.
   - Si existeix: llegeix-lo, digues en quina fase és el projecte i què hi ha pendent, i continua amb la skill de la fase `en-curs`.
   - Si no existeix: és un projecte nou. Pregunta només el que calgui per crear-lo (nom, web actual o idea, idiomes, domini si en té) i executa:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/nou_projecte.py" <carpeta> --nom "..." --tipus <directori|marca-personal|negoci-local|ecommerce|altres> --mode <existent|nou> --domini ... --idiomes ca,es
     ```
     (Si `CLAUDE_PLUGIN_ROOT` no està definit, els scripts són a `../../scripts/` des d'aquesta skill.)
2. Comprova que hi ha les llibreries: `pip install -r "${CLAUDE_PLUGIN_ROOT}/requirements.txt"` (jinja2, markdown, pyyaml).
3. Segueix la fase. **Una fase no comença fins que el propietari ha validat la sortida de l'anterior.**

## Fases

| Fase | Skill | Passos del PDF | Sortida principal |
|---|---|---|---|
| 0 Brief | `f0-brief` | — | `brief/00_brief.md` (+ inventari i auditoria si la web existeix) |
| 1 Estratègia | `f1-estrategia` | 1, 2, 3 | context, personas, arquitectura |
| 2 Paraules clau | `f2-keywords` | 4 | `keywords/mapa.yaml`, `04_keyword_research.md`, mapa paraula→URL |
| 2b Sistema de disseny | `f2b-disseny` | (nou) | tokens a `lloc.yaml`, `disseny/sistema.md` |
| 3 Pàgines | `f3-pagina` | 5–11 | `pagines/<clau>/` i `contingut/<idioma>/<clau>.md` |
| 4 Construir i publicar | `f4-construir` | 12 | `web/`, informe de comprovació, llista de llançament |
| 5 Mesurar i refrescar | `f5-mesurar` | (nou) | informe mensual, pàgines a refrescar |
| Directori (si cal) | `directori` | (nou) | `directori/fitxes.yaml`, pàgines programàtiques |
| Dashboard | `dashboard` | — | vista de tots els projectes |

## Regles de la casa (sempre)

Llegeix `referencies/regles.md` abans de la primera fase de cada sessió. Les més importants:
- **No inventis cap dada.** Si no hi ha font, posa `[VERIFICAR]` (o `[DATA]`, `[PENDENT]`). El generador les marca en groc i el mode estricte no deixa publicar.
- **Actualitza `projecte.yaml`** en acabar cada pas: estat de la fase, estat de cada pàgina, `pendents`, `seguent`. El dashboard en depèn.
- **Un pas, una validació.** Presenta la sortida, demana «ok» o correccions, i només llavors continues.
- **Escriu per a persones**: frases clares, sense farciment, en l'idioma del projecte. Res de «en el món actual…».
- Formats de fitxer: `referencies/format-contingut.md` explica com s'escriu una pàgina perquè la construeixi el generador.
