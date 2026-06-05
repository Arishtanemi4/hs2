import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config.theme import C, LAYOUT_BARE, _ha
from data.hs2_data import BENEFITS_DATA, SCOPE_DATA


def fig_benefits_journey_time():
    routes  = [d["route"]       for d in BENEFITS_DATA["journey_times"]]
    current = [d["current_min"] for d in BENEFITS_DATA["journey_times"]]
    hs2     = [d["hs2_min"]     for d in BENEFITS_DATA["journey_times"]]
    saved   = [c - h            for c, h in zip(current, hs2)]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=routes, x=hs2, name="HS2 journey time",
        orientation="h",
        marker=dict(color=_ha(C["pos"], 0.7), line=dict(color=C["pos"], width=1.5)),
        text=[f"{m}min" for m in hs2],
        textposition="inside", textfont=dict(color="white", size=11),
        hovertemplate="%{y}: HS2 = %{x}min<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=routes, x=saved, name="Time saved",
        orientation="h",
        marker=dict(color=_ha(C["acc"], 0.5), line=dict(color=C["acc"], width=1.5)),
        text=[f"−{s}min" for s in saved],
        textposition="inside", textfont=dict(color="white", size=11),
        hovertemplate="%{y}: saves %{x}min<extra></extra>",
    ))
    for i, (c, route) in enumerate(zip(current, routes)):
        fig.add_annotation(
            x=c + 3, y=i, text=f"Today: {c}min",
            font=dict(color=C["muted"], size=9, family="DM Mono, monospace"),
            showarrow=False, xanchor="left")
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Journey time savings — HS2 vs current fastest service",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Minutes", gridcolor=C["grid"], zeroline=False,
                   ticksuffix="min", tickfont=dict(color=C["muted2"], size=10), range=[0, 165]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=12)),
        barmode="stack",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.2),
        margin=dict(l=160, r=80, t=40, b=50),
        hovermode="y unified")
    return fig


def fig_capacity_comparison():
    cap        = BENEFITS_DATA["capacity"]
    categories = ["Euston seats/hr (current)", "Euston seats/hr (+HS2 Phase 1)"]
    values     = [cap["euston_peak_seats_before"], cap["euston_peak_seats_after"]]
    colours    = [_ha(C["neg"], 0.6), _ha(C["pos"], 0.7)]
    borders    = [C["neg"], C["pos"]]
    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker=dict(color=colours, line=dict(color=borders, width=1.5)),
        text=[f"{values[0]:,}", f"{values[1]:,}"],
        textposition="outside",
        textfont=dict(color=C["muted"], size=11, family="DM Mono, monospace"),
        hovertemplate="%{x}: %{y:,} seats/hr<extra></extra>",
    ))
    fig.add_annotation(
        x=0.5, y=(values[0]+values[1])//2,
        text="2.6x capacity increase",
        xref="paper",
        font=dict(color=C["acc"], size=12, family="Fraunces, serif"),
        showarrow=False,
        bgcolor=_ha(C["bg3"], 0.9), borderpad=5)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Euston peak-hour capacity — before and after HS2 Phase 1",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        yaxis=dict(range=[0, 38000], tickformat=",",
                   gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10),
                   title=dict(text="Peak seats per hour", font=dict(color=C["muted"], size=10))),
        margin=dict(l=60, r=30, t=50, b=20),
        showlegend=False)
    return fig


def fig_speed_comparison():
    sp    = BENEFITS_DATA["speed"]
    lines = ["West Coast Main Line (current)",
             "HS1 (London–Eurostar)",
             "TGV InOui (France)",
             "HS2 (320km/h, 2026)",
             "HS2 (360km/h, original)"]
    speeds = [sp["wcml_max_kmh"], sp["uk_existing_max_kmh"],
              sp["fastest_europe_kmh"], sp["current_design_kmh"],
              sp["original_design_kmh"]]
    cols  = [_ha(C["neg"], 0.5), _ha(C["neu"], 0.5), _ha(C["neu"], 0.6),
             _ha(C["acc"], 0.7), _ha(C["pos"], 0.7)]
    bords = [C["neg"], C["neu"], C["neu"], C["acc"], C["pos"]]
    fig = go.Figure(go.Bar(
        y=lines, x=speeds, orientation="h",
        marker=dict(color=cols, line=dict(color=bords, width=1.5)),
        text=[f"{s} km/h" for s in speeds],
        textposition="outside",
        textfont=dict(color=C["muted"], size=10, family="DM Mono, monospace"),
        hovertemplate="%{y}: %{x} km/h<extra></extra>",
    ))
    fig.add_vline(x=sp["current_design_kmh"],
        line=dict(color=C["acc"], width=1, dash="dot"),
        annotation_text="Current HS2 target",
        annotation_font_color=C["acc"], annotation_font_size=9)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Speed comparison: HS2 vs other rail services",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Max speed (km/h)", gridcolor=C["grid"], zeroline=False,
                   ticksuffix=" km/h", tickfont=dict(color=C["muted2"], size=10), range=[0, 420]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        margin=dict(l=200, r=80, t=40, b=40),
        showlegend=False)
    return fig


