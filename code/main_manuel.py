"""
Appariement manuel (45%) : Mosaïques sur les 3 séries de 1-PartieManuelle.

Workflow :
  1. Exécuter selection_points.py AVANT ce script pour les séries 2 et 3
     (sélectionner les points de correspondance et les sauvegarder).
  2. Exécuter ce script pour calculer les homographies et créer les mosaïques.

Pour la Serie1, les points sont fournis dans les données d'entrée.
Pour les Series 2 et 3, les points doivent avoir été sauvegardés par
selection_points.py dans data/dataOutput/points_manuels/serie2/ et serie3/.
"""
import numpy as np
import os
from pathlib import Path

from chemins import (MANUEL_SERIE1_DIR, MANUEL_SERIE1_PTS, MANUEL_SERIE2_DIR,
                     MANUEL_SERIE3_DIR, OUT_MANUEL, OUT_POINTS_MANUELS)
from utils import (charger_image, sauvegarder_image, charger_images_dossier,
                   charger_points, dessiner_correspondances, sauvegarder_figure,
                   afficher_image)
from homographie import calculerHomographie
from mosaique import creer_mosaique_ponderee, chainer_homographies


def traiter_serie1():
    """Serie1 : 3 images avec points de correspondance fournis.

    Points fournis :
    - pts1_12.txt / pts2_12.txt : paire image 0 <-> image 1
    - pts3_32.txt / pts2_32.txt : paire image 2 <-> image 1

    Image de référence : image 1 (milieu).
    """
    print("\n" + "=" * 60)
    print("SERIE 1 : Appariement avec points fournis")
    print("=" * 60)

    save_dir = os.path.join(OUT_MANUEL, 'serie1')
    os.makedirs(save_dir, exist_ok=True)

    # Charger les images (triées : IMG_2415, IMG_2416, IMG_2417)
    imgs_data = charger_images_dossier(MANUEL_SERIE1_DIR)
    noms = [d[0] for d in imgs_data]
    images = [d[1] for d in imgs_data]
    print(f"Images chargées : {noms}")

    # Charger les points de correspondance fournis
    pts1_12 = charger_points(os.path.join(MANUEL_SERIE1_PTS, 'pts1_12.txt'))
    pts2_12 = charger_points(os.path.join(MANUEL_SERIE1_PTS, 'pts2_12.txt'))
    pts3_32 = charger_points(os.path.join(MANUEL_SERIE1_PTS, 'pts3_32.txt'))
    pts2_32 = charger_points(os.path.join(MANUEL_SERIE1_PTS, 'pts2_32.txt'))

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
    H_02 = calculerHomographie(pts1_12, pts2_12)
    print(f"\nHomographie image 0 -> image 1 :\n{H_02}")

    H_22 = calculerHomographie(pts3_32, pts2_32)
    print(f"\nHomographie image 2 -> image 1 :\n{H_22}")

    idx_ref = 1
    homographies = {0: H_02, 2: H_22}

    # Créer la mosaïque
    print("\nCréation de la mosaïque...")
    mosaique = creer_mosaique_ponderee(images, homographies, idx_ref)

    sauvegarder_image(mosaique, os.path.join(save_dir, 'mosaique_serie1.jpg'))
    afficher_image(mosaique, "Mosaïque Serie 1 - Manuel")

    return mosaique


def trouver_fichiers_points(pts_dir, name_i, name_j):
    """Cherche les fichiers de points pour une paire d'images.

    Cherche dans pts_dir les fichiers créés par selection_points.py
    avec la convention : pts_{nameA}_vers_{nameB}.txt

    Retourne
    --------
    chemin_pts_i, chemin_pts_j : str ou None
    """
    # Convention de selection_points.py :
    #   pts_{name1}_vers_{name2}.txt  (points dans image 1)
    #   pts_{name2}_vers_{name1}.txt  (points dans image 2)
    f_i = os.path.join(pts_dir, f"pts_{name_i}_vers_{name_j}.txt")
    f_j = os.path.join(pts_dir, f"pts_{name_j}_vers_{name_i}.txt")

    if os.path.exists(f_i) and os.path.exists(f_j):
        return f_i, f_j

    # Essayer aussi l'inverse (au cas où l'utilisateur a sélectionné dans l'autre sens)
    f_i_inv = os.path.join(pts_dir, f"pts_{name_j}_vers_{name_i}.txt")
    f_j_inv = os.path.join(pts_dir, f"pts_{name_i}_vers_{name_j}.txt")
    # Note : c'est le même résultat, mais on vérifie quand même
    if os.path.exists(f_i_inv) and os.path.exists(f_j_inv):
        # Dans ce cas les rôles sont inversés
        return f_j_inv, f_i_inv

    return None, None


