import numpy as np
import plotly.graph_objects as go
from scipy import stats

from config.theme import C, PLOTLY_LAYOUT, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from data.hs2_data import WORKFORCE_DF, SENTIMENT_DF, STAKEHOLDER_SENT, WORKFORCE_APPROVAL
from models.viability import _combined_approval


def fig_workforce():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=WORKFORCE_DF["period"],
        y=WORKFORCE_DF["total"],
        mode="lines+markers+text",
        name="Total workforce (all)",
        line=dict(color=C["acc"], width=2.5),
        marker=dict(size=10, color=C["acc"], line=dict(color=C["bg"], width=2)),
        text=[f"{v:,}" for v in WORKFORCE_DF["total"]],
        textposition="top center",
        textfont=dict(color=C["text"], size=10),
        hovertemplate="%{x}<br>Total: %{y:,}<extra></extra>",
        fill="tozeroy", fillcolor=_ha(C["acc"], 0.08),
    ))
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Total verified workforce milestones (HS2 Ltd + supply chain)",
                   font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[0, 40000], tickformat=",", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        showlegend=False)
    fig.add_annotation(
        x=0, y=36000, xanchor="left",
        text="Note: HS2 Ltd direct staff vs supply chain split not confirmed from documents read",
        font=dict(color=C["muted2"], size=9), showarrow=False)
    return fig


def fig_sentiment_timeline():
    fig = go.Figure()
    for col_name, colour, dash in [
        ("parliament", C["neg"], "solid"),
        ("workforce",  C["pos"], "dot"),
        ("media",      C["neu"], "dash"),
    ]:
        fig.add_trace(go.Scatter(
            x=SENTIMENT_DF["year"], y=SENTIMENT_DF[col_name],
            name=col_name.capitalize(),
            line=dict(color=colour, width=2, dash=dash),
            hovertemplate="%{y:.2f}<extra>" + col_name + "</extra>"))
    fig.add_hline(y=0, line_color=C["muted2"], line_width=1)
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Stakeholder sentiment index 2016–2025 (−1 very negative → +1 very positive)",
                   font=dict(color=C["text"], size=12)),
        yaxis=dict(range=[-1.1, 0.8], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        legend=dict(orientation="h", y=-0.15))
    return fig


def fig_stakeholder_sentiment():
    sources = [s[0] for s in STAKEHOLDER_SENT]
    scores  = [s[1] for s in STAKEHOLDER_SENT]
    colours = [C["pos"] if s > 0.2 else (C["neg"] if s < -0.4 else C["neu"])
               for s in scores]
    fig = go.Figure(go.Bar(
        x=scores, y=sources, orientation="h",
        marker_color=[_ha(c, 0.53) for c in colours],
        marker_line_color=colours, marker_line_width=1.5,
        text=[f"{s:+.2f}" for s in scores],
        textposition="outside",
        textfont=dict(color=C["muted"], size=10),
        hovertemplate="%{y}: %{x:+.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=C["muted2"], line_width=1)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Composite sentiment by stakeholder group", font=dict(color=C["text"], size=13)),
        xaxis=dict(range=[-1.1, 0.7], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)),
        margin=dict(l=160, r=60, t=40, b=20))
    return fig


