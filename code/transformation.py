import numpy as np
from skimage.transform import warp, ProjectiveTransform


def appliqueTransformation(img, H):
    """Applique une homographie H à une image img.

    Gère les cas où les coordonnées transformées sont négatives ou
    dépassent les dimensions de l'image originale en ajustant la taille
    de l'image de sortie et en appliquant une translation.

    Paramètres
    ----------
    img : ndarray
        Image source (H x W x C) ou (H x W) en float [0,1].
    H : ndarray (3, 3)
        Matrice d'homographie (transformation projective).

    Retourne
    --------
    imgTrans : ndarray
        Image transformée.
    offset : ndarray (2,)
        Décalage (offset_x, offset_y) appliqué pour gérer les coordonnées négatives.
        Utile pour positionner l'image dans une mosaïque.
    """
    h, w = img.shape[:2]

    # Coins de l'image source : (x, y) en coordonnées homogènes
    coins = np.array([
        [0, 0, 1],
        [w - 1, 0, 1],
        [w - 1, h - 1, 1],
        [0, h - 1, 1]
    ], dtype=np.float64).T  # (3, 4)

    # Transformer les coins avec H (forward)
    coins_transformes = H @ coins  # (3, 4)
    coins_transformes /= coins_transformes[2, :]  # normaliser

    x_transformes = coins_transformes[0, :]
    y_transformes = coins_transformes[1, :]

    # Bornes de l'image transformée
    min_x = np.floor(x_transformes.min()).astype(int)
    max_x = np.ceil(x_transformes.max()).astype(int)
    min_y = np.floor(y_transformes.min()).astype(int)
    max_y = np.ceil(y_transformes.max()).astype(int)

    # Décalage pour ramener les coordonnées dans le positif
    offset_x = -min_x if min_x < 0 else 0
    offset_y = -min_y if min_y < 0 else 0

    # Matrice de translation pour compenser l'offset
    T = np.array([
        [1, 0, offset_x],
        [0, 1, offset_y],
        [0, 0, 1]
    ], dtype=np.float64)

    # Homographie ajustée avec la translation
    H_ajuste = T @ H

    # Dimensions de l'image de sortie
    out_w = max_x - min_x + 1
    out_h = max_y - min_y + 1

    # Créer la transformation pour skimage
    # warp attend la transformation inverse (output -> input)
    # ProjectiveTransform.inverse est appelé automatiquement par warp
    tform = ProjectiveTransform(matrix=H_ajuste)

    # Appliquer la déformation
    if img.ndim == 3:
        imgTrans = warp(img, tform.inverse, output_shape=(out_h, out_w),
                        mode='constant', cval=0)
    else:
        imgTrans = warp(img, tform.inverse, output_shape=(out_h, out_w),
                        mode='constant', cval=0)

    offset = np.array([offset_x, offset_y])
    return imgTrans, offset
