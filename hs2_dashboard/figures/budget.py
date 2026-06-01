import plotly.graph_objects as go
from ..config import C, _ha
from ..data import SPEND_DF


def fig_spend() -> go.Figure:
    """Annual spend vs budget — only years confirmed from primary AR documents."""
    df = SPEND_DF
    budget_vals = df["budget_bn"].tolist()
    actual_vals = df["actual_bn"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["year"], y=budget_vals, name="Budget",
        marker_color=_ha(C["acc"], 0.33), marker_line_color=C["acc"], marker_line_width=1.5,
        text=[f"£{v:.1f}bn" if v else "—" for v in budget_vals],
        textposition="outside", textfont=dict(color=C["muted"], size=10),
    ))
    fig.add_trace(go.Bar(
        x=df["year"], y=actual_vals, name="Actual / planned",
        marker_color=_ha(C["neu"], 0.33), marker_line_color=C["neu"], marker_line_width=1.5,
        text=[f"£{v:.1f}bn" if v else "—" for v in actual_vals],
        textposition="outside", textfont=dict(color=C["muted"], size=10),
    ))
    fig.add_annotation(x=0.5, y=-0.2, xref="paper", yref="paper", xanchor="center",
        text="Sources: AR 2023-24 (HC 106); AR 2024-25 (HC 1088). Earlier years not confirmed.",
        font=dict(color=C["muted2"], size=9), showarrow=False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=11),
        title=dict(text="Annual budget vs actual spend — verified years only (£bn)", font=dict(color=C["text"], size=13)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", zeroline=False, tickfont=dict(color=C["text"], size=10)),
        yaxis=dict(range=[0, 9.5], tickprefix="£", ticksuffix="bn", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        barmode="group",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10), orientation="h", y=-0.15),
        margin=dict(l=10, r=10, t=40, b=60),
        hovermode="x unified")
    return fig