def fig_workforce_approval_scatter():
    W = WORKFORCE_APPROVAL
    fig = go.Figure()
    x = np.array(W["wf_k"])
    y = np.array(W["parl"])
    slope, intercept, r, p_val, _ = stats.linregress(x, y)
    x_fit = np.linspace(18, 38, 100)
    y_fit = np.clip(slope * x_fit + intercept, -1.0, 0.2)
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit,
        mode="lines", name=f"Trend (r={r:.2f})",
        line=dict(color=_ha(C["muted"], 0.6), width=1.5, dash="dot"),
        hoverinfo="skip"))
    cpkms    = [c / n for c, n in zip(W["cost_bn"], W["network_km"])]
    max_cpkm = max(cpkms)
    for i, (wf, ps, ms, cost, km, per, cpkm) in enumerate(zip(
            W["wf_k"], W["parl"], W["media"], W["cost_bn"],
            W["network_km"], W["periods"], cpkms)):
        intensity = cpkm / max_cpkm
        col = C["neg"] if intensity > 0.6 else (C["neu"] if intensity > 0.3 else C["pos"])
        period_label = per.replace("\n", " ")
        fig.add_trace(go.Scatter(
            x=[wf], y=[ps], mode="markers+text",
            marker=dict(size=14, color=col, line=dict(color=C["bg"], width=2)),
            text=[period_label],
            textposition="top center",
            textfont=dict(color=C["muted"], size=9),
            name=period_label,
            showlegend=False,
            hovertemplate=(
                f"<b>{period_label}</b><br>"
                f"Workforce: {wf}k<br>"
                f"Parl sentiment: {ps:.2f}<br>"
                f"Cost: £{cost:.0f}bn<br>"
                f"Cost/km: £{cpkm:.3f}bn/km<extra></extra>"
            )))
        fig.add_annotation(
            x=wf, y=ps - 0.07,
            text=f"£{cpkm:.2f}/km",
            font=dict(color=col, size=8, family="DM Mono, monospace"),
            showarrow=False)
    fig.add_hline(y=-0.40,
        line=dict(color=C["neu"], width=1.5, dash="dash"),
        annotation_text="Viability threshold",
        annotation_font_color=C["neu"], annotation_font_size=10)
    fig.add_annotation(
        x=27, y=-0.65,
        text="Jobs grow from 22k→33k<br>but approval worsens<br>as cost/km tripled",
        font=dict(color=C["muted2"], size=10), showarrow=True,
        arrowhead=2, arrowcolor=C["muted2"], arrowwidth=1,
        ax=50, ay=-30, bgcolor=_ha(C["bg3"], 0.85), borderpad=4)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Workforce size vs parliamentary sentiment — colour = cost/km intensity",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Total workforce (thousands)", gridcolor=C["grid"],
                   zeroline=False, ticksuffix="k",
                   tickfont=dict(color=C["muted2"], size=10), range=[18, 40]),
        yaxis=dict(title="Sentiment index", gridcolor=C["grid"],
                   zeroline=False, range=[-1.0, 0.1],
                   tickfont=dict(color=C["muted2"], size=10)),
        margin=dict(l=60, r=20, t=50, b=60),
        showlegend=False)
    return fig


def fig_jobs_per_bn():
    W      = WORKFORCE_APPROVAL
    jpb    = [w * 1000 / c for w, c in zip(W["wf_k"], W["cost_bn"])]
    labels = [p.replace("\n", " ") for p in W["periods"]]
    colours = [C["pos"] if j > 400 else (C["neu"] if j > 300 else C["neg"]) for j in jpb]
    fig = go.Figure(go.Bar(
        x=labels, y=jpb,
        marker=dict(color=[_ha(c, 0.65) for c in colours],
                    line=dict(color=colours, width=1.5)),
        text=[f"{j:.0f}" for j in jpb],
        textposition="outside",
        textfont=dict(color=C["muted"], size=11, family="DM Mono, monospace"),
        hovertemplate="%{x}<br>%{y:.0f} jobs per £bn<extra></extra>",
    ))
    fig.add_hline(y=300,
        line=dict(color=C["neu"], width=1.5, dash="dash"),
        annotation_text="300 jobs/£bn — viability floor (model)",
        annotation_font_color=C["neu"], annotation_font_size=9)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Jobs-per-£bn: how efficient is HS2 at creating employment?",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        yaxis=dict(title="Jobs per £bn spent", gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10), range=[0, 650]),
        margin=dict(l=50, r=20, t=50, b=60))
    return fig


