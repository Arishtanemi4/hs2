from dash import Input, Output, callback_context
from ..components import narrative_box
from ..data import NARRATIVES


def register_narrative_callback(app) -> None:
    @app.callback(
        Output("narrative-output", "children"),
        Input("btn-pos", "n_clicks"),
        Input("btn-neu", "n_clicks"),
        Input("btn-neg", "n_clicks"),
        prevent_initial_call=False,
    )
    def switch_narrative(n_pos, n_neu, n_neg):
        ctx  = callback_context
        kind = "neu"
        if ctx.triggered:
            btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
            kind = {"btn-pos": "pos", "btn-neu": "neu", "btn-neg": "neg"}.get(btn_id, "neu")
        return narrative_box(NARRATIVES[kind]["tag"], NARRATIVES[kind]["body"])
