import plotly.graph_objects as go
from ..config import C, LAYOUT_NO_AXES, _ha
from ..data import SCHEDULE_DF


def fig_schedule() -> go.Figure:
    """Schedule slippage — verified figures from HoC Library CBP-9313 and AR 2024-25."""
    col_map = {"pos": C["pos"], "neu": C["neu"], "neg": C["neg"]}
    fig = go.Figure()
    for _, row in SCHEDULE_DF.iterrows():
        col = col_map[row["colour"]]
        fig.add_trace(go.Bar(
            x=[row["revision"]],
            y=[row["open_high"] - row["open_low"]],
            base=[row["open_low"]],
            marker_color=_ha(col, 0.53),
            marker_line_color=col, marker_line_width=1.5,
            text=[row["open_label"]],
            textposition="outside",
            textfont=dict(color=C["muted"], size=9),
            showlegend=False,
            hovertemplate=f"{row['revision']}: {row['open_label']}<extra></extra>",
        ))
    fig.add_annotation(
        x=4, y=2027, text="No confirmed date as of May 2026",
        font=dict(color=C["neg"], size=9), showarrow=False)
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Opening year forecast — each major revision (verified)", font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[2024, 2044], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10),
                   title=dict(text="Projected opening year", font=dict(color=C["muted"], size=10))),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["muted2"], size=9)),
        showlegend=False, barmode="stack")
    return fig