def fig_workforce_viability_envelope():
    wf_range   = np.linspace(10, 50, 80)
    cost_range = np.linspace(30, 120, 80)
    WF_g, C_g  = np.meshgrid(wf_range, cost_range)
    S_g        = np.vectorize(lambda w, c: _combined_approval(w, c, 400))(WF_g, C_g)

    fig = go.Figure()
    fig.add_trace(go.Contour(
        z=S_g, x=wf_range, y=cost_range,
        colorscale=[
            [0.0, "#7c2020"], [0.35, "#c04040"], [0.5, "#d47a10"],
            [0.7, "#639922"], [1.0, "#2d5a1e"],
        ],
        zmin=-1.0, zmax=0.2,
        contours=dict(start=-1.0, end=0.2, size=0.15, showlabels=True,
                      labelfont=dict(size=9, color="rgba(255,255,255,0.8)")),
        colorbar=dict(
            title=dict(text="Approval", font=dict(color=C["muted"], size=10)),
            tickfont=dict(color=C["muted"], size=9), thickness=12, len=0.8),
        hovertemplate=("Workforce: %{x:.0f}k<br>"
                       "Cost: £%{y:.0f}bn<br>"
                       "Approval: %{z:.2f}<extra></extra>"),
    ))
    bdy_wf, bdy_cost = [], []
    for wf in wf_range:
        for cost_test in np.linspace(30, 120, 500):
            if abs(_combined_approval(wf, cost_test, 400) - (-0.40)) < 0.01:
                bdy_wf.append(wf)
                bdy_cost.append(cost_test)
                break
    if bdy_wf:
        fig.add_trace(go.Scatter(
            x=bdy_wf, y=bdy_cost, mode="lines",
            name="Viability boundary (−0.40)",
            line=dict(color="white", width=2.5, dash="dash"),
            hovertemplate="Boundary: %{x:.0f}k workers / £%{y:.0f}bn<extra></extra>"))
    W = WORKFORCE_APPROVAL
    fig.add_trace(go.Scatter(
        x=W["wf_k"], y=W["cost_bn"],
        mode="lines+markers+text",
        name="HS2 trajectory",
        line=dict(color="white", width=1.5),
        marker=dict(size=10, color="white", symbol="circle",
                    line=dict(color=C["bg2"], width=2)),
        text=[p.split("\n")[0] for p in W["periods"]],
        textposition=["middle left", "top center", "top center", "top right"],
        textfont=dict(color="white", size=9),
        hovertemplate="%{text}: %{x:.0f}k workers, £%{y:.0f}bn<extra></extra>"))
    fig.add_annotation(x=40, y=45, text="Optimal zone\n(high jobs, low cost)",
        font=dict(color="rgba(255,255,255,0.85)", size=10), showarrow=False,
        bgcolor="rgba(0,0,0,0.4)", borderpad=4)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Jobs × cost approval envelope — where is the 'sweet spot'?",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Total workforce (thousands)", ticksuffix="k",
                   gridcolor="rgba(255,255,255,0.08)", zeroline=False,
                   tickfont=dict(color="rgba(255,255,255,0.5)", size=10)),
        yaxis=dict(title="Total cost (£bn)", tickprefix="£", ticksuffix="bn",
                   gridcolor="rgba(255,255,255,0.08)", zeroline=False,
                   tickfont=dict(color="rgba(255,255,255,0.5)", size=10)),
        margin=dict(l=60, r=80, t=50, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", font=dict(color="white", size=9)))
    return fig


def fig_jobs_approval_forecast():
    wf_range       = np.linspace(10, 55, 200)
    cost_scenarios = [
        (50,  C["pos"], "£50bn (cost reduced)"),
        (76,  C["acc"], "£76bn (viable threshold)"),
        (95,  C["neu"], "£95bn (current estimate)"),
        (110, C["neg"], "£110bn (escalation)"),
    ]
    fig = go.Figure()
    for cost, col, name in cost_scenarios:
        approvals = [_combined_approval(w, cost, 400) for w in wf_range]
        fig.add_trace(go.Scatter(
            x=wf_range, y=approvals, name=name,
            line=dict(color=col, width=2),
            hovertemplate=f"{name}<br>Workforce: %{{x:.0f}}k<br>Approval: %{{y:.2f}}<extra></extra>"))
        arr      = np.array(approvals)
        crossings = np.where(np.diff(np.sign(arr - (-0.40))))[0]
        for cx_i in crossings[:1]:
            cx = wf_range[cx_i]
            fig.add_trace(go.Scatter(
                x=[cx], y=[-0.40], mode="markers",
                marker=dict(size=9, color=col, symbol="diamond",
                            line=dict(color=C["bg"], width=1.5)),
                showlegend=False,
                hovertemplate=f"{name}: crosses threshold at {cx:.0f}k workers<extra></extra>"))
    fig.add_hline(y=-0.40,
        line=dict(color=C["neu"], width=1.5, dash="dash"),
        annotation_text="Viability threshold (−0.40)",
        annotation_font_color=C["neu"], annotation_font_size=10)
    fig.add_vline(x=33,
        line=dict(color=C["muted2"], width=1, dash="dot"),
        annotation_text="Current: 33k",
        annotation_font_color=C["muted2"], annotation_font_size=9)
    fig.add_annotation(
        x=45, y=-0.55,
        text="Beyond ~35k workers, job creation\nno longer shifts sentiment —\ncost/worker efficiency matters more",
        font=dict(color=C["muted2"], size=9), showarrow=False,
        bgcolor=_ha(C["bg3"], 0.9), borderpad=4)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Jobs forecast: approval as workforce grows — for each cost scenario",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Total workforce (thousands)", ticksuffix="k",
                   gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10), range=[10, 55]),
        yaxis=dict(title="Predicted approval", gridcolor=C["grid"],
                   zeroline=False, range=[-1.05, 0.25],
                   tickfont=dict(color=C["muted2"], size=10)),
        margin=dict(l=50, r=20, t=50, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.2))
    return fig
