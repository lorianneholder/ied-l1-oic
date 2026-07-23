#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Nom .......... : decodeur_brainfuck.py
# Role ......... : interprete les quatre consignes de l'exercice 4.3,
#                  ecrites en Brainfuck, et affiche le texte en clair
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 4
# Prealable .... : Python 3 seulement
# Usage ........ : python3 decodeur_brainfuck.py [fichier.bf]
# Exemple ...... : python3 decodeur_brainfuck.py consigne_1.bf
# =====================================================================

import sys
from pathlib import Path

INSTRUCTIONS = "><+-.,[]"


def executer(source):
    """Execute un programme Brainfuck et renvoie le texte affiche."""
    # En Brainfuck tout caractere inconnu est un commentaire : on ne
    # garde que les huit instructions du langage
    code = "".join(c for c in source if c in INSTRUCTIONS)

    # On note d'avance a quel crochet fermant correspond chaque crochet
    # ouvrant, sinon il faudrait relire le code a chaque tour de boucle
    sauts = {}
    pile = []
    for position, caractere in enumerate(code):
        if caractere == "[":
            pile.append(position)
        elif caractere == "]":
            if not pile:
                raise ValueError("Crochet fermant en trop.")
            ouvrant = pile.pop()
            sauts[ouvrant] = position
            sauts[position] = ouvrant
    if pile:
        raise ValueError("Crochet ouvrant jamais ferme.")

    ruban = [0] * 30000
    curseur = 0     # ou on est sur le ruban
    pointeur = 0    # ou on est dans le code
    sortie = []

    while pointeur < len(code):
        instruction = code[pointeur]
        if instruction == ">":
            curseur += 1
        elif instruction == "<":
            curseur -= 1
        elif instruction == "+":
            # Une cellule va de 0 a 255, d'ou le modulo
            ruban[curseur] = (ruban[curseur] + 1) % 256
        elif instruction == "-":
            ruban[curseur] = (ruban[curseur] - 1) % 256
        elif instruction == ".":
            sortie.append(chr(ruban[curseur]))
        elif instruction == "[" and ruban[curseur] == 0:
            pointeur = sauts[pointeur]      # on saute la boucle
        elif instruction == "]" and ruban[curseur] != 0:
            pointeur = sauts[pointeur]      # on refait un tour
        pointeur += 1

    return "".join(sortie)


def main():
    # Sans argument, on decode les quatre consignes du dossier
    if len(sys.argv) > 1:
        fichiers = sys.argv[1:]
    else:
        fichiers = sorted(Path(__file__).parent.glob("consigne_*.bf"))

    for chemin in fichiers:
        chemin = Path(chemin)
        print("---", chemin.name, "---")
        if not chemin.exists():
            # Le fichier demande n'existe pas
            print("Erreur : fichier introuvable.")
            continue
        try:
            print(executer(chemin.read_text(encoding="utf-8")))
        except ValueError as erreur:
            print("Erreur dans le code Brainfuck :", erreur)
        print("")


if __name__ == "__main__":
    main()
