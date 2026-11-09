---
name: directori
description: Mòdul de directori de la Fàbrica de webs SEO. Per a webs que llisten empreses o professionals (instal·ladors, detectius, advocats...) - fonts d'empreses, rastreig i verificació amb criteris, full de verificació, fitxes.yaml, pàgines per zona i servei×zona amb llindars de qualitat, schema LocalBusiness, i model de monetització. Fes-la servir quan el projecte és o inclou un directori.
---

# Mòdul de directori

Lliçó de Bona Tria: un directori només val si les fitxes tenen **dades comprovades** que no es troben enlloc més (de 328 empreses revisades, 81 publicables). Una llista copiada de Google Maps és contingut prim.

## 1. Criteris (abans de buscar ningú) — `directori/criteris.md`
- **Requisit per sortir** (filtre de veritat): ex. instal·lador habilitat RITE; detectiu amb llicència del Ministeri de l'Interior i inscrit al registre.
- **Dades a comprovar** (8–10, cadascuna amb la font on es mira): serveis concrets, zona real de servei, anys, certificacions, finançament, idiomes, especialitats.
- **Què no publiquem**: dades personals de particulars, valoracions copiades, res que no puguem enllaçar a una font.
- Sectors regulats: comprova què diu la llei sobre publicitat i dades (ex.: detectius privats → Llei 5/2014 de seguretat privada; només empreses i despatxos habilitats).

## 2. Fonts d'empreses — `directori/fonts.md`
Registres oficials (sempre que n'hi hagi), col·legis i associacions, Google Maps per zona (cerca manual o export), directoris del sector, webs de fabricants (instal·ladors oficials). Llista les fonts i quantes empreses aporta cadascuna.

## 3. Rastreig i verificació — full `directori/verificacio.xlsx` (o .csv)
Columnes: id, nom, web, municipi, comarca/regió, font, requisit (sí/no/dubte + enllaç), una columna per dada comprovada (valor + URL de la font), data de comprovació, estat (publicable / no publicable / pendent), motiu.
- Visita la web de cada empresa (no només la fitxa de Maps). Les dades sense font no compten.
- Treballa per lots de zona (una comarca o ciutat). Comença per la zona de llançament del brief.
- Anota el percentatge que passa el filtre: és una dada pròpia per a la web («hem revisat X, n'hem publicat Y»).

## 4. `directori/fitxes.yaml` (el llegeix el generador)
```yaml
- slug: empresa-exemple        # únic, per a la URL de la fitxa
  nom: Empresa Exemple SL
  municipi: Sabadell
  comarca: Vallès Occidental
  regio: Catalunya
  serveis: [aerotermia, aire-condicionat]   # per filtrar a ::: directori servei=...
  zona: [Sabadell, Terrassa, Sant Cugat]    # areaServed
  descripcio: { ca: "...", es: "..." }
  etiquetes: [CAE, "Alta temperatura"]
  dades: { "Habilitació RITE": "Sí", "Anys": "18" }
  fonts: [https://empresa.cat/serveis]
  web: https://empresa.cat
  verificat: 2026-11-03
  destacat: false               # fitxa destacada (monetització)
  schema_tipus: HVACBusiness    # o LocalBusiness, LegalService, ProfessionalService...
```
A `lloc.yaml → directori`: `actiu: true`, `min_fitxes_indexar` (Bona Tria: 5 per comarca, 3 per ciutat), `pagina_fitxa: true` si cada empresa té pàgina pròpia, `ruta_fitxa`, `titol_fitxa: { ca: "{nom}, {servei} a {municipi}" }`.

## 5. Pàgines programàtiques
- **Zona** (ciutat/comarca) i **servei×zona** només si el Keyword Planner hi dona cerques **i** hi ha prou fitxes. Per sota del mínim, el generador posa `noindex` sol.
- Cada pàgina de zona necessita contingut propi a més del llistat: preus o condicions locals, normativa o ajudes de l'ajuntament, preguntes locals, quantes empreses hem revisat a la zona. Mai el mateix text canviant el nom de la ciutat.
- Bloc `::: directori municipi=X servei=Y` per al llistat; FAQ locals; enllaços a les zones veïnes.

## 6. Monetització (ordre de Bona Tria)
1. Trànsit i confiança primer (fitxes gratuïtes, «reclama la teva fitxa»).
2. Fitxa destacada (`destacat: true`, marcada com a destacada de manera visible).
3. Leads de pagament / exclusivitat de zona.
4. Patrocini de marca o distribuïdor.
Anota el model triat al brief i a `projecte.yaml`.
