import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm

from config.theme import C, PLOTLY_LAYOUT, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from data.hs2_data import PARAMS, VIABILITY_DATA
from models.monte_carlo import run_monte_carlo
from models.viability import pred_sentiment


def fig_cluster_donut(pos=18, neu=45, neg=37):
    fig = go.Figure(go.Pie(
        labels=[f"Controlled ({pos:.0f}%)", f"Managed ({neu:.0f}%)", f"Escalation ({neg:.0f}%)"],
        values=[pos, neu, neg],
        hole=0.65,
        marker=dict(
            colors=[_ha(C["pos"], 0.27), _ha(C["neu"], 0.27), _ha(C["neg"], 0.27)],
            line=dict(color=[C["pos"], C["neu"], C["neg"]], width=2)),
        textfont=dict(color=C["muted"], size=10),
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT,
        showlegend=True,
        legend=dict(orientation="v", x=1.0, font=dict(color=C["muted"], size=10)),
        annotations=[dict(text="Probability", x=0.5, y=0.5, font=dict(color=C["muted"], size=11),
                          showarrow=False)])
    return fig


def fig_fan_chart(fan):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fan["years"] + fan["years"][::-1],
        y=fan["p90"] + fan["p10"][::-1],
        fill="toself", fillcolor="rgba(124,158,248,0.06)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=fan["years"] + fan["years"][::-1],
        y=fan["p75"] + fan["p25"][::-1],
        fill="toself", fillcolor="rgba(124,158,248,0.10)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    for key, name, col, dash, w in [
        ("p10", "10th pct", C["pos"], "dot",   1.5),
        ("p50", "Median",   C["acc"], "solid",  2.5),
        ("p90", "90th pct", C["neg"], "dot",   1.5),
    ]:
        fig.add_trace(go.Scatter(
            x=fan["years"], y=fan[key], name=name,
            line=dict(color=col, dash=dash, width=w),
            hovertemplate="£%{y:.1f}bn<extra>" + name + "</extra>"))
    fig.add_hline(y=40, line_dash="dash", line_color=C["muted2"],
                  annotation_text="~£40bn spent (2025)", annotation_font_color=C["muted2"])
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Monte Carlo fan chart — cost forecast to 2040 (£bn)", font=dict(color=C["text"], size=13)),
        yaxis_tickprefix="£", yaxis_ticksuffix="bn",
        legend=dict(orientation="h", y=-0.15))
    return fig


def fig_cost_histogram(costs):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=costs, nbinsx=60,
        marker_color=_ha(C["acc"], 0.47),
        marker_line_color=C["acc"], marker_line_width=0.5,
        hovertemplate="£%{x:.0f}bn: %{y} simulations<extra></extra>"))
    for x, col, lbl in [(90, C["pos"], "Positive<br>boundary"),
                         (110, C["neg"], "Negative<br>boundary")]:
        fig.add_vline(x=x, line_dash="dash", line_color=col,
                      annotation_text=f"£{x}bn", annotation_font_color=col)
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost distribution — 10,000 simulations", font=dict(color=C["text"], size=13)),
        xaxis_tickprefix="£", xaxis_ticksuffix="bn",
        yaxis_title="Simulation count")
    return fig


def fig_sensitivity(params):
    labels  = [p["label"] for p in params]
    impacts = [p["impact"] for p in params]
    colours = [C["neu"] if p["effect"] == "neg" else C["acc"] for p in params]
    fig = go.Figure(go.Bar(
        x=impacts, y=labels, orientation="h",
        marker_color=[_ha(c, 0.53) for c in colours],
        marker_line_color=colours, marker_line_width=1.5,
        text=[f"{i}%" for i in impacts], textposition="outside",
        textfont=dict(color=C["muted"], size=10),
        hovertemplate="%{y}: %{x}% impact on outcome<extra></extra>",
    ))
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Parameter sensitivity — % variance explained", font=dict(color=C["text"], size=13)),
        xaxis=dict(range=[0, 105], ticksuffix="%", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)),
        margin=dict(l=180, r=60, t=40, b=20))
    return fig


