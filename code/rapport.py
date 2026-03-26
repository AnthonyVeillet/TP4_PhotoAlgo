from __future__ import annotations

from datetime import datetime
from pathlib import Path

# =========================
# Config
# =========================

OUTPUT_HTML = Path(__file__).resolve().parent.parent / "data" / "dataRapport" / "rapport.html"

TITLE = "📸 Rapport TP4 — Panoramas"
# TODO: Mettre votre nom ici
AUTHOR = "Anthony Veillet"
COURSE_FOOTER = "Photographie algorithmique — TP4 | Panoramas"

# Racine des outputs (relatif au HTML)
OUT = Path("../dataOutput")
INP = Path("../dataInput/images")

# ---- Réchauffement ----
IMG_POULIOT_ORIG = OUT / "rechauffement" / "pouliot_original.jpg"
IMG_POULIOT_H1 = OUT / "rechauffement" / "pouliot_H1.jpg"
IMG_POULIOT_H2 = OUT / "rechauffement" / "pouliot_H2.jpg"

# ---- Manuel Serie 1 ----
MAN_S1_CORR_12 = OUT / "manuel" / "serie1" / "correspondances_12.jpg"
MAN_S1_CORR_32 = OUT / "manuel" / "serie1" / "correspondances_32.jpg"
MAN_S1_MOSAIQUE = OUT / "manuel" / "serie1" / "mosaique_serie1.jpg"

# ---- Manuel Serie 2 ----
MAN_S2_CORR_01 = OUT / "manuel" / "serie2" / "correspondances_0_1.jpg"
MAN_S2_MOSAIQUE = OUT / "manuel" / "serie2" / "mosaique_serie2.jpg"

# ---- Manuel Serie 3 ----
MAN_S3_CORR_01 = OUT / "manuel" / "serie3" / "correspondances_0_1.jpg"
MAN_S3_CORR_12 = OUT / "manuel" / "serie3" / "correspondances_1_2.jpg"
MAN_S3_MOSAIQUE = OUT / "manuel" / "serie3" / "mosaique_serie3.jpg"

# ---- Automatique Serie 1 (Golden Gate) ----
AUTO_S1_APPS = [OUT / "automatique" / "serie1" / f"appariements_{i}_{i+1}.jpg" for i in range(5)]
AUTO_S1_MOSAIQUE = OUT / "automatique" / "serie1" / "mosaique_serie1.jpg"

# ---- Automatique Serie 2 ----
AUTO_S2_APPS = [OUT / "automatique" / "serie2" / f"appariements_{i}_{i+1}.jpg" for i in range(3)]
AUTO_S2_MOSAIQUE = OUT / "automatique" / "serie2" / "mosaique_serie2.jpg"

# ---- Automatique Serie 3 ----
AUTO_S3_APPS = [OUT / "automatique" / "serie3" / f"appariements_{i}_{i+1}.jpg" for i in range(5)]
AUTO_S3_MOSAIQUE = OUT / "automatique" / "serie3" / "mosaique_serie3.jpg"

# ---- Images personnelles ----
PERSO_S1_MOSAIQUE = OUT / "ImagePerso" / "scene1" / "mosaique_scene1.jpg"
PERSO_S1_APPS = [OUT / "ImagePerso" / "scene1" / f"appariements_{i}_{i+1}.jpg" for i in range(5)]

PERSO_S2_MOSAIQUE = OUT / "ImagePerso" / "scene2" / "mosaique_scene2.jpg"
PERSO_S2_APPS = [OUT / "ImagePerso" / "scene2" / f"appariements_{i}_{i+1}.jpg" for i in range(5)]


# =============================================================================
# Réponses — Remplir les TODO restants
# =============================================================================

