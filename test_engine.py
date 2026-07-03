"""
Tests de vérification automatisés pour le moteur BTLA.
Lancer avec :  python test_engine.py

Ce sont des assertions légères (aucun framework de test nécessaire) qui
confirment que la physique et l'optimiseur se comportent correctement.
"""

import math

from config import DEFAULTS, FREQUENCIES
import engine


def base_params(**overrides):
    p = dict(DEFAULTS)
    p["frequencies"] = FREQUENCIES
    p.update(overrides)
    return p


def test_mass_conservation():
    """Les fractions optimisées doivent totaliser exactement 1 (loi physique)."""
    res = engine.optimize_composition(base_params())
    total = sum(res["composition"])
    assert math.isclose(total, 1.0, abs_tol=1e-6), f"sum was {total}"
    print(f"  [ok] conservation de la masse : somme = {total:.6f}")


def test_metrics_finite():
    """Tous les nombres rapportés doivent être finis (pas de NaN/inf)."""
    res = engine.optimize_composition(base_params())
    m = res["metrics"]
    for key in ("gamma_c", "rho_c", "phi", "alpha_mean", "Rw_mean", "T_mean", "F"):
        assert math.isfinite(m[key]), f"{key} was not finite: {m[key]}"
    for seq in (m["alpha"], m["Rw"], m["T"]):
        assert all(math.isfinite(v) for v in seq)
    print("  [ok] toutes les métriques sont finies")


def test_within_bounds():
    """Chaque fraction doit respecter sa plage autorisée."""
    p = base_params()
    comp = engine.optimize_composition(p)["composition"]
    bounds = [(p["x1_min"], p["x1_max"]), (p["x2_min"], p["x2_max"]),
              (p["x3_min"], p["x3_max"]), (p["x4_min"], p["x4_max"])]
    for xi, (lo, hi) in zip(comp, bounds):
        assert lo - 1e-6 <= xi <= hi + 1e-6, f"{xi} outside [{lo}, {hi}]"
    print(f"  [ok] composition dans les plages : "
          f"{[round(c, 3) for c in comp]}")


def test_reference_ballpark():
    """Avec les coefficients par défaut, l'optimum doit être dominé par la
    latérite, proche du mélange indicatif 75/8/10/7 de l'article."""
    comp = engine.optimize_composition(base_params())["composition"]
    assert comp[0] >= 0.50, f"laterite fraction unexpectedly low: {comp[0]}"
    print(f"  [ok] optimum dominé par la latérite : latérite = {comp[0]*100:.1f}%")


def test_infeasible_ranges_message():
    """Des plages impossibles doivent lever une erreur claire et spécifique."""
    try:
        engine.optimize_composition(base_params(
            x1_min=0.9, x2_min=0.9, x3_min=0.9, x4_min=0.9))
    except engine.InfeasibleRangesError as e:
        print(f"  [ok] erreur de plage impossible levée correctement")
        assert "100%" in str(e)
    else:
        raise AssertionError("expected InfeasibleRangesError, none raised")


if __name__ == "__main__":
    print("Exécution des tests de vérification du moteur BTLA...")
    test_mass_conservation()
    test_metrics_finite()
    test_within_bounds()
    test_reference_ballpark()
    test_infeasible_ranges_message()
    print("Tous les tests sont passés.")
