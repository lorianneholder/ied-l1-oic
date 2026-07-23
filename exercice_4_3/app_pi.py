#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Nom .......... : app_pi.py
# Role ......... : application Streamlit qui repond aux quatre consignes
#                  decodees : chercher une date de naissance dans les
#                  decimales de PI, donner le jour de la semaine,
#                  calculer deux sommes de decimales, montrer une video
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 4 (Bonus)
# Prealable .... : pip install -r requirements.txt
#                  puis python3 generer_pi.py 1000000
# Usage ........ : streamlit run app_pi.py
# Donnees ...... : pi_1000000.txt
# =====================================================================

from datetime import date
from pathlib import Path

import streamlit as st

FICHIER = Path(__file__).parent / "pi_1000000.txt"
VIDEO = "https://www.youtube.com/watch?v=w-I6XTVZXww"
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


@st.cache_data
def charger_pi():
    """Lit le fichier des decimales de PI.

    Streamlit relance tout le script a chaque clic. Sans cache_data, le
    fichier d'un million de caracteres serait relu a chaque fois.
    """
    return FICHIER.read_text().strip()


st.title("Ma date de naissance dans les decimales de PI")
st.write("IED Paris 8 - L1 Informatique - OIC - Exercice 4.3 (Bonus)")

if not FICHIER.exists():
    # Le fichier des decimales n'a pas encore ete genere
    st.error("Fichier pi_1000000.txt introuvable. Lancez d'abord "
             "python3 generer_pi.py 1000000")
    st.stop()

decimales = charger_pi()
st.write("%d decimales chargees. PI = 3,%s..." % (len(decimales), decimales[:20]))

# --- Consigne 1 : chercher la date -----------------------------------
st.header("1. Recherche de la date de naissance")
naissance = st.date_input("Date de naissance", value=date(1995, 7, 21),
                          min_value=date(1900, 1, 1))

# On teste deux ecritures : la date complete est rarement presente,
# la version courte JJMM se trouve presque toujours
formats = {
    "JJMMAAAA": naissance.strftime("%d%m%Y"),
    "JJMM": naissance.strftime("%d%m"),
}

for nom, motif in formats.items():
    position = decimales.find(motif)
    if position >= 0:
        # find renvoie 0 pour le premier caractere, d'ou le +1
        st.write("**%s** (%s) : trouve a partir de la decimale n %d"
                 % (nom, motif, position + 1))
    else:
        st.write("**%s** (%s) : absent du premier million de decimales"
                 % (nom, motif))

# --- Consigne 2 : le jour de la semaine ------------------------------
st.header("2. Jour de la semaine")
jour = JOURS[naissance.weekday()]
st.text_input("Jour de naissance",
              value="%s etait un %s" % (naissance.strftime("%d/%m/%Y"), jour),
              disabled=True)

# --- Consigne 3 : les deux sommes ------------------------------------
st.header("3. Sommes des premieres decimales")


def somme(nombre_de_decimales):
    """Additionne les premiers chiffres de PI."""
    return sum(int(chiffre) for chiffre in decimales[:nombre_de_decimales])


somme_20 = somme(20)
somme_144 = somme(12 ** 2)

st.text_input("Somme des 20 premieres decimales", value=str(somme_20),
              disabled=True)
st.text_input("Somme des 12x12 = 144 premieres decimales",
              value=str(somme_144), disabled=True)

st.write("On tombe sur deux nombres ronds : **%d** et **%d**. "
         "C'est une coincidence et non une propriete de PI : juste a "
         "cote, la somme des 143 premieres decimales vaut %d et celle "
         "des 145 premieres vaut %d."
         % (somme_20, somme_144, somme(143), somme(145)))

# --- Consigne 4 : la video -------------------------------------------
st.header("4. La somme de tous les entiers vaut -1/12")
st.video(VIDEO)
st.write("Video Numberphile. Cette egalite n'est pas une somme au sens "
         "habituel, puisque 1 + 2 + 3 + ... n'a pas de limite finie. "
         "C'est la valeur donnee par la fonction zeta de Riemann.")
