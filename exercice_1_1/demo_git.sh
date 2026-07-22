#!/bin/bash
# =====================================================================
# Nom .......... : demo_git.sh
# Role ......... : rejoue les commandes Git de base vues dans le cours
#                  sur un petit depot d'essai
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 1
# Prealable .... : Git installe
# Usage ........ : ./demo_git.sh
# =====================================================================

DOSSIER="demo_git_ied"

# On verifie que Git est bien la avant de continuer
if ! command -v git > /dev/null; then
    echo "Erreur : git n'est pas installe."
    exit 1
fi

echo "### Version de Git"
git --version

# On repart d'un dossier vide pour pouvoir relancer le script
rm -rf "$DOSSIER"
mkdir "$DOSSIER"
cd "$DOSSIER"

echo ""
echo "### 1. Creation du depot"
git init -b main

echo "Mon premier fichier" > README.md

echo ""
echo "### 2. Etat du depot (le fichier n'est pas encore suivi)"
git status --short

echo ""
echo "### 3. On ajoute le fichier et on fait le premier commit"
git add README.md
git commit -m "premier commit"

# On modifie le fichier pour voir ce que git diff affiche
echo "Une ligne ajoutee" >> README.md

echo ""
echo "### 4. Les modifications depuis le dernier commit"
git --no-pager diff

git add README.md
git commit -m "ajout d'une ligne"

echo ""
echo "### 5. On cree une branche et on travaille dessus"
git switch -c ma-branche
echo "Fichier de licence" > LICENCE.txt
git add LICENCE.txt
git commit -m "ajout du fichier de licence"

echo ""
echo "### 6. On revient sur main et on fusionne"
git switch main
git merge --no-ff ma-branche -m "fusion de ma-branche"

echo ""
echo "### 7. L'historique du depot"
git --no-pager log --oneline --graph --all

echo ""
echo "Pour envoyer ce depot sur GitHub il resterait a faire :"
echo "  git remote add origin https://github.com/UTILISATEUR/DEPOT.git"
echo "  git push -u origin main"
