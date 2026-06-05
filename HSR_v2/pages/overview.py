from dash import html, dcc

from config.theme import C, _ha
from data.hs2_data import SCOPE_DATA
from models.monte_carlo import run_monte_carlo
from components.ui_components import (
    stat_card, card, card_title, narrative_box, badge
)
from charts.cost_charts import fig_cost_history, fig_schedule
from charts.simulation_charts import fig_cluster_donut
from charts.benefit_charts import (
    fig_benefits_journey_time, fig_capacity_comparison,
    fig_speed_comparison, fig_scope_evolution, fig_infrastructure_density
)


def _tl_item(year, kind, title, detail):
    col_map = {"pos": C["pos"], "neu": C["neu"], "neg": C["neg"], "acc": C["acc"]}
    col = col_map.get(kind, C["muted"])
    return html.Div([
        html.Div(style={"position": "absolute", "left": "-27px", "top": "5px",
                        "width": "10px", "height": "10px", "borderRadius": "50%",
                        "background": _ha(col, 0.2), "border": f"2px solid {col}"}),
        html.Div(year,   style={"fontSize": "10px", "fontFamily": "DM Mono,monospace", "color": C["muted"]}),
        html.Div(title,  style={"fontSize": "12px", "color": C["text"], "lineHeight": "1.5"}),
        html.Div(detail, style={"fontSize": "11px", "color": C["muted"], "marginTop": "1px"}),
    ], style={"position": "relative", "paddingBottom": "16px", "paddingLeft": "4px"})


