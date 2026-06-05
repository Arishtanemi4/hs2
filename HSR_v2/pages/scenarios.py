from dash import html, dcc

from config.theme import C, _ha
from data.hs2_data import PARAMS
from models.monte_carlo import run_monte_carlo
from components.ui_components import card, card_title, section_header, narrative_box, badge
from charts.simulation_charts import (
    fig_sensitivity, fig_migration_heatmap, fig_positive_surface, fig_scenario_matrix
)


def _build_slider_controls():
    controls = []
    for p in PARAMS:
        controls.append(html.Div([
            html.Div([
                html.Span(p["label"], style={"fontSize": "12px", "color": C["text"]}),
                html.Span(id=f"val-{p['id']}", children=str(p["val"]),
                          style={"fontSize": "12px", "fontFamily": "DM Mono,monospace", "color": C["acc"]}),
            ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "6px"}),
            dcc.Slider(
                id=f"slider-{p['id']}",
                min=p["min"], max=p["max"], step=p["step"], value=p["val"],
                marks=None, tooltip={"always_visible": False},
                updatemode="drag",
            ),
        ], style={"marginBottom": "18px"}))
    return controls


def _cluster_card(kind, label, pct_id, default_pct, subtitle, desc):
    col_map = {"pos": C["pos"], "neu": C["neu"], "neg": C["neg"]}
    col = col_map[kind]
    return html.Div([
        html.Div(id=pct_id, children=default_pct + "%",
                 style={"fontFamily": "Fraunces,serif", "fontSize": "44px", "fontWeight": "300",
                        "letterSpacing": "-2px", "lineHeight": "1", "color": col}),
        html.Div(label, style={"fontSize": "11px", "fontFamily": "DM Mono,monospace",
                               "textTransform": "uppercase", "letterSpacing": "0.1em",
                               "color": col, "margin": "6px 0"}),
        html.Div(subtitle, style={"fontSize": "12px", "color": C["muted"], "marginBottom": "8px"}),
        html.Div(desc,     style={"fontSize": "12px", "color": C["text"], "lineHeight": "1.5", "opacity": "0.85"}),
    ], style={"borderRadius": "10px", "border": f"1px solid {col}44", "padding": "16px",
              "background": _ha(col, 0.07)})


def _scenario_row(name, params, baseline):
    mc  = run_monte_carlo(n_sims=2000, **params)
    cp  = mc["cluster_probs"]
    d_pos = cp["pos"] - baseline["pos"]
    d_neg = cp["neg"] - baseline["neg"]

    def delta(v):
        col  = C["pos"] if v < -1 else (C["neg"] if v > 1 else C["muted"])
        sign = "+" if v > 0 else ""
        return html.Span(f"{sign}{v:.0f}pp",
            style={"fontSize": "10px", "fontFamily": "DM Mono,monospace", "color": col,
                   "marginLeft": "4px", "flexShrink": "0"})

    total = cp["pos"] + cp["neu"] + cp["neg"]
    bar = html.Div([
        html.Div(style={"width": f"{cp['pos']/total*100:.0f}%", "height": "8px",
                        "background": C["pos"], "borderRadius": "2px 0 0 2px"}),
        html.Div(style={"width": f"{cp['neu']/total*100:.0f}%", "height": "8px", "background": C["neu"]}),
        html.Div(style={"width": f"{cp['neg']/total*100:.0f}%", "height": "8px",
                        "background": C["neg"], "borderRadius": "0 2px 2px 0"}),
    ], style={"display": "flex", "width": "100%", "borderRadius": "2px", "overflow": "hidden"})

    return html.Div([
        html.Span(name, style={"fontSize": "12px", "color": C["text"], "width": "140px",
                               "flexShrink": "0", "fontWeight": "500"}),
        html.Div(bar, style={"flex": "1", "display": "flex", "alignItems": "center"}),
        html.Span(f"pos {cp['pos']:.0f}%", style={"fontSize": "11px", "color": C["pos"],
                  "fontFamily": "DM Mono,monospace", "width": "55px", "textAlign": "right", "flexShrink": "0"}),
        delta(d_pos),
        html.Span(f"neg {cp['neg']:.0f}%", style={"fontSize": "11px", "color": C["neg"],
                  "fontFamily": "DM Mono,monospace", "width": "55px", "textAlign": "right",
                  "flexShrink": "0", "marginLeft": "8px"}),
        delta(d_neg),
    ], style={"display": "flex", "alignItems": "center", "gap": "8px", "padding": "7px 0",
              "borderBottom": f"1px solid {C['border']}"})