def traiter_serie_manuelle(serie_num, dossier_images, idx_ref=None):
    """Traite une série d'images en chargeant les points sauvegardés.

    Les points doivent avoir été créés au préalable avec selection_points.py
    et sauvegardés dans data/dataOutput/points_manuels/serie{N}/.
    """
    print(f"\n{'=' * 60}")
    print(f"SERIE {serie_num} : Appariement manuel")
    print("=" * 60)

    save_dir = os.path.join(OUT_MANUEL, f'serie{serie_num}')
    os.makedirs(save_dir, exist_ok=True)
    pts_dir = os.path.join(OUT_POINTS_MANUELS, f'serie{serie_num}')

    # Charger les images
    imgs_data = charger_images_dossier(dossier_images)
    noms = [d[0] for d in imgs_data]
    noms_sans_ext = [Path(n).stem for n in noms]
    images = [d[1] for d in imgs_data]
    n_images = len(images)
    print(f"Images chargées ({n_images}) : {noms}")

    if idx_ref is None:
        idx_ref = n_images // 2
    print(f"Image de référence : {noms[idx_ref]} (index {idx_ref})")

    # Vérifier que les fichiers de points existent
    if not os.path.exists(pts_dir):
        print(f"\n  ERREUR : Le dossier de points n'existe pas : {pts_dir}")
        print(f"  Exécutez d'abord selection_points.py avec le nom de série 'serie{serie_num}'")
        print(f"  pour sélectionner les points sur les paires d'images consécutives.")
        return None

    # Charger les points et calculer les homographies pour chaque paire
    H_paires = {}
    for i in range(n_images - 1):
        name_i = noms_sans_ext[i]
        name_j = noms_sans_ext[i + 1]
        print(f"\n--- Paire {i}-{i + 1} ({noms[i]} <-> {noms[i + 1]}) ---")

        f_pts_i, f_pts_j = trouver_fichiers_points(pts_dir, name_i, name_j)

        if f_pts_i is None:
            print(f"  ERREUR : Fichiers de points introuvables pour {name_i} <-> {name_j}")
            print(f"  Fichiers attendus dans {pts_dir} :")
            print(f"    pts_{name_i}_vers_{name_j}.txt")
            print(f"    pts_{name_j}_vers_{name_i}.txt")
            print(f"  Exécutez selection_points.py pour cette paire.")
            return None

        pts_i = charger_points(f_pts_i)
        pts_j = charger_points(f_pts_j)
        print(f"  Points chargés : {len(pts_i)} correspondances")
        print(f"    {f_pts_i}")
        print(f"    {f_pts_j}")

        # Visualiser les correspondances
        fig = dessiner_correspondances(images[i], images[i + 1], pts_i, pts_j,
                                        f"Correspondances {noms[i]} - {noms[i + 1]}")
        sauvegarder_figure(fig, os.path.join(save_dir, f'correspondances_{i}_{i + 1}.jpg'))

        # Homographie : image i -> image i+1
        H = calculerHomographie(pts_i, pts_j)
        H_paires[(i, i + 1)] = H
        print(f"  Homographie {i} -> {i + 1} calculée")

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

    # ----- Serie 2 : points sauvegardés par selection_points.py -----
    mosaique2 = traiter_serie_manuelle(
        serie_num=2,
        dossier_images=MANUEL_SERIE2_DIR,
        idx_ref=0  # 2 images, ref = première
    )

    # ----- Serie 3 : points sauvegardés par selection_points.py -----
    mosaique3 = traiter_serie_manuelle(
        serie_num=3,
        dossier_images=MANUEL_SERIE3_DIR,
        idx_ref=1  # 3 images, ref = milieu
    )

    print("\n" + "=" * 60)
    print("Appariement manuel terminé !")
    print("=" * 60)


if __name__ == '__main__':
    main()
