#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Nom .......... : api_bibliotheque.py
# Role ......... : API REST qui permet de consulter et de partager ma
#                  bibliotheque personnelle (25 livres)
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 3
# Prealable .... : pip install fastapi uvicorn
# Usage ........ : uvicorn api_bibliotheque:app --reload
# Donnees ...... : bibliotheque.json
# =====================================================================

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Le chemin est calcule a partir du fichier .py, sinon l'API ne trouve
# plus ses donnees si on la lance depuis un autre dossier
FICHIER = Path(__file__).parent / "bibliotheque.json"


class Livre(BaseModel):
    """Un livre de la bibliotheque.

    Pydantic verifie tout seul les types et les valeurs indiquees dans
    les Field : je n'ai pas de controle a ecrire moi-meme.
    """
    id: int
    titre: str
    auteur: str
    categorie: str
    annee: int
    note: int = Field(ge=1, le=5)   # note sur 5
    lu: bool = True


def charger():
    """Lit le fichier JSON et renvoie la liste des livres."""
    with open(FICHIER, encoding="utf-8") as fichier:
        return json.load(fichier)


def enregistrer(livres):
    """Reecrit le fichier JSON apres une modification."""
    with open(FICHIER, "w", encoding="utf-8") as fichier:
        json.dump(livres, fichier, ensure_ascii=False, indent=2)


app = FastAPI(title="Ma bibliotheque partagee")


@app.get("/")
def accueil():
    """Message d'accueil et liste des routes."""
    return {
        "message": "Bienvenue sur ma bibliotheque partagee",
        "routes": ["/livres", "/livres/{id}", "/categories", "/docs"],
        "nombre_de_livres": len(charger()),
    }


@app.get("/livres")
def lister_livres(categorie: str = None):
    """Renvoie tous les livres, ou seulement ceux d'une categorie."""
    livres = charger()
    if categorie is not None:
        # .lower() des deux cotes pour ne pas avoir a respecter la casse
        livres = [l for l in livres if l["categorie"].lower() == categorie.lower()]
    return livres


@app.get("/categories")
def lister_categories():
    """Renvoie le nombre de livres par categorie."""
    comptes = {}
    for livre in charger():
        categorie = livre["categorie"]
        comptes[categorie] = comptes.get(categorie, 0) + 1
    return comptes


@app.get("/livres/{livre_id}")
def lire_livre(livre_id: int):
    """Renvoie un livre a partir de son identifiant."""
    for livre in charger():
        if livre["id"] == livre_id:
            return livre
    # Le livre n'existe pas : on renvoie une erreur 404
    raise HTTPException(status_code=404,
                        detail="Aucun livre avec l'identifiant %d." % livre_id)


@app.post("/livres")
def ajouter_livre(livre: Livre):
    """Ajoute un livre a la bibliotheque."""
    livres = charger()
    for existant in livres:
        if existant["id"] == livre.id:
            # Identifiant deja utilise : on renvoie une erreur 409
            raise HTTPException(status_code=409,
                                detail="L'identifiant %d est deja pris." % livre.id)
    livres.append(livre.model_dump())
    enregistrer(livres)
    return livre


@app.put("/livres/{livre_id}")
def modifier_livre(livre_id: int, livre: Livre):
    """Remplace un livre existant."""
    livres = charger()
    for position, existant in enumerate(livres):
        if existant["id"] == livre_id:
            livres[position] = livre.model_dump()
            enregistrer(livres)
            return livre
    raise HTTPException(status_code=404,
                        detail="Aucun livre avec l'identifiant %d." % livre_id)


@app.delete("/livres/{livre_id}")
def supprimer_livre(livre_id: int):
    """Supprime un livre de la bibliotheque."""
    livres = charger()
    restants = [l for l in livres if l["id"] != livre_id]
    if len(restants) == len(livres):
        raise HTTPException(status_code=404,
                            detail="Aucun livre avec l'identifiant %d." % livre_id)
    enregistrer(restants)
    return {"supprime": livre_id, "livres_restants": len(restants)}