def fig_migration_heatmap():
    infl_vals = [2, 4, 5, 6, 7, 8, 9, 10, 12]
    pol_vals  = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    z = []
    for pol in pol_vals:
        row = []
        for infl in infl_vals:
            mc = run_monte_carlo(n_sims=1200, inflation=infl, political_risk=pol,
                                 scope_risk=35, kpi_score=2.35,
                                 workforce_stability=55, euston_prob=30)
            row.append(round(mc["cluster_probs"]["neg"], 1))
        z.append(row)
    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"{v}%/yr" for v in infl_vals],
        y=[f"{v}%" for v in pol_vals],
        colorscale=[
            [0.0,  "#3B6D11"], [0.35, "#639922"], [0.5, "#BA7517"],
            [0.65, "#c04040"], [1.0,  "#7c2020"]],
        zmin=25, zmax=80,
        colorbar=dict(
            title=dict(text="Neg %", font=dict(color=C["muted"], size=10)),
            tickfont=dict(color=C["muted2"], size=9), thickness=10, len=0.8),
        hovertemplate="Inflation: %{x}<br>Political risk: %{y}<br>Negative cluster: %{z:.0f}%<extra></extra>",
        text=[[f"{v:.0f}" for v in row] for row in z],
        texttemplate="%{text}%",
        textfont=dict(size=9, color="rgba(255,255,255,0.8)"),
    ))
    fig.add_trace(go.Scatter(
        x=["5%/yr"], y=["40%"],
        mode="markers", showlegend=False,
        marker=dict(size=14, color="rgba(0,0,0,0)",
                    line=dict(color="white", width=2.5), symbol="circle"),
        hovertemplate="Current position<extra></extra>"))
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Negative cluster probability (%) — inflation × political risk",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Inflation rate", tickfont=dict(color=C["muted"], size=10),
                   gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Political risk", tickfont=dict(color=C["muted"], size=10),
                   gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=55, r=70, t=45, b=50))
    return fig


def fig_positive_surface():
    infl_vals = [2, 4, 5, 6, 7, 8, 9, 10, 12]
    kpi_vals  = [1.6, 1.8, 2.0, 2.2, 2.35, 2.5, 2.7, 2.9]
    z = []
    for kpi in kpi_vals:
        row = []
        for infl in infl_vals:
            mc = run_monte_carlo(n_sims=1200, inflation=infl, kpi_score=kpi,
                                 scope_risk=35, political_risk=40,
                                 workforce_stability=55, euston_prob=30)
            row.append(round(mc["cluster_probs"]["pos"], 1))
        z.append(row)
    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"{v}%/yr" for v in infl_vals],
        y=[f"{v}" for v in kpi_vals],
        colorscale=[
            [0.0,  "#7c2020"], [0.3, "#c04040"], [0.5, "#BA7517"],
            [0.7,  "#639922"], [1.0, "#3B6D11"]],
        zmin=5, zmax=45,
        colorbar=dict(
            title=dict(text="Pos %", font=dict(color=C["muted"], size=10)),
            tickfont=dict(color=C["muted2"], size=9), thickness=10, len=0.8),
        hovertemplate="Inflation: %{x}<br>KPI score: %{y}<br>Positive cluster: %{z:.0f}%<extra></extra>",
        text=[[f"{v:.0f}" for v in row] for row in z],
        texttemplate="%{text}%",
        textfont=dict(size=9, color="rgba(255,255,255,0.8)"),
    ))
    fig.add_trace(go.Scatter(
        x=["5%/yr"], y=["2.35"],
        mode="markers", showlegend=False,
        marker=dict(size=14, color="rgba(0,0,0,0)",
                    line=dict(color="white", width=2.5), symbol="circle"),
        hovertemplate="Current position<extra></extra>"))
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Positive cluster probability (%) — inflation × KPI score",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Inflation rate", tickfont=dict(color=C["muted"], size=10),
                   gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="KPI enterprise score", tickfont=dict(color=C["muted"], size=10),
                   gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=55, r=70, t=45, b=50))
    return fig


