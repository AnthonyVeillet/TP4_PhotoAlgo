import numpy as np
from skimage.transform import estimate_transform


def calculerHomographie(im1_pts, im2_pts):
    """Calcule l'homographie H telle que im2_pts ~ H @ im1_pts.

    Utilise skimage.transform.estimate_transform avec le modèle 'projective'.
    Les points sont pré-normalisés (Hartley) avant l'estimation.

    Paramètres
    ----------
    im1_pts : ndarray (n, 2)
        Coordonnées (x, y) des points dans l'image source.
    im2_pts : ndarray (n, 2)
        Coordonnées (x, y) des points correspondants dans l'image destination.

    Retourne
    --------
    H : ndarray (3, 3)
        Matrice d'homographie.
    """
    assert len(im1_pts) >= 4, "Il faut au minimum 4 paires de correspondances."
    assert len(im1_pts) == len(im2_pts), "Le nombre de points doit être identique."

    # Estimation via skimage (gère la normalisation en interne pour 'projective')
    tform = estimate_transform('projective', im1_pts, im2_pts)
    H = tform.params

    return H


def normaliser_points(pts):
    """Normalise les points selon la méthode de Hartley.

    Soustrait la moyenne et divise par l'écart-type.

    Paramètres
    ----------
    pts : ndarray (n, 2)

    Retourne
    --------
    pts_norm : ndarray (n, 2)
        Points normalisés.
    T : ndarray (3, 3)
        Matrice de normalisation.
    """
    mean = pts.mean(axis=0)
    std = pts.std(axis=0)
    std[std < 1e-10] = 1  # éviter division par zéro

    T = np.array([
        [1.0 / std[0], 0, -mean[0] / std[0]],
        [0, 1.0 / std[1], -mean[1] / std[1]],
        [0, 0, 1]
    ])

    pts_h = np.hstack([pts, np.ones((len(pts), 1))])
    pts_norm_h = (T @ pts_h.T).T
    pts_norm = pts_norm_h[:, :2]

    return pts_norm, T


def calculerHomographie_manuelle(im1_pts, im2_pts):
    """Calcule l'homographie manuellement via le système Ah=0.

    Alternative à calculerHomographie utilisant skimage.
    Implémente la résolution via SVD avec normalisation de Hartley.

    Paramètres
    ----------
    im1_pts : ndarray (n, 2)
        Points source (x, y).
    im2_pts : ndarray (n, 2)
        Points destination (x, y).

    Retourne
    --------
    H : ndarray (3, 3)
        Matrice d'homographie.
    """
    assert len(im1_pts) >= 4

    # Normalisation de Hartley
    src_norm, T_src = normaliser_points(im1_pts)
    dst_norm, T_dst = normaliser_points(im2_pts)

    n = len(src_norm)
    A = np.zeros((2 * n, 9))

    for i in range(n):
        x, y = src_norm[i]
        xp, yp = dst_norm[i]

        A[2 * i] = [-x, -y, -1, 0, 0, 0, xp * x, xp * y, xp]
        A[2 * i + 1] = [0, 0, 0, -x, -y, -1, yp * x, yp * y, yp]

    # Résolution par SVD
    _, _, Vt = np.linalg.svd(A)
    h = Vt[-1, :]
    H_norm = h.reshape(3, 3)

    # Dé-normaliser
    H = np.linalg.inv(T_dst) @ H_norm @ T_src

    # Normaliser pour que H[2,2] = 1
    H /= H[2, 2]

    return H
