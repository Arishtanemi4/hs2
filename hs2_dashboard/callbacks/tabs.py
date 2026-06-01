from dash import Input, Output
from ..pages import (
    render_overview, render_scenarios, render_workforce,
    render_budget, render_risks, render_narrative, render_methodology,
)


def register_tab_callback(app) -> None:
    @app.callback(Output("tab-content", "children"), Input("main-tabs", "active_tab"))
    def render_tab(tab):
        if tab == "tab-overview":   return render_overview()
        if tab == "tab-scenarios":  return render_scenarios()
        if tab == "tab-workforce":  return render_workforce()
        if tab == "tab-budget":     return render_budget()
        if tab == "tab-risks":      return render_risks()
        if tab == "tab-narrative":  return render_narrative()
        if tab == "tab-method":     return render_methodology()
        from dash import html
        return html.Div()
