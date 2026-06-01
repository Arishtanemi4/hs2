from dash import dcc, html
from ..config.theme import C, _ha
from ..components import card, card_title, section_header, narrative_box, badge
from ..figures import fig_confidence
from ..data import NARRATIVES


def render_narrative() -> html.Div:
    return html.Div([
        section_header("Narrative engine",
                       "Translates Monte Carlo probability distributions into plain-language decision intelligence. Select a scenario."),

        html.Div([
            html.Button("Controlled Delivery (18%)", id="btn-pos",
                        style={"flex": "1", "border": f"1px solid {C['pos']}44", "borderRadius": "10px",
                               "padding": "12px", "background": _ha(C["pos"], 0.07), "color": C["pos"],
                               "cursor": "pointer", "fontFamily": "DM Sans,sans-serif", "fontSize": "13px"}),
            html.Button("Managed Overrun (45%)", id="btn-neu",
                        style={"flex": "1", "border": f"1px solid {C['neu']}44", "borderRadius": "10px",
                               "padding": "12px", "background": _ha(C["neu"], 0.13), "color": C["neu"],
                               "cursor": "pointer", "fontFamily": "DM Sans,sans-serif", "fontSize": "13px", "fontWeight": "500"}),
            html.Button("Escalation (37%)", id="btn-neg",
                        style={"flex": "1", "border": f"1px solid {C['neg']}44", "borderRadius": "10px",
                               "padding": "12px", "background": _ha(C["neg"], 0.07), "color": C["neg"],
                               "cursor": "pointer", "fontFamily": "DM Sans,sans-serif", "fontSize": "13px"}),
        ], style={"display": "flex", "gap": "10px", "marginBottom": "16px"}),

        html.Div(id="narrative-output", children=narrative_box(
            NARRATIVES["neu"]["tag"], NARRATIVES["neu"]["body"])),

        html.Div(style={"height": "14px"}),

        html.Div([
            card([
                card_title("Parameter → narrative trigger map"),
                *[html.Div([
                    badge(trigger, kind),
                    html.Div(desc, style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.5", "flex": "1"}),
                  ], style={"display": "flex", "gap": "12px", "alignItems": "flex-start",
                            "padding": "10px 0", "borderBottom": f"1px solid {C['border']}"})
                  for trigger, kind, desc in [
                      ("Inflation >7%",      "neg", "Triggers migration from Managed Overrun → Escalation. Model assigns 28% probability of recurrence by 2028."),
                      ("Election review",    "neg", "Any formal HS2 review post-2028 election has historically added 12–36 months and £5–15bn. Bernoulli probability: 35%."),
                      ("Euston restart",     "neu", "Confirmation of Euston construction restart is the strongest single positive signal. Shifts positive cluster prob +13pp."),
                      ("KPI score >2.4",     "pos", "Sustained above 2.4 for 3+ quarters is a leading indicator of delivery within budget."),
                      ("Workforce stable",   "pos", "Leadership continuity for 24 months is a necessary (not sufficient) condition for controlled delivery."),
                  ]],
            ]),
            card([
                card_title("Narrative confidence calibration"),
                dcc.Graph(figure=fig_confidence(), config={"displayModeBar": False}, style={"height": "200px"}),
                html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),
                html.P([
                    html.Strong("Backtesting note: ", style={"color": C["text"]}),
                    "Running this model against 2016 data would have predicted the 2019 cost revision "
                    "(actual: £88bn vs model median: £82bn). The model consistently underestimates "
                    "tail risk — wide uncertainty bands are intentional and honest.",
                ], style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.7"}),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}),

    ], style={"padding": "1.5rem 2rem"})