def _build_scenario_narrative(cp):
    pos, neu, neg = cp["pos"], cp["neu"], cp["neg"]
    dominant = "pos" if pos == max(pos, neu, neg) else ("neg" if neg == max(pos, neu, neg) else "neu")
    if dominant == "pos":
        tone = (f"Current parameters place the project in a relatively constructive position — "
                f"{pos:.0f}% of simulations end in controlled delivery. "
                f"This is above the historical base rate of ~18%. Inflation and KPI score are the "
                f"parameters most responsible for this improvement.")
    elif dominant == "neg":
        tone = (f"Current parameters push the majority of simulations toward escalation or intervention "
                f"({neg:.0f}% negative cluster). The dominant risk drivers are inflation trajectory "
                f"and political risk. A single parameter moving adversely could push this above 50%.")
    else:
        tone = (f"The managed overrun cluster ({neu:.0f}%) dominates — the most likely single outcome "
                f"and consistent with 13 years of HS2 precedent. This is the 'default future' unless "
                f"parameters shift materially in either direction.")
    return narrative_box(
        "Scenario narrative — current parameter state",
        tone + f"\n\nPositive: {pos:.0f}%  ·  Neutral: {neu:.0f}%  ·  Negative: {neg:.0f}%",
        id_body="scenario-narr-body")


_NAMED_SCENARIOS = [
    ("Baseline",         dict(inflation=5,  scope_risk=35, political_risk=40, kpi_score=2.35, workforce_stability=55, euston_prob=30)),
    ("Inflation spike",  dict(inflation=10, scope_risk=35, political_risk=40, kpi_score=2.35, workforce_stability=55, euston_prob=30)),
    ("Political review", dict(inflation=5,  scope_risk=35, political_risk=80, kpi_score=2.35, workforce_stability=55, euston_prob=30)),
    ("Leadership reset", dict(inflation=5,  scope_risk=35, political_risk=40, kpi_score=1.9,  workforce_stability=30, euston_prob=15)),
    ("KPI + Euston win", dict(inflation=5,  scope_risk=20, political_risk=30, kpi_score=2.7,  workforce_stability=75, euston_prob=70)),
    ("Perfect storm",    dict(inflation=11, scope_risk=75, political_risk=85, kpi_score=1.8,  workforce_stability=20, euston_prob=5)),
    ("Best case",        dict(inflation=2,  scope_risk=10, political_risk=15, kpi_score=2.9,  workforce_stability=90, euston_prob=90)),
]


