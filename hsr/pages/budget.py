from dash import html, dcc

from config.theme import C, _ha
from data.hs2_data import PARAMS, VIABILITY_DATA
from models.viability import pred_sentiment, _build_viability_scenarios
from components.ui_components import (
    stat_card, card, card_title, section_header, narrative_box, badge
)
from charts.viability_charts import (
    fig_scatter_correlation, fig_viability_envelope,
    fig_sentiment_forecast, fig_sentiment_gauge, fig_cpkm_gauge
)
from charts.cost_charts import fig_cost_evolution_dual
from charts.simulation_charts import fig_donut_clusters, fig_mc_cluster_bar


def render_budget():
    V            = VIABILITY_DATA
    current_sent = pred_sentiment(V["cost_mid"][-1], V["network_km"][-1])
    max_cost_540 = round(V["threshold_cpkm"] * 540, 0)
    max_cost_225 = round(V["threshold_cpkm"] * 225, 0)

    return html.Div([
        section_header(
            "Cost–Network–Sentiment: viability analysis",
            "Correlation between cost escalation, network scope, and public sentiment. "
            "Model: sentiment ~ -0.370 × ln(cost/km) - 1.124  |  R²=0.838, p=0.004. "
            "Sentiment scores are proxy indices (not official surveys). "
            "Causation inferred; confounders acknowledged."),

        html.Div([
            stat_card("Current cost/km",      "£0.423bn/km",  "£95.2bn / 225km (2026)",         "3× above viability threshold", "neg"),
            stat_card("Viability threshold",  "£0.142bn/km",  "Sentiment stays above −0.40",    "Based on log-linear model", "neu"),
            stat_card("Max cost @ 225km",     f"£{max_cost_225:.0f}bn",
                      "Phase 1 — threshold already passed in 2012",
                      "Project exceeded this at original approval", "neg"),
            stat_card("Max cost @ 540km",     f"£{max_cost_540:.0f}bn",
                      "Full network would restore viability",
                      "Only viable if cost stays below £76bn", "neu"),
            stat_card("Model fit",            "R² = 0.838",   "p = 0.004 (7 data points)",      "Log-linear OLS on cost/km", "acc"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(5,1fr)",
                  "gap": "10px", "marginBottom": "14px"}),

        narrative_box(
            "Viability engine — key finding",
            ("The data reveals a structural paradox at the heart of HS2's political position. "
             "Parliamentary sentiment is strongly correlated with cost-per-km (r=−0.84) rather than "
             "raw cost alone — suggesting the public and their representatives intuitively judge "
             "value-for-money, not just headline price. As Phase 2 was cancelled in 2023, the "
             "network halved but cost barely fell — pushing cost-per-km from £0.17bn to £0.42bn "
             "and sentiment below the viability threshold. "
             "The model implies: restoring the full 540km network at current cost (£95bn) would "
             "predict a sentiment of −0.48, still below the threshold but far better than −0.81. "
             "The only path to a viable project is either significantly reducing cost OR "
             "significantly expanding network scope — doing neither, as now, is the worst of both worlds."),
            id_body="narr-viability"),
        html.Div(style={"height": "12px"}),

        html.Div([
            card([
                card_title("Correlation: cost-per-km vs sentiment", badge("R²=0.838", "acc")),
                dcc.Graph(figure=fig_scatter_correlation(),
                          config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
            card([
                card_title("Cost and network scope over time"),
                dcc.Graph(figure=fig_cost_evolution_dual(),
                          config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "12px"}),

        card([
            card_title("Viability envelope — which (cost, network) combinations are politically survivable?",
                       badge("Viable zone = sentiment > −0.40", "neu")),
            dcc.Graph(figure=fig_viability_envelope(),
                      config={"displayModeBar": False}, style={"height": "360px"}),
            html.Div([
                html.P([
                    html.Strong("How to read this: ", style={"color": C["text"]}),
                    "Each point on the heatmap is a (cost, network size) combination. "
                    "Green = sentiment predicted above −0.40 (politically survivable). "
                    "Red = below threshold. The dashed white line is the viability boundary: "
                    "£0.142bn per km. White dots are actual HS2 cost/scope at each revision year. "
                    "The trajectory moves right (cost rising) and down (network shrinking) — "
                    "directly toward the most unviable corner.",
                ], style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.6", "marginTop": "10px"}),
            ]),
        ], style={"marginBottom": "12px"}),

        card([
            card_title("Sentiment forecast: what-if cost changes for each network scenario"),
            dcc.Graph(figure=fig_sentiment_forecast(),
                      config={"displayModeBar": False}, style={"height": "280px"}),
        ], style={"marginBottom": "12px"}),

        card([
            card_title("Viability scenarios — maximum cost before sentiment crosses threshold"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th(h, style={"padding": "7px 12px", "color": C["muted"], "fontWeight": "400",
                                      "fontFamily": "DM Mono,monospace", "fontSize": "10px",
                                      "textTransform": "uppercase", "letterSpacing": "0.06em",
                                      "borderBottom": f"1px solid {C['border']}"})
                    for h in ["Network scenario", "Route km", "Max viable cost",
                              "Cost/km threshold", "Current sentiment", "Status"]
                ])),
                html.Tbody([html.Tr([
                    html.Td(sc["name"],
                        style={"padding": "9px 12px", "color": C["text"], "fontSize": "13px",
                               "fontWeight": "500", "borderBottom": f"1px solid {C['border']}"}),
                    html.Td(f"{sc['km']}km",
                        style={"padding": "9px 12px", "color": C["muted"], "fontSize": "12px",
                               "fontFamily": "DM Mono,monospace", "borderBottom": f"1px solid {C['border']}"}),
                    html.Td(f"£{sc['max_cost']:.0f}bn",
                        style={"padding": "9px 12px", "color": C["neu"], "fontSize": "12px",
                               "fontFamily": "DM Mono,monospace", "fontWeight": "500",
                               "borderBottom": f"1px solid {C['border']}"}),
                    html.Td("£0.142bn/km",
                        style={"padding": "9px 12px", "color": C["muted"], "fontSize": "11px",
                               "fontFamily": "DM Mono,monospace", "borderBottom": f"1px solid {C['border']}"}),
                    html.Td(f"{sc['current_sent']:.2f}",
                        style={"padding": "9px 12px",
                               "color": C["neg"] if sc["current_sent"] < V["threshold_sent"] else C["pos"],
                               "fontSize": "12px", "fontFamily": "DM Mono,monospace",
                               "borderBottom": f"1px solid {C['border']}"}),
                    html.Td(
                        badge("UNVIABLE", "neg") if sc["current_sent"] < V["threshold_sent"] else badge("VIABLE", "pos"),
                        style={"padding": "9px 12px", "borderBottom": f"1px solid {C['border']}"}),
                ]) for sc in _build_viability_scenarios()]),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
            html.Div([
                html.P([
                    html.Strong("Methodology note: ", style={"color": C["text"]}),
                    "Sentiment scores are proxy indices derived from qualitative signals "
                    "(PAC hearings, media coverage, parliamentary questions) — not official surveys. "
                    "The log-linear model (7 data points, OLS) captures the observed relationship "
                    "but should not be over-interpreted. The causal mechanism proposed: "
                    "cost-per-km proxies perceived value-for-money, which drives political "
                    "support/opposition. Confounders include: political cycle, alternative transport "
                    "investment news, economic conditions.",
                ], style={"fontSize": "11px", "color": C["muted2"], "lineHeight": "1.6",
                          "marginTop": "12px", "borderTop": f"1px solid {C['border']}", "paddingTop": "10px"}),
            ]),
        ]),

        html.Div(style={"height": "16px"}),

        html.Div([
            html.H3("Monte Carlo cluster forecasting",
                style={"fontFamily": "Fraunces,serif", "fontSize": "18px", "fontWeight": "300",
                       "color": C["text"], "marginBottom": "4px", "letterSpacing": "-0.2px"}),
            html.P("Adjust cost, network scope and risk parameters to see how scenario cluster "
                   "probabilities shift — and how that maps back onto the viability envelope.",
                style={"fontSize": "12px", "color": C["muted"], "marginBottom": "14px"}),
        ]),

        html.Div([
            card([card_title("Cluster probabilities"),
                  dcc.Graph(id="vmc-donut-chart", config={"displayModeBar": False}, style={"height": "200px"})]),
            card([card_title("Predicted sentiment"),
                  dcc.Graph(id="vmc-sent-gauge", config={"displayModeBar": False}, style={"height": "200px"})]),
            card([card_title("Cost per km vs threshold"),
                  dcc.Graph(id="vmc-cpkm-gauge", config={"displayModeBar": False}, style={"height": "200px"})]),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)",
                  "gap": "10px", "marginBottom": "12px"}),

        html.Div([
            html.Div([
                card([
                    card_title("Cost & network parameters"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span("Project cost forecast (£bn)", style={"fontSize": "12px", "color": C["text"]}),
                                html.Span(id="vmc-val-cost", children="95",
                                    style={"fontSize": "12px", "fontFamily": "DM Mono,monospace", "color": C["neg"]}),
                            ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "4px"}),
                            dcc.Slider(id="vmc-slider-cost", min=30, max=130, step=1, value=95,
                                marks=None, tooltip={"always_visible": False}, updatemode="drag"),
                        ], style={"marginBottom": "14px"}),
                        html.Div([
                            html.Div([
                                html.Span("Network in scope (km)", style={"fontSize": "12px", "color": C["text"]}),
                                html.Span(id="vmc-val-km", children="225",
                                    style={"fontSize": "12px", "fontFamily": "DM Mono,monospace", "color": C["pos"]}),
                            ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "4px"}),
                            dcc.Slider(id="vmc-slider-km", min=100, max=600, step=10, value=225,
                                marks=None, tooltip={"always_visible": False}, updatemode="drag"),
                        ], style={"marginBottom": "0"}),
                    ]),
                ]),
                html.Div(style={"height": "10px"}),
                card([
                    card_title("Risk & execution parameters"),
                    html.Div([
                        *[html.Div([
                            html.Div([
                                html.Span(p["label"], style={"fontSize": "12px", "color": C["text"]}),
                                html.Span(id=f"vmc-val-{p['id']}", children=str(p["val"]),
                                    style={"fontSize": "12px", "fontFamily": "DM Mono,monospace", "color": C["acc"]}),
                            ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "4px"}),
                            dcc.Slider(id=f"vmc-slider-{p['id']}",
                                min=p["min"], max=p["max"], step=p["step"], value=p["val"],
                                marks=None, tooltip={"always_visible": False}, updatemode="drag"),
                        ], style={"marginBottom": "14px"}) for p in PARAMS],
                    ]),
                ]),
            ], style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "0"}),

            html.Div([
                card([
                    card_title("Cluster probabilities — live", badge("10k sims", "acc")),
                    dcc.Graph(id="vmc-cluster-bar", config={"displayModeBar": False}, style={"height": "140px"}),
                ]),
                html.Div(style={"height": "10px"}),
                card([
                    card_title("MC × viability narrative"),
                    html.Div(id="vmc-narrative",
                        style={"fontSize": "13px", "color": C["muted"],
                               "lineHeight": "1.7", "fontFamily": "Fraunces,serif",
                               "fontWeight": "300", "fontStyle": "italic"}),
                ]),
            ], style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "0"}),
        ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),

        card([
            card_title("Cost fan chart with sentiment forecast — current parameters"),
            dcc.Graph(id="vmc-fan-chart", config={"displayModeBar": False}, style={"height": "280px"}),
        ], style={"marginBottom": "12px"}),

        card([
            card_title("Parameter tornado — which inputs drive cluster shift AND sentiment shift?"),
            dcc.Graph(id="vmc-tornado-chart", config={"displayModeBar": False}, style={"height": "260px"}),
            html.P("Each bar shows the change when the parameter is moved by +1 standard deviation "
                   "from the current setting. Left panel: impact on escalation cluster probability (pp). "
                   "Right panel: impact on predicted parliamentary sentiment score.",
                style={"fontSize": "11px", "color": C["muted2"], "marginTop": "8px", "lineHeight": "1.6"}),
        ], style={"marginBottom": "12px"}),

        card([
            card_title("Joint optimisation map — escalation probability across all (cost, network) combinations",
                       badge("~6,400 MC runs", "acc")),
            dcc.Graph(id="vmc-matrix-chart", config={"displayModeBar": False}, style={"height": "380px"}),
            html.P("Escalation probability computed analytically using the calibrated lognormal "
                   "cost distribution (sigma=0.35, sentiment-adjusted). Renders instantly. "
                   "Star = HS2 current position. White dashed line = viability boundary (£0.142bn/km). "
                   "Diamond markers = max viable cost per network size.",
                style={"fontSize": "11px", "color": C["muted2"], "marginTop": "8px", "lineHeight": "1.6"}),
        ]),

    ], style={"padding": "1.5rem 2rem"})
