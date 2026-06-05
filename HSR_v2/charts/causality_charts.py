import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.theme import C, PLOTLY_LAYOUT, LAYOUT_NO_AXES, LAYOUT_BARE, _ha
from data.causality_data import (
    PARLIAMENTARY_EVENTS, NEWS_EVENTS, ALL_EVENTS_SORTED,
    MONTHLY_SENTIMENT, LAG_CORRELATIONS,
)

_PARL_COL = C["acc"]
_NEWS_COL = C["pu"]
_BOTH_COL = C["neu"]


# ── helpers ───────────────────────────────────────────────────────────────────

def _event_marker_colour(category, impact):
    if impact >= 0:
        return C["pos"]
    if category == "Parliamentary":
        return _PARL_COL
    return _NEWS_COL


# ── 1. SENTIMENT TIMELINE WITH EVENT MARKERS ──────────────────────────────────

def fig_event_timeline():
    xs     = [r[0] for r in MONTHLY_SENTIMENT]
    y_parl = [r[1] for r in MONTHLY_SENTIMENT]
    y_med  = [r[2] for r in MONTHLY_SENTIMENT]
    y_comb = [r[3] for r in MONTHLY_SENTIMENT]

    fig = go.Figure()

    # Sentiment bands
    fig.add_trace(go.Scatter(
        x=xs + xs[::-1],
        y=y_parl + y_med[::-1],
        fill="toself", fillcolor=_ha(C["muted"], 0.07),
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
        name="Parl-Media band"))

    # Parliamentary sentiment line
    fig.add_trace(go.Scatter(
        x=xs, y=y_parl, name="Parliamentary",
        line=dict(color=_PARL_COL, width=2),
        hovertemplate="Parl: %{y:.2f}<extra></extra>"))

    # Media sentiment line
    fig.add_trace(go.Scatter(
        x=xs, y=y_med, name="Media",
        line=dict(color=_NEWS_COL, width=2, dash="dot"),
        hovertemplate="Media: %{y:.2f}<extra></extra>"))

    # Viability threshold
    fig.add_hline(y=-0.40,
        line=dict(color=C["neg"], width=1, dash="dash"),
        annotation_text="Viability threshold (−0.40)",
        annotation_font_color=C["neg"], annotation_font_size=9)

    # Parliamentary event markers
    for ev in PARLIAMENTARY_EVENTS:
        col = C["pos"] if ev["impact"] >= 0 else _PARL_COL
        fig.add_trace(go.Scatter(
            x=[ev["year_frac"]], y=[ev["sentiment_after"]],
            mode="markers",
            marker=dict(size=12, color=col, symbol="diamond",
                        line=dict(color=C["bg"], width=1.5)),
            name=ev["label"],
            showlegend=False,
            hovertemplate=(
                f"<b>{ev['label']}</b><br>"
                f"Body: {ev['body']}<br>"
                f"Impact: {ev['impact']:+.2f}<br>"
                f"{ev['description'][:80]}...<extra>Parliamentary</extra>"
            )))
        # Vertical drop line
        fig.add_shape(type="line",
            x0=ev["year_frac"], x1=ev["year_frac"],
            y0=ev["sentiment_before"], y1=ev["sentiment_after"],
            line=dict(color=col, width=1.5, dash="dot"))

    # News event markers
    for ev in NEWS_EVENTS:
        col = C["pos"] if ev["impact"] >= 0 else _NEWS_COL
        fig.add_trace(go.Scatter(
            x=[ev["year_frac"]], y=[ev["sentiment_after"]],
            mode="markers",
            marker=dict(size=10, color=col, symbol="circle",
                        line=dict(color=C["bg"], width=1.5)),
            name=ev["label"],
            showlegend=False,
            hovertemplate=(
                f"<b>{ev['label']}</b><br>"
                f"Channel: {ev['channel']}<br>"
                f"Impact: {ev['impact']:+.2f}<br>"
                f"{ev['description'][:80]}...<extra>News / Media</extra>"
            )))

    # Phase 2 cancellation region
    fig.add_vrect(x0=2023.65, x1=2023.95,
        fillcolor=_ha(C["neg"], 0.07),
        line=dict(color=C["neg"], width=1, dash="dot"),
        annotation_text="Phase 2\ncancelled",
        annotation_position="top left",
        annotation_font_color=C["neg"], annotation_font_size=9)

    # Legend annotations for symbols
    fig.add_annotation(x=2025.8, y=-0.55, text="◆ Parliamentary event",
        font=dict(color=_PARL_COL, size=10), showarrow=False)
    fig.add_annotation(x=2025.8, y=-0.60, text="● News / media event",
        font=dict(color=_NEWS_COL, size=10), showarrow=False)
    fig.add_annotation(x=2025.8, y=-0.65, text="Green = positive impact",
        font=dict(color=C["pos"], size=10), showarrow=False)

    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(
            text="Sentiment timeline with event causality markers — 2016–2026",
            font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[-1.0, 0.15], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10),
                   title=dict(text="Sentiment index (proxy)", font=dict(color=C["muted"], size=10))),
        xaxis=dict(gridcolor=C["grid"], tickfont=dict(color=C["muted2"], size=10),
                   tickvals=list(range(2016, 2027))),
        legend=dict(orientation="h", y=-0.18, bgcolor="rgba(0,0,0,0)",
                    font=dict(color=C["muted"], size=10)))
    fig.update_layout(hovermode="closest", margin=dict(l=55, r=20, t=50, b=60))
    return fig


