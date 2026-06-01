import plotly.graph_objects as go
from ..config import C, PLOTLY_LAYOUT, LAYOUT_NO_AXES, _ha


def fig_risk_radar() -> go.Figure:
    categories  = ["Inflation", "Political", "Workforce", "Contractor<br>failure",
                   "Scope<br>change", "Euston<br>risk", "Skill<br>shortage"]
    probability = [65, 70, 55, 45, 40, 60, 72]
    impact      = [85, 90, 60, 80, 75, 70, 65]
    fig = go.Figure()
    for data, name, col in [(probability, "Probability", C["neg"]),
                             (impact,      "Impact",      C["neu"])]:
        fig.add_trace(go.Scatterpolar(
            r=data + [data[0]], theta=categories + [categories[0]],
            name=name, fill="toself",
            fillcolor=_ha(col, 0.13), line=dict(color=col, width=2),
            hovertemplate="%{theta}: %{r}<extra>" + name + "</extra>"))
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Risk probability vs impact radar", font=dict(color=C["text"], size=13)),
        polar=dict(
            bgcolor=C["bg3"],
            radialaxis=dict(range=[0, 100], gridcolor=C["border2"],
                            tickfont=dict(color=C["muted2"], size=9)),
            angularaxis=dict(gridcolor=C["border"], tickfont=dict(color=C["muted"], size=10))),
        legend=dict(orientation="h", y=-0.1))
    return fig


def fig_confidence() -> go.Figure:
    metrics = ["Cost band", "Schedule", "Sentiment\nlead", "Workforce\nsignal", "Narrative\ncluster"]
    scores  = [72, 58, 45, 41, 68]
    colours = [C["pos"] if s > 60 else (C["neu"] if s > 50 else C["neg"]) for s in scores]
    fig = go.Figure(go.Bar(
        x=metrics, y=scores,
        marker_color=[_ha(c, 0.67) for c in colours],
        marker_line_color=colours, marker_line_width=1.5,
        text=[f"{s}%" for s in scores], textposition="outside",
        textfont=dict(color=C["muted"], size=10),
    ))
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Model confidence calibration by output type", font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[0, 100], ticksuffix="%", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)))
    return fig
