import plotly.graph_objects as go
from ..config import C, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from ..data import SENTIMENT_DF, STAKEHOLDER_SENT


def fig_sentiment_timeline() -> go.Figure:
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


def fig_stakeholder_sentiment() -> go.Figure:
    sources = [s[0] for s in STAKEHOLDER_SENT]
    scores  = [s[1] for s in STAKEHOLDER_SENT]
    colours = [C["pos"] if s > 0.2 else (C["neg"] if s < -0.4 else C["neu"]) for s in scores]
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
