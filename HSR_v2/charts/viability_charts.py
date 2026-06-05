import numpy as np
import plotly.graph_objects as go

from config.theme import C, LAYOUT_BARE, _ha
from data.hs2_data import VIABILITY_DATA
from models.viability import pred_sentiment


def fig_scatter_correlation():
    V    = VIABILITY_DATA
    cpkm = [c / n for c, n in zip(V["cost_mid"], V["network_km"])]
    x_fit = np.linspace(0.04, 0.65, 300)
    y_fit = np.clip(V["slope"] * np.log(x_fit) + V["intercept"], -1.0, 0.1)
    se    = 0.08
    fig   = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_fit, name="Log-linear fit (R²=0.838)",
        line=dict(color=C["acc"], width=2, dash="solid"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=list(x_fit)+list(x_fit[::-1]),
        y=list(np.clip(y_fit+se, -1, 0.1))+list(np.clip(y_fit-se, -1, 0.1)[::-1]),
        fill="toself", fillcolor=_ha(C["acc"], 0.08),
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    fig.add_hline(y=V["threshold_sent"],
        line=dict(color=C["neu"], width=1.5, dash="dash"),
        annotation_text="Viability threshold (−0.40)",
        annotation_font_color=C["neu"], annotation_font_size=10)
    fig.add_vline(x=V["threshold_cpkm"],
        line=dict(color=C["neu"], width=1, dash="dot"),
        annotation_text="£0.142bn/km max", annotation_position="top right",
        annotation_font_color=C["neu"], annotation_font_size=9)
    fig.add_shape(type="rect",
        x0=0.04, x1=V["threshold_cpkm"],
        y0=V["threshold_sent"], y1=0.15,
        fillcolor=_ha(C["pos"], 0.06),
        line=dict(color="rgba(0,0,0,0)"))
    for i, (x, y, yr, v) in enumerate(zip(cpkm, V["sentiment"], V["years"], V["verified"])):
        col     = C["neg"] if y < -0.5 else (C["neu"] if y < -0.25 else C["pos"])
        size    = 12 if v else 8
        opacity = 1.0 if v else 0.45
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            name=str(yr),
            marker=dict(size=size, color=col, opacity=opacity,
                        line=dict(color=C["bg"], width=2)),
            text=[str(yr)], textposition="top center",
            textfont=dict(color=C["muted"], size=9),
            hovertemplate=(
                f"<b>{yr}</b><br>"
                f"Cost: £{V['cost_mid'][i]:.0f}bn<br>"
                f"Network: {V['network_km'][i]}km<br>"
                f"Cost/km: £{x:.3f}bn/km<br>"
                f"Sentiment: {y:.2f}<br>"
                f"{'Verified' if v else 'Estimated'}"
                "<extra></extra>"
            ),
            showlegend=False))
    fig.add_annotation(
        x=cpkm[-1], y=V["sentiment"][-1]-0.05,
        text="Current (2026)",
        font=dict(color=C["neg"], size=10),
        showarrow=True, arrowhead=2,
        arrowcolor=C["neg"], arrowsize=0.8, arrowwidth=1, ax=40, ay=30)
    fig.add_annotation(x=0.08, y=-0.15, text="Viable zone",
        font=dict(color=C["pos"], size=10), showarrow=False)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Cost-per-km vs parliamentary sentiment — log-linear correlation (R²=0.838, p=0.004)",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Cost per km (£bn/km)", gridcolor=C["grid"], zeroline=False,
                   tickprefix="£", ticksuffix="bn/km",
                   tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(title="Sentiment index", gridcolor=C["grid"], zeroline=False,
                   range=[-1.05, 0.2], tickfont=dict(color=C["muted2"], size=10)),
        margin=dict(l=60, r=20, t=50, b=60),
        showlegend=False)
    return fig


