"""
BTLA Acoustic Optimizer — INTERFACE WEB
========================================

Lancer avec :  streamlit run app.py   (ou double-cliquer sur run.bat)

Ceci est une application mono-processus.
"""

import plotly.graph_objects as go
import streamlit as st

import engine
from config import DEFAULTS, FREQUENCIES, REFERENCE_MIX

st.set_page_config(page_title="BTLA Acoustic Optimizer", layout="wide")

st.title("BTLA Acoustic Optimizer")
st.caption(
    "Trouve le meilleur mélange de latérite + ciment + fibre de chiendent + "
    "sciure pour la performance acoustique."
)

st.warning(
    "Modifiez les valeurs dans `config.py` pour intégrer de vraies données de "
    "laboratoire. Cela inclut les coefficients expérimentaux (a0..a3, A0..A5, "
    "B0..B4) et la bande de fréquences. "
    "Ce n'est qu'ensuite que l'optimiseur produira des résultats scientifiquement valides."
)

# -----------------------------------------------------------------------------
#  Barre latérale : entrées
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("1 · Poids volumiques (N/m³)")
    g1 = st.number_input("Latérite (γ1)", value=DEFAULTS["gamma1"], step=500.0)
    g2 = st.number_input("Ciment (γ2)", value=DEFAULTS["gamma2"], step=500.0)
    g3 = st.number_input(
        "Fibre de chiendent (γ3)", value=DEFAULTS["gamma3"], step=100.0
    )
    g4 = st.number_input("Sciure (γ4)", value=DEFAULTS["gamma4"], step=100.0)

    st.header("2 · Plages de mélange autorisées")
    st.caption(
        "L'optimiseur cherche à l'intérieur de ces plages ; les quatre doivent totaliser 100 %."
    )
    x1_b = st.slider(
        "Plage latérite", 0.0, 1.0, (DEFAULTS["x1_min"], DEFAULTS["x1_max"])
    )
    x2_b = st.slider("Plage ciment", 0.0, 1.0, (DEFAULTS["x2_min"], DEFAULTS["x2_max"]))
    x3_b = st.slider(
        "Plage fibre de chiendent", 0.0, 1.0, (DEFAULTS["x3_min"], DEFAULTS["x3_max"])
    )
    x4_b = st.slider("Plage sciure", 0.0, 1.0, (DEFAULTS["x4_min"], DEFAULTS["x4_max"]))

    st.header("3 · Épaisseur de la brique (m)")
    thick = st.number_input(
        "Épaisseur (e)", value=DEFAULTS["e"], step=0.01, format="%.3f"
    )

    st.header("4 · Pondération des objectifs")
    w1 = st.slider("Récompenser l'absorption (w1)", 0.0, 5.0, DEFAULTS["w1"], 0.1)
    w2 = st.slider(
        "Récompenser la réduction sonore (w2)", 0.0, 5.0, DEFAULTS["w2"], 0.1
    )
    w3 = st.slider("Pénaliser la transmission (w3)", 0.0, 5.0, DEFAULTS["w3"], 0.1)


def build_params():
    """Assemble le dictionnaire complet des paramètres à partir des valeurs par défaut de config + des entrées de la barre latérale."""
    params = dict(DEFAULTS)  # part de tous les coefficients
    params.update(
        {
            "gamma1": g1,
            "gamma2": g2,
            "gamma3": g3,
            "gamma4": g4,
            "x1_min": x1_b[0],
            "x1_max": x1_b[1],
            "x2_min": x2_b[0],
            "x2_max": x2_b[1],
            "x3_min": x3_b[0],
            "x3_max": x3_b[1],
            "x4_min": x4_b[0],
            "x4_max": x4_b[1],
            "e": thick,
            "w1": w1,
            "w2": w2,
            "w3": w3,
            "frequencies": FREQUENCIES,
        }
    )
    return params


# -----------------------------------------------------------------------------
#  Principal : calcul + affichage
# -----------------------------------------------------------------------------
if st.button(
    "Calculer le mélange optimal",
    type="primary",
    help="Cliquez pour lancer l'optimiseur avec les entrées actuelles",
    icon="⚡",
):
    try:
        result = engine.optimize_composition(build_params())
    except engine.InfeasibleRangesError as e:
        st.error(f"Veuillez ajuster les plages — {e}")
    except Exception as e:  # noqa: BLE001 — signale gentiment toute erreur inattendue
        st.error(f"Une erreur est survenue pendant le calcul : {e}")
    else:
        comp = result["composition"]
        m = result["metrics"]

        st.subheader("Composition optimale", divider="─")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latérite", f"{comp[0]*100:.1f}%")
        c2.metric("Ciment", f"{comp[1]*100:.1f}%")
        c3.metric("Fibre de chiendent", f"{comp[2]*100:.1f}%")
        c4.metric("Sciure", f"{comp[3]*100:.1f}%")

        total = sum(comp)
        st.success(
            f"✅ Vérification de la conservation de la masse : les fractions "
            f"totalisent **{total:.3f}** (doit être 1.000)."
        )

        st.subheader("Performance prédite")
        p1, p2, p3 = st.columns(3)
        p1.metric("Absorption moyenne α", f"{m['alpha_mean']:.3f}")
        p2.metric("Réduction sonore moyenne Rw", f"{m['Rw_mean']:.1f} dB")
        p3.metric("Porosité Φ", f"{m['phi']*100:.1f}%")

        # Comparaison avec le mélange de référence indicatif de l'article ?
        ref = REFERENCE_MIX
        st.caption(
            f"À titre de référence, l'optimum indicatif de l'article est "
            f"{ref['x1']*100:.0f}/{ref['x2']*100:.0f}/{ref['x3']*100:.0f}/"
            f"{ref['x4']*100:.0f}% (latérite/ciment/fibre/sciure)."
        )

        # Graphique du spectre : absorption + réduction en fonction de la fréquence (double axe)
        freqs = [str(f) for f in m["frequencies"]]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=freqs,
                y=m["alpha"],
                name="Absorption α(f)",
                mode="lines+markers",
                yaxis="y1",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=freqs,
                y=m["Rw"],
                name="Réduction Rw(f) [dB]",
                mode="lines+markers",
                yaxis="y2",
            )
        )
        fig.update_layout(
            title="Performance acoustique selon la fréquence",
            xaxis=dict(title="Fréquence (Hz)", type="category"),
            yaxis=dict(title="Absorption α", rangemode="tozero"),
            yaxis2=dict(
                title="Réduction Rw (dB)",
                overlaying="y",
                side="right",
                rangemode="tozero",
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Afficher tous les chiffres"):
            st.write(
                {
                    "poids composite γc (N/m³)": round(m["gamma_c"], 1),
                    "densité composite ρc (kg/m³)": round(m["rho_c"], 1),
                    "transmission moyenne T": round(m["T_mean"], 5),
                    "objectif F": round(m["F"], 4),
                }
            )
else:
    st.info(
        "Définissez vos entrées dans la barre latérale, puis cliquez sur **Calculer le mélange optimal**."
    )