# ---- Réchauffement ----
APPROCHE_RECHAUFFEMENT = """
La fonction appliqueTransformation applique une homographie H à une image en utilisant skimage.transform.warp.
Pour gérer les coordonnées négatives ou dépassant l'image originale, on transforme d'abord les 4 coins de l'image avec H
afin de calculer la boîte englobante du résultat. On détermine ensuite un offset de translation pour ramener toutes les
coordonnées dans le positif, et on ajuste H en conséquence (H_ajusté = T @ H). L'image de sortie est dimensionnée
selon la boîte englobante complète, ce qui garantit qu'aucune partie de l'image transformée n'est coupée.
"""

COMMENTAIRE_RECHAUFFEMENT = """
H1 produit une image cisaillée vers la gauche avec un décalage négatif en x — on voit que l'image finale est plus large
car le code a ajouté un offset pour conserver les pixels aux coordonnées négatives. H2 applique une rotation importante
qui fait pivoter l'image d'environ 90 degrés. Les deux résultats montrent que la gestion des bordures fonctionne
correctement : aucune partie de l'image transformée n'est perdue.
"""

# ---- Appariement manuel ----
APPROCHE_MANUEL = """
L'algorithme suit 4 étapes : (1) sélection manuelle de points de correspondance entre paires d'images consécutives
à l'aide d'un outil matplotlib (ginput), (2) calcul de l'homographie H pour chaque paire via
skimage.transform.estimate_transform('projective'), (3) chaînage des homographies vers une image de référence
centrale pour minimiser les distorsions, et (4) fusion des images déformées par moyenne pondérée — les pixels
proches du centre de leur image d'origine ont plus de poids, ce qui donne des transitions douces dans les zones
de chevauchement.
"""

COMMENTAIRE_MANUEL_S1 = """
La mosaïque de la série 1 donne un bon résultat grâce aux points fournis qui sont précis. L'image de référence
est l'image du milieu, ce qui minimise la déformation des images latérales. Les transitions entre les images
sont relativement douces grâce au mélange pondéré par distance au centre. On observe quelques légers artefacts
aux jonctions, typiques de la différence d'exposition entre les photos.
"""

COMMENTAIRE_MANUEL_S2 = """
Le panorama de la série 2 montre un fleuve gelé avec la rive opposée visible à l'horizon. Le résultat est
convaincant avec seulement 2 images. On observe une légère déformation en forme de « bow-tie » sur les bords,
typique de la projection planaire quand le champ de vue commence à être large. Les transitions entre les deux
images sont fluides grâce au mélange pondéré.
"""

COMMENTAIRE_MANUEL_S3 = """
La mosaïque de la série 3 assemble correctement les 3 images en un panorama d'un parc enneigé vu depuis un pont.
L'image de référence centrale minimise bien les distorsions : les bâtiments restent droits au centre tandis que
les bords montrent la courbure typique de la projection planaire. Les joints entre les images sont peu visibles,
ce qui confirme la bonne qualité des points de correspondance sélectionnés manuellement.
"""

# ---- Appariement automatique ----
APPROCHE_AUTOMATIQUE = """
L'appariement manuel est remplacé par une détection automatique en 3 étapes : (1) extraction de points d'intérêt
et descripteurs avec SIFT (skimage.feature.SIFT), (2) appariement des descripteurs entre images consécutives avec
match_descriptors (cross_check + ratio de Lowe à 0.8), et (3) estimation robuste de l'homographie par RANSAC
(skimage.measure.ransac) qui élimine les faux appariements (outliers). Les homographies sont ensuite chaînées
vers l'image de référence centrale, puis la mosaïque est créée avec le même mélange pondéré que la partie manuelle.
"""

COMMENTAIRE_AUTO_S1 = """
La mosaïque du Golden Gate fonctionne bien malgré le fait que les images soient en niveaux de gris. SIFT détecte
de nombreux points d'intérêt sur les structures du pont et le paysage. Le nombre élevé d'inliers par paire
(plusieurs centaines) confirme la robustesse de l'estimation. Le panorama final couvre un large champ de vue
avec des transitions cohérentes entre les 6 images.
"""

