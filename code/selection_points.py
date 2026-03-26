#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Outil de sélection de points de correspondance pour TP4.
Adapté du selectpoints_V2.py du TP3.

Workflow :
  1. Entrer un nom de série (ex: serie2, serie3)
  2. Sélectionner TOUTES les images de la série (sélection multiple)
  3. Pour chaque paire consécutive (img0↔img1, img1↔img2, ...),
     cliquer les points de correspondance
  4. Les points sont sauvegardés en CSV dans data/dataOutput/points_manuels/

Format de sortie : x,y par ligne (compatible np.loadtxt(path, delimiter=","))

Utilisation :
  python selection_points.py
"""

from __future__ import print_function
import os
import numpy as np
from pylab import *
from skimage import io
from pathlib import Path
from tkinter import Tk, filedialog, simpledialog

from chemins import OUT_POINTS_MANUELS as OUTPUT_POINTS_DIR
from chemins import IMAGES_DIR as INPUT_IMAGES_DIR


# ============================================================
# Classe Cursor adaptée du TP3
# ============================================================
class Cursor:
    def __init__(self, ax, s, output_file):
        self.ax = ax
        self.lx = ax.axhline(color='k', linewidth=0.5)
        self.ly = ax.axvline(color='k', linewidth=0.5)

        self.f = output_file
        self.count = 1
        self.s = s
        self.points = []

    def mousemove(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        self.lx.set_ydata([y, y])
        self.ly.set_xdata([x, x])
        self.ax.figure.canvas.draw_idle()

    def mouseclick(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        self.points.append([x, y])
        print(f"  Point {self.count}: ({x:.2f}, {y:.2f})")

        # Écrire dans le fichier au format CSV (x,y)
        with open(self.f, 'a', encoding='utf-8') as h:
            h.write(f"{x:.6f},{y:.6f}\n")

        self.ax.text(x + 4, y - 4, str(self.count), fontsize=14, color='r',
                     fontweight='bold')
        self.ax.plot(x, y, '.r', markersize=10)
        self.count += 1
        draw()


# ============================================================
# Fonctions utilitaires
# ============================================================
def select_multiple_images(title="Sélectionner les images de la série"):
    """Ouvre un file dialog pour choisir PLUSIEURS images d'un coup."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    image_files = filedialog.askopenfilenames(
        title=title,
        initialdir=INPUT_IMAGES_DIR,
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
            ("Tous les fichiers", "*.*")
        ]
    )
    root.destroy()

    if not image_files:
        print("Aucune image sélectionnée.")
        return []

    # Trier par nom de fichier pour garder l'ordre
    image_files = sorted(image_files)
    return list(image_files)


def select_points_on_image(image_path, title, output_file):
    """Affiche une image, laisse l'utilisateur cliquer des points, puis fermer."""
    # Vider le fichier au démarrage
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    Path(output_file).write_text("", encoding="utf-8")

    fig, ax = subplots(figsize=(14, 10))
    img = io.imread(str(image_path))
    ax.imshow(img)
    ax.set_title(f"{title}\nCliquez les points, puis FERMEZ la fenêtre quand terminé")

    cursor = Cursor(ax, img.shape, output_file)
    cid_click = connect('button_press_event', cursor.mouseclick)
    cid_move = connect('motion_notify_event', cursor.mousemove)

    show()  # Bloque jusqu'à fermeture de la fenêtre

    n = len(cursor.points)
    print(f"  -> {n} points sauvegardés : {output_file}")
    return np.array(cursor.points) if cursor.points else np.array([])


