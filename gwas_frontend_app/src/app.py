import dash
from dash import html
import dash_bootstrap_components as dbc
from components.app.sidebar_icons import PAGE_ICONS

external_stylesheets = [
    dbc.themes.YETI,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
]

app = dash.Dash(__name__, 
                use_pages=True, 
                suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets)
server = app.server

# ──────────────── Sidebar ────────────────
sidebar = html.Div(
    dbc.Nav(
        [
            html.Div(
                html.Img(
                    src=dash.get_asset_url("GWAS-P.png"),
                    alt="Logo",
                    style={"width": "75px", "display": "block", "margin": "1rem auto"},
                )
            ),
            html.Hr(),

            *[
                dbc.NavLink(
                    [
                        html.I(className=PAGE_ICONS.get(page["name"], "bi bi-file-text"),
                               style={"marginRight": "8px"}),  # icon
                        page["name"]
                    ],
                    href=page["path"],
                    active="exact",
                    className="mb-1",
                )
                for page in dash.page_registry.values()
                if page["name"] != "Results"
            ],
        ],
        vertical=True,
        pills=True,
        style={"padding": "1rem"},
    ),
    style={
        "width": "220px",
        "height": "100vh",
        "backgroundColor": "#f5f7fa",
        "borderRight": "1px solid #d6dbe3",
    },
)

# ──────────────── Layout of the app ────────────────
app.layout = dbc.Container([
# ──────────────── Pages layout ────────────────
    dbc.Row(
        [
            dbc.Col(
                [
                    sidebar
                ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

            dbc.Col(
                [
                    dash.page_container
                ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10, class_name="pt-3"),
        ],
        style={"minHeight": "100vh"} 
    ),
# ──────────────── Footnote ────────────────
    dbc.Row([
        dbc.Col(html.Div("\u00A9 MaastrichtUniversity2025",
                         style={'fontSize':16, 'textAlign':'center'}), class_name="p-2"),
    ],
    class_name="pb-2"),
], fluid=True)

if __name__ == "__main__":
    app.run(debug=False)