def fig_scope_evolution():
    years = [str(d["year"]) for d in SCOPE_DATA]
    metrics = {
        "Route (km)":       [d["route_km"]       for d in SCOPE_DATA],
        "Stations":         [d["stations"]        for d in SCOPE_DATA],
        "Cities served":    [d["cities_served"]   for d in SCOPE_DATA],
        "Max speed (km/h)": [d["max_speed_kmh"]   for d in SCOPE_DATA],
    }
    label_years = [d["label"].replace(" -- ", "<br>") for d in SCOPE_DATA]
    cols_by_year = [C["pos"] if d["colour"] == "pos" else (C["neu"] if d["colour"] == "neu" else C["neg"])
                    for d in SCOPE_DATA]
    fig = make_subplots(rows=1, cols=4, shared_yaxes=False,
        subplot_titles=["Route length (km)", "Stations", "Cities served", "Max speed (km/h)"],
        horizontal_spacing=0.08)
    metric_keys = ["Route (km)", "Stations", "Cities served", "Max speed (km/h)"]
    for col_i, key in enumerate(metric_keys, 1):
        vals      = metrics[key]
        bar_cols  = [_ha(c, 0.7) for c in cols_by_year]
        border_cols = cols_by_year
        fig.add_trace(go.Bar(
            x=label_years, y=vals,
            marker=dict(color=bar_cols, line=dict(color=border_cols, width=1.5)),
            text=[str(v) for v in vals],
            textposition="outside",
            textfont=dict(color=C["muted"], size=10),
            showlegend=False,
            hovertemplate=f"{key}: %{{y}}<br>%{{x}}<extra></extra>",
        ), row=1, col=col_i)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=10),
        margin=dict(l=10, r=10, t=50, b=20),
        showlegend=False)
    for i in range(1, 5):
        fig.update_xaxes(gridcolor="rgba(0,0,0,0)",
                         tickfont=dict(color=C["text"], size=9), row=1, col=i)
        fig.update_yaxes(gridcolor=C["grid"], zeroline=False,
                         tickfont=dict(color=C["muted2"], size=9), row=1, col=i)
    for ann in fig.layout.annotations:
        ann.update(font=dict(color=C["muted"], size=11))
    return fig


def fig_infrastructure_density():
    years          = [d["year"]     for d in SCOPE_DATA]
    route          = [d["route_km"] for d in SCOPE_DATA]
    tunnels_per_km = [d["tunnels_km"] / d["route_km"] * 100 for d in SCOPE_DATA]
    bridges_per_km = [d["bridges"]   / d["route_km"]       for d in SCOPE_DATA]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=years, y=tunnels_per_km, name="Tunnel % of route",
        mode="lines+markers",
        line=dict(color=C["acc"], width=2),
        marker=dict(size=8, color=C["acc"], line=dict(color=C["bg"], width=1.5)),
        hovertemplate="Tunnels: %{y:.1f}% of route<extra></extra>"),
        secondary_y=False)
    fig.add_trace(go.Scatter(
        x=years, y=bridges_per_km, name="Bridges per km",
        mode="lines+markers",
        line=dict(color=C["neu"], width=2, dash="dot"),
        marker=dict(size=8, color=C["neu"], symbol="square",
                    line=dict(color=C["bg"], width=1.5)),
        hovertemplate="Bridges: %{y:.2f} per km<extra></extra>"),
        secondary_y=True)
    fig.add_vline(x=2023, line=dict(color=C["muted2"], width=1, dash="dot"),
        annotation_text="Phase 2 cancelled", annotation_font_color=C["muted2"],
        annotation_font_size=9)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=10),
        title=dict(text="Infrastructure density rising as route shrinks",
                   font=dict(color=C["text"], size=12)),
        margin=dict(l=50, r=60, t=50, b=30),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.15),
        xaxis=dict(gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10),
                   tickvals=years, ticktext=[str(y) for y in years]),
        hovermode="x unified")
    fig.update_yaxes(title_text="Tunnel % of route", gridcolor=C["grid"],
                     zeroline=False, ticksuffix="%",
                     tickfont=dict(color=C["muted2"], size=10), secondary_y=False)
    fig.update_yaxes(title_text="Bridges per km", gridcolor="rgba(0,0,0,0)",
                     zeroline=False, tickfont=dict(color=C["muted2"], size=10),
                     secondary_y=True)
    return fig
