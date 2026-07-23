#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Nom .......... : collecte_openfoodfacts.py
# Role ......... : interroge l'API Open Food Facts avec deux requetes
#                  differentes, puis trace deux graphiques
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 2
# Prealable .... : pip install requests matplotlib
# Usage ........ : python3 collecte_openfoodfacts.py [CODE_BARRES]
# Exemple ...... : python3 collecte_openfoodfacts.py 3017620422003
# Sortie ....... : nutriscore.png, marques.png
# =====================================================================

import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")   # pour enregistrer les images sans ouvrir de fenetre
import matplotlib.pyplot as plt
import requests

URL = "https://world.openfoodfacts.org/api/v2"
# Open Food Facts demande de s'identifier dans les requetes
ENTETES = {"User-Agent": "IED-P8-L1-OIC-exo2.2"}


def chercher_produits():
    """Requete 1 : les produits halal vendus en France."""
    parametres = {
        "labels_tags_fr": "halal",
        "countries_tags_fr": "france",
        "fields": "code,product_name,brands,nutriscore_grade",
        "page_size": 100,
    }
    reponse = requests.get(URL + "/search", params=parametres,
                           headers=ENTETES, timeout=20)
    reponse.raise_for_status()
    return reponse.json().get("products", [])


def lire_produit(code_barres):
    """Requete 2 : la fiche d'un produit a partir de son code-barres."""
    parametres = {"fields": "product_name,brands,quantity,nutriscore_grade,labels"}
    reponse = requests.get(URL + "/product/" + code_barres,
                           params=parametres, headers=ENTETES, timeout=20)
    reponse.raise_for_status()
    donnees = reponse.json()
    if donnees.get("status") != 1:
        return None          # le produit n'existe pas dans la base
    return donnees["product"]


def graphique_nutriscore(produits):
    """Trace le nombre de produits par Nutri-Score."""
    # On ne garde que les produits dont le Nutri-Score est renseigne
    notes = [p["nutriscore_grade"].upper() for p in produits
             if p.get("nutriscore_grade") in ("a", "b", "c", "d", "e")]
    comptes = Counter(notes)
    lettres = ["A", "B", "C", "D", "E"]
    valeurs = [comptes.get(lettre, 0) for lettre in lettres]

    plt.figure(figsize=(7, 4))
    plt.bar(lettres, valeurs, color="steelblue")
    plt.title("Nutri-Score des produits halal (%d produits)" % len(notes))
    plt.xlabel("Nutri-Score")
    plt.ylabel("Nombre de produits")
    plt.savefig("nutriscore.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("Graphique ecrit : nutriscore.png")
    return comptes


def graphique_marques(produits):
    """Trace les 10 marques les plus presentes."""
    # Le champ brands contient parfois plusieurs marques separees par
    # des virgules : on ne garde que la premiere
    marques = [p["brands"].split(",")[0].strip()
               for p in produits if p.get("brands")]
    top = Counter(marques).most_common(10)
    if not top:
        print("Pas assez de marques renseignees pour le graphique.")
        return

    noms = [nom for nom, nombre in top]
    valeurs = [nombre for nom, nombre in top]

    plt.figure(figsize=(7, 4))
    plt.barh(noms[::-1], valeurs[::-1], color="seagreen")  # inverse : la plus grande en haut
    plt.title("Les 10 marques les plus presentes")
    plt.xlabel("Nombre de produits")
    plt.savefig("marques.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("Graphique ecrit : marques.png")


def main():
    # Le code-barres peut etre donne en argument
    if len(sys.argv) > 1:
        code_barres = sys.argv[1]
    else:
        code_barres = "3017620422003"

    try:
        print("=== Requete 1 : les produits halal vendus en France ===")
        produits = chercher_produits()
        print("%d produits recuperes." % len(produits))

        comptes = graphique_nutriscore(produits)
        graphique_marques(produits)
        total = sum(comptes.values())
        if total > 0:
            mauvais = comptes.get("D", 0) + comptes.get("E", 0)
            print("Produits notes D ou E : %.1f %%" % (100 * mauvais / total))

        print("")
        print("=== Requete 2 : la fiche du produit %s ===" % code_barres)
        produit = lire_produit(code_barres)
        if produit is None:
            print("Aucun produit ne correspond a ce code-barres.")
            return 1
        print("Nom .......... :", produit.get("product_name", "inconnu"))
        print("Marque ....... :", produit.get("brands", "inconnue"))
        print("Quantite ..... :", produit.get("quantity", "inconnue"))
        print("Nutri-Score .. :", produit.get("nutriscore_grade", "?").upper())
        print("Labels ....... :", produit.get("labels", "aucun"))

    except requests.RequestException as erreur:
        # Erreur de reseau ou reponse d'erreur du serveur
        print("Erreur lors de l'appel a l'API :", erreur)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
