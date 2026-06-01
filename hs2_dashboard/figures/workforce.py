import plotly.graph_objects as go
from ..config import C, LAYOUT_NO_AXES, _ha
from ..data import WORKFORCE_DF


def fig_workforce() -> go.Figure:
    """Total workforce (HS2 Ltd + supply chain combined) — verified data points only."""
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
