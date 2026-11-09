# Estructura d'un projecte

| Carpeta / fitxer | Què hi va | Fase |
|---|---|---|
| `projecte.yaml` | Estat del projecte (el llegeix el dashboard) | totes |
| `lloc.yaml` | Configuració de la web: domini, idiomes, autors, disseny, menú | 0, 2b, 4 |
| `brief/` | `00_brief.md`; si la web ja existeix, `inventari.csv` i `auditoria.md` | 0 |
| `estrategia/` | `01_context.md`, `02_personas.md`, `03_arquitectura.md` | 1 |
| `keywords/` | `INSTRUCCIONS.md`, `csv/` (exports del Keyword Planner), `mapa.yaml`, `keywords.csv`, `04_keyword_research.md` | 2 |
| `disseny/` | `sistema.md` (components i regles), proves visuals | 2b |
| `pagines/<clau>/` | Treball de cada pàgina: `05_competencia.md`, `06_encapcalaments.md`, `07_disseny.md`, `08_text.md` | 3 |
| `contingut/<idioma>/` | Text final de cada pàgina en Markdown amb capçalera YAML (és el que es publica) | 3 |
| `directori/` | `fitxes.yaml` i el full de verificació | directori |
| `tema/` | Plantilles pròpies si el tema base no n'hi ha prou | 2b |
| `web/` | Web generada (no s'edita a mà) | 4 |
| `informes/` | Comprovacions SEO i informes mensuals | 4, 5 |