COMMENTAIRE_AUTO_S2 = """
La série 2 automatique utilise 4 images de la même scène que la série 1 manuelle (terrasse en bois avec vue
sur un quartier enneigé). SIFT détecte un grand nombre de points d'intérêt grâce aux textures riches (planches
de bois, clôtures, bâtiments). Le résultat est comparable à la version manuelle, ce qui montre que l'appariement
automatique est fiable quand les images ont suffisamment de texture et un chevauchement adéquat.
"""

COMMENTAIRE_AUTO_S3 = """
La mosaïque de la série 3 échoue en grande partie. Les images 2434-2436 et 2466-2468 forment deux groupes
pris sous des angles très différents (saut de 30 numéros dans les noms de fichiers). La paire 2436↔2466
présente un changement d'orientation important visible par les lignes d'appariement diagonales. Quand on chaîne
les homographies à travers cette transition, l'erreur accumulée projette les images éloignées dans un coin
minuscule du panorama. C'est une limitation connue du chaînage d'homographies planaires sur de grands angles.
"""

# ---- Images personnelles ----
APPROCHE_PERSO = """
Les photos ont été prises à main levée avec un téléphone intelligent, sans trépied. Ces photos avaient été prise pour faire
des panoramique, ce qui est intéressant de pouvoir comparer avec celles fait par mon algorithme. Pour chaque scène, 6 photos
ont été capturées en pivotant sur place avec un chevauchement d'environ 50% entre chaque prise. La scène 1
a été prise de nuit lors d'un événement de snowboard (rail jam), et la scène 2 a été prise au coucher du soleil
devant un pont ferroviaire au bord de l'eau.
"""

COMMENTAIRE_PERSO_S1 = """
Le panorama du rail jam est bien assemblé malgré les conditions difficiles : scène de nuit avec éclairage
artificiel et ombres marquées sur la neige. SIFT a pu trouver suffisamment de points grâce aux textures des
bannières Burton, de la foule et de la neige. On remarque une légère courbure du rail en forme de « sourire »
due à la projection planaire sur un champ de vue large, mais les transitions sont propres.
"""

COMMENTAIRE_PERSO_S2 = """
Le panorama du pont au coucher du soleil est le meilleur résultat de mes images personnelles. La structure
métallique du pont offre beaucoup de points d'intérêt pour SIFT et les reflets sur l'eau sont cohérents entre
les images. On note une légère variation d'exposition entre les photos (le soleil couchant crée un dégradé),
mais le mélange pondéré atténue bien cette différence. Le résultat final est un panorama large et naturel.
"""

# ---- Prompts IA ----
PROMPT_IA_1 = """
Exemple prompt 1:
Yo
1. Analyse et comprend le travail que je dois faire en Python, soit TP4.pdf
2. Analyse le fichier arbo_images.txt qui contient l'arborescence du dossier images qu'il est mentionné dans l'énoncé du projet. Il pourrait t'être utile.
3. Fait moi un plan détaillé de ce que je vais devoir faire ainsi qu'un plan des différents dossiers et fichiers que je vais devoir créer et faire (arborescence de mon projet).
4. S'il te manque d'informations pour en compléter certain, dit moi le.
5. Ne t'occupe pas de la section des questions à répondre dans le rapport, pour l'instant, ni de la section des crédits supplémentaires.
6. Donne moi un fichier ARBORESCENCE.txt qui montrera l'arborescence que vas avoir mon projet.
7. Fait moi un plan détaillé (nom des fonctions, noms des variables, et explication de ce que fait chaque fonction)
8. Je veux que tu sois mon tuteur et que tu favories mon apprentissage, donc ne me donne pas le code complêt. Je veux que te m'aide.
9. Le seule code que je te permet de me faire au complet sont les fichiers de code qui ne sont pas directement lié au fonction que je
doit faire dans le projet, par exemple le code pour s'occuper d'importer et d'exporter.
10. Avant de donner ta réponse, mentionne moi s'il te manque des informations où si quelque chose est pas clair. Si tu as toutes l'informations nécessaire
pour faire ta réponse, analyse la pour etre certain qu'elle répond à mes critères et aux attentes de TP4.pdf. Tu n'as aucune limite de temps pour répondre.

"""

