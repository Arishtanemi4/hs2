from dash import html, dcc

from config.theme import C, _ha
from components.ui_components import (
    stat_card, card, card_title, section_header, narrative_box, badge
)
from charts.workforce_charts import (
    fig_workforce, fig_sentiment_timeline, fig_stakeholder_sentiment,
    fig_workforce_approval_scatter, fig_jobs_per_bn,
    fig_workforce_viability_envelope, fig_jobs_approval_forecast
)
from components.ui_components import kpi_table


def _signal_box(status, kind, title, desc):
    col = C[kind]
    return html.Div([
        html.Div(status, style={"fontSize": "11px", "fontWeight": "500", "color": col, "marginBottom": "4px", "fontFamily": "DM Mono,monospace"}),
        html.Div(title,  style={"fontSize": "13px", "fontWeight": "500", "color": C["text"], "marginBottom": "4px"}),
        html.Div(desc,   style={"fontSize": "11px", "color": C["muted"], "lineHeight": "1.5"}),
    ], style={"background": C["bg3"], "borderRadius": "8px", "padding": "14px", "border": f"1px solid {col}33"})


def render_workforce():
    return html.Div([
        section_header("Workforce & sentiment intelligence",
                       "Human-centric signals from HS2 Annual Reports, EDI reports, PAC hearings, and parliamentary statements 2019–2025."),

        html.Div([
            stat_card("HS2 Ltd headcount",        "~3,200", "Direct employees", kind="acc"),
            stat_card("Supply chain workforce",    "~28k",   "Peak Phase 1 construction", kind="acc"),
            stat_card("Women in workforce",        "38%",    "vs 40% target (near-met)", kind="neu"),
            stat_card("Safety LTIFR (2023–24)",    "↓ 0.02", "Improved year-on-year", kind="pos"),
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
                    id_body="narr-sentiment"),
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

        html.Div(style={"height": "16px"}),

        html.Div([
            html.H3("Workforce & approval: jobs, cost and public favour",
                style={"fontFamily": "Fraunces,serif", "fontSize": "18px", "fontWeight": "300",
                       "color": C["text"], "marginBottom": "4px", "letterSpacing": "-0.2px"}),
            html.P("Does building more jobs improve public approval? "
                   "Only when cost-efficiency is maintained. "
                   "Beyond ~35k workers, job creation no longer shifts sentiment — "
                   "cost-per-worker and cost-per-km dominate.",
                style={"fontSize": "12px", "color": C["muted"], "marginBottom": "14px"}),
        ]),

        html.Div([
            stat_card("Jobs per £bn (2020)", "550",       "22k workers / £40bn",   "Best efficiency in the programme", "pos"),
            stat_card("Jobs per £bn (2026)", "347",       "33k workers / £95.2bn", "37% drop since 2020", "neg"),
            stat_card("Optimal workforce",   "30–40k",    "Model: diminishing returns above 40k",
                      "Jobs bonus capped at +0.15 sentiment", "neu"),
            stat_card("Key conclusion",      "Jobs alone","do NOT rescue approval when cost rises",
                      "Cost/km remains the dominant signal", "acc"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "10px", "marginBottom": "14px"}),

        narrative_box(
            "Workforce × approval — key finding",
            ("Despite HS2's workforce growing from 22k to 33k between 2020 and 2025, "
             "parliamentary sentiment declined from −0.40 to −0.72. "
             "More jobs made things worse — because cost rose proportionally faster. "
             "The jobs-per-£bn metric tells the story: in 2020, HS2 employed 550 people "
             "per £1bn spent. By 2025 that dropped to 347. "
             "A project becomes publicly favourable when it creates high employment relative "
             "to cost — above roughly 400 jobs per £bn. Below that, each additional worker "
             "at current cost-per-worker rates (£2.9m each) delivers insufficient perceived "
             "value to offset the cost signal. "
             "The optimal zone is 30–40k workers at costs below £76bn — a combination "
             "HS2 has never achieved simultaneously."),
            id_body="narr-workforce-approval"),
        html.Div(style={"height": "12px"}),

        html.Div([
            card([
                card_title("Workforce vs sentiment — does more jobs = better approval?", badge("4 verified data points", "acc")),
                dcc.Graph(figure=fig_workforce_approval_scatter(),
                          config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
            card([
                card_title("Jobs-per-£bn: employment efficiency over time"),
                dcc.Graph(figure=fig_jobs_per_bn(),
                          config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "12px"}),

        card([
            card_title("Approval forecast as workforce grows — by cost scenario"),
            dcc.Graph(figure=fig_jobs_approval_forecast(),
                      config={"displayModeBar": False}, style={"height": "280px"}),
            html.P("Each line shows predicted approval as total workforce grows from 10k→55k "
                   "at a fixed cost. Diamond markers show where each scenario crosses the "
                   "viability threshold (−0.40). At £95bn (current), no amount of job creation "
                   "restores viability. At £50bn, ~30k workers is sufficient.",
                style={"fontSize": "12px", "color": C["muted"], "marginTop": "10px", "lineHeight": "1.6"}),
        ], style={"marginBottom": "12px"}),

        card([
            card_title("Jobs × cost approval envelope — the viable sweet spot", badge("Model-derived", "neu")),
            dcc.Graph(figure=fig_workforce_viability_envelope(),
                      config={"displayModeBar": False}, style={"height": "360px"}),
            html.P([
                html.Strong("How to read this: ", style={"color": C["text"]}),
                "Each cell is a (workforce size, cost) combination. Green = approval above "
                "the viability threshold. Red = below. The white trajectory shows where "
                "HS2 has actually been — moving right and up, staying entirely in the "
                "unviable red zone since 2022. Uses a 400km reference network.",
            ], style={"fontSize": "12px", "color": C["muted"], "marginTop": "10px", "lineHeight": "1.6"}),
            html.P("Methodology: base = log-linear cost/km model (R²=0.838) + "
                   "jobs bonus (max +0.15, diminishing above 40k) − "
                   "efficiency penalty (cost-per-worker > £2bn/k). "
                   "The workforce component is modelled; the cost/km base is empirical.",
                style={"fontSize": "11px", "color": C["muted2"], "marginTop": "8px", "lineHeight": "1.6",
                       "borderTop": f"1px solid {C['border']}", "paddingTop": "8px"}),
        ]),

    ], style={"padding": "1.5rem 2rem"})
