from dash import html
from config.theme import C, _ha
from data.hs2_data import KPI_DATA


def badge(text, kind="neg"):
    colour_map = {
        "pos": ("#4ade80", "rgba(74,222,128,0.12)"),
        "neu": ("#f59e0b", "rgba(245,158,11,0.12)"),
        "neg": ("#f87171", "rgba(248,113,113,0.12)"),
        "acc": ("#7c9ef8", "rgba(124,158,248,0.12)"),
    }
    fg, bg = colour_map.get(kind, colour_map["neg"])
    return html.Span(text, style={
        "fontSize": "10px", "fontFamily": "DM Mono,monospace", "fontWeight": "500",
        "padding": "3px 9px", "borderRadius": "20px",
        "color": fg, "background": bg, "border": f"1px solid {fg}44",
    })


def stat_card(label, value, sub, delta=None, kind="neg"):
    colour_map = {"pos": C["pos"], "neu": C["neu"], "neg": C["neg"], "acc": C["acc"], "pu": C["pu"]}
    val_col  = colour_map.get(kind, C["neg"])
    children = [
        html.Div(label, style={"fontSize": "10px", "fontFamily": "DM Mono,monospace",
                               "textTransform": "uppercase", "letterSpacing": "0.08em",
                               "color": C["muted"], "marginBottom": "6px"}),
        html.Div(value, style={"fontSize": "22px", "fontWeight": "300",
                               "fontFamily": "Fraunces,serif", "color": val_col}),
        html.Div(sub,   style={"fontSize": "11px", "color": C["muted"], "marginTop": "2px"}),
    ]
    if delta:
        dkind = "neg" if "↑" in delta else "pos"
        children.append(html.Div(delta, style={
            "fontSize": "11px", "fontFamily": "DM Mono,monospace", "marginTop": "4px",
            "color": C["neg"] if dkind == "neg" else C["pos"]}))
    return html.Div(children, style={
        "background": C["bg2"], "border": f"1px solid {C['border']}",
        "borderRadius": "10px", "padding": "14px 16px",
        "borderTop": f"2px solid {val_col}",
    })


def card(children, style=None):
    base = {"background": C["bg2"], "border": f"1px solid {C['border']}",
            "borderRadius": "10px", "padding": "18px 20px", "height": "100%"}
    if style:
        base.update(style)
    return html.Div(children, style=base)


def card_title(text, right=None):
    children = [html.Span(text)]
    if right:
        children.append(right)
    return html.Div(children, style={
        "fontSize": "11px", "color": C["muted"], "textTransform": "uppercase",
        "letterSpacing": "0.08em", "fontFamily": "DM Mono,monospace",
        "marginBottom": "14px", "display": "flex", "justifyContent": "space-between",
        "alignItems": "center"})


def section_header(title, subtitle=""):
    return html.Div([
        html.H2(title, style={"fontFamily": "Fraunces,serif", "fontSize": "22px",
                              "fontWeight": "300", "color": C["text"], "marginBottom": "4px",
                              "letterSpacing": "-0.3px"}),
        html.P(subtitle, style={"fontSize": "12px", "color": C["muted"], "marginBottom": "18px"}),
    ])


def narrative_box(tag_text, body_text, id_body="narr-body-default"):
    return html.Div([
        html.Div(f"⬡ {tag_text}", style={"fontSize": "10px", "fontFamily": "DM Mono,monospace",
                                          "color": C["acc"], "textTransform": "uppercase",
                                          "letterSpacing": "0.1em", "marginBottom": "10px"}),
        html.Div(body_text, id=id_body, style={
            "fontFamily": "Fraunces,serif", "fontSize": "15px", "fontWeight": "300",
            "lineHeight": "1.8", "color": C["text"], "whiteSpace": "pre-line"}),
    ], style={"background": C["bg3"], "border": f"1px solid {C['border2']}",
              "borderRadius": "10px", "padding": "20px 22px"})


def kpi_table():
    rows   = []
    header = html.Tr([
        html.Th(h, style={"padding": "6px 10px", "color": C["muted"], "fontWeight": "400",
                          "fontFamily": "DM Mono,monospace", "fontSize": "10px",
                          "textTransform": "uppercase", "letterSpacing": "0.06em",
                          "borderBottom": f"1px solid {C['border']}"})
        for h in ["Metric", "Target", "Actual", "Status", "Source"]
    ])
    for metric, target, actual, kind, source in KPI_DATA:
        status_text = {"pos": "MET", "neu": "NOTE", "neg": "MISSED"}[kind]
        rows.append(html.Tr([
            html.Td(metric,  style={"padding": "7px 10px", "color": C["text"],   "borderBottom": f"1px solid {C['border']}", "fontSize": "12px"}),
            html.Td(target,  style={"padding": "7px 10px", "color": C["muted"],  "borderBottom": f"1px solid {C['border']}", "fontSize": "11px", "fontFamily": "DM Mono,monospace"}),
            html.Td(actual,  style={"padding": "7px 10px", "color": C["text"],   "borderBottom": f"1px solid {C['border']}", "fontSize": "12px", "fontFamily": "DM Mono,monospace"}),
            html.Td(badge(status_text, kind), style={"padding": "7px 10px", "borderBottom": f"1px solid {C['border']}"}),
            html.Td(source,  style={"padding": "7px 10px", "color": C["muted2"], "borderBottom": f"1px solid {C['border']}", "fontSize": "10px", "fontFamily": "DM Mono,monospace"}),
        ]))
    return html.Table([html.Thead(header), html.Tbody(rows)],
                      style={"width": "100%", "borderCollapse": "collapse", "fontSize": "12px"})


def risk_item(severity, name, desc):
    sev_col = {"HIGH": C["neg"], "MED": C["neu"], "LOW": C["pos"]}[severity]
    return html.Div([
        html.Div(html.Span(severity, style={"fontSize": "10px", "fontFamily": "DM Mono,monospace",
                                            "fontWeight": "500", "color": sev_col}),
                 style={"width": "46px", "height": "22px", "borderRadius": "5px", "flexShrink": "0",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "background": _ha(sev_col, 0.13), "border": f"1px solid {sev_col}44"}),
        html.Div([
            html.Div(name, style={"fontSize": "12px", "fontWeight": "500", "color": C["text"], "marginBottom": "2px"}),
            html.Div(desc, style={"fontSize": "11px", "color": C["muted"], "lineHeight": "1.5"}),
        ])
    ], style={"display": "flex", "gap": "12px", "alignItems": "flex-start",
              "padding": "10px 0", "borderBottom": f"1px solid {C['border']}"})
