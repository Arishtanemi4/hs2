import plotly.graph_objects as go
from dash import html, Input, Output, callback_context

from app import app
from config.theme import C, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from data.hs2_data import PARAMS, NARRATIVES, VIABILITY_DATA
from models.monte_carlo import run_monte_carlo
from models.viability import pred_sentiment
from charts.simulation_charts import (
    fig_parameter_sweep, fig_scenario_matrix,
    fig_donut_clusters, fig_mc_cluster_bar,
    fig_mc_fan_with_sentiment, fig_cluster_sentiment_matrix,
    fig_sensitivity_vs_sentiment,
)
from charts.viability_charts import fig_sentiment_gauge, fig_cpkm_gauge
from components.ui_components import narrative_box
from pages.scenarios import _build_scenario_narrative


# ── Tab content router ────────────────────────────────────────────────────────

@app.callback(Output("tab-content", "children"), Input("main-tabs", "active_tab"))
def render_tab(tab):
    from pages.overview    import render_overview
    from pages.scenarios   import render_scenarios
    from pages.workforce   import render_workforce
    from pages.budget      import render_budget
    from pages.risks       import render_risks
    from pages.narrative   import render_narrative
    from pages.methodology import render_methodology

    if tab == "tab-overview":   return render_overview()
    if tab == "tab-scenarios":  return render_scenarios()
    if tab == "tab-workforce":  return render_workforce()
    if tab == "tab-budget":     return render_budget()
    if tab == "tab-risks":      return render_risks()
    if tab == "tab-narrative":  return render_narrative()
    if tab == "tab-causality":
        from pages.causality import render_causality
        return render_causality()
    if tab == "tab-method":     return render_methodology()
    return html.Div()


# ── Slider value display (one callback per param) ─────────────────────────────

for _p in PARAMS:
    @app.callback(
        Output(f"val-{_p['id']}", "children"),
        Input(f"slider-{_p['id']}", "value"),
    )
    def _update_val(v, pid=_p["id"]):
        step     = next(x["step"] for x in PARAMS if x["id"] == pid)
        fmt      = f"{v:.2f}" if step < 0.1 else (f"{v:.1f}" if step < 1 else f"{v:.0f}")
        unit_map = {"inflation": "%/yr", "scope": "%", "political": "%",
                    "kpi": "", "workforce": "%", "euston": "%"}
        return fmt + unit_map.get(pid, "")


# ── Live MC: sliders → cluster charts + fan + histogram ──────────────────────

