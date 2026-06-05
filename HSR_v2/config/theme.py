C = dict(
    bg      = "#0c0e13",
    bg2     = "#13161d",
    bg3     = "#1a1e28",
    border  = "rgba(255,255,255,0.07)",
    border2 = "rgba(255,255,255,0.12)",
    text    = "#e8eaf0",
    muted   = "#7a7f94",
    muted2  = "#525769",
    pos     = "#4ade80",
    neu     = "#f59e0b",
    neg     = "#f87171",
    acc     = "#7c9ef8",
    pu      = "#c084fc",
    grid    = "rgba(255,255,255,0.04)",
)


def _hex_alpha(hex6, alpha=0.5):
    h = hex6.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def _ha(hex6, alpha=0.5):
    return _hex_alpha(hex6, alpha)


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

LAYOUT_NO_AXES = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}
LAYOUT_BARE    = {k: v for k, v in PLOTLY_LAYOUT.items()
                  if k not in ("xaxis", "yaxis", "margin", "hovermode")}
_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10))
