import numpy as np
import matplotlib.pyplot as plt
import os


def selectionner_points(img, n_points=8, titre="Cliquez sur les points"):
    """Interface de sélection manuelle de points sur une image via ginput."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(img)
    ax.set_title(f"{titre} ({n_points} points - clic gauche pour sélectionner)")
    plt.tight_layout()

    pts = plt.ginput(n_points, timeout=0)
    plt.close(fig)

    pts = np.array(pts, dtype=np.float64)
    print(f"Points sélectionnés : {len(pts)}")
    return pts


def selectionner_correspondances(img1, img2, n_points=8):
    """Sélectionne des paires de points correspondants sur deux images."""
    print(f"\n=== Sélectionnez {n_points} points sur l'IMAGE 1 ===")
    pts1 = selectionner_points(img1, n_points, "IMAGE 1 : sélectionnez les points")

    print(f"\n=== Sélectionnez {n_points} points correspondants sur l'IMAGE 2 ===")
    print("(dans le même ordre que l'image 1)")
    pts2 = selectionner_points(img2, n_points, "IMAGE 2 : sélectionnez les points correspondants")

    return pts1, pts2


def sauvegarder_points(pts, chemin):
    """Sauvegarde des points dans un fichier texte (x,y par ligne)."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    np.savetxt(chemin, pts, delimiter=",", fmt="%.6f")
    print(f"Points sauvegardés : {chemin}")


def charger_points(chemin):
    """Charge des points depuis un fichier texte."""
    pts = np.loadtxt(chemin, delimiter=",", dtype=np.float64)
    return pts


def selectionner_et_sauvegarder(img1, img2, chemin_pts1, chemin_pts2, n_points=8):
    """Sélectionne des correspondances et les sauvegarde.
    Si les fichiers existent déjà, propose de les recharger."""
    if os.path.exists(chemin_pts1) and os.path.exists(chemin_pts2):
        print(f"Points déjà sauvegardés :")
        print(f"  {chemin_pts1}")
        print(f"  {chemin_pts2}")
        reponse = input("Recharger les points existants ? (o/n) : ").strip().lower()
        if reponse in ('o', 'y', ''):
            pts1 = charger_points(chemin_pts1)
            pts2 = charger_points(chemin_pts2)
            print(f"Points rechargés : {len(pts1)} paires")
            return pts1, pts2

    pts1, pts2 = selectionner_correspondances(img1, img2, n_points)
    sauvegarder_points(pts1, chemin_pts1)
    sauvegarder_points(pts2, chemin_pts2)
    return pts1, pts2