def fig_viability_envelope():
    V          = VIABILITY_DATA
    cost_range = np.linspace(20, 130, 220)
    km_range   = np.linspace(100, 600, 220)
    C_grid, K_grid = np.meshgrid(cost_range, km_range)
    S_grid = np.vectorize(lambda c, k: pred_sentiment(c, k))(C_grid, K_grid)
    fig = go.Figure()
    fig.add_trace(go.Contour(
        z=S_grid, x=cost_range, y=km_range,
        colorscale=[
            [0.0, "#7c2020"], [0.3, "#c04040"], [0.5, "#d47a10"],
            [0.7, "#639922"], [1.0, "#3B6D11"],
        ],
        zmin=-1.0, zmax=0.1,
        contours=dict(start=-1.0, end=0.1, size=0.1, showlabels=True,
                      labelfont=dict(size=9, color="rgba(255,255,255,0.7)")),
        colorbar=dict(
            title=dict(text="Sentiment", font=dict(color=C["muted"], size=10)),
            tickfont=dict(color=C["muted"], size=9), thickness=12, len=0.8),
        hovertemplate="Cost: £%{x:.0f}bn<br>Network: %{y:.0f}km<br>Sentiment: %{z:.2f}<extra></extra>",
        showscale=True))
    boundary_cost = np.linspace(14, 130, 200)
    boundary_km   = np.clip(boundary_cost / V["threshold_cpkm"], 100, 600)
    fig.add_trace(go.Scatter(
        x=boundary_cost, y=boundary_km,
        mode="lines", name="Viability boundary",
        line=dict(color="white", width=2.5, dash="dash"),
        hovertemplate="Boundary: £%{x:.0f}bn / %{y:.0f}km = £0.142bn/km<extra></extra>"))
    for i, (c, k, yr, v) in enumerate(zip(
            V["cost_mid"], V["network_km"], V["years"], V["verified"])):
        fig.add_trace(go.Scatter(
            x=[c], y=[k], mode="markers+text",
            name=str(yr),
            marker=dict(size=14 if i == len(V["years"])-1 else 10,
                        color="white", opacity=1.0 if v else 0.55,
                        line=dict(color=C["bg2"], width=2), symbol="circle"),
            text=[str(yr)], textposition="top center",
            textfont=dict(color="white", size=9), showlegend=False,
            hovertemplate=(
                f"<b>{yr}</b>: £{c:.0f}bn / {k}km<br>"
                f"Sentiment: {pred_sentiment(c, k):.2f}<br>"
                f"{'Verified' if v else 'Estimated'}<extra></extra>"
            )))
    for i in range(len(V["years"])-1):
        fig.add_annotation(
            x=V["cost_mid"][i+1], y=V["network_km"][i+1],
            ax=V["cost_mid"][i],  ay=V["network_km"][i],
            xref="x", yref="y", axref="x", ayref="y",
            arrowhead=2, arrowsize=1, arrowwidth=1.5,
            arrowcolor="rgba(255,255,255,0.6)", showarrow=True)
    for sc_km, sc_name, sc_x_offset in [(540, "540km", 5), (400, "400km", 5), (225, "225km", 5)]:
        max_cost_viable = V["threshold_cpkm"] * sc_km
        if max_cost_viable <= 130:
            fig.add_trace(go.Scatter(
                x=[max_cost_viable], y=[sc_km],
                mode="markers+text",
                marker=dict(size=8, color=C["neu"], symbol="diamond",
                            line=dict(color=C["bg2"], width=1)),
                text=[f"Max £{max_cost_viable:.0f}bn"],
                textposition="middle right",
                textfont=dict(color=C["neu"], size=9),
                name=f"Max viable cost ({sc_name})",
                showlegend=False,
                hovertemplate=f"{sc_name}: max viable £{max_cost_viable:.0f}bn<extra></extra>"))
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Viability envelope: which combinations of cost and network size keep sentiment viable?",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Total project cost (£bn)", gridcolor="rgba(255,255,255,0.1)",
                   zeroline=False, tickprefix="£", ticksuffix="bn",
                   tickfont=dict(color="rgba(255,255,255,0.6)", size=10), range=[20, 130]),
        yaxis=dict(title="Network length (km)", gridcolor="rgba(255,255,255,0.1)",
                   zeroline=False, ticksuffix="km",
                   tickfont=dict(color="rgba(255,255,255,0.6)", size=10), range=[100, 610]),
        margin=dict(l=60, r=80, t=50, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", font=dict(color="white", size=9)))
    return fig


def fig_sentiment_forecast(cost_target=95.2, km_target=225):
    V          = VIABILITY_DATA
    cost_range = np.linspace(20, 130, 300)
    scenarios  = [
        (540, C["pos"], "540km — full original network"),
        (400, C["acc"], "400km — reduced network"),
        (225, C["neu"], "225km — Phase 1 only (current)"),
        (160, C["neg"], "160km — core spine only"),
    ]
    fig = go.Figure()
    for km, col, name in scenarios:
        sents     = [pred_sentiment(c, km) for c in cost_range]
        sents_arr = np.array(sents)
        fig.add_trace(go.Scatter(
            x=cost_range, y=sents, name=name,
            line=dict(color=col, width=2),
            hovertemplate=f"{name}<br>Cost: £%{{x:.0f}}bn<br>Sentiment: %{{y:.2f}}<extra></extra>"))
        crossings = np.where(np.diff(np.sign(sents_arr - V["threshold_sent"])))[0]
        if len(crossings):
            cx = cost_range[crossings[0]]
            fig.add_trace(go.Scatter(
                x=[cx], y=[V["threshold_sent"]], mode="markers",
                marker=dict(size=8, color=col, symbol="x",
                            line=dict(color=C["bg2"], width=1)),
                showlegend=False,
                hovertemplate=f"{name}: crosses threshold at £{cx:.0f}bn<extra></extra>"))
    fig.add_hline(y=V["threshold_sent"],
        line=dict(color=C["neu"], width=1.5, dash="dash"),
        annotation_text="Viability threshold",
        annotation_font_color=C["neu"], annotation_font_size=10)
    fig.add_vline(x=cost_target,
        line=dict(color=C["neg"], width=1, dash="dot"),
        annotation_text=f"Current: £{cost_target:.0f}bn",
        annotation_font_color=C["neg"], annotation_font_size=9)
    fig.add_annotation(x=35, y=-0.25, text="Viable zone →",
        font=dict(color=C["pos"], size=10), showarrow=False)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Sentiment forecast: what £1bn more costs the project's political viability",
                   font=dict(color=C["text"], size=12)),
        xaxis=dict(title="Total cost (£bn)", gridcolor=C["grid"], zeroline=False,
                   tickprefix="£", ticksuffix="bn",
                   tickfont=dict(color=C["muted2"], size=10), range=[20, 130]),
        yaxis=dict(title="Predicted sentiment", gridcolor=C["grid"],
                   zeroline=False, range=[-1.05, 0.15],
                   tickfont=dict(color=C["muted2"], size=10)),
        margin=dict(l=60, r=20, t=50, b=60),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10),
                    orientation="h", y=-0.2))
    return fig


