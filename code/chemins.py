"""
Configuration centralisée de tous les chemins du projet.

Structure attendue :
    TP4/
    ├── code/               <- les scripts sont ici
    │   ├── chemins.py      <- CE FICHIER
    │   ├── main_rechauffement.py
    │   └── ...
    └── data/
        ├── dataInput/
        │   ├── images/     <- images.zip dézippé ici
        │   │   ├── 0-Rechauffement/
        │   │   ├── 1-PartieManuelle/
        │   │   ├── 2-PartieAutomatique/
        │   │   └── 3-ProjCylindrique/
        │   └── 4-ImagePerso/
        │       ├── Scene1/
        │       └── Scene2/
        └── dataOutput/     <- tous les résultats vont ici
            ├── rechauffement/
            ├── manuel/
            ├── automatique/
            ├── ImagePerso/
            └── points_manuels/
"""
import os

# Racine du projet (TP4/)
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.join(_CODE_DIR, '..')

# ---------- INPUT ----------
IMAGES_DIR = os.path.join(_PROJECT_DIR, 'data', 'dataInput', 'images')

# Réchauffement
IMG_POULIOT = os.path.join(IMAGES_DIR, '0-Rechauffement', 'pouliot.jpg')

# Partie manuelle
MANUEL_SERIE1_DIR = os.path.join(IMAGES_DIR, '1-PartieManuelle', 'Serie1')
MANUEL_SERIE1_PTS = os.path.join(MANUEL_SERIE1_DIR, 'pts_serie1')
MANUEL_SERIE2_DIR = os.path.join(IMAGES_DIR, '1-PartieManuelle', 'Serie2')
MANUEL_SERIE3_DIR = os.path.join(IMAGES_DIR, '1-PartieManuelle', 'Serie3')

# Partie automatique
AUTO_SERIE1_DIR = os.path.join(IMAGES_DIR, '2-PartieAutomatique', 'Serie1')
AUTO_SERIE2_DIR = os.path.join(IMAGES_DIR, '2-PartieAutomatique', 'Serie2')
AUTO_SERIE3_DIR = os.path.join(IMAGES_DIR, '2-PartieAutomatique', 'Serie3')

# Images personnelles (input dans dataInput, PAS dans images/)
PERSO_DIR = os.path.join(_PROJECT_DIR, 'data', 'dataInput', '4-ImagePerso')

# ---------- OUTPUT ----------
OUTPUT_DIR = os.path.join(_PROJECT_DIR, 'data', 'dataOutput')

OUT_RECHAUFFEMENT = os.path.join(OUTPUT_DIR, 'rechauffement')
OUT_MANUEL = os.path.join(OUTPUT_DIR, 'manuel')
OUT_AUTOMATIQUE = os.path.join(OUTPUT_DIR, 'automatique')
OUT_PERSO_IMAGES = os.path.join(OUTPUT_DIR, 'ImagePerso')
OUT_POINTS_MANUELS = os.path.join(OUTPUT_DIR, 'points_manuels')