def render_overview():
    mc = run_monte_carlo()
    cp = mc["cluster_probs"]
    return html.Div([
        html.Div([
            stat_card("Cost estimate (2026)", "£102.7bn", "Upper range", "↑ 214% vs 2012 baseline", "neg"),
            stat_card("Schedule delay", "+13yr", "2026 → 2039 opening", "↑ 3 further delays in 2025", "neg"),
            stat_card("% complete (Phase 1)", ">80% tunnelling", "Tunnelling >80% done (AR 2024-25)", "Overall phase 1 % not stated in sources", "neu"),
            stat_card("Total workforce (2024–25)", "33,000", "AR 2024-25, CEO intro (verified)", "↑ from 30,204 peak in Sep 2023", "acc"),
            stat_card("Positive outcome prob.", f"{cp['pos']:.0f}%", "Monte Carlo (10k sims)", "↓ from 31% in 2023", "pu"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(5,1fr)", "gap": "10px", "marginBottom": "16px"}),

        narrative_box(
            "Narrative Engine Output — Overview",
            ("HS2 has entered a structural crisis loop — where each governance reset improves "
             "confidence briefly before structural cost and schedule pressures reassert. With only "
             "one-third of Phase 1 complete, £40bn already spent, and costs now reaching £102.7bn, "
             "the project faces a paradox: cancellation costs nearly the same as completion. "
             "The most likely future is managed overrun to 2039–2041, contingent on political "
             "continuity and no further scope intervention."),
            id_body="narr-overview"
        ),
        html.Div(style={"height": "14px"}),

        html.Div([
            html.Div(card([
                card_title("Cost estimate evolution 2012–2026", badge("214% overrun", "neg")),
                dcc.Graph(figure=fig_cost_history(), config={"displayModeBar": False}, style={"height": "240px"}),
            ]), style={"flex": "2"}),
            html.Div(card([
                card_title("Critical regime changes"),
                html.Div([
                    _tl_item("2012", "pos", "Original budget approved: £32.7bn", "Opening target: 2026"),
                    _tl_item("2016", "neu", "NAO flags 'unrealistic timetable'", "First schedule slippage signal"),
                    _tl_item("2019", "neg", "Oakervee Review: costs £88bn", "Opening pushed to 2028–2031"),
                    _tl_item("2023", "neg", "Phase 2 cancelled by Sunak", "£2.7bn written off. Leeds & Manchester axed."),
                    _tl_item("2025", "neg", "Lovegrove review: 'litany of failure'", "Full programme reset announced"),
                    _tl_item("2026", "neg", "Cost hits £102.7bn. Opening: 2039", "Programme under reset — current status"),
                ], style={"paddingLeft": "20px", "borderLeft": f"1px solid {C['border2']}"}),
            ]), style={"flex": "1"}),
        ], style={"display": "flex", "gap": "12px", "marginTop": "14px"}),

        html.Div([
            html.Div(card([
                card_title("Schedule evolution — original vs actuals"),
                dcc.Graph(figure=fig_schedule(), config={"displayModeBar": False}, style={"height": "200px"}),
            ])),
            html.Div(card([
                card_title("Monte Carlo cluster probabilities"),
                dcc.Graph(figure=fig_cluster_donut(cp["pos"], cp["neu"], cp["neg"]),
                          config={"displayModeBar": False}, style={"height": "200px"}),
            ])),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginTop": "12px"}),

        html.Div(style={"height": "16px"}),

        html.Div([
            html.H3("Project benefits: what HS2 delivers",
                style={"fontFamily": "Fraunces,serif", "fontSize": "18px", "fontWeight": "300",
                       "color": C["text"], "marginBottom": "4px", "letterSpacing": "-0.2px"}),
            html.P("The case for HS2 rests on three pillars: faster journeys, greater capacity, "
                   "and higher speed. These benefits remain valid for Phase 1 regardless of the cost story.",
                style={"fontSize": "12px", "color": C["muted"], "marginBottom": "14px"}),
        ]),

        html.Div([
            stat_card("Journey time cut",    "45 min",  "London → Birmingham (HS2)",       "vs 81 min today — 44% faster", "pos"),
            stat_card("Trains per hour",     "18 tph",  "Design capacity (each direction)", "More than any high-speed line in the world", "pos"),
            stat_card("Passengers per train","1,100",   "Per 400m HS2 train",              "~3 jumbo jets of passengers per service", "pos"),
            stat_card("Peak seats at Euston","2.6×",    "12,100 → 31,200 seats/hour",      "With Phase 1 operational — Rail Engineer", "pos"),
            stat_card("Max speed",           "320 km/h","Reduced from 360km/h in 2026 reset","Fastest railway in the UK by far", "acc"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(5,1fr)", "gap": "10px", "marginBottom": "14px"}),

        html.Div([
            card([
                card_title("Journey time savings vs current fastest service", badge("verified DfT sources", "acc")),
                dcc.Graph(figure=fig_benefits_journey_time(),
                          config={"displayModeBar": False}, style={"height": "200px"}),
                html.P("Note: London-Manchester and London-Leeds figures use Phase 1 + WCML "
                       "continuation. Phase 2 cancellation significantly reduced benefits to northern cities.",
                    style={"fontSize": "11px", "color": C["muted2"], "marginTop": "8px", "lineHeight": "1.5"}),
            ]),
            html.Div([
                card([
                    card_title("Euston peak-hour capacity uplift", badge("Rail Engineer", "acc")),
                    dcc.Graph(figure=fig_capacity_comparison(),
                              config={"displayModeBar": False}, style={"height": "140px"}),
                ]),
                html.Div(style={"height": "8px"}),
                card([
                    card_title("Speed vs other rail services"),
                    dcc.Graph(figure=fig_speed_comparison(),
                              config={"displayModeBar": False}, style={"height": "160px"}),
                ]),
            ], style={"display": "flex", "flexDirection": "column"}),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "16px"}),

        html.Div([
            html.H3("High-level scope: tracking the cuts",
                style={"fontFamily": "Fraunces,serif", "fontSize": "18px", "fontWeight": "300",
                       "color": C["text"], "marginBottom": "4px", "letterSpacing": "-0.2px"}),
            html.P("How the project's physical scope has evolved from the original 2012 Y-network "
                   "to the current Phase 1 only. Sources: Gov.uk 2013; HoC CBP-9313; HS2 project update 2026.",
                style={"fontSize": "12px", "color": C["muted"], "marginBottom": "14px"}),
        ]),

        card([
            card_title("Scope metrics at each revision — route, stations, cities, speed"),
            dcc.Graph(figure=fig_scope_evolution(),
                      config={"displayModeBar": False}, style={"height": "240px"}),
        ], style={"marginBottom": "12px"}),

        html.Div([
            card([
                card_title("Infrastructure density: tunnels and bridges per km", badge("rises as route shrinks", "neg")),
                dcc.Graph(figure=fig_infrastructure_density(),
                          config={"displayModeBar": False}, style={"height": "220px"}),
                html.P("As the route shortened from 540km to 225km, the proportion in tunnels "
                       "stayed constant (Phase 1 always had the same Chiltern and London tunnels) "
                       "while bridges/km fell as the Midlands structures were retained. "
                       "The result: a shorter, more expensive route with the same hard infrastructure. "
                       "Infrastructure density is a key driver of cost-per-km.",
                    style={"fontSize": "11px", "color": C["muted2"], "marginTop": "8px", "lineHeight": "1.5"}),
            ]),
            card([
                card_title("Scope timeline — what was cut and when"),
                *[html.Div([
                    html.Div([
                        html.Div(d["label"].replace(" -- ", "\n"),
                            style={"fontSize": "11px", "fontFamily": "DM Mono,monospace",
                                   "color": (C["pos"] if d["colour"] == "pos"
                                             else C["neu"] if d["colour"] == "neu"
                                             else C["neg"]),
                                   "fontWeight": "500", "marginBottom": "4px"}),
                        html.Div(f"{d['route_miles']} miles · {d['stations']} stations · "
                                 f"{d['cities_served']} cities · {d['max_speed_kmh']}km/h",
                            style={"fontSize": "11px", "fontFamily": "DM Mono,monospace",
                                   "color": C["muted"], "marginBottom": "4px"}),
                        html.Div(d["scope_note"],
                            style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.5"}),
                    ], style={"paddingLeft": "12px",
                              "borderLeft": f"2px solid {C['pos'] if d['colour'] == 'pos' else C['neu'] if d['colour'] == 'neu' else C['neg']}",
                              "marginBottom": "14px"}),
                ]) for d in SCOPE_DATA],
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}),

    ], style={"padding": "1.5rem 2rem"})
