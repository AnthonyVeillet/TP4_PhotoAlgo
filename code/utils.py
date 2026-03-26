import numpy as np
from skimage import io, img_as_float, img_as_ubyte
import os
import matplotlib.pyplot as plt


def charger_image(chemin):
    """Charge une image et la retourne en float64 [0, 1]."""
    img = io.imread(chemin)
    img = img_as_float(img)
    return img


def sauvegarder_image(img, chemin, qualite=90):
    """Sauvegarde une image (float [0,1] ou uint8) en JPG."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    img_clip = np.clip(img, 0, 1)
    img_uint8 = img_as_ubyte(img_clip)
    io.imsave(chemin, img_uint8, quality=qualite)
    print(f"Image sauvegardée : {chemin}")


def afficher_image(img, titre="", cmap=None):
    """Affiche une image avec matplotlib."""
    plt.figure(figsize=(12, 8))
    if img.ndim == 2:
        plt.imshow(img, cmap=cmap or 'gray')
    else:
        plt.imshow(img)
    plt.title(titre)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def afficher_images_cote_a_cote(images, titres=None, figsize=(18, 6)):
    """Affiche plusieurs images côte à côte."""
    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=figsize)
    if n == 1:
        axes = [axes]
    for i, img in enumerate(images):
        if img.ndim == 2:
            axes[i].imshow(img, cmap='gray')
        else:
            axes[i].imshow(img)
        if titres:
            axes[i].set_title(titres[i])
        axes[i].axis('off')
    plt.tight_layout()
    plt.show()


def charger_points(chemin):
    """Charge des points de correspondance depuis un fichier texte.
    Format attendu : chaque ligne contient x,y séparés par une virgule.
    Retourne un array numpy (n, 2).
    """
    pts = np.loadtxt(chemin, delimiter=",", dtype=np.float64)
    return pts


def charger_images_dossier(dossier, extensions=('.jpg', '.jpeg', '.png')):
    """Charge toutes les images d'un dossier, triées par nom.
    Retourne une liste de tuples (nom_fichier, image).
    """
    fichiers = sorted([
        f for f in os.listdir(dossier)
        if os.path.splitext(f)[1].lower() in extensions
    ])
    images = []
    for f in fichiers:
        chemin = os.path.join(dossier, f)
        img = charger_image(chemin)
        images.append((f, img))
    return images


def dessiner_points(img, pts, couleur='r', taille=50):
    """Dessine des points sur une image et retourne la figure."""
    plt.figure(figsize=(10, 8))
    plt.imshow(img)
    plt.scatter(pts[:, 0], pts[:, 1], c=couleur, s=taille, marker='x', linewidths=2)
    for i, (x, y) in enumerate(pts):
        plt.text(x + 10, y + 10, str(i), color=couleur, fontsize=10, fontweight='bold')
    plt.axis('off')
    return plt.gcf()


def dessiner_correspondances(img1, img2, pts1, pts2, titre="Correspondances"):
    """Affiche deux images côte à côte avec les correspondances dessinées."""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    h_max = max(h1, h2)
    canvas = np.zeros((h_max, w1 + w2, 3))
    canvas[:h1, :w1] = img1[:, :, :3] if img1.ndim == 3 else np.stack([img1]*3, axis=-1)
    canvas[:h2, w1:w1+w2] = img2[:, :, :3] if img2.ndim == 3 else np.stack([img2]*3, axis=-1)

    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.imshow(canvas)
    ax.set_title(titre)

    for i in range(len(pts1)):
        x1, y1 = pts1[i]
        x2, y2 = pts2[i]
        ax.plot([x1, x2 + w1], [y1, y2], 'o-', linewidth=1, markersize=5)

    ax.axis('off')
    plt.tight_layout()
    return fig


def sauvegarder_figure(fig, chemin, dpi=150):
    """Sauvegarde une figure matplotlib."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    fig.savefig(chemin, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure sauvegardée : {chemin}")