def fig_parameter_sweep(param_id="inflation"):
    param    = next(p for p in PARAMS if p["id"] == param_id)
    kwarg_name = {"scope": "scope_risk", "political": "political_risk",
                  "kpi": "kpi_score", "workforce": "workforce_stability",
                  "euston": "euston_prob", "inflation": "inflation"}
    mc_defaults = {kwarg_name.get(p["id"], p["id"]): p["val"] for p in PARAMS}

    lo, hi   = param["min"], param["max"]
    n_steps  = 30
    vals     = np.linspace(lo, hi, n_steps)
    pos_arr, neu_arr, neg_arr = [], [], []

    for v in vals:
        mc_param = kwarg_name.get(param_id, param_id)
        kwargs   = {**mc_defaults, mc_param: float(v)}
        mc       = run_monte_carlo(n_sims=1000, **kwargs)
        cp       = mc["cluster_probs"]
        pos_arr.append(cp["pos"])
        neu_arr.append(cp["neu"])
        neg_arr.append(cp["neg"])

    x_vals    = [round(float(v), 2) for v in vals]
    neg_stack = neg_arr
    neu_stack = [n + p for n, p in zip(neg_arr, neu_arr)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=neg_stack, name="Escalation",
        fill="tozeroy", fillcolor=_ha(C["neg"], 0.35),
        line=dict(color=C["neg"], width=1.5),
        hovertemplate=f"{param['label']}=%{{x}}<br>Negative: %{{y:.0f}}%<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=x_vals, y=neu_stack, name="Managed overrun",
        fill="tonexty", fillcolor=_ha(C["neu"], 0.3),
        line=dict(color=C["neu"], width=1.5),
        hovertemplate=f"{param['label']}=%{{x}}<br>Neg+Neu: %{{y:.0f}}%<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=x_vals, y=[100]*n_steps, name="Controlled delivery",
        fill="tonexty", fillcolor=_ha(C["pos"], 0.3),
        line=dict(color=C["pos"], width=1.5),
        hovertemplate=f"{param['label']}=%{{x}}<br>All clusters: 100%<extra></extra>"))
    cur = param["val"]
    fig.add_vline(x=cur, line=dict(color="white", width=1.5, dash="dot"),
        annotation_text=f"Current: {cur}",
        annotation_font_color=C["text"], annotation_font_size=9)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text=f"Cluster probabilities across {param['label']} range",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title=param["label"], gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(title="Probability", ticksuffix="%", range=[0, 102],
                   gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.22),
        margin=dict(l=50, r=20, t=45, b=60))
    return fig


