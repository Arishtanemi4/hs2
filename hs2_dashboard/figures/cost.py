import plotly.graph_objects as go
from ..config import C, PLOTLY_LAYOUT, _ha
from ..data import COST_DF


def fig_cost_history() -> go.Figure:
    """Cost revision chart — verified primary source figures only.
    Pre-2024 = full network (Phases 1+2a+2b). Post-2024 = Phase 1 only."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=COST_DF["year"], y=COST_DF["baseline"],
        name="2012 baseline (£32.7bn)", line=dict(color=C["pos"], width=1.5, dash="dash"),
        hovertemplate="Baseline: £%{y:.1f}bn<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=COST_DF["year"], y=COST_DF["low"],
        name="Low estimate", line=dict(color=C["neu"], width=1.5, dash="dot"),
        hovertemplate="Low: £%{y:.1f}bn<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=COST_DF["year"], y=COST_DF["high"],
        name="High estimate", line=dict(color=C["neg"], width=2.5),
        fill="tonexty", fillcolor="rgba(248,113,113,0.08)",
        hovertemplate="High: £%{y:.1f}bn<extra></extra>"))
    fig.add_vline(x=2023.75, line_dash="dot", line_color=C["muted2"],
                  annotation_text="Phase 2 cancelled", annotation_font_color=C["muted2"],
                  annotation_font_size=9)
    fig.add_annotation(x=2024, y=22, text="* Post-2023 = Phase 1 only",
                       font=dict(color=C["muted2"], size=9), showarrow=False, xanchor="left")
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost estimate revision history — verified figures only (£bn)", font=dict(color=C["text"], size=13)),
        yaxis_tickprefix="£", yaxis_ticksuffix="bn",
        legend=dict(orientation="h", y=-0.15))
    return fig


def fig_waterfall() -> go.Figure:
    labels   = ["2012 Baseline", "+Inflation", "+ Design Δ", "+ Scope adds",
                 "+ Delay cost", "2019 Est.",
                 "− Phase 2\ncancel", "+ Further\noverruns", "2025 Reset",
                 "− Speed saving", "2026 Current"]
    values   = [32.7, 14, 9, 8, 12, 0, -2.7, 18, 0, -2.5, 0]
    measures = ["absolute", "relative", "relative", "relative", "relative", "total",
                "relative", "relative", "total", "relative", "total"]
    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        connector=dict(line=dict(color=C["border2"], width=1)),
        increasing=dict(marker_color="rgba(248,113,113,0.7)"),
        decreasing=dict(marker_color="rgba(74,222,128,0.7)"),
        totals=dict(marker_color=_ha(C["neu"], 0.67)),
        hovertemplate="£%{y:.1f}bn<extra></extra>",
        textfont=dict(color=C["text"], size=10),
    ))
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost overrun waterfall: 2012 → 2026 (£bn)", font=dict(color=C["text"], size=13)),
        yaxis_tickprefix="£", yaxis_ticksuffix="bn")
    return fig


def fig_cost_drivers() -> go.Figure:
    labels  = ["Construction inflation", "Design changes", "Programme delay",
               "Governance / contractor", "Tunnel complexity"]
    values  = [24, 18, 14, 10, 4]
    colours = [C["neg"], C["neu"], C["acc"], C["pu"], C["pos"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=[_ha(c, 0.67) for c in colours],
                    line=dict(color=colours, width=1.5)),
        textfont=dict(color=C["text"], size=10),
        hovertemplate="%{label}: £%{value}bn (%{percent})<extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost overrun attribution (£bn)", font=dict(color=C["text"], size=13)),
        showlegend=True,
        legend=dict(font=dict(color=C["muted"], size=10), x=1.0))
    return fig