# ── 2. BEFORE/AFTER IMPACT LOLLIPOP ──────────────────────────────────────────

def fig_impact_lollipop():
    all_evs = sorted(
        [(ev["year_frac"], ev["label"], ev["impact"], ev["sentiment_before"],
          ev["sentiment_after"], "Parliamentary", ev["verified"])
         for ev in PARLIAMENTARY_EVENTS]
        + [(ev["year_frac"], ev["label"], ev["impact"], ev["sentiment_before"],
            ev["sentiment_after"], "News / Media", ev["verified"])
           for ev in NEWS_EVENTS],
        key=lambda x: x[2]   # sort by impact (most negative first)
    )

    labels   = [f"[{x[5][:1]}] {x[1]}" for x in all_evs]
    impacts  = [x[2] for x in all_evs]
    cats     = [x[5] for x in all_evs]
    verified = [x[6] for x in all_evs]
    colours  = [(_PARL_COL if c == "Parliamentary" else _NEWS_COL)
                if i < 0 else C["pos"]
                for i, c in zip(impacts, cats)]
    opacities = [1.0 if v else 0.5 for v in verified]

    fig = go.Figure()

    # Stem lines
    for i, (lbl, imp, col, op) in enumerate(zip(labels, impacts, colours, opacities)):
        fig.add_shape(type="line",
            x0=0, x1=imp, y0=i, y1=i,
            line=dict(color=col, width=1.5, dash="dot" if imp >= 0 else "solid"))

    # Dots
    fig.add_trace(go.Scatter(
        x=impacts, y=list(range(len(labels))),
        mode="markers",
        marker=dict(
            size=10,
            color=colours,
            opacity=opacities,
            line=dict(color=C["bg"], width=1.5)),
        text=[f"{imp:+.3f}" for imp in impacts],
        hovertemplate="%{y}: %{x:+.3f} sentiment shift<extra></extra>",
        showlegend=False))

    # Impact value labels
    for i, (imp, col) in enumerate(zip(impacts, colours)):
        fig.add_annotation(
            x=imp + (0.005 if imp >= 0 else -0.005),
            y=i, text=f"{imp:+.3f}",
            font=dict(color=col, size=9, family="DM Mono, monospace"),
            showarrow=False,
            xanchor="left" if imp >= 0 else "right")

    # Zero line
    fig.add_vline(x=0, line_color=C["muted2"], line_width=1)

    # Category legend
    fig.add_annotation(x=-0.38, y=len(labels)-0.5,
        text="[P] = Parliamentary  [N] = News/Media  opacity = verified",
        font=dict(color=C["muted2"], size=9), showarrow=False, xanchor="left")

    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Estimated sentiment impact per event — negative = worsened public perception",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Sentiment shift (proxy)", gridcolor=C["grid"], zeroline=False,
                   tickfont=dict(color=C["muted2"], size=10), range=[-0.45, 0.15]),
        yaxis=dict(tickvals=list(range(len(labels))), ticktext=labels,
                   gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(color=C["text"], size=9)),
        margin=dict(l=310, r=60, t=40, b=40),
        height=max(400, len(labels) * 28))
    return fig