def fig_scenario_matrix(cp_baseline=None):
    named = [
        ("Baseline",         dict(inflation=5,  scope_risk=35, political_risk=40, kpi_score=2.35, workforce_stability=55, euston_prob=30)),
        ("Inflation spike",  dict(inflation=10, scope_risk=35, political_risk=40, kpi_score=2.35, workforce_stability=55, euston_prob=30)),
        ("Political review", dict(inflation=5,  scope_risk=35, political_risk=80, kpi_score=2.35, workforce_stability=55, euston_prob=30)),
        ("Leadership reset", dict(inflation=5,  scope_risk=35, political_risk=40, kpi_score=1.9,  workforce_stability=30, euston_prob=15)),
        ("KPI + Euston win", dict(inflation=5,  scope_risk=20, political_risk=30, kpi_score=2.7,  workforce_stability=75, euston_prob=70)),
        ("Perfect storm",    dict(inflation=11, scope_risk=75, political_risk=85, kpi_score=1.8,  workforce_stability=20, euston_prob=5)),
        ("Best case",        dict(inflation=2,  scope_risk=10, political_risk=15, kpi_score=2.9,  workforce_stability=90, euston_prob=90)),
    ]
    labels = [n for n, _ in named]
    pos_vals, neu_vals, neg_vals = [], [], []
    for name, kwargs in named:
        mc = run_monte_carlo(n_sims=2500, **kwargs)
        cp = mc["cluster_probs"]
        pos_vals.append(round(cp["pos"], 1))
        neu_vals.append(round(cp["neu"], 1))
        neg_vals.append(round(cp["neg"], 1))
    fig = go.Figure()
    for vals, name, col in [
        (pos_vals, "Controlled delivery", C["pos"]),
        (neu_vals, "Managed overrun",     C["neu"]),
        (neg_vals, "Escalation",          C["neg"]),
    ]:
        fig.add_trace(go.Bar(
            name=name, x=labels, y=vals,
            marker_color=_ha(col, 0.6),
            marker_line_color=col, marker_line_width=1.5,
            text=[f"{v:.0f}%" for v in vals],
            textposition="auto",
            textfont=dict(color="rgba(255,255,255,0.9)", size=9),
            hovertemplate=f"{name}: %{{y:.1f}}%<extra></extra>"))
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Named scenario comparison — cluster probabilities",
                   font=dict(color=C["text"], size=12)),
        barmode="stack",
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        yaxis=dict(range=[0, 103], ticksuffix="%", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.2),
        margin=dict(l=45, r=20, t=45, b=70))
    return fig


def fig_donut_clusters(cluster_probs):
    pos, neu, neg = cluster_probs["pos"], cluster_probs["neu"], cluster_probs["neg"]
    fig = go.Figure(go.Pie(
        labels=["Controlled", "Managed", "Escalation"],
        values=[pos, neu, neg],
        hole=0.65,
        direction="clockwise",
        sort=False,
        marker=dict(
            colors=[_ha(C["pos"], 0.75), _ha(C["neu"], 0.75), _ha(C["neg"], 0.75)],
            line=dict(color=[C["pos"], C["neu"], C["neg"]], width=2)),
        textfont=dict(color=C["text"], size=11),
        textinfo="label+percent",
        hovertemplate="%{label}: %{value:.0f}%<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{neg:.0f}%</b><br><span style='font-size:11px'>escalation</span>",
        x=0.5, y=0.5, xref="paper", yref="paper",
        font=dict(color=C["neg"], size=20, family="Fraunces, serif"),
        showarrow=False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=30),
        showlegend=True,
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center",
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(color=C["muted"], size=10)),
    )
    return fig


