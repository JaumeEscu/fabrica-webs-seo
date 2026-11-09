# Format d'una pàgina (contingut/<idioma>/<clau>.md)

```markdown
---
clau: preu                      # igual a totes les versions d'idioma (hreflang)
slug: preu-aerotermia           # ruta sense l'idioma; "" per a la portada
titol: "Preu de l'aerotèrmia el 2026: quant costa a Catalunya"   # <title>, 30–60 caràcters
descripcio: "..."               # meta description, 70–160 caràcters
tipus: guia                     # pagina | hub | guia | article | ciutat | legal
keyword: preu aerotèrmia        # paraula clau principal (informatiu, el comprovador la fa servir)
pare: aerotermia                # clau de la pàgina mare (molles de pa). Per defecte, la portada
molla: Preu                     # text curt a les molles (opcional)
avantitol: "Guia de preus"      # opcional, sobre l'H1
entradeta: "..."                # opcional, sota l'H1
autor: jaume                    # id de lloc.yaml → autors (E-E-A-T)
revisor: installador-1          # opcional
actualitzat: 2026-11-09
noindex: false
relacionades: [radiadors, ajudes]   # targetes «També et pot interessar» (enllaçat intern)
faq:                            # es mostra al final i genera FAQPage (mateix text)
  - p: "Quant costa...?"
    r: "Entre 7.000 i 12.000 €... Font: ... [VERIFICAR]"
schema: []                      # JSON-LD extra (opcional)
min_fitxes: 3                   # pàgines amb directori: noindex si n'hi ha menys
---
# H1 amb la paraula clau

Text en Markdown. Enllaç intern: [preu per m²](@preu#preu-per-m2). Taules Markdown.

::: resum
Resposta directa de 1–2 frases (fragment destacat i IA).
:::

::: targetes columnes=2
### [Títol amb enllaç](@clau)
Text de la targeta.
### Títol sense enllaç
Text.
:::

::: cta text="Demana pressupost" enllac="@pressupost" nota="Gratis i sense compromís"
### Títol de la crida
Text curt.
:::

::: avis tipus=alerta
Text destacat.
:::

::: xifres
- **81** especialistes verificats
- **328** empreses revisades
:::

::: passos
1. Primer pas
2. Segon pas
:::

::: directori municipi=Sabadell servei=aerotermia limit=10
Text d'introducció del llistat.
:::
```

Components nous: crea `tema/components/<nom>.html` al projecte (i posa `tema: tema` a `lloc.yaml`) o afegeix-los al tema base del plugin si serveixen per a tothom.
