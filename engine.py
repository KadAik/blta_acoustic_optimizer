"""
BTLA Acoustic Optimizer — MOTEUR DE CALCUL
===========================================

Ce module :
  1. Calcule les métriques acoustiques pour un mélange donné (calculate_metrics).
  2. Trouve le meilleur mélange par optimisation continue SLSQP (optimize_composition).

Les formules sont tirées directement de l'article de recherche YAMONCHE (section 25).

POURQUOI SLSQP PLUTÔT QU'UNE BOUCLE FOR :
  Le pseudo-code de l'article lui-même parcourt tous les mélanges possibles
  (une recherche par grille). C'est lent et la précision dépend du pas de la
  grille. Ici, l'objectif est mathématiquement "concave sur une région
  convexe" (l'absorption/réduction sont linéaires dans le mélange, la
  pénalité de transmission est concave), ce qui signifie qu'il existe une
  seule meilleure réponse et que SLSQP la trouve exactement en quelques
  dizaines d'essais au lieu de millions.
"""

import numpy as np
from scipy.optimize import minimize

from config import G


class InfeasibleRangesError(ValueError):
    """Levée lorsque les plages min/max choisies ne peuvent pas totaliser 100 %."""


def calculate_metrics(x, params):
    """Calcule toutes les grandeurs physiques + acoustiques pour un mélange x = [x1,x2,x3,x4].

    Renvoie un dict contenant le poids/densité composite, la porosité, les
    spectres par fréquence (alpha, Rw, T), leurs moyennes, et la valeur de
    l'objectif F.
    """
    x = np.asarray(x, dtype=float)

    gamma = np.array(
        [params["gamma1"], params["gamma2"], params["gamma3"], params["gamma4"]]
    )

    # Poids volumique composite et densité équivalente
    gamma_c = float(np.dot(x, gamma))
    rho_c = gamma_c / G

    # Porosité estimée :  phi = a0 + a1*x3 + a2*x4 - a3*x2
    phi = params["a0"] + params["a1"] * x[2] + params["a2"] * x[3] - params["a3"] * x[1]

    # Performance dépendant de la fréquence (vectorisée sur toutes les fréquences)
    frequencies = np.array(params["frequencies"], dtype=float)
    log_f = np.log10(frequencies)

    alpha = (
        params["A0"]
        + params["A1"] * phi
        + params["A2"] * x[2]
        + params["A3"] * x[3]
        - params["A4"] * rho_c
        + params["A5"] * log_f
    )

    Rw = (
        params["B0"]
        + params["B1"] * rho_c
        + params["B2"] * params["e"]
        - params["B3"] * phi
        + params["B4"] * log_f
    )

    T = 10.0 ** (-Rw / 10.0)

    alpha_mean = float(np.mean(alpha))
    Rw_mean = float(np.mean(Rw))
    T_mean = float(np.mean(T))

    # Objectif : récompense l'absorption + la réduction, pénalise la transmission
    F = params["w1"] * alpha_mean + params["w2"] * Rw_mean - params["w3"] * T_mean

    return {
        "gamma_c": gamma_c,
        "rho_c": rho_c,
        "phi": float(phi),
        "frequencies": frequencies.tolist(),
        "alpha": alpha.tolist(),
        "Rw": Rw.tolist(),
        "T": T.tolist(),
        "alpha_mean": alpha_mean,
        "Rw_mean": Rw_mean,
        "T_mean": T_mean,
        "F": float(F),
    }


def _bounds_from(params):
    return [
        (params["x1_min"], params["x1_max"]),
        (params["x2_min"], params["x2_max"]),
        (params["x3_min"], params["x3_max"]),
        (params["x4_min"], params["x4_max"]),
    ]


def optimize_composition(params):
    """Trouve le mélange qui maximise l'objectif F, sous réserve que :
        - chaque matériau reste dans sa plage [min, max], et
        - les quatre fractions totalisent exactement 1 (100 %).

    Lève InfeasibleRangesError si les plages rendent
    cela impossible.
    """
    bounds = _bounds_from(params)
    lows = np.array([b[0] for b in bounds])
    highs = np.array([b[1] for b in bounds])

    # --- Vérification de faisabilité préalable -----------------------
    # Le plan x1+x2+x3+x4 = 1 doit intersecter la boîte des plages autorisées.
    if lows.sum() > 1.0 + 1e-9:
        raise InfeasibleRangesError(
            f"Les proportions minimales totalisent {lows.sum()*100:.0f}%, ce qui "
            "dépasse 100%. Réduisez certains minimums pour que le mélange puisse totaliser 100%."
        )
    if highs.sum() < 1.0 - 1e-9:
        raise InfeasibleRangesError(
            f"Les proportions maximales ne totalisent que {highs.sum()*100:.0f}%, "
            "ce qui est inférieur à 100%. Augmentez certains maximums pour que le mélange puisse totaliser 100%."
        )

    def objective(x):
        return -calculate_metrics(x, params)["F"]  # négation : minimiseur -> maximiser

    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1.0},)

    # Point de départ faisable : milieu de chaque plage (corrige le
    # [0.25,0.25,0.25,0.25] du cahier des charges qui viole la borne par
    # défaut x1 >= 0.50).
    x0_mid = (lows + highs) / 2.0

    # Multi-démarrage léger : le point milieu plus quelques graines aléatoires
    # faisables. Le problème est convexe donc un seul départ suffit, mais
    # c'est une assurance peu coûteuse.
    rng = np.random.default_rng(0)
    starts = [x0_mid] + [lows + rng.random(4) * (highs - lows) for _ in range(4)]

    best = None  # meilleur résultat trouvé jusqu'à présent (point de départ).
    for x0 in starts:
        res = minimize(
            objective, x0, method="SLSQP", bounds=bounds, constraints=constraints
        )
        if res.success and (best is None or res.fun < best.fun):
            best = res

    if best is None:
        raise InfeasibleRangesError(
            "L'optimiseur n'a trouvé aucun mélange valide dans ces plages. "
            "Essayez d'élargir les plages min/max pour qu'elles puissent totaliser 100%."
        )

    return {
        "composition": best.x.tolist(),
        "metrics": calculate_metrics(best.x, params),
    }
