#!/usr/bin/env python3
"""Crea un projecte nou a partir de la plantilla.

Ús:
    python3 nou_projecte.py <carpeta-desti> --nom "Detectius.cat" --tipus directori --mode nou \
        --domini detectius.cat --idiomes ca,es [--descripcio "..."]
"""
import argparse
import datetime as dt
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(os.path.dirname(AQUI), "plantilla")
FITXERS_AMB_VARIABLES = ["projecte.yaml", "lloc.yaml"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("desti")
    ap.add_argument("--nom", required=True)
    ap.add_argument("--tipus", default="altres", choices=["directori", "marca-personal", "negoci-local", "ecommerce", "altres"])
    ap.add_argument("--mode", default="nou", choices=["nou", "existent"])
    ap.add_argument("--domini", default="exemple.cat")
    ap.add_argument("--idiomes", default="ca")
    ap.add_argument("--descripcio", default="")
    a = ap.parse_args()

    desti = os.path.abspath(a.desti)
    if os.path.exists(desti) and os.listdir(desti):
        if os.path.exists(os.path.join(desti, "projecte.yaml")):
            sys.exit(f"Ja hi ha un projecte a {desti}")
    shutil.copytree(PLANTILLA, desti, dirs_exist_ok=True)
    idiomes = [i.strip() for i in a.idiomes.split(",") if i.strip()]
    valors = {
        "{{NOM}}": a.nom, "{{TIPUS}}": a.tipus, "{{MODE}}": a.mode, "{{DOMINI}}": a.domini.replace("https://", "").strip("/"),
        "{{IDIOMES}}": "[" + ", ".join(idiomes) + "]", "{{IDIOMA_DEFECTE}}": idiomes[0],
        "{{DESCRIPCIO}}": a.descripcio.replace('"', "'"), "{{DATA}}": dt.date.today().isoformat(),
    }
    for nom in FITXERS_AMB_VARIABLES:
        ruta = os.path.join(desti, nom)
        text = open(ruta, encoding="utf-8").read()
        for k, v in valors.items():
            text = text.replace(k, v)
        open(ruta, "w", encoding="utf-8").write(text)
    for idioma in idiomes:
        os.makedirs(os.path.join(desti, "contingut", idioma), exist_ok=True)
    for arrel, _, fitxers in os.walk(desti):
        for f in fitxers:
            if f == ".keep":
                os.remove(os.path.join(arrel, f))
    print(f"✓ Projecte «{a.nom}» creat a {desti}")
    print("  Següent pas: fase 0 (brief). Obre brief/ i segueix la skill f0-brief.")


if __name__ == "__main__":
    main()
