"""
Home Page – GWAS-P
------------------

This is the landing page for the GWAS-P application.
It provides:
    - An introductory description of the app.
    - Search inputs for traits and (optionally) specific genes.
    - Redirect to the results page with query parameters.
"""

import dash
from dash import dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc
from urllib.parse import urlencode


# ───────────────────────────────
# Page Registration
# ───────────────────────────────
dash.register_page(
    __name__,
    path="/",
    name="Home",
    title="GWAS-P",
)


# ───────────────────────────────
# Page Layout
# ───────────────────────────────
layout = html.Div([
    dcc.Location(id="url", refresh=True),

    # ──────────────── Header ────────────────
    dbc.Row(
        dbc.Col(
            [
                html.Img(
                    src=dash.get_asset_url("text2trait_logo.png"),
                    alt="GWAS-P logo",
                    style={
                        "width": "200px",
                        "height": "200px",
                        "display": "block",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                        "marginBottom": "15px"
                    },
                ),
                html.H4(
                    (
                        "This application helps you explore traits and related genes "
                        "to discover meaningful biological associations."
                    ),
                    className="text-center mb-3"
                ),
            ],
            width={"size": 8, "offset": 2}
        ),
        className="pb-4"
    ),

    # ──────────────── Search Options ────────────────
    dbc.Row([

        # LEFT COLUMN – Search instructions
        dbc.Col([
            html.H4("Search instructions:", className="pb-1"),
                html.H5(
                    "If you are interested in a trait please fill in your input on the right. "
                    "If you are looking for a specific trait that may influence this input, "
                    "please define it in the field below.",
                    style={"wordWrap": "break-word", "overflowWrap": "break-word"}
                ),
        ], width=6, class_name="ps-4"),

        # RIGHT COLUMN – Two stacked input sections
        dbc.Col([

            # Trait input section
            html.Div([
                html.H6("Search by the trait you're interested in:", style={'fontSize': 16}),
                dbc.InputGroup([
                    dbc.Input(
                        id="input-query-trait",
                        placeholder="e.g. Flowering time",
                        type="text",
                    ),
                    dbc.Button(
                        [
                            "Search ",
                            html.I(
                                className="bi bi-search",
                                style={"fontSize": "1rem", "verticalAlign": "middle"}
                            )
                        ],
                        id="input-button-trait",
                        n_clicks=0,
                        className="ms-2",
                    ),
                ])
            ], className="mb-3"),

            # Gene input section
            html.Div([
                html.H6("Looking for something more specific? Search by gene:", style={'fontSize': 16}),
                dbc.InputGroup([
                    dbc.Input(
                        id="input-query-gene",
                        placeholder="e.g. FT",
                        type="text",
                    ),
                    dbc.Button(
                        [
                            "Search ",
                            html.I(
                                className="bi bi-search",
                                style={"fontSize": "1rem", "verticalAlign": "middle"}
                            )
                        ],
                        id="input-button-gene",
                        n_clicks=0,
                        className="ms-2",
                    ),
                ])
            ]),
        ], width=6)
    ]),
])


# ───────────────────────────────
# Callbacks
# ───────────────────────────────

@callback(
    Output("input-button-gene", "disabled"),
    Input("input-query-gene", "value"),
)
def toggle_gene_button(gene_input: str) -> bool:
    """
    Disable the gene search button if the input is empty.

    Args:
        gene_input: The text entered into the gene search input.

    Returns:
        True if the button should be disabled, False otherwise.
    """
    return not bool(gene_input)


@callback(
    Output("url", "href"),
    Input("input-button-trait", "n_clicks"),
    Input("input-button-gene", "n_clicks"),
    State("input-query-trait", "value"),
    State("input-query-gene", "value"),
    prevent_initial_call=True
)
def redirect_to_results(_, __, trait_value: str, gene_value: str) -> str:
    """
    Redirect to the results page with the selected query parameters.

    Args:
        trait_value: Value from the trait search input (required).
        gene_value: Value from the gene search input (optional).

    Returns:
        URL string with query parameters for the results page.
        If no trait is provided, does not trigger a redirect.
    """
    if not trait_value:
        return dash.no_update

    query = {"trait": trait_value}
    if gene_value:
        query["gene"] = gene_value

    return "/results?" + urlencode(query)