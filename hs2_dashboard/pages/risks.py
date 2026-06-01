from dash import dcc, html
from ..config.theme import C
from ..components import card, card_title, section_header, badge, risk_item
from ..figures import fig_risk_radar


_RISKS_HIGH = [
    ("HIGH", "Political intervention post-2028 election",
     "Any change in government or policy review could trigger another full reset. HS2 has survived 3 elections; the next is a major inflection point."),
    ("HIGH", "Construction inflation spike",
     "Construction inflation ran at 8–12% 2021–23. A return to this level would push costs well above £110bn. Remaining works are most inflation-sensitive."),
    ("HIGH", "Skill & labour shortage",
     "PAC 2024 identified worsening technical skill shortages. Global infrastructure boom competing for the same labour pool."),
    ("HIGH", "Euston station uncertainty",
     "Euston construction paused. No confirmed restart timeline. Without Euston, Phase 1 delivers reduced benefit and the benefit-cost ratio falls below 1.5."),
    ("HIGH", "Further scope reduction",
     "Speed reduced from 360 km/h to 320 km/h in 2025 to save £2.5bn. Further reductions possible, each weakening the economic case."),
    ("HIGH", "Contractor Joint Venture failure",
     "Multiple JVs running simultaneously. If one faces financial difficulty (as on Crossrail), cascade effects on the programme are severe."),
    ("HIGH", "Updated cost estimate delay",
     "Full programme reset cost estimate was due mid-2026, now delayed to end-2026. Uncertainty itself is a risk — it delays contractor decisions."),
]

_RISKS_MED = [
    ("MED", "Community & legal challenges",
     "Independent Commissioner appointed. Ongoing legal challenges along the route add cost and schedule variance."),
    ("MED", "Carbon target shortfall",
     "Current trajectory at 33.8% reduction vs 50% target. Shortfall could trigger additional spend on green materials."),
    ("MED", "Leadership continuity",
     "New Chair and CEO reset in 2025. Learning curve during critical construction phase adds execution risk."),
    ("LOW", "Safety incident escalation",
     "Safety KPIs are currently on-target and improving. Low risk but high impact — a major incident would trigger a public inquiry."),
]


def render_risks() -> html.Div:
    return html.Div([
        section_header("Risk signal monitor",
                       "Structured risk register derived from NAO reports, PAC transcripts, and Lovegrove review."),

        html.Div([
            html.Div(card([
                card_title("Active risk register", badge("7 HIGH · 4 MED", "neg")),
                *[risk_item(s, n, d) for s, n, d in _RISKS_HIGH + _RISKS_MED],
            ]), style={"flex": "1"}),
            html.Div([
                card([
                    card_title("Risk radar — probability vs impact"),
                    dcc.Graph(figure=fig_risk_radar(), config={"displayModeBar": False}, style={"height": "320px"}),
                ]),
                html.Div(style={"height": "12px"}),
                card([
                    card_title("Monte Carlo — distribution assumptions"),
                    html.Table([
                        html.Thead(html.Tr([html.Th(h, style={
                            "padding": "6px 8px", "color": C["muted"], "fontWeight": "400",
                            "fontFamily": "DM Mono,monospace", "fontSize": "10px",
                            "textTransform": "uppercase", "letterSpacing": "0.06em",
                            "borderBottom": f"1px solid {C['border']}"})
                            for h in ["Parameter", "Distribution", "Range"]])),
                        html.Tbody([html.Tr([
                            html.Td(a, style={"padding": "7px 8px", "color": C["text"],   "fontSize": "12px", "borderBottom": f"1px solid {C['border']}"}),
                            html.Td(b, style={"padding": "7px 8px", "color": C["muted"],  "fontSize": "11px", "fontFamily": "DM Mono,monospace", "borderBottom": f"1px solid {C['border']}"}),
                            html.Td(c, style={"padding": "7px 8px", "color": C["muted"],  "fontSize": "11px", "fontFamily": "DM Mono,monospace", "borderBottom": f"1px solid {C['border']}"}),
                        ]) for a, b, c in [
                            ("Inflation rate",          "Log-normal",         "2%–12% p.a."),
                            ("Scope change event",      "Poisson (λ=0.4/yr)", "0–2 per year"),
                            ("Political risk event",    "Bernoulli",          "P=0.35 at elections"),
                            ("Contractor performance",  "Beta(α=3,β=1.5)",    "KPI score 1.8–2.8"),
                            ("Workforce ramp rate",     "Normal",             "±15% of plan"),
                            ("Design change cost",      "Pareto tail",        "£0.5bn–£8bn"),
                        ]]),
                    ], style={"width": "100%", "borderCollapse": "collapse"}),
                ]),
            ], style={"flex": "1", "display": "flex", "flexDirection": "column"}),
        ], style={"display": "flex", "gap": "12px"}),

    ], style={"padding": "1.5rem 2rem"})
