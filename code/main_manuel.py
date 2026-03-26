"""
Appariement manuel (45%) : Mosaïques sur les 3 séries de 1-PartieManuelle.
"""
import numpy as np
import os
import matplotlib.pyplot as plt

from utils import (charger_image, sauvegarder_image, charger_images_dossier,
                   charger_points, dessiner_correspondances, sauvegarder_figure,
                   afficher_image)
from homographie import calculerHomographie
from transformation import appliqueTransformation
from mosaique import creer_mosaique_ponderee, chainer_homographies
from selection_points import selectionner_et_sauvegarder

# ============================================================
# Configuration des chemins
# ============================================================
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
RAPPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'rapport', 'images', 'manuel')
POINTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'points_manuels')


def traiter_serie1():
    """Serie1 : 3 images avec points de correspondance fournis.

    Fichiers de points fournis :
    - pts1_12.txt : points dans l'image 1 pour la paire (1, 2)
    - pts2_12.txt : points dans l'image 2 pour la paire (1, 2)
    - pts2_32.txt : points dans l'image 2 pour la paire (3, 2)
    - pts3_32.txt : points dans l'image 3 pour la paire (3, 2)

    L'image de référence est l'image 2 (milieu).
    """
    print("\n" + "=" * 60)
    print("SERIE 1 : Appariement avec points fournis")
    print("=" * 60)

    serie_dir = os.path.join(BASE_DIR, '1-PartieManuelle', 'Serie1')
    pts_dir = os.path.join(serie_dir, 'pts_serie1')
    save_dir = os.path.join(RAPPORT_DIR, 'serie1')
    os.makedirs(save_dir, exist_ok=True)

    # Charger les images (triées : IMG_2415, IMG_2416, IMG_2417)
    imgs_data = charger_images_dossier(serie_dir)
    noms = [d[0] for d in imgs_data]
    images = [d[1] for d in imgs_data]
    print(f"Images chargées : {noms}")

    # Charger les points de correspondance fournis
    # Paire 1-2 : image 0 (IMG_2415) <-> image 1 (IMG_2416)
    pts1_12 = charger_points(os.path.join(pts_dir, 'pts1_12.txt'))
    pts2_12 = charger_points(os.path.join(pts_dir, 'pts2_12.txt'))
    # Paire 3-2 : image 2 (IMG_2417) <-> image 1 (IMG_2416)
    pts3_32 = charger_points(os.path.join(pts_dir, 'pts3_32.txt'))
    pts2_32 = charger_points(os.path.join(pts_dir, 'pts2_32.txt'))

    print(f"Points paire 1-2 : {len(pts1_12)} correspondances")
    print(f"Points paire 3-2 : {len(pts3_32)} correspondances")

    # Visualiser les correspondances
    fig1 = dessiner_correspondances(images[0], images[1], pts1_12, pts2_12,
                                     "Correspondances images 1-2")
    sauvegarder_figure(fig1, os.path.join(save_dir, 'correspondances_12.jpg'))

    fig2 = dessiner_correspondances(images[2], images[1], pts3_32, pts2_32,
                                     "Correspondances images 3-2")
    sauvegarder_figure(fig2, os.path.join(save_dir, 'correspondances_32.jpg'))

    # Calculer les homographies
    # H_02 : transforme image 0 -> image 1 (référence)
    H_02 = calculerHomographie(pts1_12, pts2_12)
    print(f"\nHomographie image 0 -> image 1 :\n{H_02}")

    # H_22 : transforme image 2 -> image 1 (référence)
    H_22 = calculerHomographie(pts3_32, pts2_32)
    print(f"\nHomographie image 2 -> image 1 :\n{H_22}")

    # Image de référence = image 1 (milieu)
    idx_ref = 1
    homographies = {0: H_02, 2: H_22}

    # Créer la mosaïque
    print("\nCréation de la mosaïque...")
    mosaique = creer_mosaique_ponderee(images, homographies, idx_ref)

    sauvegarder_image(mosaique, os.path.join(save_dir, 'mosaique_serie1.jpg'))
    afficher_image(mosaique, "Mosaïque Serie 1 - Manuel")

    return mosaique


