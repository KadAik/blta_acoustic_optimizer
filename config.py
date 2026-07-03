# =============================================================================
#  BTLA Acoustic Optimizer — CONFIGURATION
# =============================================================================
#  C'est le SEUL fichier que vous avez besoin de modifier. Changez un nombre,
#  enregistrez, relancez.
#
#
#  Les coefficients expérimentaux (a0..a3, A0..A5, B0..B4) sont des valeurs
#  provisoires. L'article source définit les formules mais pas les constantes
#  numériques. Remplacez-les par de vraies données de laboratoire avant de
#  faire confiance aux résultats.
# =============================================================================

# Accélération de la pesanteur (m/s^2) — utilisée pour la densité rho_c = gamma_c / g
G = 9.81

# Bande de fréquences étudiée (Hz). À modifier si nécessaire.
FREQUENCIES = [100, 250, 500, 1000, 2000, 4000]

# Mélange "optimal attendu" indicatif (utilisé uniquement comme note de
# comparaison dans l'interface — PAS une cible imposée à l'optimiseur).
REFERENCE_MIX = {"x1": 0.75, "x2": 0.08, "x3": 0.10, "x4": 0.07}

# -----------------------------------------------------------------------------
#  DEFAULTS : tous les nombres ajustables utilisés.
# -----------------------------------------------------------------------------
DEFAULTS = {
    # --- Poids volumiques de chaque matériau (N/m^3) --------------------------
    "gamma1": 18000.0,  # Latérite (terre latéritique)
    "gamma2": 31000.0,  # Ciment
    "gamma3": 1500.0,  # Fibre de chiendent (fibres de chiendent)
    "gamma4": 4000.0,  # Sciure de bois
    # --- Modèle de porosité :  phi = a0 + a1*x3 + a2*x4 - a3*x2 --------------
    "a0": 0.35,  # porosité de base
    "a1": 0.45,  # effet de la fibre de chiendent (x3) — augmente la porosité
    "a2": 0.30,  # effet de la sciure (x4)              — augmente la porosité
    "a3": 0.15,  # effet du ciment (x2)                 — diminue la porosité
    # --- Modèle d'absorption :
    #     alpha(f) = A0 + A1*phi + A2*x3 + A3*x4 - A4*rho_c + A5*log10(f) -----
    "A0": 0.05,
    "A1": 0.40,  # porosité -> plus d'absorption
    "A2": 0.15,  # fibre de chiendent -> plus d'absorption
    "A3": 0.10,  # sciure -> plus d'absorption
    "A4": 0.00001,  # densité -> légèrement moins d'absorption (faible)
    "A5": 0.12,  # terme de fréquence
    # --- Modèle de réduction sonore :
    #     Rw(f) = B0 + B1*rho_c + B2*e - B3*phi + B4*log10(f) ----------------
    "B0": 10.0,
    "B1": 0.005,  # densité -> plus de réduction (blocs plus lourds = mieux)
    "B2": 150.0,  # épaisseur -> plus de réduction
    "B3": 5.0,  # porosité -> moins de réduction
    "B4": 4.5,  # terme de fréquence
    # --- Géométrie du bloc ---------------------------------------------------
    "e": 0.15,  # Épaisseur de la brique (m)
    # --- Pondération des objectifs :  F = w1*mean(alpha) + w2*mean(Rw) - w3*mean(T) ---
    "w1": 1.0,  # récompense l'absorption
    "w2": 1.0,  # récompense la réduction sonore
    "w3": 1.0,  # pénalise la transmission
    # --- Plages de mélange autorisées (fractions, 0..1). L'optimiseur cherche à l'intérieur. ---
    #     La proportion de chaque matériau reste entre *_min et *_max, et les
    #     quatre doivent totaliser exactement 1 (100 %).
    "x1_min": 0.50,
    "x1_max": 0.85,  # Latérite
    "x2_min": 0.05,
    "x2_max": 0.20,  # Ciment
    "x3_min": 0.02,
    "x3_max": 0.15,  # Fibre de chiendent
    "x4_min": 0.02,
    "x4_max": 0.15,  # Sciure
}