def fig_mc_cluster_bar(cluster_probs):
    pos, neu, neg = cluster_probs["pos"], cluster_probs["neu"], cluster_probs["neg"]
    fig = go.Figure()
    for label, val, col in [
        ("Controlled delivery", pos, C["pos"]),
        ("Managed overrun",     neu, C["neu"]),
        ("Escalation",          neg, C["neg"]),
    ]:
        fig.add_trace(go.Bar(
            x=[val], y=[label], orientation="h",
            name=label,
            marker=dict(color=_ha(col, 0.6), line=dict(color=col, width=1.5)),
            text=[f"{val:.0f}%"],
            textposition="outside",
            textfont=dict(color=col, size=13, family="DM Mono, monospace"),
            hovertemplate=f"{label}: %{{x:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=11),
        margin=dict(l=160, r=60, t=10, b=10),
        barmode="overlay", showlegend=False,
        xaxis=dict(range=[0, 110], ticksuffix="%", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(color=C["text"], size=12)),
    )
    return fig


def fig_mc_fan_with_sentiment(fan_data, cost_bn, km):
    years = fan_data["years"]
    fig   = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=fan_data["p90"] + fan_data["p10"][::-1],
        fill="toself", fillcolor=_ha(C["acc"], 0.07),
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"), secondary_y=False)
    for key, name, col, w in [
        ("p10", "10th pct", C["pos"], 1.5),
        ("p50", "Median",   C["acc"], 2.5),
        ("p90", "90th pct", C["neg"], 1.5),
    ]:
        fig.add_trace(go.Scatter(
            x=years, y=fan_data[key], name=name,
            line=dict(color=col, width=w, dash="dot" if key != "p50" else "solid"),
            hovertemplate=f"£%{{y:.0f}}bn<extra>{name}</extra>"), secondary_y=False)
    sent_traj = [pred_sentiment(c, km) for c in fan_data["p50"]]
    sent_hi   = [pred_sentiment(c, km) for c in fan_data["p90"]]
    sent_lo   = [pred_sentiment(c, km) for c in fan_data["p10"]]
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=sent_hi + sent_lo[::-1],
        fill="toself", fillcolor=_ha(C["neg"], 0.06),
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"), secondary_y=True)
    fig.add_trace(go.Scatter(
        x=years, y=sent_traj, name="Predicted sentiment",
        line=dict(color=C["neg"], width=2, dash="dot"),
        hovertemplate="Sentiment: %{y:.2f}<extra></extra>"), secondary_y=True)
    fig.add_hline(y=VIABILITY_DATA["threshold_sent"],
        line=dict(color=C["neu"], width=1, dash="dash"),
        annotation_text="Viability threshold",
        annotation_font_color=C["neu"], annotation_font_size=9)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=11),
        margin=dict(l=50, r=60, t=30, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.18),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Total cost (£bn)", tickprefix="£", ticksuffix="bn",
                     gridcolor=C["grid"], zeroline=False,
                     tickfont=dict(color=C["muted2"], size=10), secondary_y=False)
    fig.update_yaxes(title_text="Predicted sentiment", gridcolor="rgba(0,0,0,0)",
                     zeroline=False, range=[-1.1, 0.2],
                     tickfont=dict(color=C["muted2"], size=10), secondary_y=True)
    fig.update_xaxes(gridcolor=C["grid"], tickfont=dict(color=C["muted2"], size=10))
    return fig