# ── 3. EVENT CATEGORY COMPARISON ─────────────────────────────────────────────

def fig_event_type_comparison():
    parl_impacts = [abs(e["impact"]) for e in PARLIAMENTARY_EVENTS if e["impact"] < 0]
    news_impacts = [abs(e["impact"]) for e in NEWS_EVENTS        if e["impact"] < 0]
    parl_pos     = [e["impact"] for e in PARLIAMENTARY_EVENTS if e["impact"] > 0]
    news_pos     = [e["impact"] for e in NEWS_EVENTS        if e["impact"] > 0]

    categories = ["Parliamentary\n(negative)", "News / Media\n(negative)",
                  "Parliamentary\n(positive)", "News / Media\n(positive)"]
    means  = [np.mean(parl_impacts), np.mean(news_impacts),
              np.mean(parl_pos) if parl_pos else 0,
              np.mean(news_pos) if news_pos else 0]
    maxes  = [max(parl_impacts),   max(news_impacts),
              max(parl_pos) if parl_pos else 0,
              max(news_pos) if news_pos else 0]
    counts = [len(parl_impacts), len(news_impacts),
              len(parl_pos), len(news_pos)]
    colours = [_PARL_COL, _NEWS_COL, C["pos"], C["pos"]]
    bar_opac = [0.7, 0.7, 0.5, 0.5]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories, y=means,
        name="Mean |impact|",
        marker=dict(color=[_ha(c, 0.55) for c in colours],
                    line=dict(color=colours, width=1.5)),
        text=[f"μ={m:.3f}<br>n={n}" for m, n in zip(means, counts)],
        textposition="outside",
        textfont=dict(color=C["muted"], size=10, family="DM Mono, monospace"),
        hovertemplate="%{x}<br>Mean: %{y:.3f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=categories, y=maxes,
        name="Max |impact|",
        mode="markers",
        marker=dict(size=10, color=colours, symbol="diamond",
                    line=dict(color=C["bg"], width=1.5)),
        hovertemplate="%{x}<br>Max: %{y:.3f}<extra></extra>",
    ))

    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Average vs peak sentiment impact by event category",
                   font=dict(color=C["text"], size=12)),
        yaxis=dict(range=[0, 0.35], gridcolor=C["grid"],
                   title=dict(text="Absolute sentiment change", font=dict(color=C["muted"], size=10)),
                   tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.2))
    fig.update_layout(margin=dict(l=50, r=20, t=50, b=60))
    return fig


# ── 4. LAG CORRELATION ANALYSIS ───────────────────────────────────────────────

def fig_lag_analysis():
    lags   = [d["lag_months"] for d in LAG_CORRELATIONS]
    rs     = [d["r"] for d in LAG_CORRELATIONS]
    labels = [d["label"] for d in LAG_CORRELATIONS]
    sigs   = [d["significant"] for d in LAG_CORRELATIONS]
    colours = [C["pos"] if r > 0 else C["neg"] for r in rs]
    opacities = [0.85 if s else 0.40 for s in sigs]

    fig = go.Figure()
    # Bars
    fig.add_trace(go.Bar(
        x=labels, y=rs,
        marker=dict(
            color=[_ha(c, 0.6) for c in colours],
            line=dict(color=colours, width=1.5),
            opacity=opacities),
        text=[f"r={r:.2f}{'*' if s else ''}" for r, s in zip(rs, sigs)],
        textposition="outside",
        textfont=dict(color=C["muted"], size=10, family="DM Mono, monospace"),
        hovertemplate="%{x}<br>Pearson r: %{y:.2f}<extra></extra>",
        showlegend=False,
    ))

    # Significance threshold line
    fig.add_hline(y=0, line_color=C["muted2"], line_width=1)
    fig.add_hline(y=0.40, line=dict(color=C["pos"], width=1, dash="dot"),
        annotation_text="Moderate correlation", annotation_font_color=C["pos"],
        annotation_font_size=9)
    fig.add_hline(y=-0.40, line=dict(color=C["neg"], width=1, dash="dot"),
        annotation_font_size=9)

    # Key finding annotation
    fig.add_annotation(
        x=2, y=0.65,
        text="News leads parliament\nby ~1 month (r=0.54, p=0.03)",
        font=dict(color=C["acc"], size=10), showarrow=True,
        arrowhead=2, arrowcolor=C["acc"], arrowwidth=1,
        ax=60, ay=-30, bgcolor=_ha(C["bg3"], 0.9), borderpad=4)

    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Lag analysis: does news lead parliamentary scrutiny? (* = p<0.05)",
                   font=dict(color=C["text"], size=12)),
        yaxis=dict(range=[-0.45, 0.80], gridcolor=C["grid"],
                   title=dict(text="Pearson correlation (r)", font=dict(color=C["muted"], size=10)),
                   tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)))
    fig.update_layout(margin=dict(l=50, r=20, t=50, b=60))
    return fig


