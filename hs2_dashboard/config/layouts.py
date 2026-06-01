from .theme import C

PLOTLY_LAYOUT = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(family="DM Mono, monospace", color=C["muted"], size=11),
    margin        = dict(l=10, r=10, t=30, b=10),
    xaxis         = dict(gridcolor=C["grid"], zeroline=False,
                         tickfont=dict(color=C["muted2"], size=10)),
    yaxis         = dict(gridcolor=C["grid"], zeroline=False,
                         tickfont=dict(color=C["muted2"], size=10)),
    hovermode     = "x unified",
)

# Layout base without axis defs — use when overriding xaxis/yaxis explicitly
LAYOUT_NO_AXES = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}

# Layout with no axes AND no margin — for charts that override both
LAYOUT_BARE = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis", "margin")}

# Default legend style — merge into update_layout calls that need it
_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10))
