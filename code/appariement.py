import numpy as np
from skimage.color import rgb2gray
from skimage.feature import SIFT, match_descriptors
from skimage.measure import ransac
from skimage.transform import ProjectiveTransform


def appariement_automatique(img_ref, img_other, max_ratio=0.8, residual_threshold=2,
                             max_trials=1000):
    """Appariement automatique de deux images via SIFT + RANSAC.

    Paramètres
    ----------
    img_ref : ndarray
        Image de référence (RGB float).
    img_other : ndarray
        Autre image (RGB float).
    max_ratio : float
        Ratio max pour le test de Lowe dans match_descriptors.
    residual_threshold : float
        Seuil de résidu pour RANSAC.
    max_trials : int
        Nombre max d'itérations RANSAC.

    Retourne
    --------
    H : ndarray (3, 3)
        Homographie transformant img_other vers img_ref.
    pts_ref : ndarray (n, 2)
        Points inliers dans img_ref (x, y).
    pts_other : ndarray (n, 2)
        Points inliers dans img_other (x, y).
    all_pts_ref : ndarray (m, 2)
        Tous les points appariés dans img_ref.
    all_pts_other : ndarray (m, 2)
        Tous les points appariés dans img_other.
    inliers : ndarray (m,) bool
        Masque des inliers.
    """
    gray1 = rgb2gray(img_ref)
    gray2 = rgb2gray(img_other)

    # Détection et extraction SIFT
    sift1 = SIFT()
    sift1.detect_and_extract(gray1)
    kp1, desc1 = sift1.keypoints, sift1.descriptors

    sift2 = SIFT()
    sift2.detect_and_extract(gray2)
    kp2, desc2 = sift2.keypoints, sift2.descriptors

    # Appariement des descripteurs
    matches = match_descriptors(
        desc1, desc2,
        cross_check=True,
        max_ratio=max_ratio
    )

    if len(matches) < 4:
        raise ValueError(
            f"Pas assez d'appariements ({len(matches)}) pour estimer l'homographie. "
            "Essayez d'ajuster max_ratio ou vérifiez que les images se chevauchent."
        )

    # Convertir de (row, col) = (y, x) à (x, y)
    all_pts_ref = kp1[matches[:, 0]][:, [1, 0]]
    all_pts_other = kp2[matches[:, 1]][:, [1, 0]]

    # RANSAC pour estimation robuste
    model_robust, inliers = ransac(
        (all_pts_other, all_pts_ref),
        ProjectiveTransform,
        min_samples=4,
        residual_threshold=residual_threshold,
        max_trials=max_trials
    )

    if model_robust is None:
        raise RuntimeError("RANSAC a échoué à estimer l'homographie.")

    H = model_robust.params

    pts_ref = all_pts_ref[inliers]
    pts_other = all_pts_other[inliers]

    print(f"  Appariements : {len(matches)} total, {inliers.sum()} inliers")

    return H, pts_ref, pts_other, all_pts_ref, all_pts_other, inliers


def appariement_automatique_paires(images, max_ratio=0.8, residual_threshold=2,
                                     max_trials=1000):
    """Apparie automatiquement des images consécutives.

    Paramètres
    ----------
    images : list of ndarray
        Liste d'images (RGB float).

    Retourne
    --------
    H_paires : dict
        {(i, i+1): H} homographies entre paires consécutives.
        H transforme l'image i vers l'image i+1.
    info_paires : dict
        Infos détaillées pour chaque paire (points, inliers, etc.).
    """
    n = len(images)
    H_paires = {}
    info_paires = {}

    for i in range(n - 1):
        print(f"Appariement images {i} - {i + 1}...")
        try:
            H, pts_ref, pts_other, all_ref, all_other, inliers = appariement_automatique(
                images[i + 1], images[i],
                max_ratio=max_ratio,
                residual_threshold=residual_threshold,
                max_trials=max_trials
            )
            # H transforme images[i] vers images[i+1]
            H_paires[(i, i + 1)] = H
            info_paires[(i, i + 1)] = {
                'pts_ref': pts_ref,       # dans image i+1
                'pts_other': pts_other,   # dans image i
                'all_pts_ref': all_ref,
                'all_pts_other': all_other,
                'inliers': inliers,
                'H': H
            }
        except (ValueError, RuntimeError) as e:
            print(f"  ERREUR: {e}")
            raise

    return H_paires, info_paires