# ── 5. CUMULATIVE IMPACT WATERFALL ────────────────────────────────────────────

def fig_cumulative_impact():
    evs = ALL_EVENTS_SORTED
    labels   = ["Baseline\n(2016)"] + [e["label"][:28] + ("…" if len(e["label"]) > 28 else "")
                                       for e in evs] + ["Current\n(2026)"]
    impacts  = [0] + [e["impact"] for e in evs] + [0]
    measures = ["absolute"] + ["relative"] * len(evs) + ["total"]
    cats     = [""] + [e["category"] for e in evs] + [""]

    running = -0.23
    totals  = [running]
    for imp in impacts[1:-1]:
        running += imp
        totals.append(running)
    totals.append(running)

    # Colours per bar
    inc_col = _ha(C["neg"], 0.75)
    dec_col = _ha(C["pos"], 0.75)
    tot_col = _ha(C["neu"], 0.75)

    marker_colours = []
    for m, imp in zip(measures, impacts):
        if m == "absolute" or m == "total":
            marker_colours.append(tot_col)
        elif imp < 0:
            marker_colours.append(inc_col)
        else:
            marker_colours.append(dec_col)

    fig = go.Figure(go.Waterfall(
        x=labels, y=impacts, measure=measures,
        connector=dict(line=dict(color=C["border2"], width=1)),
        increasing=dict(marker_color=dec_col),
        decreasing=dict(marker_color=inc_col),
        totals=dict(marker_color=tot_col),
        hovertemplate="%{x}<br>Impact: %{y:+.3f}<extra></extra>",
        textfont=dict(color=C["text"], size=8),
    ))

    # Viability threshold
    fig.add_hline(y=-0.40,
        line=dict(color=C["neg"], width=1.5, dash="dash"),
        annotation_text="Viability threshold (−0.40)",
        annotation_font_color=C["neg"], annotation_font_size=9)

    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cumulative sentiment erosion — from 2016 baseline to 2026 (each event's contribution)",
                   font=dict(color=C["text"], size=12)))
    fig.update_layout(
        yaxis=dict(range=[-1.05, 0.15], tickfont=dict(color=C["muted2"], size=9),
                   gridcolor=C["grid"], zeroline=False),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["muted2"], size=8),
                   tickangle=-45),
        margin=dict(l=50, r=20, t=50, b=120))
    return fig


# ── 6. NEWS vs PARLIAMENT SCATTER ─────────────────────────────────────────────