def render_scenarios():
    mc_base  = run_monte_carlo(n_sims=5000)
    cp_base  = mc_base["cluster_probs"]
    slider_controls = _build_slider_controls()

    return html.Div([
        section_header(
            "Monte Carlo cluster forecasting",
            "10,000 simulations per run. Drag any parameter to recompute cluster probabilities live. "
            "Compare scenarios, explore parameter sweeps, and interrogate cluster migration paths."),

        html.Div([
            _cluster_card("pos", "Controlled delivery", "pos-pct-live", f"{cp_base['pos']:.0f}",
                          "Cost: <£90bn · Opens: 2037–38",
                          "Inflation <4%, no scope change, KPI >2.2 — all simultaneously."),
            _cluster_card("neu", "Managed overrun", "neu-pct-live", f"{cp_base['neu']:.0f}",
                          "Cost: £90–115bn · Opens: 2039–41",
                          "Current trajectory. Reflects 13 years of precedent."),
            _cluster_card("neg", "Escalation / intervention", "neg-pct-live", f"{cp_base['neg']:.0f}",
                          "Cost: >£115bn · Opens: 2043+ or cancelled",
                          "Triggered by: political review, contractor failure, inflation spike."),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)", "gap": "10px", "marginBottom": "14px"}),

        html.Div([
            html.Div(card([
                card_title("Parameter controls", html.Span("drag to recompute",
                    style={"fontSize": "10px", "color": C["muted"], "fontFamily": "DM Mono,monospace"})),
                html.Div(slider_controls),
            ]), style={"flex": "1"}),
            html.Div([
                card([
                    card_title("Live cluster split"),
                    dcc.Graph(id="live-cluster-chart",
                              config={"displayModeBar": False}, style={"height": "180px"}),
                ]),
                html.Div(style={"height": "10px"}),
                card([
                    card_title("Parameter sensitivity"),
                    dcc.Graph(figure=fig_sensitivity(PARAMS),
                              config={"displayModeBar": False}, style={"height": "200px"}),
                ]),
            ], style={"flex": "1", "display": "flex", "flexDirection": "column"}),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),

        html.Div([
            card([
                card_title("Cost forecast fan — Monte Carlo paths to 2040", badge("updates live", "acc")),
                dcc.Graph(id="fan-chart", config={"displayModeBar": False}, style={"height": "240px"}),
            ]),
            card([
                card_title("Cost distribution — simulation histogram", badge("cluster boundaries", "neu")),
                dcc.Graph(id="cost-histogram", config={"displayModeBar": False}, style={"height": "240px"}),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "12px"}),

        card([
            card_title("Parameter sweep — how each input shifts cluster probabilities",
                       badge("one parameter at a time", "acc")),
            html.Div([
                html.Div([
                    html.Div(id="sweep-param-selector", children=html.Div([
                        html.Button(p["label"], id=f"sweep-btn-{p['id']}",
                            n_clicks=0 if p["id"] != "inflation" else 1,
                            style={"fontSize": "11px", "padding": "5px 12px",
                                   "border": f"1px solid {C['border2']}",
                                   "borderRadius": "20px", "cursor": "pointer",
                                   "background": _ha(C["acc"], 0.15) if p["id"] == "inflation" else C["bg3"],
                                   "color": C["acc"] if p["id"] == "inflation" else C["muted"],
                                   "fontFamily": "DM Mono,monospace", "marginBottom": "6px",
                                   "width": "100%", "textAlign": "left"})
                        for p in PARAMS
                    ], style={"display": "flex", "flexDirection": "column", "gap": "4px"})),
                ], style={"width": "180px", "flexShrink": "0"}),
                html.Div(
                    dcc.Graph(id="sweep-chart", config={"displayModeBar": False}, style={"height": "280px"}),
                    style={"flex": "1"}),
            ], style={"display": "flex", "gap": "14px"}),
        ], style={"marginBottom": "12px"}),

        card([
            card_title("Named scenario comparison — cluster probabilities across key futures",
                       badge("7 scenarios", "neu")),
            dcc.Graph(id="scenario-matrix-chart",
                      config={"displayModeBar": False}, style={"height": "320px"}),
            html.Div([
                html.Div([
                    _scenario_row(name, params, baseline=cp_base)
                    for name, params in _NAMED_SCENARIOS
                ]),
            ], style={"marginTop": "12px"}),
        ], style={"marginBottom": "12px"}),

        html.Div([
            card([
                card_title("Cluster migration — inflation × political risk", badge("how pairs interact", "pu")),
                dcc.Graph(figure=fig_migration_heatmap(),
                          config={"displayModeBar": False}, style={"height": "260px"}),
            ]),
            card([
                card_title("Positive cluster probability surface", badge("inflation × KPI", "pos")),
                dcc.Graph(figure=fig_positive_surface(),
                          config={"displayModeBar": False}, style={"height": "260px"}),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "12px"}),

        html.Div(id="scenario-narrative-box",
                 children=_build_scenario_narrative(cp_base)),

    ], style={"padding": "1.5rem 2rem"})
