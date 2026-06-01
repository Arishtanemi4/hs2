from dash import dcc, html
from ..config.theme import C
from ..components import card, card_title, section_header, stat_card, narrative_box, kpi_table
from ..figures import fig_stakeholder_sentiment, fig_workforce, fig_sentiment_timeline


def _signal_box(status: str, kind: str, title: str, desc: str) -> html.Div:
    col = C[kind]
    return html.Div([
        html.Div(status, style={"fontSize": "11px", "fontWeight": "500", "color": col, "marginBottom": "4px", "fontFamily": "DM Mono,monospace"}),
        html.Div(title,  style={"fontSize": "13px", "fontWeight": "500", "color": C["text"], "marginBottom": "4px"}),
        html.Div(desc,   style={"fontSize": "11px", "color": C["muted"], "lineHeight": "1.5"}),
    ], style={"background": C["bg3"], "borderRadius": "8px", "padding": "14px", "border": f"1px solid {col}33"})


def render_workforce() -> html.Div:
    return html.Div([
        section_header("Workforce & sentiment intelligence",
                       "Human-centric signals from HS2 Annual Reports, EDI reports, PAC hearings, and parliamentary statements 2019–2025."),

        html.Div([
            stat_card("HS2 Ltd headcount",     "~3,200", "Direct employees",              kind="acc"),
            stat_card("Supply chain workforce", "~28k",   "Peak Phase 1 construction",     kind="acc"),
            stat_card("Women in workforce",     "38%",    "vs 40% target (near-met)",       kind="neu"),
            stat_card("Safety LTIFR (2023–24)", "↓ 0.02", "Improved year-on-year",         kind="pos"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "10px", "marginBottom": "14px"}),

        html.Div([
            card([
                card_title("Composite sentiment by stakeholder group"),
                dcc.Graph(figure=fig_stakeholder_sentiment(), config={"displayModeBar": False}, style={"height": "280px"}),
                narrative_box(
                    "Narrative signal",
                    ("Sentiment is strongly bifurcated: external stakeholders (Parliament, media, communities) "
                     "are deeply negative. Internal and economic stakeholders remain cautiously supportive. "
                     "This divergence is itself a risk signal — it reduces political protection for the project."),
                    id_body="narr-sentiment",
                ),
            ]),
            card([
                card_title("Workforce headcount trend 2019–2025"),
                dcc.Graph(figure=fig_workforce(), config={"displayModeBar": False}, style={"height": "220px"}),
                html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),
                card_title("KPI performance vs target (2023–24)"),
                kpi_table(),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "14px"}),

        card([
            card_title("Stakeholder sentiment timeline 2016–2025"),
            dcc.Graph(figure=fig_sentiment_timeline(), config={"displayModeBar": False}, style={"height": "220px"}),
        ]),

        html.Div(style={"height": "12px"}),
        html.Div([
            _signal_box("HIGH RISK", "neg", "Skill gap signal",
                        "PAC 2024: technical & engineering shortages set to worsen. Competition from global infrastructure projects."),
            _signal_box("HIGH RISK", "neg", "Leadership stability",
                        "5 CEOs and 3 Chairs in 10 years. New Chair (Mike Brown) appointed June 2025 following Lovegrove review."),
            _signal_box("IMPROVING", "pos", "Safety trajectory",
                        "LTIFR improved year-on-year in 2023–24. Enterprise safety score exceeded target. Positive signal amid wider failure."),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)", "gap": "10px"}),

    ], style={"padding": "1.5rem 2rem"})
