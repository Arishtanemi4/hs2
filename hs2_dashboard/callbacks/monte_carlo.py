import plotly.graph_objects as go
from dash import Input, Output
from ..config import C, LAYOUT_NO_AXES, _ha
from ..data import PARAMS
from ..engine import run_monte_carlo
from ..figures import fig_fan_chart, fig_cost_histogram


def register_mc_callbacks(app) -> None:
    # Slider display values
    for p in PARAMS:
        @app.callback(
            Output(f"val-{p['id']}", "children"),
            Input(f"slider-{p['id']}", "value"),
        )
        def update_val(v, pid=p["id"]):
            step = next(x["step"] for x in PARAMS if x["id"] == pid)
            fmt  = f"{v:.2f}" if step < 0.1 else (f"{v:.1f}" if step < 1 else f"{v:.0f}")
            unit_map = {"inflation": "%/yr", "scope": "%", "political": "%",
                        "kpi": "", "workforce": "%", "euston": "%"}
            return fmt + unit_map.get(pid, "")

    # Live Monte Carlo update
    @app.callback(
        Output("live-cluster-chart", "figure"),
        Output("fan-chart",          "figure"),
        Output("cost-histogram",     "figure"),
        Output("pos-pct-live",       "children"),
        Output("neu-pct-live",       "children"),
        Output("neg-pct-live",       "children"),
        [Input(f"slider-{p['id']}", "value") for p in PARAMS],
        prevent_initial_call=False,
    )
    def update_mc(*vals):
        inflation, scope, political, kpi, workforce, euston = vals
        mc = run_monte_carlo(
            n_sims=5000,
            inflation=inflation,
            scope_risk=scope,
            political_risk=political,
            kpi_score=kpi,
            workforce_stability=workforce,
            euston_prob=euston,
        )
        cp = mc["cluster_probs"]

        cluster_fig = go.Figure(go.Bar(
            x=["Controlled", "Managed", "Escalation"],
            y=[cp["pos"], cp["neu"], cp["neg"]],
            marker_color=[_ha(C["pos"], 0.47), _ha(C["neu"], 0.47), _ha(C["neg"], 0.47)],
            marker_line_color=[C["pos"], C["neu"], C["neg"]], marker_line_width=2,
            text=[f"{cp['pos']:.0f}%", f"{cp['neu']:.0f}%", f"{cp['neg']:.0f}%"],
            textposition="outside", textfont=dict(color=C["muted"], size=11),
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        ))
        cluster_fig.update_layout(**LAYOUT_NO_AXES,
            yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor=C["grid"],
                       tickfont=dict(color=C["muted2"], size=10)),
            xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)))

        return (
            cluster_fig,
            fig_fan_chart(mc["fan_data"]),
            fig_cost_histogram(mc["costs"]),
            f"{cp['pos']:.0f}%",
            f"{cp['neu']:.0f}%",
            f"{cp['neg']:.0f}%",
        )
