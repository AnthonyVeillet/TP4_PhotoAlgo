"""
Réchauffement (20%) : Application d'homographies H1 et H2 sur pouliot.jpg.
"""
import numpy as np
import os
import sys

from utils import charger_image, sauvegarder_image, afficher_images_cote_a_cote
from transformation import appliqueTransformation

# ============================================================
# Configuration des chemins
# ============================================================
# Ajuster BASE_DIR selon l'emplacement de votre dossier images/
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
RAPPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'rapport', 'images', 'rechauffement')

IMG_PATH = os.path.join(BASE_DIR, '0-Rechauffement', 'pouliot.jpg')


def main():
    # Charger l'image
    print("Chargement de pouliot.jpg...")
    img = charger_image(IMG_PATH)
    print(f"  Dimensions : {img.shape}")

    # Homographies fournies
    H1 = np.array([
        [0.9752, 0.0013, -100.3164],
        [-0.4886, 1.7240, 24.8480],
        [-0.0016, 0.0004, 1.0000]
    ])

    H2 = np.array([
        [0.1814, 0.7402, 34.3412],
        [1.0209, 0.1534, 60.3258],
        [0.0005, 0, 1.0000]
    ])

    # Appliquer H1
    print("\nApplication de H1...")
    img_H1, offset_H1 = appliqueTransformation(img, H1)
    print(f"  Dimensions résultat : {img_H1.shape}")
    print(f"  Offset : {offset_H1}")

    # Appliquer H2
    print("\nApplication de H2...")
    img_H2, offset_H2 = appliqueTransformation(img, H2)
    print(f"  Dimensions résultat : {img_H2.shape}")
    print(f"  Offset : {offset_H2}")

    # Sauvegarder les résultats
    os.makedirs(RAPPORT_DIR, exist_ok=True)
    sauvegarder_image(img, os.path.join(RAPPORT_DIR, 'pouliot_original.jpg'))
    sauvegarder_image(img_H1, os.path.join(RAPPORT_DIR, 'pouliot_H1.jpg'))
    sauvegarder_image(img_H2, os.path.join(RAPPORT_DIR, 'pouliot_H2.jpg'))

    # Afficher
    afficher_images_cote_a_cote(
        [img, img_H1, img_H2],
        ['Original', 'H1 appliquée', 'H2 appliquée'],
        figsize=(20, 6)
    )

    print("\nRéchauffement terminé !")


if __name__ == '__main__':
    main()