PROMPT_IA_2 = """
Yo
1) Analyse un exemple exemple_rapport.py de structure du rapport que j'ai déjà fait. Dane le même style.
2) Fait moi le code python pour faire mon rapport du TP4.pdf
3) Pour chaque étape du TP4 que je dois faire (sauf les credits supplémentaire), affiche les images original, puis en
dessous l'image resultante. Ajoute aussi une section de texte pour faire les explication, la où il l'est demandé.
4) A la fin du rapport ajoute une zone de texte pour mettre les 2 exemple de prompt que j'ai utiliser avec ChatGPT
6) Concernant les images a mettre dans le rapport, avec l'arborescence de mon projet tu sais où elles se trouvent. Les seules images
que tu ne connais pas leur nom sont mes deux images persos et voici leur nom:
Image original 1 ont les nom RailJam_001.jpeg jusqu'a RailJam_006.jpeg, et le nom de l'image resultant est obtenue avec le code main_automatique
Image original 2 ont les nom Pont_pano_x_001.jpeg jusqu'a Pont_pano_x_006.jpeg, et le nom de l'image resultant est obtenue avec le code main_automatique
7) Donne moi le code python pour générer ce rapport. Le but est que le correct pour simplement ouvrir le rapport html qui aura été
générer dans le même dossier que le code du rapport.py (idem pour l'emplacement des images et videos). Il pourra corriger le rapport a partir de la
8) Pas besoin de mettre les images originales s'il y en a trop, par exemple pour les images personnel.

C'est moi qui générer le rapport.html avec les zone de texte déjà écrisent. C'est zone contiendrons mes réponses. Il faut que j'ecrive
mes réponses dans le rapport.py pour que le rapport.html soit générer avec mes réponses dedans, donc indique clairement avec des TODO où que je dois ecrire.
Le rapport.html sera générer dans le dossier TP4/data/dataRapport/, et le code rapport.py sera dans le dossier TP4/code/
"""


# =========================
# Helpers HTML
# =========================

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _nl2br(s: str) -> str:
    return s.strip().replace("\n", "<br>\n")


def figure(src: Path, caption: str, max_width: str = "80%") -> str:
    return f"""
    <div class="figure-container">
        <img src="{src.as_posix()}" alt="{_esc(caption)}" data-fullsize="{src.as_posix()}"
             onclick="openLightbox(this)" style="max-width:{max_width};" />
        <p class="figure-caption">{_esc(caption)}</p>
    </div>"""


def pair_two(a: Path, cap_a: str, b: Path, cap_b: str) -> str:
    return f"""
    <div class="comparison-images">
        <div class="comparison-image-item" onclick="openLightbox(this.querySelector('img'))">
            <img src="{a.as_posix()}" alt="{_esc(cap_a)}" data-fullsize="{a.as_posix()}">
            <div class="comparison-image-label">{_esc(cap_a)}</div>
        </div>
        <div class="comparison-image-item" onclick="openLightbox(this.querySelector('img'))">
            <img src="{b.as_posix()}" alt="{_esc(cap_b)}" data-fullsize="{b.as_posix()}">
            <div class="comparison-image-label">{_esc(cap_b)}</div>
        </div>
    </div>"""


def grid_images(paths: list, captions: list, cols: int = 3) -> str:
    items = ""
    for p, c in zip(paths, captions):
        items += f"""
        <div class="comparison-image-item" onclick="openLightbox(this.querySelector('img'))">
            <img src="{p.as_posix()}" alt="{_esc(c)}" data-fullsize="{p.as_posix()}">
            <div class="comparison-image-label">{_esc(c)}</div>
        </div>"""
    return f'<div class="comparison-images" style="grid-template-columns: repeat({cols}, 1fr);">{items}</div>'


def text_block(title: str, content: str) -> str:
    return f"""
    <div class="text-block">
        <div class="text-block-title">📝 {_esc(title)}</div>
        <div class="text-content">{_nl2br(content)}</div>
    </div>"""


