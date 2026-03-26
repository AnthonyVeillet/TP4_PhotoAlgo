import numpy as np
from skimage.color import rgb2gray
from skimage.feature import SIFT, match_descriptors
from skimage.measure import ransac
from skimage.transform import ProjectiveTransform


def appariement_automatique(img_ref, img_other, max_ratio=0.8, residual_threshold=2,
                             max_trials=1000):

    # Gérer les images déjà en niveaux de gris (2D) ou avec canal alpha (4 canaux)
    if img_ref.ndim == 2:
        gray1 = img_ref
    elif img_ref.shape[2] == 4:
        gray1 = rgb2gray(img_ref[:, :, :3])
    else:
        gray1 = rgb2gray(img_ref)

    if img_other.ndim == 2:
        gray2 = img_other
    elif img_other.shape[2] == 4:
        gray2 = rgb2gray(img_other[:, :, :3])
    else:
        gray2 = rgb2gray(img_other)

    sift1 = SIFT()
    sift1.detect_and_extract(gray1)
    kp1, desc1 = sift1.keypoints, sift1.descriptors

    sift2 = SIFT()
    sift2.detect_and_extract(gray2)
    kp2, desc2 = sift2.keypoints, sift2.descriptors

    matches = match_descriptors(
        desc1, desc2,
        cross_check=True,
        max_ratio=max_ratio
    )

    if len(matches) < 4:
        raise ValueError(
            f"Pas assez d'appariements ({len(matches)}) pour estimer l'homographie."
        )

    # (row, col) -> (x, y)
    all_pts_ref = kp1[matches[:, 0]][:, [1, 0]]
    all_pts_other = kp2[matches[:, 1]][:, [1, 0]]

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
            H_paires[(i, i + 1)] = H
            info_paires[(i, i + 1)] = {
                'pts_ref': pts_ref,
                'pts_other': pts_other,
                'all_pts_ref': all_ref,
                'all_pts_other': all_other,
                'inliers': inliers,
                'H': H
            }
        except (ValueError, RuntimeError) as e:
            print(f"  ERREUR: {e}")
            raise

    return H_paires, info_paires
