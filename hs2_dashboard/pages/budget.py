from dash import dcc, html
from ..config.theme import C
from ..components import card, card_title, section_header, stat_card, badge
from ..figures import fig_waterfall, fig_spend, fig_cost_drivers


def render_budget() -> html.Div:
    return html.Div([
        section_header("Budget & spend analysis",
                       "Cost revision history from 2012 to 2026. Sources: NAO, House of Commons Library CBP-9313, HS2 Annual Reports."),

        html.Div([
            stat_card("Original budget (2012)", "£32.7bn", "In 2019 prices",                               kind="neg"),
            stat_card("Latest estimate (2026)",  "£102.7bn","Upper range, 2026 prices",                    kind="neg"),
            stat_card("Already spent (2025)",    "~£40bn",  "Cash terms, Phase 1 only",                    kind="neg"),
            stat_card("Phase 2 prep costs",      "~£2.3bn", "Manchester leg alone (Railway News Apr 2026)", kind="neu"),
            stat_card("Annual budget 2025-26",   "£7.1bn",  "AR 2024-25 HC1088 (confirmed)",               kind="neu"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(5,1fr)", "gap": "10px", "marginBottom": "14px"}),

        card([
            card_title("Cost overrun waterfall: 2012 → 2026", badge("+£70bn total increase", "neg")),
            dcc.Graph(figure=fig_waterfall(), config={"displayModeBar": False}, style={"height": "300px"}),
        ]),
        html.Div(style={"height": "12px"}),

        html.Div([
            card([
                card_title("Annual spend vs budget (£bn)"),
                dcc.Graph(figure=fig_spend(), config={"displayModeBar": False}, style={"height": "220px"}),
            ]),
            card([
                card_title("Cost overrun attribution"),
                dcc.Graph(figure=fig_cost_drivers(), config={"displayModeBar": False}, style={"height": "200px"}),
                html.Hr(style={"borderColor": C["border"], "margin": "12px 0"}),
                *[html.Div([
                    html.Span(k, style={"fontSize": "12px", "color": C["muted"]}),
                    html.Span(v, style={"fontSize": "13px", "fontFamily": "DM Mono,monospace", "color": C["neg"]}),
                  ], style={"display": "flex", "justifyContent": "space-between", "padding": "7px 0",
                            "borderBottom": f"1px solid {C['border']}"})
                  for k, v in [
                      ("Construction inflation",        "~£24bn"),
                      ("Design changes & rescoping",    "~£18bn"),
                      ("Programme delays",              "~£14bn"),
                      ("Governance & contractor overruns", "~£10bn"),
                      ("Tunnel complexity uplift",      "~£4bn"),
                  ]],
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}),

    ], style={"padding": "1.5rem 2rem"})