def decl_ia_block(content: str) -> str:
    return f"""
    <div class="decl-ia">
        <div class="text-block-title">🤖 Déclaration relative à l'IA</div>
        <div class="text-content">{_nl2br(content)}</div>
    </div>"""


def section(title: str, inner: str) -> str:
    return f"""
    <section class="image-section">
        <h2>{_esc(title)}</h2>
        {inner}
    </section>"""


# =========================
# Build sections
# =========================

def build_rechauffement() -> str:
    s = ""
    s += text_block("Approche", APPROCHE_RECHAUFFEMENT)

    s += "<h3>Image originale</h3>"
    s += figure(IMG_POULIOT_ORIG, "pouliot.jpg — Image originale")

    s += "<h3>Résultat avec H1</h3>"
    s += figure(IMG_POULIOT_H1, "pouliot.jpg transformée par H1")

    s += "<h3>Résultat avec H2</h3>"
    s += figure(IMG_POULIOT_H2, "pouliot.jpg transformée par H2")

    s += text_block("Commentaires", COMMENTAIRE_RECHAUFFEMENT)
    return s


def build_manuel() -> str:
    s = ""
    s += text_block("Approche", APPROCHE_MANUEL)

    # Serie 1
    s += "<h3>Série 1 — Points fournis</h3>"
    s += "<h4>Correspondances</h4>"
    s += pair_two(MAN_S1_CORR_12, "Correspondances images 1↔2",
                  MAN_S1_CORR_32, "Correspondances images 3↔2")
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(MAN_S1_MOSAIQUE, "Mosaïque Serie 1 — Appariement manuel", "90%")
    s += text_block("Commentaires — Série 1", COMMENTAIRE_MANUEL_S1)

    s += "<hr class='soft-hr' />"

    # Serie 2
    s += "<h3>Série 2 — Points sélectionnés manuellement</h3>"
    s += "<h4>Correspondances</h4>"
    s += figure(MAN_S2_CORR_01, "Correspondances images 0↔1", "90%")
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(MAN_S2_MOSAIQUE, "Mosaïque Serie 2 — Appariement manuel", "90%")
    s += text_block("Commentaires — Série 2", COMMENTAIRE_MANUEL_S2)

    s += "<hr class='soft-hr' />"

    # Serie 3
    s += "<h3>Série 3 — Points sélectionnés manuellement</h3>"
    s += "<h4>Correspondances</h4>"
    s += pair_two(MAN_S3_CORR_01, "Correspondances images 0↔1",
                  MAN_S3_CORR_12, "Correspondances images 1↔2")
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(MAN_S3_MOSAIQUE, "Mosaïque Serie 3 — Appariement manuel", "90%")
    s += text_block("Commentaires — Série 3", COMMENTAIRE_MANUEL_S3)

    return s


def build_automatique() -> str:
    s = ""
    s += text_block("Approche", APPROCHE_AUTOMATIQUE)

    # Serie 1 — Golden Gate
    s += "<h3>Série 1 — Golden Gate</h3>"
    s += "<h4>Appariements automatiques (SIFT + RANSAC)</h4>"
    s += grid_images(AUTO_S1_APPS,
                     [f"Appariements {i}↔{i+1}" for i in range(5)], cols=3)
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(AUTO_S1_MOSAIQUE, "Mosaïque Serie 1 — Golden Gate (automatique)", "95%")
    s += text_block("Commentaires — Série 1 (Golden Gate)", COMMENTAIRE_AUTO_S1)

    s += "<hr class='soft-hr' />"

    # Serie 2
    s += "<h3>Série 2</h3>"
    s += "<h4>Appariements automatiques</h4>"
    s += grid_images(AUTO_S2_APPS,
                     [f"Appariements {i}↔{i+1}" for i in range(3)], cols=3)
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(AUTO_S2_MOSAIQUE, "Mosaïque Serie 2 (automatique)", "95%")
    s += text_block("Commentaires — Série 2", COMMENTAIRE_AUTO_S2)

    s += "<hr class='soft-hr' />"

    # Serie 3
    s += "<h3>Série 3</h3>"
    s += "<h4>Appariements automatiques</h4>"
    s += grid_images(AUTO_S3_APPS,
                     [f"Appariements {i}↔{i+1}" for i in range(5)], cols=3)
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(AUTO_S3_MOSAIQUE, "Mosaïque Serie 3 (automatique)", "95%")
    s += text_block("Commentaires — Série 3", COMMENTAIRE_AUTO_S3)

    return s


