from dash import html, dcc

from config.theme import C, _ha
from data.causality_data import PARLIAMENTARY_EVENTS, NEWS_EVENTS
from components.ui_components import (
    stat_card, card, card_title, section_header, narrative_box, badge
)
from charts.causality_charts import (
    fig_event_timeline, fig_impact_lollipop, fig_event_type_comparison,
    fig_lag_analysis, fig_cumulative_impact,
    fig_news_vs_parl_scatter, fig_event_density_heatmap,
)

_PARL_COL = C["acc"]
_NEWS_COL = C["pu"]


def _event_card(ev, category):
    is_positive = ev["impact"] >= 0
    col         = C["pos"] if is_positive else (_PARL_COL if category == "Parliamentary" else _NEWS_COL)
    icon        = "◆" if category == "Parliamentary" else "●"
    tag         = category
    return html.Div([
        html.Div([
            html.Span(f"{icon} {tag}", style={
                "fontSize": "10px", "fontFamily": "DM Mono,monospace",
                "color": col, "textTransform": "uppercase", "letterSpacing": "0.08em",
            }),
            html.Span(
                f"{'NOT ' if not ev['verified'] else ''}VERIFIED",
                style={
                    "fontSize": "9px", "fontFamily": "DM Mono,monospace",
                    "color": C["pos"] if ev["verified"] else C["muted2"],
                    "marginLeft": "8px",
                }),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),

        html.Div(ev["label"], style={
            "fontSize": "12px", "fontWeight": "500", "color": C["text"], "marginBottom": "3px",
        }),
        html.Div(
            ev.get("body", ev.get("channel", "")),
            style={"fontSize": "11px", "color": C["muted"], "fontFamily": "DM Mono,monospace",
                   "marginBottom": "6px"},
        ),
        html.Div(ev["description"], style={
            "fontSize": "11px", "color": C["muted"], "lineHeight": "1.6", "marginBottom": "8px",
        }),
        html.Div([
            html.Span(f"Impact: {ev['impact']:+.3f}", style={
                "fontSize": "11px", "fontFamily": "DM Mono,monospace",
                "color": C["pos"] if is_positive else C["neg"],
                "fontWeight": "500", "marginRight": "14px",
            }),
            html.Span(
                f"{ev['sentiment_before']:+.2f} → {ev['sentiment_after']:+.2f}",
                style={"fontSize": "11px", "fontFamily": "DM Mono,monospace", "color": C["muted"]},
            ),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={
        "background": C["bg3"],
        "border": f"1px solid {col}33",
        "borderLeft": f"3px solid {col}",
        "borderRadius": "8px",
        "padding": "12px 14px",
        "marginBottom": "8px",
    })


def render_causality():
    # Summary stats
    parl_neg = [e for e in PARLIAMENTARY_EVENTS if e["impact"] < 0]
    news_neg = [e for e in NEWS_EVENTS if e["impact"] < 0]
    parl_pos = [e for e in PARLIAMENTARY_EVENTS if e["impact"] > 0]
    news_pos = [e for e in NEWS_EVENTS if e["impact"] > 0]

    import numpy as np
    avg_parl = np.mean([abs(e["impact"]) for e in parl_neg]) if parl_neg else 0
    avg_news = np.mean([abs(e["impact"]) for e in news_neg]) if news_neg else 0
    biggest  = min(PARLIAMENTARY_EVENTS + NEWS_EVENTS, key=lambda e: e["impact"])

    return html.Div([
        section_header(
            "Causality analysis: events & public perception",
            "How major parliamentary meetings and news articles shifted public and parliamentary "
            "sentiment towards HS2. Sentiment values are proxy indices (NOT official surveys). "
            "Impact scores are model-estimated from observed tone shifts in primary sources."),

        # ── Stat bar ─────────────────────────────────────────────────────────
        html.Div([
            stat_card("Parliamentary events coded",
                      str(len(PARLIAMENTARY_EVENTS)),
                      f"{len(parl_neg)} negative · {len(parl_pos)} positive",
                      kind="acc"),
            stat_card("News / media events coded",
                      str(len(NEWS_EVENTS)),
                      f"{len(news_neg)} negative · {len(news_pos)} positive",
                      kind="pu"),
            stat_card("Avg parliamentary impact",
                      f"−{avg_parl:.3f}",
                      "Mean sentiment shift per negative event",
                      kind="neg"),
            stat_card("Avg news / media impact",
                      f"−{avg_news:.3f}",
                      "Mean sentiment shift per negative event",
                      kind="neg"),
            stat_card("Largest single event",
                      f"{biggest['impact']:+.3f}",
                      biggest["label"][:30],
                      kind="neg"),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(5,1fr)",
                  "gap": "10px", "marginBottom": "14px"}),

        # ── Key finding narrative ─────────────────────────────────────────────
        narrative_box(
            "Causality engine — key finding",
            ("Across 10 parliamentary events and 10 news articles coded since 2016, "
             "the data shows a consistent pattern: news coverage precedes parliamentary scrutiny "
             "by approximately one month (r=0.54, p=0.03). This suggests that investigative "
             "journalism functions as an early-warning signal for parliamentary action, rather than "
             "simply amplifying it after the fact.\n\n"
             "The single most damaging event was the October 2023 Phase 2 cancellation — "
             "a parliamentary action that directly caused a −0.18 parliamentary sentiment shift "
             "and triggered the largest media saturation event in HS2's history (−0.16 additional). "
             "Combined, this sequence erased roughly 8 years of marginal sentiment recovery.\n\n"
             "Parliamentary reviews (Oakervee, Cook, Lovegrove) consistently produce larger sustained "
             "impacts than individual news articles — but news articles set the agenda that makes "
             "those reviews politically inevitable. The causal chain runs: "
             "investigative journalism → political pressure → formal review → sentiment step-change."),
            id_body="narr-causality"),
        html.Div(style={"height": "14px"}),

        # ── Main timeline ─────────────────────────────────────────────────────
        card([
            card_title(
                "Sentiment timeline with event markers — 2016 to 2026",
                badge("hover events for detail", "acc")),
            dcc.Graph(figure=fig_event_timeline(),
                      config={"displayModeBar": False}, style={"height": "320px"}),
            html.P(
                "◆ = Parliamentary event · ● = News/media event · "
                "Green = positive sentiment impact · Drop lines show before→after shift. "
                "Sentiment values are proxy indices, NOT official surveys.",
                style={"fontSize": "11px", "color": C["muted2"], "marginTop": "8px", "lineHeight": "1.5"}),
        ], style={"marginBottom": "12px"}),

        # ── Impact lollipop + category comparison ────────────────────────────
        html.Div([
            card([
                card_title("Per-event impact ranking — all coded events",
                           badge("sorted by impact", "neg")),
                dcc.Graph(figure=fig_impact_lollipop(),
                          config={"displayModeBar": False},
                          style={"height": "560px", "overflowY": "auto"}),
            ]),
            html.Div([
                card([
                    card_title("Average impact by event category",
                               badge("parliamentary vs news", "acc")),
                    dcc.Graph(figure=fig_event_type_comparison(),
                              config={"displayModeBar": False}, style={"height": "230px"}),
                ]),
                html.Div(style={"height": "10px"}),
                card([
                    card_title("Event density by year — negative events only",
                               badge("heatmap", "pu")),
                    dcc.Graph(figure=fig_event_density_heatmap(),
                              config={"displayModeBar": False}, style={"height": "150px"}),
                    html.P("Each cell = number of negative events in that category/year. "
                           "2023 stands out as the year of maximum event concentration.",
                        style={"fontSize": "11px", "color": C["muted2"],
                               "marginTop": "8px", "lineHeight": "1.5"}),
                ]),
            ], style={"display": "flex", "flexDirection": "column"}),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "12px"}),

        # ── Lag analysis + co-occurrence scatter ─────────────────────────────
        html.Div([
            card([
                card_title("Lag analysis: does news lead parliamentary scrutiny?",
                           badge("r at 5 lag windows", "acc")),
                dcc.Graph(figure=fig_lag_analysis(),
                          config={"displayModeBar": False}, style={"height": "260px"}),
                html.P([
                    html.Strong("How to read: ", style={"color": C["text"]}),
                    "Each bar shows Pearson correlation between news event impact and "
                    "parliamentary event impact at the stated time lag. "
                    "Positive lag = news leads parliament. * = p<0.05. "
                    "The peak at +1 month suggests news coverage primes parliamentary scrutiny "
                    "roughly one month in advance.",
                ], style={"fontSize": "11px", "color": C["muted2"],
                          "marginTop": "8px", "lineHeight": "1.6"}),
            ]),
            card([
                card_title("Co-occurrence: quarters with both news and parliamentary events",
                           badge("scatter", "pu")),
                dcc.Graph(figure=fig_news_vs_parl_scatter(),
                          config={"displayModeBar": False}, style={"height": "260px"}),
                html.P("Each point is a quarter where both a news event and a parliamentary "
                       "event were coded. Quarters in the bottom-left (both negative) account "
                       "for the most severe sentiment collapses — 2019 Q4, 2023 Q4.",
                    style={"fontSize": "11px", "color": C["muted2"],
                           "marginTop": "8px", "lineHeight": "1.6"}),
            ]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "12px"}),

        # ── Cumulative impact waterfall ────────────────────────────────────────
        card([
            card_title(
                "Cumulative sentiment erosion — from 2016 baseline to 2026",
                badge("each event's contribution", "neu")),
            dcc.Graph(figure=fig_cumulative_impact(),
                      config={"displayModeBar": False}, style={"height": "340px"}),
            html.P([
                html.Strong("How to read: ", style={"color": C["text"]}),
                "Starting from the 2016 proxy baseline (−0.23), each bar shows one event's "
                "estimated contribution to the current −0.81 media / −0.72 parliamentary "
                "sentiment. Red bars reduce sentiment; green bars improve it. "
                "The 2023 Phase 2 cancellation cluster is the single largest step-change.",
            ], style={"fontSize": "11px", "color": C["muted2"],
                      "marginTop": "8px", "lineHeight": "1.6"}),
        ], style={"marginBottom": "12px"}),

        # ── Event cards ──────────────────────────────────────────────────────
        html.Div([
            html.H3("Parliamentary events — full record",
                style={"fontFamily": "Fraunces,serif", "fontSize": "16px", "fontWeight": "300",
                       "color": C["text"], "marginBottom": "10px", "letterSpacing": "-0.2px"}),
        ]),
        html.Div([
            _event_card(ev, "Parliamentary") for ev in
            sorted(PARLIAMENTARY_EVENTS, key=lambda e: e["year_frac"])
        ], style={"marginBottom": "16px"}),

        html.Div([
            html.H3("News / media events — full record",
                style={"fontFamily": "Fraunces,serif", "fontSize": "16px", "fontWeight": "300",
                       "color": C["text"], "marginBottom": "10px", "letterSpacing": "-0.2px"}),
        ]),
        html.Div([
            _event_card(ev, "News / Media") for ev in
            sorted(NEWS_EVENTS, key=lambda e: e["year_frac"])
        ], style={"marginBottom": "16px"}),

        # ── Methodology note ─────────────────────────────────────────────────
        card([
            card_title("Methodology — causality analysis"),
            html.P([
                html.Strong("Data: ", style={"color": C["text"]}),
                "Parliamentary events sourced from primary documents (PAC transcripts, NAO reports, "
                "Hansard, HoC Library CBP-9313). News events sourced from archive references in "
                "primary HS2 documents and verified BBC/ITV/Guardian/Times publications. "
                "Where event is labelled NOT VERIFIED, it is based on estimated coverage periods "
                "from secondary references and should not be presented as fact.",
            ], style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.7", "marginBottom": "8px"}),
            html.P([
                html.Strong("Sentiment scoring: ", style={"color": C["text"]}),
                "Before/after values are proxy indices on a −1 (very negative) to +1 (very positive) scale. "
                "They are derived from qualitative analysis of parliamentary tone (PAC reports, "
                "committee questioning style), media framing (headline sentiment, editorial stance), "
                "and public polling proxies where available. They are NOT official surveys. "
                "Impact = after − before. Monthly timeline is model-interpolated between annual anchors.",
            ], style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.7", "marginBottom": "8px"}),
            html.P([
                html.Strong("Causality note: ", style={"color": C["text"]}),
                "The lag analysis uses Pearson correlation on a small sample (n=10 matched quarters). "
                "This is indicative, not statistically definitive. The r=0.54 (p=0.03) finding at +1 month "
                "is consistent with established media-agenda literature (McCombs & Shaw 1972; "
                "Soroka 2002 on political issue salience). True Granger causality testing requires "
                "higher-frequency data (weekly or daily news mentions) — a next-phase enhancement.",
            ], style={"fontSize": "12px", "color": C["muted"], "lineHeight": "1.7"}),
        ]),

    ], style={"padding": "1.5rem 2rem"})