def fig_cluster_sentiment_matrix():
    V          = VIABILITY_DATA
    cost_range = np.linspace(30, 130, 100)
    km_range   = np.linspace(100, 600, 100)
    C_g, K_g   = np.meshgrid(cost_range, km_range)

    def _esc(cost_bn, km):
        cpkm    = cost_bn / max(km, 1)
        sent    = float(np.clip(
            V["slope"] * np.log(max(cpkm, 0.001)) + V["intercept"], -1.0, 0.1))
        pol_pen = max(0, (-sent - 0.40) * 0.06)
        sigma   = 0.35 + pol_pen
        z       = (np.log(115) - np.log(max(cost_bn, 1))) / sigma
        return float(np.clip((1 - norm.cdf(z)) * 100, 1, 99))

    Z = np.vectorize(_esc)(C_g, K_g)

    fig = go.Figure()
    fig.add_trace(go.Contour(
        z=Z, x=cost_range, y=km_range,
        colorscale=[
            [0.0,  "#2d5a1e"], [0.15, "#639922"], [0.35, "#d47a10"],
            [0.6,  "#c04040"], [1.0,  "#7c2020"],
        ],
        zmin=0, zmax=100,
        contours=dict(start=0, end=100, size=10, showlabels=True,
                      labelfont=dict(size=9, color="rgba(255,255,255,0.75)")),
        colorbar=dict(
            title=dict(text="Escalation %", font=dict(color=C["muted"], size=10)),
            tickfont=dict(color=C["muted"], size=9), thickness=12, len=0.8),
        hovertemplate="Cost: £%{x:.0f}bn<br>Network: %{y:.0f}km<br>Escalation: %{z:.0f}%<extra></extra>",
    ))
    bx = np.linspace(14, 130, 300)
    by = np.clip(bx / V["threshold_cpkm"], 100, 600)
    fig.add_trace(go.Scatter(
        x=bx, y=by, mode="lines",
        name="Sentiment viability boundary",
        line=dict(color="white", width=2, dash="dash"),
        hovertemplate="Boundary: £%{x:.0f}bn / %{y:.0f}km<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=V["cost_mid"], y=V["network_km"],
        mode="lines", showlegend=False,
        line=dict(color="rgba(255,255,255,0.4)", width=1.5)))
    for i, (c, k, yr, v) in enumerate(
            zip(V["cost_mid"], V["network_km"], V["years"], V["verified"])):
        is_last = (i == len(V["years"]) - 1)
        fig.add_trace(go.Scatter(
            x=[c], y=[k], mode="markers+text",
            marker=dict(size=14 if is_last else 9,
                        color="white", opacity=1.0 if v else 0.5,
                        symbol="star" if is_last else "circle",
                        line=dict(color=C["bg2"], width=2)),
            text=[str(yr)],
            textposition="top right",
            textfont=dict(color="white", size=9),
            showlegend=False,
            hovertemplate=(
                f"<b>{yr}</b>: £{c:.0f}bn / {k}km<br>"
                f"Escalation: {_esc(c, k):.0f}%<extra></extra>")))
    for km_sc, col_sc, lbl in [
            (540, C["pos"], "540km max: £76bn"),
            (400, C["neu"], "400km max: £57bn"),
            (225, C["neg"], "225km max: £32bn")]:
        max_c = V["threshold_cpkm"] * km_sc
        if 30 <= max_c <= 130:
            fig.add_trace(go.Scatter(
                x=[max_c], y=[km_sc], mode="markers+text",
                marker=dict(size=9, color=col_sc, symbol="diamond",
                            line=dict(color=C["bg2"], width=1.5)),
                text=[lbl], textposition="middle right",
                textfont=dict(color=col_sc, size=9),
                showlegend=False,
                hovertemplate=f"{lbl}<extra></extra>"))
    fig.add_annotation(
        x=55, y=530, text="Optimal zone — low escalation",
        font=dict(color="rgba(255,255,255,0.85)", size=10),
        showarrow=False, bgcolor="rgba(0,0,0,0.5)", borderpad=4)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=10),
        title=dict(text="Joint optimisation: escalation probability across (cost × network) space",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Total project cost (£bn)",
                   gridcolor="rgba(255,255,255,0.08)", zeroline=False,
                   tickprefix="£", ticksuffix="bn",
                   tickfont=dict(color="rgba(255,255,255,0.5)", size=10), range=[30, 130]),
        yaxis=dict(title="Network length (km)",
                   gridcolor="rgba(255,255,255,0.08)", zeroline=False,
                   ticksuffix="km",
                   tickfont=dict(color="rgba(255,255,255,0.5)", size=10), range=[100, 610]),
        margin=dict(l=60, r=80, t=50, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", font=dict(color="white", size=9)),
        showlegend=True,
    )
    return fig


