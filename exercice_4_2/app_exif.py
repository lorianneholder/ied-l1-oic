#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Nom .......... : app_exif.py
# Role ......... : application Streamlit qui affiche une photo, permet
#                  de modifier ses metadonnees EXIF et ses coordonnees
#                  GPS, puis affiche deux cartes
# Auteur ....... : Lorianne HOLDER
# Version ...... : V1.0 du 21/07/2026
# Licence ...... : IED Paris 8 - L1 - OIC - Chapitre 4
# Prealable .... : pip install -r requirements.txt
# Usage ........ : streamlit run app_exif.py
# Donnees ...... : photo.jpg, lieux.json
# =====================================================================

import io
import json
from datetime import datetime
from pathlib import Path

import folium
import piexif
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium

DOSSIER = Path(__file__).parent


def vers_dms(valeur):
    """Convertit un angle decimal en degres, minutes, secondes.

    L'EXIF ne stocke pas 47.4358 mais 47 degres 26 minutes 8.88
    secondes, et chaque nombre est un couple (numerateur, denominateur).
    """
    valeur = abs(valeur)
    degres = int(valeur)
    minutes = int((valeur - degres) * 60)
    secondes = (valeur - degres - minutes / 60) * 3600
    return ((degres, 1), (minutes, 1), (int(secondes * 100), 100))


def lire_exif(image_octets):
    """Renvoie les metadonnees EXIF de l'image, ou un dictionnaire vide."""
    try:
        return piexif.load(image_octets)
    except Exception:
        # Beaucoup d'images n'ont pas d'EXIF du tout (captures d'ecran...)
        return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}


def afficher_exif(exif):
    """Transforme les metadonnees en tableau lisible."""
    lignes = []
    for bloc in ("0th", "Exif", "GPS"):
        for cle, valeur in exif.get(bloc, {}).items():
            nom = piexif.TAGS[bloc][cle]["name"]
            if isinstance(valeur, bytes):
                valeur = valeur.decode("utf-8", errors="replace")
            lignes.append({"Champ": nom, "Valeur": str(valeur)[:60]})
    return lignes


def ecrire_exif(image_octets, champs, latitude, longitude):
    """Reecrit l'image avec les nouvelles metadonnees."""
    exif = lire_exif(image_octets)

    # Les champs texte
    exif["0th"][piexif.ImageIFD.Make] = champs["marque"].encode()
    exif["0th"][piexif.ImageIFD.Model] = champs["modele"].encode()
    exif["0th"][piexif.ImageIFD.Artist] = champs["auteur"].encode()
    exif["0th"][piexif.ImageIFD.Copyright] = champs["droits"].encode()
    exif["0th"][piexif.ImageIFD.ImageDescription] = champs["description"].encode()
    exif["0th"][piexif.ImageIFD.DateTime] = champs["date"].encode()

    # Les coordonnees GPS. Le signe n'est pas dans la valeur mais dans
    # une balise a part : N ou S pour la latitude, E ou W pour la longitude.
    exif["GPS"] = {
        piexif.GPSIFD.GPSLatitudeRef: b"N" if latitude >= 0 else b"S",
        piexif.GPSIFD.GPSLatitude: vers_dms(latitude),
        piexif.GPSIFD.GPSLongitudeRef: b"E" if longitude >= 0 else b"W",
        piexif.GPSIFD.GPSLongitude: vers_dms(longitude),
    }

    # La miniature fait souvent echouer piexif.dump, on l'enleve
    exif["thumbnail"] = None
    exif["1st"] = {}

    image = Image.open(io.BytesIO(image_octets))
    sortie = io.BytesIO()
    image.save(sortie, format="JPEG", exif=piexif.dump(exif))
    return sortie.getvalue()


# ---------------------------------------------------------------------
# L'interface
# ---------------------------------------------------------------------
st.title("Editeur de metadonnees EXIF")
st.write("IED Paris 8 - L1 Informatique - OIC - Exercice 4.2")

fichier = st.file_uploader("Choisir une image JPEG", type=["jpg", "jpeg"])
if fichier is not None:
    octets = fichier.read()
elif (DOSSIER / "photo.jpg").exists():
    octets = (DOSSIER / "photo.jpg").read_bytes()
else:
    # Ni televersement, ni photo par defaut : on arrete proprement
    st.error("Aucune image : televersez un JPEG ou placez photo.jpg "
             "dans le dossier du script.")
    st.stop()

st.image(octets)

st.subheader("Metadonnees actuelles")
st.dataframe(afficher_exif(lire_exif(octets)))

st.subheader("Modifier les metadonnees")
with st.form("formulaire"):
    marque = st.text_input("Appareil (Make)", "IED-P8")
    modele = st.text_input("Modele (Model)", "Editeur Streamlit")
    auteur = st.text_input("Auteur (Artist)", "Lorianne HOLDER")
    droits = st.text_input("Droits (Copyright)", "Usage pedagogique")
    description = st.text_input("Description", "Photo de l'exercice 4.2")
    date = st.text_input("Date (AAAA:MM:JJ HH:MM:SS)",
                         datetime.now().strftime("%Y:%m:%d %H:%M:%S"))
    st.write("Coordonnees GPS a inscrire dans l'image :")
    latitude = st.number_input("Latitude", value=47.4358, format="%.4f")
    longitude = st.number_input("Longitude", value=-1.4986, format="%.4f")
    valider = st.form_submit_button("Ecrire les metadonnees")

if valider:
    champs = {"marque": marque, "modele": modele, "auteur": auteur,
              "droits": droits, "description": description, "date": date}
    try:
        nouvelle_image = ecrire_exif(octets, champs, latitude, longitude)
    except Exception as erreur:
        # Par exemple si la date n'est pas au bon format
        st.error("Impossible d'ecrire les metadonnees : %s" % erreur)
    else:
        st.success("Metadonnees ecrites. Relecture de la nouvelle image :")
        st.dataframe(afficher_exif(lire_exif(nouvelle_image)))
        st.download_button("Telecharger l'image modifiee", nouvelle_image,
                           "photo_modifiee.jpg", "image/jpeg")

# --- Carte 1 : le point GPS de la photo ------------------------------
st.subheader("Carte 1 : position GPS inscrite dans la photo")
carte1 = folium.Map(location=[latitude, longitude], zoom_start=6)
folium.Marker([latitude, longitude], tooltip="Position de la photo",
              icon=folium.Icon(color="red")).add_to(carte1)
st_folium(carte1, width=700, height=400, key="carte1")

# --- Carte 2 : les lieux ou je suis alle -----------------------------
st.subheader("Carte 2 : les lieux ou je me suis rendu")
with open(DOSSIER / "lieux.json", encoding="utf-8") as f:
    lieux = json.load(f)

points = [(lieu["latitude"], lieu["longitude"]) for lieu in lieux]
carte2 = folium.Map(location=points[0], zoom_start=4)
for numero, lieu in enumerate(lieux, start=1):
    folium.Marker([lieu["latitude"], lieu["longitude"]],
                  tooltip="%d. %s (%d)" % (numero, lieu["nom"], lieu["annee"])
                  ).add_to(carte2)
# On relie les points entre eux, dans l'ordre du fichier
folium.PolyLine(points).add_to(carte2)
st_folium(carte2, width=700, height=400, key="carte2")