@app.callback(
    Output("live-cluster-chart", "figure"),
    Output("fan-chart",          "figure"),
    Output("cost-histogram",     "figure"),
    Output("pos-pct-live",       "children"),
    Output("neu-pct-live",       "children"),
    Output("neg-pct-live",       "children"),
    [Input(f"slider-{p['id']}", "value") for p in PARAMS],
    prevent_initial_call=False,
)
def update_mc(*vals):
    inflation, scope, political, kpi, workforce, euston = vals
    mc = run_monte_carlo(
        n_sims=5000,
        inflation=inflation, scope_risk=scope,
        political_risk=political, kpi_score=kpi,
        workforce_stability=workforce, euston_prob=euston,
    )
    cp = mc["cluster_probs"]

    cluster_fig = go.Figure(go.Bar(
        x=["Controlled", "Managed", "Escalation"],
        y=[cp["pos"], cp["neu"], cp["neg"]],
        marker_color=[_ha(C["pos"], 0.6), _ha(C["neu"], 0.6), _ha(C["neg"], 0.6)],
        marker_line_color=[C["pos"], C["neu"], C["neg"]], marker_line_width=2,
        text=[f"{cp['pos']:.0f}%", f"{cp['neu']:.0f}%", f"{cp['neg']:.0f}%"],
        textposition="outside",
        textfont=dict(color=C["muted"], size=12, family="DM Mono,monospace"),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    cluster_fig.update_layout(**LAYOUT_NO_AXES,
        yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)))

    fan   = mc["fan_data"]
    years = fan["years"]
    fan_fig = go.Figure()
    fan_fig.add_trace(go.Scatter(
        x=years+years[::-1], y=fan["p90"]+fan["p10"][::-1],
        fill="toself", fillcolor=_ha(C["acc"], 0.07),
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    for key, name, col, w in [
        ("p10", "10th pct", C["pos"], 1.5),
        ("p50", "Median",   C["acc"], 2.5),
        ("p90", "90th pct", C["neg"], 1.5),
    ]:
        fan_fig.add_trace(go.Scatter(
            x=years, y=fan[key], name=name,
            line=dict(color=col, width=w, dash="dot" if key != "p50" else "solid"),
            hovertemplate=f"£%{{y:.0f}}bn<extra>{name}</extra>"))
    fan_fig.add_hline(y=40, line_dash="dash", line_color=C["muted2"],
                      annotation_text="~£40bn spent", annotation_font_color=C["muted2"],
                      annotation_font_size=9)
    fan_fig.update_layout(**LAYOUT_BARE,
        yaxis=dict(tickprefix="£", ticksuffix="bn", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["muted2"], size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.18),
        hovermode="x unified", margin=dict(l=50, r=10, t=10, b=40))

    costs   = mc["costs"]
    hist_fig = go.Figure(go.Histogram(
        x=costs, nbinsx=55,
        marker_color=_ha(C["acc"], 0.5),
        marker_line_color=C["acc"], marker_line_width=0.5,
        hovertemplate="£%{x:.0f}bn: %{y}<extra></extra>"))
    for threshold, col, lbl in [(90, C["pos"], "£90bn"), (115, C["neg"], "£115bn")]:
        hist_fig.add_vline(x=threshold, line_dash="dash", line_color=col,
                           annotation_text=lbl, annotation_font_color=col, annotation_font_size=9)
    hist_fig.update_layout(**LAYOUT_NO_AXES,
        xaxis=dict(tickprefix="£", ticksuffix="bn", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(gridcolor=C["grid"], zeroline=False, tickfont=dict(color=C["muted2"], size=10)))

    return (cluster_fig, fan_fig, hist_fig,
            f"{cp['pos']:.0f}%", f"{cp['neu']:.0f}%", f"{cp['neg']:.0f}%")


# ── Parameter sweep buttons ───────────────────────────────────────────────────

_sweep_btn_inputs = [Input(f"sweep-btn-{p['id']}", "n_clicks") for p in PARAMS]

@app.callback(
    Output("sweep-chart", "figure"),
    *[(Output(f"sweep-btn-{p['id']}", "style"),) for p in PARAMS],
    _sweep_btn_inputs,
    prevent_initial_call=False,
)
def update_sweep(*all_clicks):
    ctx       = callback_context
    active_id = "inflation"
    if ctx.triggered:
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if btn_id.startswith("sweep-btn-"):
            active_id = btn_id.replace("sweep-btn-", "")
    styles = []
    for p in PARAMS:
        active = (p["id"] == active_id)
        styles.append({
            "fontSize": "11px", "padding": "5px 12px",
            "border": f"1px solid {C['border2']}",
            "borderRadius": "20px", "cursor": "pointer",
            "background": _ha(C["acc"], 0.15) if active else C["bg3"],
            "color": C["acc"] if active else C["muted"],
            "fontFamily": "DM Mono,monospace", "marginBottom": "6px",
            "width": "100%", "textAlign": "left",
        })
    return (fig_parameter_sweep(active_id), *styles)


# ── Scenario matrix (pre-computed on tab load) ────────────────────────────────

@app.callback(
    Output("scenario-matrix-chart", "figure"),
    Input("main-tabs", "active_tab"),
    prevent_initial_call=False,
)
def update_scenario_matrix(tab):
    return fig_scenario_matrix()


# ── Scenario narrative (updates with sliders) ─────────────────────────────────

@app.callback(
    Output("scenario-narrative-box", "children"),
    [Input(f"slider-{p['id']}", "value") for p in PARAMS],
    prevent_initial_call=False,
)
def update_scenario_narrative(*vals):
    inflation, scope, political, kpi, workforce, euston = vals
    mc = run_monte_carlo(n_sims=3000, inflation=inflation, scope_risk=scope,
                         political_risk=political, kpi_score=kpi,
                         workforce_stability=workforce, euston_prob=euston)
    return _build_scenario_narrative(mc["cluster_probs"])


# ── Budget tab: live MC + viability ──────────────────────────────────────────

@app.callback(
    Output("vmc-val-cost",      "children"),
    Output("vmc-val-km",        "children"),
    *[Output(f"vmc-val-{p['id']}", "children") for p in PARAMS],
    Output("vmc-donut-chart",   "figure"),
    Output("vmc-sent-gauge",    "figure"),
    Output("vmc-cpkm-gauge",    "figure"),
    Output("vmc-cluster-bar",   "figure"),
    Output("vmc-fan-chart",     "figure"),
    Output("vmc-tornado-chart", "figure"),
    Output("vmc-narrative",     "children"),
    Input("vmc-slider-cost",    "value"),
    Input("vmc-slider-km",      "value"),
    *[Input(f"vmc-slider-{p['id']}", "value") for p in PARAMS],
    prevent_initial_call=False,
)
def update_vmc(cost_bn, km, *param_vals):
    inflation, scope, political, kpi, workforce, euston = param_vals

    unit_map = {"inflation": "%/yr", "scope": "%", "political": "%",
                "kpi": "", "workforce": "%", "euston": "%"}
    step_map = {p["id"]: p["step"] for p in PARAMS}
    val_labels = []
    for p, v in zip(PARAMS, param_vals):
        fmt = f"{v:.2f}" if step_map[p['id']] < 0.1 else (
              f"{v:.1f}" if step_map[p['id']] < 1 else f"{v:.0f}")
        val_labels.append(fmt + unit_map.get(p["id"], ""))

    sent    = pred_sentiment(cost_bn, km)
    pol_adj = min(political + max(0, (-sent - 0.40) * 40), 90)
    cpkm    = cost_bn / max(km, 1)

    mc = run_monte_carlo(
        n_sims=5000, inflation=inflation, scope_risk=scope,
        political_risk=pol_adj, kpi_score=kpi,
        workforce_stability=workforce, euston_prob=euston,
    )
    cp     = mc["cluster_probs"]
    viable = sent > VIABILITY_DATA["threshold_sent"]

    if cp["neg"] < 25 and viable:
        narr = (f"At £{cost_bn:.0f}bn across {km}km, the project sits in the "
                f"viable zone with predicted sentiment {sent:.2f}. "
                f"Monte Carlo gives {cp['pos']:.0f}% probability of controlled delivery — "
                f"the strongest positive signal in this analysis. "
                f"Maintain inflation below 5% and KPI score above 2.2 to hold this trajectory.")
    elif cp["neg"] < 45 and sent > -0.6:
        _ab = "above" if viable else "below"
        _pn = ("Conditions are survivable but costs need active control."
               if viable else
               "Political risk is elevated. Each further 1bn increases worsens sentiment ~0.004 pts.")
        narr = (f"At £{cost_bn:.0f}bn / {km}km (£{cpkm:.3f}bn/km), "
                f"sentiment is predicted at {sent:.2f} — {_ab} the viability threshold. "
                f"Escalation probability is {cp['neg']:.0f}%. "
                f"The managed overrun cluster dominates at {cp['neu']:.0f}%. "
                + _pn)
    else:
        narr = (f"At £{cost_bn:.0f}bn / {km}km (£{cpkm:.3f}bn/km), the project is "
                f"deeply unviable. Predicted sentiment {sent:.2f} is far below the "
                f"viability threshold of −0.40. Escalation probability reaches {cp['neg']:.0f}%. "
                f"The model suggests that at this cost-per-km, no governance reset can "
                f"restore political survivability — only a structural change in cost or "
                f"network scope can shift the trajectory.")

    return (
        f"£{cost_bn:.0f}bn",
        f"{km:.0f}km",
        *val_labels,
        fig_donut_clusters(cp),
        fig_sentiment_gauge(sent),
        fig_cpkm_gauge(cpkm),
        fig_mc_cluster_bar(cp),
        fig_mc_fan_with_sentiment(mc["fan_data"], cost_bn, km),
        fig_sensitivity_vs_sentiment(cost_bn, km),
        narr,
    )


# ── Joint optimisation matrix ────────────────────────────────────────────────

@app.callback(
    Output("vmc-matrix-chart", "figure"),
    Input("vmc-slider-cost",   "value"),
    Input("vmc-slider-km",     "value"),
    prevent_initial_call=False,
)
def update_vmc_matrix(cost_bn, km):
    return fig_cluster_sentiment_matrix()


# ── Narrative tab switcher ────────────────────────────────────────────────────

@app.callback(
    Output("narrative-output", "children"),
    Input("btn-pos", "n_clicks"),
    Input("btn-neu", "n_clicks"),
    Input("btn-neg", "n_clicks"),
    prevent_initial_call=False,
)
def switch_narrative(n_pos, n_neu, n_neg):
    ctx  = callback_context
    kind = "neu"
    if ctx.triggered:
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        kind   = {"btn-pos": "pos", "btn-neu": "neu", "btn-neg": "neg"}.get(btn_id, "neu")
    return narrative_box(NARRATIVES[kind]["tag"], NARRATIVES[kind]["body"])
