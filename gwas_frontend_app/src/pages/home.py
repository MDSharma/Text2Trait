import dash
from dash import dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc
from urllib.parse import urlencode

dash.register_page(
    __name__,
    path="/",
    name="Home",
    title="GWAS-P",
)

# Page layout
layout = html.Div([
    dcc.Location(id="url", refresh=True),
    # ──────────────── Header ────────────────
    dbc.Row(
        dbc.Col(
            [
                html.Img(
                    src=dash.get_asset_url("GWAS-P.png"),
                    alt="GWAS-P logo",
                    style={
                        "width": "150px",
                        "height": "150px",
                        "display": "block",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                        "marginBottom": "15px"
                    },
                ),
                html.H4(
                    "This application helps you explore traits and related genes to discover meaningful biological associations.",
                    className="text-center mb-3"
                ),
            ],
            width={"size": 8, "offset": 2}
        ),
        className="pb-4"
    ),
    # ──────────────── Search options ────────────────
    dbc.Row([
        # LEFT COLUMN - Text only
        dbc.Col([
            html.H4("Search instructions:", className="pb-1"),
            html.H5("If you are interested in a trait please fill in your input on the right."
                    " If you are looking for a specific trait that may influence this input please define it in the field below."),
        ], width=6),

        # RIGHT COLUMN - Two stacked input sections
        dbc.Col([
            # Trait input
            html.Div([
                html.H6("Search by the trait you're interested in:", style={'fontSize': 16}),
                dbc.InputGroup([
                    dbc.Input(
                        id="input-query-trait",
                        placeholder="e.g. Flowering time",
                        type="text",
                    ),
                    dbc.Button([
                        "Search ",
                        html.I(className="bi bi-search", style={"fontSize": "1rem", "verticalAlign": "middle"})
                    ],
                        id="input-button-trait",
                        n_clicks=0,
                        className="ms-2",
                    ),
                ])
            ], className="mb-3"),

            # Gene input
            html.Div([
                html.H6("Looking for something more specific? Search by gene:", style={'fontSize': 16}),
                dbc.InputGroup([
                    dbc.Input(
                        id="input-query-gene",
                        placeholder="e.g. FT",
                        type="text",
                    ),
                    dbc.Button([
                        "Search ",
                        html.I(className="bi bi-search", style={"fontSize": "1rem", "verticalAlign": "middle"})
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

# ──────────────── Disable gene search button if input is empty ────────────────
@callback(
    Output("input-button-gene", "disabled"),
    Input("input-query-gene", "value"),
)
def toggle_gene_button(gene_input):
    return not bool(gene_input)

# ──────────────── Redirect to results page with query string ────────────────
@callback(
    Output("url", "href"),
    Input("input-button-trait", "n_clicks"),
    Input("input-button-gene", "n_clicks"),
    State("input-query-trait", "value"),
    State("input-query-gene", "value"),
    prevent_initial_call=True
)
def redirect_to_results(_, __, trait_value, gene_value):
    if not trait_value:
        return dash.no_update

    query = {"trait": trait_value}
    if gene_value:
        query["gene"] = gene_value

    return "/results?" + urlencode(query)