def fig_news_vs_parl_scatter():
    """
    Scatter: news impact (x) vs parliamentary impact (y) for events that
    occurred in the same quarter. Shows whether news and parliament amplify
    each other or act independently.
    """
    # Bin events by quarter
    quarters = {}
    for ev in PARLIAMENTARY_EVENTS:
        q = round(ev["year_frac"] * 4) / 4
        quarters.setdefault(q, {"parl": [], "news": []})["parl"].append(ev["impact"])
    for ev in NEWS_EVENTS:
        q = round(ev["year_frac"] * 4) / 4
        quarters.setdefault(q, {"parl": [], "news": []})["news"].append(ev["impact"])

    xs, ys, sizes, labels_sc, years_sc = [], [], [], [], []
    for q, data in sorted(quarters.items()):
        if data["parl"] and data["news"]:
            x = np.mean(data["news"])
            y = np.mean(data["parl"])
            xs.append(x)
            ys.append(y)
            sizes.append(8 + abs(x + y) * 60)
            yr_str = f"{int(q)}-Q{int((q % 1)*4)+1}"
            labels_sc.append(yr_str)
            years_sc.append(q)

    if not xs:
        return go.Figure()

    # Linear fit
    coeffs = np.polyfit(xs, ys, 1)
    x_fit  = np.linspace(min(xs)-0.02, max(xs)+0.02, 100)
    y_fit  = np.polyval(coeffs, x_fit)
    r      = np.corrcoef(xs, ys)[0, 1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit, mode="lines",
        name=f"Linear fit (r={r:.2f})",
        line=dict(color=_ha(C["acc"], 0.6), width=1.5, dash="dot"),
        hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(size=sizes, color=[_ha(C["neg"], 0.6) if (x+y) < -0.1
                                       else _ha(C["neu"], 0.6) for x, y in zip(xs, ys)],
                    line=dict(color=C["bg"], width=1.5)),
        text=labels_sc, textposition="top center",
        textfont=dict(color=C["muted"], size=9),
        hovertemplate="%{text}<br>News impact: %{x:+.3f}<br>Parl impact: %{y:+.3f}<extra></extra>",
        name="Co-occurrence quarter", showlegend=False))

    fig.add_hline(y=0, line_color=C["muted2"], line_width=1)
    fig.add_vline(x=0, line_color=C["muted2"], line_width=1)

    # Quadrant labels
    for txt, xp, yp in [
        ("News negative\nParl negative", -0.15, -0.20),
        ("News positive\nParl negative", +0.04, -0.20),
        ("News negative\nParl positive", -0.15, +0.06),
    ]:
        fig.add_annotation(x=xp, y=yp, text=txt,
            font=dict(color=C["muted2"], size=9), showarrow=False)

    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Co-occurrence: when news and parliament act in the same quarter",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Average news event impact (quarter)", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(title="Average parliamentary event impact (quarter)", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10)),
        margin=dict(l=60, r=20, t=50, b=60))
    return fig


# ── 7. EVENT DENSITY HEATMAP ──────────────────────────────────────────────────

def fig_event_density_heatmap():
    """
    Heatmap: number of negative events per year × category,
    overlaid with the average sentiment that year.
    """
    years = list(range(2016, 2027))
    cats  = ["Parliamentary", "News / Media"]

    # Count negative events per year per category
    counts = {yr: {"Parliamentary": 0, "News / Media": 0} for yr in years}
    for ev in PARLIAMENTARY_EVENTS:
        if ev["impact"] < 0:
            yr = int(ev["year_frac"])
            if yr in counts:
                counts[yr]["Parliamentary"] += 1
    for ev in NEWS_EVENTS:
        if ev["impact"] < 0:
            yr = int(ev["year_frac"])
            if yr in counts:
                counts[yr]["News / Media"] += 1

    z = [[counts[yr][cat] for yr in years] for cat in cats]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[str(yr) for yr in years],
        y=cats,
        colorscale=[
            [0.0,  C["bg3"]],
            [0.25, _ha(_NEWS_COL, 0.4)],
            [0.5,  _ha(_NEWS_COL, 0.7)],
            [0.75, _ha(C["neg"], 0.7)],
            [1.0,  C["neg"]],
        ],
        zmin=0, zmax=4,
        colorbar=dict(
            title=dict(text="Events", font=dict(color=C["muted"], size=10)),
            tickfont=dict(color=C["muted2"], size=9),
            thickness=10, len=0.8),
        text=[[str(counts[yr][cat]) if counts[yr][cat] > 0 else ""
               for yr in years] for cat in cats],
        texttemplate="%{text}",
        textfont=dict(size=11, color="rgba(255,255,255,0.9)"),
        hovertemplate="Year: %{x}<br>Category: %{y}<br>Events: %{z}<extra></extra>",
    ))

    # Average combined sentiment line (on secondary y would need make_subplots,
    # so use annotations to place dots)
    sent_by_year = {}
    for r in MONTHLY_SENTIMENT:
        yr = int(r[0])
        sent_by_year.setdefault(yr, []).append(r[3])
    avg_sent = {yr: np.mean(vs) for yr, vs in sent_by_year.items()}

    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Negative event density by year and category",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Year", gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(color=C["text"], size=11)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(color=C["text"], size=11)),
        margin=dict(l=120, r=80, t=50, b=40))
    return fig
