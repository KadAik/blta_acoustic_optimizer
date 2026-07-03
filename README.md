# 🧱 BTLA Acoustic Optimizer

Une petite application web de bureau qui trouve le **meilleur mélange** pour une
brique de construction en terre latéritique — **latérite + ciment + fibre de
chiendent + sciure de bois** — pour une bonne isolation acoustique. Vous définissez
les plages autorisées et ce qui compte pour vous : pondération (absorber le son, bloquer le
son, ou les deux) ; l'application calcule les proportions idéales et trace la
performance selon les fréquences.

---

## ▶️ Comment la lancer

1. Assurez-vous que **Python** est installé. Sinon, téléchargez-le depuis
   <https://www.python.org/downloads/> et **cochez "Add Python to PATH"** pendant
   l'installation. (Python 3.12 ou plus récent convient.)
2. Ouvrez le dossier `btla`.
3. **Double-cliquez sur `run.bat`.**
   - La **première fois**, une fenêtre noire s'ouvre et passe quelques minutes à
     tout installer et télécharger ce dont elle a besoin. C'est normal — laissez-la
     terminer.
   - Votre navigateur web ouvre alors l'application automatiquement.
   - **Les lancements suivants démarrent en quelques secondes.**
4. Laissez la fenêtre noire ouverte pendant que vous utilisez l'application.
   Fermez-la quand vous avez terminé.

---

## 🖱️ Comment l'utiliser

Dans la barre latérale à gauche :

1. **Poids des matériaux** — le poids volumique de chaque ingrédient (N/m³).
2. **Plages de mélange autorisées** — la part minimale et maximale que chaque
   ingrédient peut prendre. L'application cherche à l'intérieur de ces plages ;
   les quatre parts totalisent toujours 100 %.
3. **Épaisseur de la brique** — en mètres.
4. **Ce qui compte le plus** — déplacez ces curseurs pour favoriser
   *l'absorption* du son, *la réduction* du son (blocage), ou pour pénaliser
   plus fortement la *transmission* du son.

Cliquez ensuite sur **Calculer le mélange optimal**. Vous verrez :

- les meilleurs pourcentages pour chaque ingrédient,
- une vérification qu'ils totalisent exactement 100 %,
- l'absorption, la réduction sonore et la porosité prédites,
- un graphique de la performance selon les fréquences.

Si vous choisissez des plages qui ne peuvent pas totaliser 100 %, l'application
vous indique exactement quelles limites assouplir — elle ne plante pas.

---

## ⚙️ Comment ça marche (la technique)

**Le modèle (la physique).** À partir des parts des ingrédients, l'application
calcule le poids et la densité de la brique, estime sa **porosité**, et en déduit
trois grandeurs acoustiques à chaque fréquence : l'absorption **α**, l'indice de
réduction sonore **Rw**, et la transmission **T**. Celles-ci sont combinées en un
seul score à maximiser :

> **F = w1 · (absorption moyenne) + w2 · (réduction moyenne) − w3 · (transmission moyenne)**

**L'optimiseur (la partie astucieuse).** La méthode de l'article de recherche
essaie *chaque* mélange possible dans une série de boucles imbriquées — une
"recherche par grille". C'est lent et la précision dépend de la finesse de la
grille. Cette application utilise plutôt **SLSQP** (Sequential Least Squares
Programming, de la bibliothèque SciPy), un **optimiseur continu sous
contraintes**. Il :

- maintient chaque ingrédient dans sa plage autorisée (bornes), et
- force les quatre parts à totaliser exactement 1 (une contrainte d'égalité),

puis converge directement vers le meilleur mélange. Comme l'absorption et la
réduction sont des relations *linéaires* dans les parts des ingrédients et que la
pénalité de transmission se courbe dans le bon sens, le problème possède une
**seule vraie meilleure réponse**, et SLSQP la trouve **exactement en quelques
dizaines de calculs** au lieu de millions. C'est à la fois plus rapide *et* plus
précis que la recherche par grille.

---

## 📐 Les équations (référence)

```
Conservation de la masse : x1 + x2 + x3 + x4 = 1
Poids composite :          γc = x1·γ1 + x2·γ2 + x3·γ3 + x4·γ4
Densité :                  ρc = γc / g            (g = 9,81)
Porosité :                 φ  = a0 + a1·x3 + a2·x4 − a3·x2
Absorption :               α(f) = A0 + A1·φ + A2·x3 + A3·x4 − A4·ρc + A5·log10(f)
Réduction :                Rw(f) = B0 + B1·ρc + B2·e − B3·φ + B4·log10(f)
Transmission :             T(f) = 10^(−Rw(f)/10)
Objectif :                 F = w1·ᾱ + w2·R̄w − w3·T̄
Fréquences (Hz) :          100, 250, 500, 1000, 2000, 4000
```

---

## ⚠️ IMPORTANT — à lire avant de faire confiance aux chiffres

L'article source définit les **formules** ci-dessus mais indique que ses
coefficients (`a0…a3`, `A0…A5`, `B0…B4`) sont **"identifiés expérimentalement"**
et n'en donne **aucune valeur numérique**.

Les constantes fournies dans cette application sont donc des **valeurs
provisoires **, pas les véritables valeurs de référence.
L'application démontre correctement la *méthode*, mais les chiffres exacts en
sortie ne sont **pas validés**.

**Pour la rendre précise :** ouvrez **`config.py`** dans un éditeur de texte
(comme le Bloc-notes), remplacez les valeurs provisoires par de vrais
coefficients expérimentaux/ajustés, enregistrez, puis relancez. Chaque nombre
ajustable se trouve dans ce seul fichier, avec un commentaire en langage clair.

---

## 🧪 Vérifier que tout fonctionne (facultatif)

Les développeurs peuvent lancer les tests de vérification intégrés :

```
python test_engine.py
```

Cela confirme que le mélange totalise toujours 100 %, que tous les chiffres sont
valides, que le résultat reste dans les plages, et que des plages impossibles
donnent un message clair.

---

## 🗂️ Contenu de ce dossier

| Fichier            | Description                                              |
|---------------------|----------------------------------------------------------|
| `run.bat`          | Double-cliquez pour lancer l'application.                |
| `config.py`        | **Le seul fichier à modifier** — tous les nombres s'y trouvent. |
| `app.py`           | L'interface web.                                         |
| `engine.py`        | Les calculs + l'optimiseur (pas besoin d'y toucher).     |
| `test_engine.py`   | Tests de vérification automatisés.                       |
| `requirements.txt` | La liste des paquets logiciels requis par l'application. |

---

## 🩹 Dépannage

- **"Python was not found"** — installez Python et cochez *Add Python to PATH*,
  puis double-cliquez à nouveau sur `run.bat`.
- **L'étape d'installation échoue à installer les paquets** — vérifiez votre
  connexion Internet et relancez `run.bat`.
- **"Please adjust the ranges…"** — vos limites min/max ne peuvent pas totaliser
  100 %. Suivez l'indication affichée à l'écran et élargissez-les.
- **Le navigateur ne s'est pas ouvert** — cherchez dans la fenêtre noire une
  ligne du type `Local URL: http://localhost:8501` et ouvrez cette adresse
  manuellement.

---

## 🚧 Non inclus (travaux futurs possibles)

- L'article mentionne une contrainte optionnelle de **résistance mécanique**
  (σc ≥ σmin) mais ne fournit aucune formule pour celle-ci, donc elle n'est pas
  modélisée.
- La **calibration** réelle des coefficients à partir de mesures de laboratoire.
