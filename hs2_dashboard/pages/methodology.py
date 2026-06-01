from dash import html
from ..config.theme import C
from ..components import card, card_title, section_header


_PHASES = [
    ("01", "Data extraction & time series", "Weeks 1–2", [
        "Extract cost revision series from CBP-9313 (2012–2026)",
        "Parse HS2 Annual Reports 2019–2025 for KPI tables",
        "Extract workforce headcount, EDI, safety from PDFs",
        "Download PAC hearing transcripts for sentiment signals",
        "Tag discrete events (elections, reviews, scope changes)",
        "Output: clean CSV time series per parameter",
    ]),
    ("02", "Monte Carlo model calibration", "Weeks 2–3", [
        "Fit distributions to each parameter from historical data",
        "Calibrate inflation using ONS construction price indices",
        "Set Poisson rate for scope change events",
        "Run 10,000 paths; validate against known outcomes",
        "Backtest: 2016 data → does model predict 2019 revision?",
        "Output: cluster probabilities + sensitivity rankings",
    ]),
    ("03", "Sentiment & NLP layer", "Weeks 3–4", [
        "Parse PAC transcripts for tone signals by quarter",
        "Apply sentiment scoring to parliamentary questions",
        "Build stakeholder sentiment index (7 groups)",
        "Correlate sentiment shifts with subsequent cost events",
        "Does negative PAC sentiment lead cost overruns by 6 months?",
        "Output: sentiment time series + leading indicator signals",
    ]),
    ("04", "Narrative engine v1", "Weeks 4–5", [
        "Template-based narrative from cluster + key parameters",
        "LLM layer to generate natural language from model outputs",
        "Parameter trigger map: which inputs change the narrative?",
        "Confidence calibration — what can the model not predict?",
        "Decision intelligence layer: actionable recommendations",
        "Output: auto-generated report from live data",
    ]),
    ("05", "Interactive dashboard", "Weeks 5–6", [
        "Dashboard as shown (this is your v1.0)",
        "Connect to live data pipeline (auto-refresh on new reports)",
        "Scenario slider controls for client exploration",
        "Narrative engine output rendered inline",
        "Export to PDF report on demand",
        "Output: client-facing deliverable",
    ]),
    ("06", "Client delivery & productisation", "Weeks 6–8", [
        "Present to anchor client — this dashboard is the demo",
        "Document what took manual effort → automate it",
        "Identify which elements generalise to other projects",
        "Begin second client conversation (same domain)",
        "IP documentation: what is the reusable product?",
        "Output: paid engagement + product v1 blueprint",
    ]),
]

_SOURCES = [
    ("HoC Library CBP-9313",         "Full cost & schedule revision history",  "commonslibrary.parliament.uk"),
    ("HS2 Annual Reports 2019–2025",  "KPIs, workforce, spend, safety",         "assets.publishing.service.gov.uk"),
    ("HS2 EDI Report 2024–25",        "Workforce diversity by band",            "assets.publishing.service.gov.uk"),
    ("NAO HS2 reports (8 reports)",   "Cost, governance, risk findings",        "nao.org.uk"),
    ("PAC hearing transcripts",       "Sentiment signals, governance critique", "committees.parliament.uk"),
    ("HS2 6-monthly Parliament Reports","Progress, milestones, minister statements","data.parliament.uk"),
    ("ONS Construction Output Price Index","Inflation parameter calibration",   "ons.gov.uk"),
]


def render_methodology() -> html.Div:
    phase_cards = [
        html.Div([
            html.Div(num, style={"fontFamily": "Fraunces,serif", "fontSize": "32px",
                                  "color": C["border2"], "fontWeight": "300", "marginBottom": "4px"}),
            html.Div(title, style={"fontSize": "13px", "fontWeight": "500", "color": C["text"], "marginBottom": "3px"}),
            html.Div(dur,   style={"fontSize": "11px", "color": C["acc"], "fontFamily": "DM Mono,monospace", "marginBottom": "10px"}),
            *[html.Div(f"→ {item}", style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.6", "padding": "1px 0"})
              for item in items],
        ], style={"background": C["bg3"], "border": f"1px solid {C['border']}", "borderRadius": "10px", "padding": "16px"})
        for num, title, dur, items in _PHASES
    ]

    return html.Div([
        section_header("Implementation plan & methodology",
                       "Phased roadmap for building the full HS2 analysis pipeline — from data extraction to live narrative engine."),

        html.Div(phase_cards,
                 style={"display": "grid", "gridTemplateColumns": "repeat(3,1fr)", "gap": "12px", "marginBottom": "16px"}),

        card([
            card_title("Public data sources"),
            html.Table([
                html.Thead(html.Tr([html.Th(h, style={
                    "padding": "6px 10px", "color": C["muted"], "fontWeight": "400",
                    "fontFamily": "DM Mono,monospace", "fontSize": "10px",
                    "textTransform": "uppercase", "letterSpacing": "0.06em",
                    "borderBottom": f"1px solid {C['border']}"})
                    for h in ["Source", "What you get", "URL"]])),
                html.Tbody([html.Tr([
                    html.Td(a, style={"padding": "8px 10px", "color": C["text"],  "fontSize": "12px", "fontWeight": "500", "borderBottom": f"1px solid {C['border']}"}),
                    html.Td(b, style={"padding": "8px 10px", "color": C["muted"], "fontSize": "12px", "borderBottom": f"1px solid {C['border']}"}),
                    html.Td(c, style={"padding": "8px 10px", "color": C["acc"],   "fontSize": "11px", "fontFamily": "DM Mono,monospace", "borderBottom": f"1px solid {C['border']}"}),
                ]) for a, b, c in _SOURCES]),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
        ]),

    ], style={"padding": "1.5rem 2rem"})
