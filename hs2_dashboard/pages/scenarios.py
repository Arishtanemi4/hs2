from dash import dcc, html
from ..config.theme import C, _ha
from ..components import card, card_title, section_header, badge
from ..figures import fig_sensitivity
from ..data import PARAMS


def _cluster_card(kind: str, label: str, pct_id: str, default_pct: str, subtitle: str, desc: str) -> html.Div:
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


def _build_slider_controls() -> list:
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


def render_scenarios() -> html.Div:
    return html.Div([
        section_header("Scenario cluster analysis",
                       "10,000 Monte Carlo simulations grouped into 3 outcome clusters. Adjust parameters to update probabilities live."),

        html.Div([
            _cluster_card("pos", "Controlled Delivery",    "pos-pct-live", "18",
                          "Cost: <£90bn · Opens: 2037–38",
                          "Inflation below 4%, no scope change, KPI score >2.2 — all three simultaneously. Historically present for at most 18 months at a time."),
            _cluster_card("neu", "Managed Overrun",        "neu-pct-live", "45",
                          "Cost: £90–110bn · Opens: 2039–41",
                          "Current trajectory. Reflects 13 years of precedent. Most likely single outcome."),
            _cluster_card("neg", "Escalation / Intervention", "neg-pct-live", "37",
                          "Cost: >£110bn · Opens: 2043+ or cancelled",
                          "Triggered by: political review post-2028 election, contractor failure, inflation spike."),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)", "gap": "10px", "marginBottom": "14px"}),

        html.Div([
            html.Div(card([
                card_title("Parameter controls — drag to simulate"),
                html.Div(_build_slider_controls()),
            ]), style={"flex": "1"}),
            html.Div([
                card([
                    card_title("Cluster probability — live simulation"),
                    dcc.Graph(id="live-cluster-chart", config={"displayModeBar": False}, style={"height": "200px"}),
                ]),
                html.Div(style={"height": "12px"}),
                card([
                    card_title("Parameter sensitivity — impact on outcome"),
                    dcc.Graph(figure=fig_sensitivity(PARAMS), config={"displayModeBar": False}, style={"height": "220px"}),
                ]),
            ], style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "0"}),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "14px"}),

        card([
            card_title("Monte Carlo fan chart — cost forecast to 2040", badge("10,000 paths", "neg")),
            dcc.Graph(id="fan-chart", config={"displayModeBar": False}, style={"height": "280px"}),
        ]),
        html.Div(style={"height": "12px"}),
        card([
            card_title("Cost distribution — simulation results"),
            dcc.Graph(id="cost-histogram", config={"displayModeBar": False}, style={"height": "220px"}),
        ]),

    ], style={"padding": "1.5rem 2rem"})