def build_perso() -> str:
    s = ""
    s += text_block("Approche / Conditions de prise de vue", APPROCHE_PERSO)

    # Scene 1 — RailJam
    s += "<h3>Scène 1 — RailJam</h3>"
    s += "<h4>Quelques appariements</h4>"
    s += grid_images(PERSO_S1_APPS[:3],
                     [f"Appariements {i}↔{i+1}" for i in range(3)], cols=3)
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(PERSO_S1_MOSAIQUE, "Panorama Scene 1 — RailJam", "95%")
    s += text_block("Commentaires — Scène 1 (RailJam)", COMMENTAIRE_PERSO_S1)

    s += "<hr class='soft-hr' />"

    # Scene 2 — Pont
    s += "<h3>Scène 2 — Pont</h3>"
    s += "<h4>Quelques appariements</h4>"
    s += grid_images(PERSO_S2_APPS[:3],
                     [f"Appariements {i}↔{i+1}" for i in range(3)], cols=3)
    s += "<h4>Mosaïque résultante</h4>"
    s += figure(PERSO_S2_MOSAIQUE, "Panorama Scene 2 — Pont", "95%")
    s += text_block("Commentaires — Scène 2 (Pont)", COMMENTAIRE_PERSO_S2)

    return s


def build_prompts_ia() -> str:
    s = ""
    s += text_block("Exemple de prompt 1", PROMPT_IA_1)
    s += "<hr class='soft-hr' />"
    s += text_block("Exemple de prompt 2", PROMPT_IA_2)
    return s


# =========================
# HTML Template
# =========================

