import plotly.graph_objects as go
from ..config import C, PLOTLY_LAYOUT, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from ..data import PARAMS


def fig_cluster_donut(pos: float = 18, neu: float = 45, neg: float = 37) -> go.Figure:
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


def fig_fan_chart(fan: dict) -> go.Figure:
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


def fig_cost_histogram(costs) -> go.Figure:
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


def fig_sensitivity(params: list) -> go.Figure:
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
