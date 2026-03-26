import numpy as np
from skimage.transform import warp, ProjectiveTransform


def calculer_boite_englobante(img_shape, H):
    """Calcule la boîte englobante de l'image après transformation par H."""
    h, w = img_shape[:2]
    coins = np.array([
        [0, 0, 1],
        [w - 1, 0, 1],
        [w - 1, h - 1, 1],
        [0, h - 1, 1]
    ], dtype=np.float64).T

    coins_t = H @ coins
    coins_t /= coins_t[2, :]

    min_x = int(np.floor(coins_t[0].min()))
    max_x = int(np.ceil(coins_t[0].max()))
    min_y = int(np.floor(coins_t[1].min()))
    max_y = int(np.ceil(coins_t[1].max()))

    return min_x, min_y, max_x, max_y


def creer_mosaique(images, homographies, idx_ref):
    """Crée une mosaïque à partir de plusieurs images et homographies.

    Paramètres
    ----------
    images : list of ndarray
        Liste d'images (en float [0,1]).
    homographies : dict
        {idx_img: H} où H transforme l'image idx_img vers le repère de référence.
    idx_ref : int
        Index de l'image de référence.

    Retourne
    --------
    mosaique : ndarray
    """
    global_min_x, global_min_y = 0, 0
    global_max_x, global_max_y = 0, 0

    for i, img in enumerate(images):
        H = np.eye(3) if i == idx_ref else homographies[i]
        bmin_x, bmin_y, bmax_x, bmax_y = calculer_boite_englobante(img.shape, H)
        global_min_x = min(global_min_x, bmin_x)
        global_min_y = min(global_min_y, bmin_y)
        global_max_x = max(global_max_x, bmax_x)
        global_max_y = max(global_max_y, bmax_y)

    offset_x = -global_min_x
    offset_y = -global_min_y
    T_global = np.array([
        [1, 0, offset_x],
        [0, 1, offset_y],
        [0, 0, 1]
    ], dtype=np.float64)

    out_w = global_max_x - global_min_x + 1
    out_h = global_max_y - global_min_y + 1

    # Normaliser : RGBA -> RGB
    images = [img[:, :, :3] if (img.ndim == 3 and img.shape[2] == 4) else img for img in images]

    n_channels = images[0].shape[2] if images[0].ndim == 3 else 1
    mosaique = np.zeros((out_h, out_w, n_channels), dtype=np.float64)
    poids = np.zeros((out_h, out_w), dtype=np.float64)

    for i, img in enumerate(images):
        H = np.eye(3) if i == idx_ref else homographies[i]
        H_ajuste = T_global @ H
        tform = ProjectiveTransform(matrix=H_ajuste)

        if img.ndim == 2:
            img_3d = img[:, :, np.newaxis]
        else:
            img_3d = img

        img_warp = warp(img_3d, tform.inverse, output_shape=(out_h, out_w),
                        mode='constant', cval=0)

        masque = np.any(img_warp > 0, axis=2).astype(np.float64) if img_warp.ndim == 3 else (img_warp > 0).astype(np.float64)

        mosaique += img_warp * masque[:, :, np.newaxis]
        poids += masque

    poids_safe = np.maximum(poids, 1)
    mosaique = mosaique / poids_safe[:, :, np.newaxis]

    if n_channels == 1:
        mosaique = mosaique[:, :, 0]

    return np.clip(mosaique, 0, 1)


def creer_mosaique_ponderee(images, homographies, idx_ref):
    """Crée une mosaïque avec mélange pondéré par la distance au centre."""
    global_min_x, global_min_y = 0, 0
    global_max_x, global_max_y = 0, 0

    for i, img in enumerate(images):
        H = np.eye(3) if i == idx_ref else homographies[i]
        bmin_x, bmin_y, bmax_x, bmax_y = calculer_boite_englobante(img.shape, H)
        global_min_x = min(global_min_x, bmin_x)
        global_min_y = min(global_min_y, bmin_y)
        global_max_x = max(global_max_x, bmax_x)
        global_max_y = max(global_max_y, bmax_y)

    offset_x = -global_min_x
    offset_y = -global_min_y
    T_global = np.array([
        [1, 0, offset_x],
        [0, 1, offset_y],
        [0, 0, 1]
    ], dtype=np.float64)

    out_w = global_max_x - global_min_x + 1
    out_h = global_max_y - global_min_y + 1

    # Normaliser : RGBA -> RGB
    images = [img[:, :, :3] if (img.ndim == 3 and img.shape[2] == 4) else img for img in images]

    n_channels = images[0].shape[2] if images[0].ndim == 3 else 1
    mosaique = np.zeros((out_h, out_w, n_channels), dtype=np.float64)
    poids_total = np.zeros((out_h, out_w), dtype=np.float64)

    for i, img in enumerate(images):
        H = np.eye(3) if i == idx_ref else homographies[i]
        H_ajuste = T_global @ H
        tform = ProjectiveTransform(matrix=H_ajuste)

        if img.ndim == 2:
            img_3d = img[:, :, np.newaxis]
        else:
            img_3d = img

        img_warp = warp(img_3d, tform.inverse, output_shape=(out_h, out_w),
                        mode='constant', cval=0)

        h_img, w_img = img.shape[:2]
        weight_map = _creer_carte_poids(h_img, w_img)

        weight_warp = warp(weight_map, tform.inverse, output_shape=(out_h, out_w),
                           mode='constant', cval=0)

        mosaique += img_warp * weight_warp[:, :, np.newaxis]
        poids_total += weight_warp

    poids_safe = np.maximum(poids_total, 1e-10)
    mosaique = mosaique / poids_safe[:, :, np.newaxis]

    if n_channels == 1:
        mosaique = mosaique[:, :, 0]

    return np.clip(mosaique, 0, 1)


def _creer_carte_poids(h, w):
    """Carte de poids linéaire : 1 au centre, ~0 aux bords."""
    x = np.linspace(0, 1, w)
    y = np.linspace(0, 1, h)
    wx = np.minimum(x, 1 - x) * 2
    wy = np.minimum(y, 1 - y) * 2
    weight = np.outer(wy, wx)
    weight = np.clip(weight, 0.01, 1.0)
    return weight


def chainer_homographies(H_paires, idx_ref, n_images):
    """Chaîne les homographies par paires pour obtenir H_i -> ref.

    Paramètres
    ----------
    H_paires : dict
        {(i, j): H_ij} homographies entre paires consécutives.
    idx_ref : int
        Index de l'image de référence.
    n_images : int
        Nombre total d'images.

    Retourne
    --------
    homographies : dict {i: H_i_to_ref}
    """
    homographies = {}

    for i in range(n_images):
        if i == idx_ref:
            continue

        H_cumul = np.eye(3)

        if i < idx_ref:
            for k in range(i, idx_ref):
                if (k, k + 1) in H_paires:
                    H_cumul = H_paires[(k, k + 1)] @ H_cumul
                else:
                    H_cumul = np.linalg.inv(H_paires[(k + 1, k)]) @ H_cumul
        else:
            for k in range(i, idx_ref, -1):
                if (k, k - 1) in H_paires:
                    H_cumul = H_paires[(k, k - 1)] @ H_cumul
                else:
                    H_cumul = np.linalg.inv(H_paires[(k - 1, k)]) @ H_cumul

        homographies[i] = H_cumul

    return homographies