def build_html() -> str:
    now = datetime.now().strftime("%d %B %Y à %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_esc(TITLE)}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&family=Fira+Code:wght@400;500&display=swap');
    * {{ box-sizing: border-box; }}

    body {{
      font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      color: #e8e8e8;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 30px 20px;
    }}

    header {{
      text-align: center;
      padding: 40px 0;
      border-bottom: 2px solid rgba(255,255,255,0.1);
      margin-bottom: 40px;
    }}

    h1 {{
      font-size: 2.5em;
      font-weight: 700;
      margin: 0 0 10px 0;
      text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}

    .author {{
      font-size: 1.15em;
      color: #b0b0b0;
      margin-bottom: 6px;
    }}

    .date-badge {{
      display: inline-block;
      background: rgba(255,255,255,0.1);
      padding: 8px 20px;
      border-radius: 20px;
      margin-top: 12px;
      font-size: 0.9em;
      color: #b0b0b0;
    }}

    .image-section {{
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 30px;
      margin-bottom: 40px;
      border: 1px solid rgba(255,255,255,0.1);
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}

    .image-section h2 {{
      color: #778da9;
      font-size: 1.6em;
      margin: 0 0 25px 0;
      padding-bottom: 15px;
      border-bottom: 2px solid rgba(119, 141, 169, 0.25);
    }}

    h3 {{ color: #e0e1dd; font-size: 1.3em; margin: 26px 0 14px 0; }}
    h4 {{ margin: 18px 0 10px 0; color: #dbe2ef; }}

    .figure-container {{
      text-align: center;
      margin: 15px 0;
      padding: 15px;
      background: rgba(0,0,0,0.2);
      border-radius: 12px;
    }}

    .figure-container img {{
      max-width: 100%;
      max-height: 600px;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }}

    .figure-container img:hover {{
      transform: scale(1.015);
      box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }}

    .figure-caption {{
      margin-top: 10px;
      font-style: italic;
      color: #a0a0a0;
      font-size: 0.9em;
    }}

    .comparison-images {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin: 10px 0;
    }}

    .comparison-image-item {{
      position: relative;
      border-radius: 10px;
      overflow: hidden;
      background: rgba(0,0,0,0.2);
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }}

    .comparison-image-item:hover {{
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }}

    .comparison-image-item img {{
      width: 100%;
      height: auto;
      display: block;
    }}

    .comparison-image-label {{
      position: absolute;
      bottom: 0; left: 0; right: 0;
      background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
      color: #fff;
      padding: 12px 8px 8px;
      font-size: 0.85em;
      text-align: center;
      font-weight: 500;
    }}

    .text-block, .decl-ia {{
      background: rgba(0,0,0,0.25);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px;
      padding: 18px;
      margin: 18px 0 0 0;
    }}

    .decl-ia {{ border-left: 4px solid #778da9; }}

    .text-block-title {{
      font-weight: 700;
      color: #cbd5e1;
      margin-bottom: 10px;
    }}

    .text-content {{
      color: #d0d0d0;
      line-height: 1.7;
      font-size: 1em;
    }}

    .soft-hr {{
      border: none;
      height: 1px;
      background: rgba(255,255,255,0.12);
      margin: 22px 0;
    }}

    footer {{
      text-align: center;
      padding: 30px;
      color: #777;
      font-size: 0.95em;
    }}

    .lightbox {{
      display: none;
      position: fixed;
      z-index: 9999;
      left: 0; top: 0;
      width: 100%; height: 100%;
      background-color: rgba(0,0,0,0.92);
      animation: fadeIn 0.2s;
    }}

    .lightbox.active {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .lightbox-content {{
      max-width: 95vw;
      max-height: 95vh;
      padding: 18px;
    }}

    .lightbox-content img {{
      max-width: 100%;
      max-height: 95vh;
      object-fit: contain;
      border-radius: 10px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.8);
    }}

    .lightbox-close {{
      position: absolute;
      top: 16px; right: 30px;
      color: #fff;
      font-size: 44px;
      font-weight: bold;
      cursor: pointer;
      user-select: none;
    }}

    .lightbox-close:hover {{ color: #ffc107; }}

    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}

    @media (max-width: 900px) {{
      .comparison-images {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>

<body>
  <div id="lightbox" class="lightbox" onclick="closeLightbox(event)">
    <span class="lightbox-close">&times;</span>
    <div class="lightbox-content">
      <img id="lightbox-img" src="" alt="">
    </div>
  </div>

  <div class="container">
    <header>
      <h1>{_esc(TITLE)}</h1>
      <div class="author">{_esc(AUTHOR)}</div>
      <div class="date-badge">Généré le {now}</div>
    </header>

    {section("1. Réchauffement (20%)", build_rechauffement())}
    {section("2. Appariement manuel (45%)", build_manuel())}
    {section("3. Appariement automatique (15%)", build_automatique())}
    {section("4. Vos images (20%)", build_perso())}
    {section("Annexe — Exemples de prompts IA utilisés", build_prompts_ia())}

    <footer>
      <p>{_esc(COURSE_FOOTER)}</p>
    </footer>
  </div>

  <script>
    function openLightbox(img) {{
      const lightbox = document.getElementById('lightbox');
      const lightboxImg = document.getElementById('lightbox-img');
      lightboxImg.src = img.getAttribute('data-fullsize') || img.src;
      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    }}

    function closeLightbox(event) {{
      const lightbox = document.getElementById('lightbox');
      if (event.target === lightbox || event.target.classList.contains('lightbox-close')) {{
        lightbox.classList.remove('active');
        document.body.style.overflow = 'auto';
      }}
    }}

    document.addEventListener('keydown', function(event) {{
      if (event.key === 'Escape') {{
        document.getElementById('lightbox').classList.remove('active');
        document.body.style.overflow = 'auto';
      }}
    }});
  </script>
</body>
</html>"""
    return html


def main() -> None:
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    html = build_html()
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"[OK] Rapport généré: {OUTPUT_HTML.resolve()}")


if __name__ == "__main__":
    main()