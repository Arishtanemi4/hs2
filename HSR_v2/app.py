import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from config.theme import C

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&family=DM+Sans:wght@300;400;500&display=swap",
    ],
    title="HS2 Intelligence Dashboard",
    suppress_callback_exceptions=True,
)

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
body { background: #0c0e13 !important; margin: 0; }
* { box-sizing: border-box; }
.tab-content { background: transparent !important; border: none !important; }
.nav-tabs { border-bottom: 1px solid rgba(255,255,255,0.07) !important; background: #13161d; padding: 0 1rem; display: flex !important; flex-wrap: nowrap !important; overflow-x: auto !important; overflow-y: hidden !important; scrollbar-width: thin; }
.nav-tabs .nav-link { color: #7a7f94 !important; font-size: 11px; font-family: DM Sans, sans-serif; font-weight: 500; letter-spacing: 0.02em; border: none !important; border-bottom: 2px solid transparent !important; padding: 12px 11px !important; border-radius: 0 !important; white-space: nowrap !important; flex-shrink: 0 !important; }
.nav-tabs .nav-link:hover { color: #e8eaf0 !important; }
.nav-tabs .nav-link.active { color: #7c9ef8 !important; border-bottom: 2px solid #7c9ef8 !important; background: transparent !important; }
input[type=range] { accent-color: #7c9ef8; cursor: pointer; width: 100%; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #13161d; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


def make_layout():
    return html.Div([
        html.Div([
            html.Div([
                html.Span(["HS", html.Span("2", style={"color": C["acc"]}), " Intelligence"],
                          style={"fontFamily": "Fraunces,serif", "fontSize": "18px",
                                 "fontWeight": "600", "color": C["text"]}),
                html.Span("MONTE CARLO · SCENARIO ANALYSIS · v1.0",
                          style={"fontSize": "10px", "fontFamily": "DM Mono,monospace",
                                 "color": C["muted"], "background": C["bg3"],
                                 "border": f"1px solid {C['border']}", "padding": "3px 8px",
                                 "borderRadius": "20px", "letterSpacing": "0.05em"}),
            ], style={"display": "flex", "alignItems": "center", "gap": "16px"}),
            html.Div([
                html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%",
                               "background": C["pos"], "animation": "pulse 2s infinite"}),
                html.Span("LIVE MODEL", style={"fontSize": "12px", "fontFamily": "DM Mono,monospace", "color": C["muted"]}),
                html.Span("Updated: May 2026 · 10,000 simulations",
                          style={"fontSize": "11px", "fontFamily": "DM Mono,monospace", "color": C["muted2"]}),
            ], style={"display": "flex", "alignItems": "center", "gap": "10px"}),
        ], style={"background": C["bg2"], "borderBottom": f"1px solid {C['border']}",
                  "padding": "0 2rem", "height": "56px", "display": "flex", "alignItems": "center",
                  "justifyContent": "space-between", "position": "sticky", "top": "0", "zIndex": "100"}),

        dbc.Tabs(id="main-tabs", active_tab="tab-overview", children=[
            dbc.Tab(label="Overview",             tab_id="tab-overview"),
            dbc.Tab(label="Scenario Clusters",    tab_id="tab-scenarios"),
            dbc.Tab(label="Workforce & Sentiment", tab_id="tab-workforce"),
            dbc.Tab(label="Budget Analysis",      tab_id="tab-budget"),
            dbc.Tab(label="Risk Signals",         tab_id="tab-risks"),
            dbc.Tab(label="Narrative Engine",     tab_id="tab-narrative"),
            dbc.Tab(label="Causality",            tab_id="tab-causality"),
            dbc.Tab(label="Methodology",          tab_id="tab-method"),
        ]),
        html.Div(id="tab-content", style={"padding": "0"}),

    ], style={"background": C["bg"], "minHeight": "100vh", "fontFamily": "DM Sans,sans-serif",
              "color": C["text"], "fontSize": "14px"})


app.layout = make_layout()
