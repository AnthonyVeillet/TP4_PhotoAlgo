"""
PERSO images (20%) — Version optimisée avec multiprocessing.

Pourquoi le CPU n'était qu'à 30% avant :
  ProcessPoolExecutor doit sérialiser (pickle) les arguments envoyés aux workers.
  Une photo de téléphone (4000x3000x3 float64) = ~72 MB par image.
  Envoyer 2 images par paire = ~144 MB pickled, ce qui prend plus de temps que le SIFT.

Solution : passer des CHEMINS de fichiers aux workers. Chaque process charge ses
propres images depuis le disque (rapide sur SSD), évitant toute sérialisation.
"""
import numpy as np
import os
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from chemins import PERSO_DIR, OUT_PERSO_IMAGES
from utils import (charger_image, sauvegarder_image, charger_images_dossier,
                   sauvegarder_figure, img_to_rgb)
from appariement import appariement_automatique
from mosaique import creer_mosaique_ponderee, chainer_homographies


# =============================================================
# Workers — reçoivent des CHEMINS, pas des arrays
# =============================================================

def _worker_sift_pair(args):
    """Appariement SIFT+RANSAC d'une paire.
    Charge les images dans le process enfant pour éviter le pickle.
    Downscale avant SIFT pour réduire la RAM (~4x moins de mémoire)."""
    from skimage.transform import rescale

    i, j, path_ref, path_other = args

    img_ref = charger_image(path_ref)
    img_other = charger_image(path_other)

    # Downscale si images trop grandes (> 2000px de large)
    # SIFT n'a pas besoin de la pleine résolution pour trouver des correspondances
    max_dim = 2000
    h_ref, w_ref = img_ref.shape[:2]
    h_oth, w_oth = img_other.shape[:2]

    scale_ref = min(1.0, max_dim / max(h_ref, w_ref))
    scale_oth = min(1.0, max_dim / max(h_oth, w_oth))

    if scale_ref < 1.0:
        img_ref_sift = rescale(img_ref, scale_ref, channel_axis=2 if img_ref.ndim == 3 else None, anti_aliasing=True)
    else:
        img_ref_sift = img_ref
        scale_ref = 1.0

    if scale_oth < 1.0:
        img_other_sift = rescale(img_other, scale_oth, channel_axis=2 if img_other.ndim == 3 else None, anti_aliasing=True)
    else:
        img_other_sift = img_other
        scale_oth = 1.0

    H, pts_ref, pts_other, all_ref, all_other, inliers = appariement_automatique(
        img_ref_sift, img_other_sift
    )

    # Remettre les coordonnées à l'échelle originale
    if scale_ref < 1.0:
        pts_ref = pts_ref / scale_ref
        all_ref = all_ref / scale_ref
    if scale_oth < 1.0:
        pts_other = pts_other / scale_oth
        all_other = all_other / scale_oth

    # Recalculer H à l'échelle originale si downscale
    if scale_ref < 1.0 or scale_oth < 1.0:
        from skimage.transform import estimate_transform
        if len(pts_other) >= 4:
            tform = estimate_transform('projective', pts_other, pts_ref)
            H = tform.params

    n_inliers = int(inliers.sum())
    n_total = len(inliers)

    return (i, j), {
        'pts_ref': pts_ref,
        'pts_other': pts_other,
        'all_pts_ref': all_ref,
        'all_pts_other': all_other,
        'inliers': inliers,
        'H': H,
        'n_inliers': n_inliers,
        'n_total': n_total,
    }


def _save_appariement_fig(args):
    """Génère et sauvegarde une figure d'appariements en thread."""
    i, j, img_i, img_j, nom_i, nom_j, info, save_dir = args

    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    h1, w1 = img_i.shape[:2]
    h2, w2 = img_j.shape[:2]
    h_max = max(h1, h2)
    canvas = np.zeros((h_max, w1 + w2, 3))
    canvas[:h1, :w1] = img_to_rgb(img_i)
    canvas[:h2, w1:] = img_to_rgb(img_j)
    ax.imshow(canvas)

    inliers = info['inliers']
    pts_other = info['all_pts_other']
    pts_ref = info['all_pts_ref']

    for k in range(len(pts_other)):
        if inliers[k]:
            x1, y1 = pts_other[k]
            x2, y2 = pts_ref[k]
            ax.plot([x1, x2 + w1], [y1, y2], 'g-', linewidth=1)

    ax.set_title(f"Appariements {nom_i} - {nom_j} : {info['n_inliers']}/{info['n_total']} inliers")
    ax.axis('off')
    plt.tight_layout()
    sauvegarder_figure(fig, os.path.join(save_dir, f'appariements_{i}_{j}.jpg'))


