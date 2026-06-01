from dash import dcc, html
from ..config.theme import C, _ha
from ..components import card, card_title, stat_card, narrative_box
from ..figures import fig_cost_history, fig_schedule, fig_cluster_donut
from ..engine import run_monte_carlo


def _tl_item(year: str, kind: str, title: str, detail: str) -> html.Div:
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


def render_overview() -> html.Div:
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
            id_body="narr-overview",
        ),
        html.Div(style={"height": "14px"}),

        html.Div([
            html.Div(card([
                card_title("Cost estimate evolution 2012–2026"),
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

    ], style={"padding": "1.5rem 2rem"})
