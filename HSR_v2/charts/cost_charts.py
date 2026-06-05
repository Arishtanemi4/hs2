import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config.theme import C, PLOTLY_LAYOUT, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from data.hs2_data import COST_DF, SCHEDULE_DF, SPEND_DF, VIABILITY_DATA
from models.viability import pred_sentiment


def fig_cost_history():
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


def fig_schedule():
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


def fig_waterfall():
    labels   = ["2012 Baseline","+Inflation","+ Design Δ","+ Scope adds",
                "+ Delay cost","2019 Est.",
                "− Phase 2\ncancel","+ Further\noverruns","2025 Reset",
                "− Speed saving","2026 Current"]
    values   = [32.7, 14, 9, 8, 12, 0, -2.7, 18, 0, -2.5, 0]
    measures = ["absolute","relative","relative","relative","relative","total",
                "relative","relative","total","relative","total"]
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


def fig_spend():
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


def fig_cost_drivers():
    labels  = ["Construction inflation","Design changes","Programme delay",
               "Governance / contractor","Tunnel complexity"]
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


def fig_cost_evolution_dual():
    V = VIABILITY_DATA
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=V["years"]+V["years"][::-1],
        y=V["cost_high"]+V["cost_low"][::-1],
        fill="toself", fillcolor=_ha(C["neg"], 0.12),
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=V["years"], y=V["cost_mid"],
        name="Cost estimate (midpoint)",
        line=dict(color=C["neg"], width=2.5),
        mode="lines+markers",
        marker=dict(size=8, color=C["neg"], line=dict(color=C["bg"], width=1.5)),
        hovertemplate="£%{y:.0f}bn<extra>Cost</extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=V["years"], y=V["network_km"],
        name="Network in scope (km)",
        line=dict(color=C["pos"], width=2, dash="dot"),
        mode="lines+markers",
        marker=dict(size=8, color=C["pos"], symbol="square",
                    line=dict(color=C["bg"], width=1.5)),
        hovertemplate="%{y}km<extra>Network</extra>"), secondary_y=True)
    fig.add_vline(x=2023, line=dict(color=C["muted2"], width=1, dash="dot"),
        annotation_text="Phase 2 cancelled", annotation_font_color=C["muted2"],
        annotation_font_size=9)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Cost rises as network shrinks — the cost-per-km crisis",
                   font=dict(color=C["text"], size=12)),
        margin=dict(l=60, r=60, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.15))
    fig.update_yaxes(title_text="Total cost (£bn)", tickprefix="£", ticksuffix="bn",
                     gridcolor=C["grid"], zeroline=False,
                     tickfont=dict(color=C["muted2"], size=10), secondary_y=False)
    fig.update_yaxes(title_text="Network in scope (km)", ticksuffix="km",
                     gridcolor="rgba(0,0,0,0)", zeroline=False,
                     tickfont=dict(color=C["muted2"], size=10), secondary_y=True)
    fig.update_xaxes(gridcolor=C["grid"], tickfont=dict(color=C["muted2"], size=10))
    return fig