# =============================================================
# Pipeline d'une scène
# =============================================================

def traiter_scene(scene_num, dossier_images, idx_ref=None):
    t0 = time.perf_counter()

    print(f"\n{'=' * 60}")
    print(f"SCÈNE {scene_num}")
    print("=" * 60)

    save_dir = os.path.join(OUT_PERSO_IMAGES, f'scene{scene_num}')
    os.makedirs(save_dir, exist_ok=True)

    # 1. Lister les fichiers (pas encore charger les images)
    extensions = ('.jpg', '.jpeg', '.png')
    fichiers = sorted([
        f for f in os.listdir(dossier_images)
        if os.path.splitext(f)[1].lower() in extensions
    ])
    n_images = len(fichiers)
    chemins = [os.path.join(dossier_images, f) for f in fichiers]
    print(f"  {n_images} images trouvées : {fichiers}")

    if idx_ref is None:
        idx_ref = n_images // 2
    print(f"  Référence : {fichiers[idx_ref]} (index {idx_ref})")

    # 2. SIFT + RANSAC en parallèle — on passe des CHEMINS, pas des images
    #    max_workers=2 pour ne pas saturer la RAM (SIFT utilise ~3-5 GB par process
    #    avec des photos de téléphone). Augmenter si vous avez 64+ GB de RAM.
    n_workers = min(n_images - 1, 2)
    print(f"\n  Appariement SIFT // sur {n_images - 1} paires ({n_workers} workers)...")
    t1 = time.perf_counter()

    pair_args = [
        (i, i + 1, chemins[i + 1], chemins[i])
        for i in range(n_images - 1)
    ]

    H_paires = {}
    info_paires = {}

    with ProcessPoolExecutor(max_workers=n_workers) as pool:
        for (i, j), info in pool.map(_worker_sift_pair, pair_args):
            H_paires[(i, j)] = info['H']
            info_paires[(i, j)] = info
            print(f"    Paire {i}↔{j} : {info['n_inliers']}/{info['n_total']} inliers")

    print(f"  SIFT terminé en {time.perf_counter() - t1:.1f}s")

    # 3. Charger toutes les images (nécessaire pour mosaïque + figures)
    print(f"\n  Chargement des images...")
    images = [charger_image(c) for c in chemins]

    # 4. Sauvegarder originales + figures d'appariement (threads — I/O)
    def _save_original(idx):
        sauvegarder_image(images[idx], os.path.join(save_dir, f'img_{idx}_{fichiers[idx]}'))

    fig_args = [
        (i, j, images[i], images[j], fichiers[i], fichiers[j], info, save_dir)
        for (i, j), info in info_paires.items()
    ]

    with ThreadPoolExecutor() as pool:
        pool.map(_save_original, range(n_images))
        list(pool.map(_save_appariement_fig, fig_args))

    # 5. Chaîner les homographies + mosaïque
    homographies = chainer_homographies(H_paires, idx_ref, n_images)

    print(f"\n  Création de la mosaïque...")
    t2 = time.perf_counter()
    mosaique = creer_mosaique_ponderee(images, homographies, idx_ref)
    print(f"  Mosaïque créée en {time.perf_counter() - t2:.1f}s")

    sauvegarder_image(mosaique, os.path.join(save_dir, f'mosaique_scene{scene_num}.jpg'))

    total = time.perf_counter() - t0
    print(f"\n  Scène {scene_num} terminée en {total:.1f}s")
    return mosaique


# =============================================================
# Main
# =============================================================

def main():
    t_start = time.perf_counter()

    scene1_dir = os.path.join(PERSO_DIR, 'Scene1')
    scene2_dir = os.path.join(PERSO_DIR, 'Scene2')

    if not os.path.exists(scene1_dir):
        print(f"ERREUR : Le dossier {scene1_dir} n'existe pas.")
        return

    traiter_scene(1, scene1_dir)

    if os.path.exists(scene2_dir):
        traiter_scene(2, scene2_dir)

    print(f"\n{'=' * 60}")
    print(f"Tout terminé en {time.perf_counter() - t_start:.1f}s")
    print("=" * 60)


if __name__ == '__main__':
    main()