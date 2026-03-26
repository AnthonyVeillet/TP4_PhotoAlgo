"""
Appariement automatique (15%) : SIFT + RANSAC sur les 3 séries de 2-PartieAutomatique.
"""
import numpy as np
import os
import matplotlib.pyplot as plt

from chemins import AUTO_SERIE1_DIR, AUTO_SERIE2_DIR, AUTO_SERIE3_DIR, OUT_AUTOMATIQUE
from utils import (charger_image, sauvegarder_image, charger_images_dossier,
                   dessiner_correspondances, sauvegarder_figure, afficher_image)
from appariement import appariement_automatique_paires
from mosaique import creer_mosaique_ponderee, chainer_homographies


def traiter_serie_automatique(serie_num, dossier_images, idx_ref=None,
                                max_ratio=0.8, residual_threshold=2):
    """Traite une série d'images avec appariement automatique."""
    print(f"\n{'=' * 60}")
    print(f"SERIE {serie_num} : Appariement automatique (SIFT + RANSAC)")
    print("=" * 60)

    save_dir = os.path.join(OUT_AUTOMATIQUE, f'serie{serie_num}')
    os.makedirs(save_dir, exist_ok=True)

    # Charger les images
    imgs_data = charger_images_dossier(dossier_images)
    noms = [d[0] for d in imgs_data]
    images = [d[1] for d in imgs_data]
    n_images = len(images)
    print(f"Images chargées ({n_images}) : {noms}")

    if idx_ref is None:
        idx_ref = n_images // 2
    print(f"Image de référence : {noms[idx_ref]} (index {idx_ref})")

    # Appariement automatique entre paires consécutives
    H_paires, info_paires = appariement_automatique_paires(
        images,
        max_ratio=max_ratio,
        residual_threshold=residual_threshold
    )

    # Visualiser les appariements
    for (i, j), info in info_paires.items():
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        h1, w1 = images[i].shape[:2]
        h2, w2 = images[j].shape[:2]
        h_max = max(h1, h2)
        canvas = np.zeros((h_max, w1 + w2, 3))
        canvas[:h1, :w1] = images[i][:, :, :3]
        canvas[:h2, w1:] = images[j][:, :, :3]
        ax.imshow(canvas)

        inliers = info['inliers']
        all_pts_other = info['all_pts_other']
        all_pts_ref = info['all_pts_ref']

        # Outliers en rouge
        for k in range(len(all_pts_other)):
            if not inliers[k]:
                x1, y1 = all_pts_other[k]
                x2, y2 = all_pts_ref[k]
                ax.plot([x1, x2 + w1], [y1, y2], 'r-', alpha=0.3, linewidth=0.5)

        # Inliers en vert
        for k in range(len(all_pts_other)):
            if inliers[k]:
                x1, y1 = all_pts_other[k]
                x2, y2 = all_pts_ref[k]
                ax.plot([x1, x2 + w1], [y1, y2], 'g-', linewidth=1, markersize=3)
                ax.plot(x1, y1, 'go', markersize=3)
                ax.plot(x2 + w1, y2, 'go', markersize=3)

        n_inliers = inliers.sum()
        n_total = len(inliers)
        ax.set_title(f"Appariements {noms[i]} - {noms[j]} : {n_inliers}/{n_total} inliers")
        ax.axis('off')
        plt.tight_layout()
        sauvegarder_figure(fig, os.path.join(save_dir, f'appariements_{i}_{j}.jpg'))

    # Chaîner les homographies vers l'image de référence
    homographies = chainer_homographies(H_paires, idx_ref, n_images)

    # Créer la mosaïque
    print(f"\nCréation de la mosaïque (ref = {noms[idx_ref]})...")
    mosaique = creer_mosaique_ponderee(images, homographies, idx_ref)

    sauvegarder_image(mosaique, os.path.join(save_dir, f'mosaique_serie{serie_num}.jpg'))
    afficher_image(mosaique, f"Mosaïque Serie {serie_num} - Automatique")

    return mosaique


def main():
    # ----- Serie 1 : Golden Gate (6 images) -----
    mosaique1 = traiter_serie_automatique(
        serie_num=1,
        dossier_images=AUTO_SERIE1_DIR,
        idx_ref=None  # milieu automatique
    )

    # ----- Serie 2 : 4 images -----
    mosaique2 = traiter_serie_automatique(
        serie_num=2,
        dossier_images=AUTO_SERIE2_DIR,
        idx_ref=None
    )

    # ----- Serie 3 : 6 images -----
    mosaique3 = traiter_serie_automatique(
        serie_num=3,
        dossier_images=AUTO_SERIE3_DIR,
        idx_ref=None
    )

    print("\n" + "=" * 60)
    print("Appariement automatique terminé !")
    print("=" * 60)


if __name__ == '__main__':
    main()