def fig_sentiment_gauge(predicted_sentiment):
    col = (C["pos"] if predicted_sentiment > -0.2
           else C["neu"] if predicted_sentiment > -0.5
           else C["neg"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(predicted_sentiment, 2),
        delta=dict(reference=-0.40, valueformat=".2f",
                   increasing=dict(color=C["pos"]),
                   decreasing=dict(color=C["neg"])),
        number=dict(font=dict(color=col, size=28, family="Fraunces, serif"),
                    valueformat=".2f"),
        gauge=dict(
            axis=dict(range=[-1.0, 0.2],
                      tickvals=[-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2],
                      ticktext=["-1.0","-0.8","-0.6","-0.4","-0.2","0","0.2"],
                      tickfont=dict(color=C["muted2"], size=9),
                      tickcolor=C["muted2"]),
            bar=dict(color=col, thickness=0.25),
            bgcolor=C["bg3"], borderwidth=0,
            steps=[
                dict(range=[-1.0, -0.5], color=_ha(C["neg"], 0.22)),
                dict(range=[-0.5, -0.4], color=_ha(C["neu"], 0.18)),
                dict(range=[-0.4,  0.2], color=_ha(C["pos"], 0.14)),
            ],
            threshold=dict(line=dict(color=C["neu"], width=3),
                           thickness=0.8, value=-0.40),
            shape="angular"),
        title=dict(text="Predicted sentiment",
                   font=dict(color=C["muted"], size=11, family="DM Mono, monospace")),
        domain=dict(x=[0, 1], y=[0, 1]),
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=20, r=20, t=40, b=20), height=200)
    return fig


def fig_cpkm_gauge(cpkm):
    col = (C["pos"] if cpkm < 0.142 else C["neu"] if cpkm < 0.28 else C["neg"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(cpkm, 3),
        delta=dict(reference=0.142, valueformat=".3f",
                   increasing=dict(color=C["neg"]),
                   decreasing=dict(color=C["pos"])),
        number=dict(font=dict(color=col, size=28, family="Fraunces, serif"),
                    prefix="£", suffix=" bn/km", valueformat=".3f"),
        gauge=dict(
            axis=dict(range=[0, 0.65],
                      tickvals=[0, 0.1, 0.2, 0.142, 0.3, 0.4, 0.5, 0.6],
                      ticktext=["0","0.1","0.2","⚠0.14","0.3","0.4","0.5","0.6"],
                      tickfont=dict(color=C["muted2"], size=9),
                      tickcolor=C["muted2"]),
            bar=dict(color=col, thickness=0.25),
            bgcolor=C["bg3"], borderwidth=0,
            steps=[
                dict(range=[0,     0.142], color=_ha(C["pos"], 0.14)),
                dict(range=[0.142, 0.30],  color=_ha(C["neu"], 0.18)),
                dict(range=[0.30,  0.65],  color=_ha(C["neg"], 0.22)),
            ],
            threshold=dict(line=dict(color=C["neu"], width=3),
                           thickness=0.8, value=0.142),
            shape="angular"),
        title=dict(text="Cost per km (£bn/km)",
                   font=dict(color=C["muted"], size=11, family="DM Mono, monospace")),
        domain=dict(x=[0, 1], y=[0, 1]),
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=20, r=20, t=40, b=20), height=200)
    return fig