def charger_points(chemin):
    """Charge des points depuis un fichier CSV (x,y par ligne)."""
    return np.loadtxt(chemin, delimiter=",", dtype=np.float64)


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("Sélection de points de correspondance — TP4")
    print("=" * 60)

    # Demander un nom de sous-dossier (série)
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    serie_name = simpledialog.askstring(
        "Nom de série",
        "Sous-dossier pour les points :\n(ex: serie2, serie3)",
        parent=root
    )
    root.destroy()
    serie_name = serie_name.strip() if serie_name else ""

    # Dossier de sortie
    if serie_name:
        out_dir = os.path.join(OUTPUT_POINTS_DIR, serie_name)
    else:
        out_dir = OUTPUT_POINTS_DIR
    os.makedirs(out_dir, exist_ok=True)

    # Sélection de TOUTES les images de la série
    print("\n--- Sélectionnez TOUTES les images de la série (sélection multiple) ---")
    print("    Astuce : Ctrl+clic ou Shift+clic pour sélectionner plusieurs fichiers")
    image_paths = select_multiple_images("Sélectionner TOUTES les images de la série")

    if len(image_paths) < 2:
        print("Il faut au moins 2 images pour créer des correspondances.")
        return

    n_images = len(image_paths)
    noms = [Path(p).name for p in image_paths]
    noms_sans_ext = [Path(p).stem for p in image_paths]

    print(f"\n{n_images} images sélectionnées (triées par nom) :")
    for i, nom in enumerate(noms):
        print(f"  [{i}] {nom}")

    n_paires = n_images - 1
    print(f"\n{n_paires} paire(s) consécutive(s) à traiter :")
    for i in range(n_paires):
        print(f"  Paire {i + 1}/{n_paires} : {noms[i]} <-> {noms[i + 1]}")

    # Demander le nombre de points par paire
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    n_points = simpledialog.askinteger(
        "Nombre de points",
        f"Combien de points de correspondance par paire ?",
        initialvalue=8, minvalue=4, maxvalue=50,
        parent=root
    )
    root.destroy()
    if n_points is None:
        n_points = 8

    # Traiter chaque paire consécutive
    for p in range(n_paires):
        i, j = p, p + 1
        name_i = noms_sans_ext[i]
        name_j = noms_sans_ext[j]

        print(f"\n{'=' * 60}")
        print(f"PAIRE {p + 1}/{n_paires} : {noms[i]} <-> {noms[j]}")
        print(f"{'=' * 60}")

        out_i = os.path.join(out_dir, f"pts_{name_i}_vers_{name_j}.txt")
        out_j = os.path.join(out_dir, f"pts_{name_j}_vers_{name_i}.txt")

        # Points sur image i
        print(f"\n>>> Cliquez {n_points} points sur {noms[i]}, puis fermez la fenêtre")
        pts_i = select_points_on_image(
            image_paths[i],
            f"[Paire {p + 1}/{n_paires}] IMAGE GAUCHE : {noms[i]}  —  ({n_points} points)",
            out_i
        )

        # Points sur image j
        print(f"\n>>> Cliquez {n_points} points CORRESPONDANTS sur {noms[j]} (même ordre!)")
        pts_j = select_points_on_image(
            image_paths[j],
            f"[Paire {p + 1}/{n_paires}] IMAGE DROITE : {noms[j]}  —  ({n_points} points, même ordre!)",
            out_j
        )

        # Vérification
        print(f"\n  Résumé paire {p + 1} :")
        print(f"    {noms[i]} : {len(pts_i)} points -> {out_i}")
        print(f"    {noms[j]} : {len(pts_j)} points -> {out_j}")

        if len(pts_i) != len(pts_j):
            print(f"    ⚠ ATTENTION : nombre de points différent ({len(pts_i)} vs {len(pts_j)}) !")
        if len(pts_i) != n_points or len(pts_j) != n_points:
            print(f"    ⚠ ATTENTION : attendu {n_points} points par image !")

    # Résumé final
    print(f"\n{'=' * 60}")
    print(f"TERMINÉ — {n_paires} paire(s) traitée(s)")
    print(f"Points sauvegardés dans : {out_dir}")
    print(f"{'=' * 60}")

    fichiers = sorted(os.listdir(out_dir))
    print(f"\nFichiers créés :")
    for f in fichiers:
        chemin = os.path.join(out_dir, f)
        pts = charger_points(chemin)
        print(f"  {f}  ({len(pts)} points)")


if __name__ == '__main__':
    main()
