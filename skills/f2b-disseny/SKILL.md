---
name: f2b-disseny
description: Fase 2b de la Fàbrica de webs SEO (nova respecte del playbook). Defineix el sistema de disseny del projecte (colors, tipografia, components, regles de conversió i accessibilitat) abans de fer cap pàgina, i el tradueix als tokens de lloc.yaml i als components del generador. Fes-la servir abans de la primera pàgina o quan es vol canviar l'aspecte de tota la web.
---

# Fase 2b — Sistema de disseny

Per què: a Bona Tria vam dissenyar pàgina a pàgina (pas 7 del PDF) i vam haver de redissenyar tres cops tota la web amb scripts. Ara el disseny es defineix una vegada i les pàgines només combinen components.

Sortida: `disseny/sistema.md`, tokens a `lloc.yaml → disseny`, i (si cal) components propis a `tema/`.

## 1. Direcció visual (amb la skill frontend-design)
Si la skill **frontend-design** està disponible (plugin `frontend-design` d'Anthropic), carrega-la abans de proposar res i segueix el seu procés: pla → revisió contra el brief → construcció → autocrítica amb captures. Si no hi és, aplica aquests mateixos principis:
- **La direcció surt del tema del projecte**: sector, materials, vocabulari i públic (pas 1). Un directori de detectius i una marca personal de consultoria no s'han d'assemblar.
- Proposa **2 direccions** contrastades. Per a cadascuna: paleta de 4–6 colors amb nom i ús, 1–2 famílies tipogràfiques clarament diferents (Google Fonts) amb la seva escala, concepte de maquetació amb un esquema ASCII, i 2–3 principis.
- **Revisa-les contra els tòpics** abans de construir: fons crema amb serif i accent terracota; fons negre amb un sol accent àcid; maquetació de diari amb filets; kit de targetes SaaS amb ombres i degradats; etiquetes en majúscules sobre cada títol, separadors «·» i fletxes «→» a tots els botons. Si una direcció hi cau sense motiu, canvia-la i explica per què.
- **Una sola cosa memorable** (l'H1, la resposta ràpida, una il·lustració, una eina) i tota la resta tranquil·la.
- Construeix la mateixa pàgina real amb cada direcció (tokens a `lloc.yaml`, i CSS propi a `tema/assets/` si cal), fes captures a mòbil i escriptori, i critica-les abans d'ensenyar-les.
- El propietari en tria una. Anota-la a `disseny/sistema.md` amb el pla complet i el que s'ha descartat.

El tema base (`temes/base`) és el punt de partida neutre: grotesca per als títols i la interfície, serif per a la lectura, index lateral, targetes planes i directori en files. Per a un projecte amb personalitat pròpia, sobreescriu-ne els tokens i, si cal, afegeix `tema/assets/projecte.css` (amb `css_extra: /assets/projecte.css` a `lloc.yaml`).

## 2. Tokens (`lloc.yaml → disseny`)
`color_text`, `color_fons`, `color_suau`, `color_primari`, `color_accent`, `color_linia`, `font_titols`, `font_text`, `google_fonts`, `radi`, `amplada`. El generador els escriu a `assets/tokens.css`.
Comprova el **contrast AA** (4,5:1 per al text, 3:1 per a botons i text gran) entre text/fons i blanc/primari/accent.

## 3. Components
El tema base té: hero amb molles i signatura (autor, revisor, data), `resum`, `targetes`, `cta`, `avis`, `xifres`, `passos`, `directori`, taules, FAQ, relacionades. Per a cada tipus de pàgina del projecte (hub, guia, ciutat, fitxa…), decideix quins components fa servir i en quin ordre (plantilla de pàgina).
Si cal un component nou (calculadora, comparador, mapa), crea'l a `tema/components/<nom>.html` amb `tema: tema` a `lloc.yaml`, i documenta'l a `disseny/sistema.md`.

## 4. Regles de conversió
- **Una acció principal** per pàgina (demanar pressupost, contactar, subscriure's), al primer pantallàs i al final. `cta_principal` a `lloc.yaml` per al botó del menú.
- **Senyals de confiança** a prop de l'acció: xifres pròpies, com treballem, autor/revisor, garanties.
- Formularis curts (3–5 camps); diu què passarà després d'enviar.

## 5. Accessibilitat i rendiment
Mòbil primer; mida de text ≥ 16 px; focus visible; enllaç «vés al contingut»; imatges amb `alt`, mida declarada i `loading="lazy"`; com a màxim 2 famílies tipogràfiques; sense JavaScript imprescindible.

## 6. Imatges
Prioritza fotos pròpies (equip, feina feta, zona) per sobre d'il·lustracions genèriques. Imatge Open Graph de 1200×630 per a les pàgines principals (`og_imatge` a la capçalera).

En acabar: `fases.f2b_disseny.estat: fet` a `projecte.yaml`.
