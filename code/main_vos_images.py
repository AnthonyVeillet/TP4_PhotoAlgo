import numpy as np
import os
import matplotlib.pyplot as plt

from chemins import PERSO_DIR, OUT_PERSO_IMAGES
from utils import (charger_image, sauvegarder_image, charger_images_dossier,
                   dessiner_correspondances, sauvegarder_figure, afficher_image,
                   img_to_rgb)
from appariement import appariement_automatique_paires
from mosaique import creer_mosaique_ponderee, chainer_homographies


def traiter_scene(scene_num, dossier_images, idx_ref=None):
    # Traite une scène personnelle avec appariement automatique
    print(f"\n{'=' * 60}")
    print(f"SCÈNE {scene_num} : Images")
    print("=" * 60)

    save_dir = os.path.join(OUT_PERSO_IMAGES, f'scene{scene_num}')
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

    # Sauvegarder les images individuelles dans l'output
    for i, (nom, img) in enumerate(zip(noms, images)):
        sauvegarder_image(img, os.path.join(save_dir, f'img_{i}_{nom}'))

    # Appariement automatique
    H_paires, info_paires = appariement_automatique_paires(images)

    # Visualiser les appariements
    for (i, j), info in info_paires.items():
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        h1, w1 = images[i].shape[:2]
        h2, w2 = images[j].shape[:2]
        h_max = max(h1, h2)
        canvas = np.zeros((h_max, w1 + w2, 3))
        canvas[:h1, :w1] = img_to_rgb(images[i])
        canvas[:h2, w1:] = img_to_rgb(images[j])
        ax.imshow(canvas)

        inliers = info['inliers']
        all_pts_other = info['all_pts_other']
        all_pts_ref = info['all_pts_ref']

        for k in range(len(all_pts_other)):
            if inliers[k]:
                x1, y1 = all_pts_other[k]
                x2, y2 = all_pts_ref[k]
                ax.plot([x1, x2 + w1], [y1, y2], 'g-', linewidth=1)

        n_inliers = inliers.sum()
        ax.set_title(f"Appariements {noms[i]} - {noms[j]} : {n_inliers} inliers")
        ax.axis('off')
        plt.tight_layout()
        sauvegarder_figure(fig, os.path.join(save_dir, f'appariements_{i}_{j}.jpg'))

    # Chainer les homographies
    homographies = chainer_homographies(H_paires, idx_ref, n_images)

    # Créer la mosaïque
    print(f"\nCréation de la mosaïque...")
    mosaique = creer_mosaique_ponderee(images, homographies, idx_ref)

    sauvegarder_image(mosaique, os.path.join(save_dir, f'mosaique_scene{scene_num}.jpg'))
    afficher_image(mosaique, f"Mosaïque Scène {scene_num}")

    return mosaique


def main():

    scene1_dir = os.path.join(PERSO_DIR, 'Scene1')
    scene2_dir = os.path.join(PERSO_DIR, 'Scene2')

    if not os.path.exists(scene1_dir):
        print(f"ERREUR : Le dossier {scene1_dir} n'existe pas.")
        print("Créez vos sous-dossiers Scene1/ et Scene2/ dans :")
        print(f"  {PERSO_DIR}")
        return

    mosaique1 = traiter_scene(1, scene1_dir)

    if os.path.exists(scene2_dir):
        mosaique2 = traiter_scene(2, scene2_dir)

    print("\nTraitement d'images terminé !")


if __name__ == '__main__':
    main()