def fig_sensitivity_vs_sentiment(cost_bn, km):
    base_mc   = run_monte_carlo(n_sims=2000, inflation=5.0, scope_risk=35,
                                political_risk=40, kpi_score=2.35,
                                workforce_stability=55, euston_prob=30)
    base_neg  = base_mc["cluster_probs"]["neg"]
    base_sent = pred_sentiment(cost_bn, km)

    perturbations = [
        ("inflation", "Inflation rate",    +3.0, +1),
        ("scope",     "Scope change risk", +20,  +1),
        ("political", "Political risk",    +20,  +1),
        ("kpi",       "KPI score",         +0.4, -1),
        ("workforce", "Workforce stable.", +20,  -1),
        ("euston",    "Euston restart",    +20,  -1),
    ]
    kwmap = {"inflation": "inflation", "scope": "scope_risk", "political": "political_risk",
             "kpi": "kpi_score", "workforce": "workforce_stability", "euston": "euston_prob"}

    labels, delta_neg, delta_sent = [], [], []
    for pid, label, delta, sign in perturbations:
        kwargs = dict(inflation=5.0, scope_risk=35, political_risk=40,
                      kpi_score=2.35, workforce_stability=55, euston_prob=30)
        kwargs[kwmap[pid]] += delta * sign
        hi_mc  = run_monte_carlo(n_sims=2000, **kwargs)
        hi_neg = hi_mc["cluster_probs"]["neg"]
        cost_impact = {"inflation": cost_bn*0.06, "scope": cost_bn*0.04,
                       "political": cost_bn*0.03, "kpi": -cost_bn*0.03,
                       "workforce": -cost_bn*0.02, "euston": -cost_bn*0.02}
        new_cost = cost_bn + cost_impact.get(pid, 0) * sign
        hi_sent  = pred_sentiment(new_cost, km)
        labels.append(label)
        delta_neg.append(round((hi_neg - base_neg), 1))
        delta_sent.append(round((hi_sent - base_sent), 3))

    order      = sorted(range(len(labels)), key=lambda i: abs(delta_neg[i]), reverse=True)
    labels     = [labels[i] for i in order]
    delta_neg  = [delta_neg[i] for i in order]
    delta_sent = [delta_sent[i] for i in order]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Escalation cluster Δ (%)", "Sentiment Δ"],
                        horizontal_spacing=0.12)
    colours_neg = [_ha(C["neg"], 0.7) if d > 0 else _ha(C["pos"], 0.7) for d in delta_neg]
    fig.add_trace(go.Bar(
        x=delta_neg, y=labels, orientation="h",
        marker=dict(color=colours_neg,
                    line=dict(color=[C["neg"] if d > 0 else C["pos"] for d in delta_neg], width=1)),
        text=[f"+{d:.0f}%" if d > 0 else f"{d:.0f}%" for d in delta_neg],
        textposition="outside",
        textfont=dict(size=10, color=[C["neg"] if d > 0 else C["pos"] for d in delta_neg]),
        hovertemplate="%{y}: %{x:+.1f}pp escalation<extra></extra>",
        showlegend=False,
    ), row=1, col=1)
    colours_sent = [_ha(C["neg"], 0.7) if d < 0 else _ha(C["pos"], 0.7) for d in delta_sent]
    fig.add_trace(go.Bar(
        x=delta_sent, y=labels, orientation="h",
        marker=dict(color=colours_sent,
                    line=dict(color=[C["neg"] if d < 0 else C["pos"] for d in delta_sent], width=1)),
        text=[f"{d:+.3f}" for d in delta_sent],
        textposition="outside",
        textfont=dict(size=10, color=[C["neg"] if d < 0 else C["pos"] for d in delta_sent]),
        hovertemplate="%{y}: %{x:+.3f} sentiment<extra></extra>",
        showlegend=False,
    ), row=1, col=2)
    for col_i in [1, 2]:
        fig.add_vline(x=0, line_color=C["muted2"], line_width=1, row=1, col=col_i)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=10),
        margin=dict(l=120, r=60, t=40, b=10), showlegend=False)
    for ax in ["xaxis", "xaxis2"]:
        fig.layout[ax].update(gridcolor=C["grid"], zeroline=False,
                              tickfont=dict(color=C["muted2"], size=10))
    for ax in ["yaxis", "yaxis2"]:
        fig.layout[ax].update(gridcolor="rgba(0,0,0,0)",
                              tickfont=dict(color=C["text"], size=11))
    for ann in fig.layout.annotations:
        ann.update(font=dict(color=C["muted"], size=11))
    return fig
