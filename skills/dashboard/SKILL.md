---
name: dashboard
description: Dashboard de tots els projectes de la Fàbrica de webs SEO. Genera una pàgina amb l'estat de cada projecte (fase, pàgines per estat, volum objectiu, marques [VERIFICAR] pendents, pendents del propietari, mètriques de Search Console). Fes-la servir quan el propietari vulgui veure com van els projectes o després d'actualitzar-ne un.
---

# Dashboard de projectes

1. Troba la carpeta arrel on viuen els projectes (per defecte `~/Projectes` al Mac del propietari, o la carpeta de treball). Cada projecte és una carpeta amb `projecte.yaml`.
2. Abans de generar, comprova que cada `projecte.yaml` està al dia (fase, `pagines[].estat`, `pendents`, `seguent`). Si has treballat en un projecte en aquesta sessió, actualitza'l primer.
3. Genera:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py" ~/Projectes --sortida ~/Projectes/dashboard.html
   ```
   Escriu `dashboard.html` (pàgina autònoma) i `dashboard.json`.
4. Ensenya-la: si hi ha eina d'artifacts, publica el contingut de `dashboard.html` com a artifact privat (actualitza el mateix artifact les vegades següents, no en creïs un de nou); si no, digues on és el fitxer.
5. Resumeix en 3–5 línies: què ha avançat, què està bloquejat i què toca al propietari.

Per tenir-lo al dia sol, es pot programar una tasca setmanal que executi aquests passos.
