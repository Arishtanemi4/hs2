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


def _hex_alpha(hex6: str, alpha: float = 0.5) -> str:
    """Convert a 6-digit hex colour + alpha float to rgba() string.
    Plotly 6.x does not accept 8-digit hex colours."""
    h = hex6.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _ha(hex6: str, alpha: float = 0.5) -> str:
    return _hex_alpha(hex6, alpha)
