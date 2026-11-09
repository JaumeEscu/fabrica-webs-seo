---
name: f5-mesurar
description: Fase 5 de la Fàbrica de webs SEO (nova respecte del playbook). Revisió mensual d'una web publicada amb dades de Search Console - què puja, què cau, oportunitats ràpides, pàgines a refrescar i noves pàgines - i actualització de les mètriques del dashboard. Fes-la servir cada mes o quan el trànsit canvia.
---

# Fase 5 — Mesurar i refrescar (cada mes)

## 1. Dades
Demana al propietari l'export de Search Console (Rendiment → últims 3 mesos comparats amb els 3 anteriors → Exportar → pestanyes Consultes i Pàgines) a `informes/gsc/AAAA-MM/`. Si hi ha un connector de Search Console disponible, fes-lo servir.

## 2. Anàlisi (`informes/AAAA-MM.md`)
- **Resum**: clics, impressions, CTR i posició mitjana vs el període anterior.
- **Guanyadores i perdedores**: les 5 pàgines que més pugen i les 5 que més cauen, amb una hipòtesi per a cada caiguda (estacionalitat, competidor nou, canvi d'algoritme, canibalització, problema tècnic).
- **Oportunitats ràpides**: consultes en posició 5–20 amb moltes impressions → millorar title/description, afegir una secció o FAQ que respongui exactament la consulta, reforçar enllaços interns.
- **CTR baix** (posició < 5 i CTR inferior al normal): reescriure el title i la description.
- **Canibalització**: consultes per a les quals surten dues URL → decidir quina mana i ajustar.
- **Consultes noves sense pàgina** → candidates a pàgina nova (tornen a la fase 2 → 3).
- **Indexació**: pàgines «Descoberta: actualment sense indexar» o «Rastrejada, no indexada» → millorar-les o desindexar-les.

## 3. Refrescar
- Revisa les dades amb data (preus, ajudes, normativa) un cop cada trimestre i abans de la temporada alta. Actualitza `actualitzat:` a la capçalera només quan el canvi és real.
- Treu les marques `[VERIFICAR]` que s'hagin confirmat.
- Torna a construir i comprovar (fase 4).

## 4. Dashboard
Actualitza `projecte.yaml`:
```yaml
metriques:
  gsc: { periode: "2027-03", clics: 1234, impressions: 56789, ctr: 2.2, posicio: 14.3 }
```
i `pendents` / `seguent` amb les accions del mes. Després regenera el dashboard (skill `dashboard`).
