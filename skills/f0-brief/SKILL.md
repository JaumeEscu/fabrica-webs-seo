---
name: f0-brief
description: Fase 0 de la Fàbrica de webs SEO. Fes el brief d'un projecte web, tant si parteix d'una web existent (rastreig, inventari i auditoria de continguts) com d'una idea nova (model de negoci, públic, diferenciació). Fes-la servir en començar un projecte o quan el model de negoci canvia.
---

# Fase 0 — Brief

Objectiu: entendre què volem aconseguir i amb què comptem abans de buscar cap paraula clau.
Sortida: `brief/00_brief.md` validat pel propietari i `projecte.yaml` actualitzat.

## Entrada A — La web ja existeix (`mode: existent`)

1. **Rastreja la web:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rastrejar.py" https://www.domini.com <carpeta-projecte> --max 500
   ```
   Genera `brief/inventari.csv` i `brief/inventari_resum.md` (errors, titles, H1, paraules, canonical, schema, pàgines òrfenes, duplicats).
2. **Demana dades reals** si n'hi ha: export de Search Console (Rendiment → Pàgines i Consultes, 12 mesos) a `brief/gsc/`. Sense GSC, continua amb l'inventari.
3. **Auditoria de continguts** (`brief/auditoria.md`): per a cada URL, decideix una acció:
   | Acció | Quan |
   |---|---|
   | Mantenir | Té trànsit o enllaços i respon bé la intenció |
   | Millorar | Té impressions però posició 8–30, o text prim/antic |
   | Fusionar | Dues pàgines competeixen per la mateixa consulta |
   | Redirigir (301) | Pàgina sense valor però amb enllaços o trànsit |
   | Eliminar (410) | Sense trànsit, sense enllaços, sense valor |
   Anota-ho com a columna `accio` a l'inventari i resumeix-ho per grups.
4. **Identitat i E-E-A-T**: qui hi ha darrere (bio, experiència demostrable, perfils), proves (casos, clients, dades pròpies), i si el nom i la descripció són coherents a la web, Google Business, LinkedIn, etc.
5. Per a una **marca personal**, pregunta també: de què vol ser referent (2–3 temes com a màxim), què ven o vol aconseguir (feina, clients, conferències, audiència), i quins continguts ja té fora de la web (articles, vídeos, xerrades) que es poden aprofitar.

## Entrada B — Idea nova (`mode: nou`)

Fes les preguntes en una sola tanda i proposa respostes per defecte perquè el propietari només hagi de corregir:
1. **Què és** i per a qui (una frase).
2. **Model de negoci**: com guanyarà diners (anuncis, leads, fitxes destacades, afiliació, servei propi) i en quin ordre. Primer trànsit i després monetització és vàlid, però s'ha de dir.
3. **Zona i idiomes**: on es llança (començar petit: 1 regió, 3–5 ciutats) i en quins idiomes es cerca.
4. **Diferenciació real**: què tindrà la web que no tingui ningú (dades comprovades, eines, experiència). Sense això, no hi ha SEO que aguanti.
5. **Dades pròpies**: d'on sortiran (rastreig de webs, registres oficials, enquestes, fitxes reclamades). Si és un directori, carrega també la skill `directori`.
6. **Riscos**: legals (dades personals, sectors regulats; per exemple, detectius = llicència i registre oficial), de qualitat (fitxes buides), de dependència (un sol canal).
7. **Competència a primer cop d'ull**: 3–5 webs que ja surten a Google per al tema. Mira-les i anota què fan.

## Sortida: `brief/00_brief.md`

```markdown
# <Projecte> — Brief
## En una frase
## Objectiu i com mesurarem l'èxit (ex.: 5.000 visites/mes en 12 mesos; 50 leads/mes)
## Públic i idiomes
## Model de negoci (ara i després)
## Diferenciació i dades pròpies
## Zona de llançament
## Punt de partida (web existent: resum de l'inventari i l'auditoria)
## Riscos i decisions obertes
```

En acabar: actualitza `projecte.yaml` (`fases.f0_brief.estat: fet`, `descripcio`, `pendents`, `seguent: "Fase 1: context i personas"`). Si es pren una decisió important, anota-la amb data a `brief/decisions.md`.