def traiter_serie_manuelle(serie_num, dossier_images, noms_images=None,
                            n_points=8, idx_ref=None):
    """Traite une série d'images avec sélection manuelle de points.

    Paramètres
    ----------
    serie_num : int
        Numéro de la série (2 ou 3).
    dossier_images : str
        Chemin du dossier contenant les images.
    n_points : int
        Nombre de points de correspondance à sélectionner par paire.
    idx_ref : int or None
        Index de l'image de référence. Si None, utilise le milieu.
    """
    print(f"\n{'=' * 60}")
    print(f"SERIE {serie_num} : Appariement manuel")
    print("=" * 60)

    save_dir = os.path.join(RAPPORT_DIR, f'serie{serie_num}')
    os.makedirs(save_dir, exist_ok=True)
    pts_save_dir = os.path.join(POINTS_DIR, f'serie{serie_num}')
    os.makedirs(pts_save_dir, exist_ok=True)

    # Charger les images
    imgs_data = charger_images_dossier(dossier_images)
    noms = [d[0] for d in imgs_data]
    images = [d[1] for d in imgs_data]
    n_images = len(images)
    print(f"Images chargées ({n_images}) : {noms}")

    if idx_ref is None:
        idx_ref = n_images // 2
    print(f"Image de référence : {noms[idx_ref]} (index {idx_ref})")

    # Sélectionner les correspondances pour chaque paire consécutive
    H_paires = {}
    for i in range(n_images - 1):
        print(f"\n--- Paire images {i}-{i + 1} ({noms[i]} <-> {noms[i + 1]}) ---")

        chemin_pts_i = os.path.join(pts_save_dir, f'pts{i}_{i}{i + 1}.txt')
        chemin_pts_j = os.path.join(pts_save_dir, f'pts{i + 1}_{i}{i + 1}.txt')

        pts_i, pts_j = selectionner_et_sauvegarder(
            images[i], images[i + 1],
            chemin_pts_i, chemin_pts_j,
            n_points=n_points
        )

        # Visualiser
        fig = dessiner_correspondances(images[i], images[i + 1], pts_i, pts_j,
                                        f"Correspondances {noms[i]} - {noms[i + 1]}")
        sauvegarder_figure(fig, os.path.join(save_dir, f'correspondances_{i}_{i + 1}.jpg'))

        # Homographie : image i -> image i+1
        H = calculerHomographie(pts_i, pts_j)
        H_paires[(i, i + 1)] = H
        print(f"Homographie {i} -> {i + 1} calculée")

    # Chaîner les homographies vers l'image de référence
    homographies = chainer_homographies(H_paires, idx_ref, n_images)

    # Créer la mosaïque
    print(f"\nCréation de la mosaïque (ref = {noms[idx_ref]})...")
    mosaique = creer_mosaique_ponderee(images, homographies, idx_ref)

    sauvegarder_image(mosaique, os.path.join(save_dir, f'mosaique_serie{serie_num}.jpg'))
    afficher_image(mosaique, f"Mosaïque Serie {serie_num} - Manuel")

    return mosaique


def main():
    # ----- Serie 1 : points fournis -----
    mosaique1 = traiter_serie1()

    # ----- Serie 2 : sélection manuelle -----
    serie2_dir = os.path.join(BASE_DIR, '1-PartieManuelle', 'Serie2')
    mosaique2 = traiter_serie_manuelle(
        serie_num=2,
        dossier_images=serie2_dir,
        n_points=8,
        idx_ref=0  # Serie2 : 2 images, ref = première image
    )

    # ----- Serie 3 : sélection manuelle -----
    serie3_dir = os.path.join(BASE_DIR, '1-PartieManuelle', 'Serie3')
    mosaique3 = traiter_serie_manuelle(
        serie_num=3,
        dossier_images=serie3_dir,
        n_points=8,
        idx_ref=1  # Serie3 : 3 images, ref = milieu
    )

    print("\n" + "=" * 60)
    print("Appariement manuel terminé !")
    print("=" * 60)


if __name__ == '__main__':
    main()
