#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Nom .......... : generer_pi.py
# Role ......... : calcule le premier million de decimales de PI et les
#                  enregistre dans un fichier texte
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 4
# Prealable .... : pip install mpmath
# Usage ........ : python3 generer_pi.py [NB_DECIMALES]
# Exemple ...... : python3 generer_pi.py 1000000
# Sortie ....... : pi_1000000.txt
# =====================================================================

import sys
import time

from mpmath import mp

try:
    nombre = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
except ValueError:
    print("Erreur : il faut donner un nombre entier de decimales.")
    sys.exit(1)

debut = time.time()

# On demande dix chiffres de plus que necessaire : les derniers chiffres
# d'un calcul ne sont jamais fiables, on les jette ensuite
mp.dps = nombre + 10
texte = mp.nstr(mp.pi, nombre + 5, strip_zeros=False)
decimales = texte.split(".")[1][:nombre]

with open("pi_%d.txt" % nombre, "w") as fichier:
    fichier.write(decimales)

print("%d decimales calculees en %.2f s." % (len(decimales), time.time() - debut))
print("Fichier ecrit : pi_%d.txt" % nombre)
print("Verification  : 3.%s..." % decimales[:15])
