"""
Application Main Entry Script
----------------------------------

This script initializes and runs a Dash web application with a Bootstrap-based layout.
It includes:
    - A sidebar with page navigation (using icons from `PAGE_ICONS`).
    - A main content area for dynamic page rendering.
    - A footer with copyright.
"""

import dash
from dash import html
import dash_bootstrap_components as dbc
from components.app.sidebar_icons import PAGE_ICONS

# ───────────────────────────────
# External Stylesheets
# ───────────────────────────────
external_stylesheets = [
    dbc.themes.YETI,  # Bootstrap theme
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"  # Bootstrap Icons
]

# ───────────────────────────────
# Dash App Initialization
# ───────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,  # Enables Dash multi-page support
    suppress_callback_exceptions=True,  # Allows callbacks for unloaded pages
    external_stylesheets=external_stylesheets
)
server = app.server  # Expose the WSGI server for deployment

# ───────────────────────────────
# Sidebar Component
# ───────────────────────────────
sidebar = html.Div(
    dbc.Nav(
        [
            # Logo at the top of the sidebar
            html.Div(
                html.Img(
                    src=dash.get_asset_url("GWAS-P.png"),
                    alt="Logo",
                    style={"width": "75px", "display": "block", "margin": "1rem auto"},
                )
            ),
            html.Hr(),

            # Navigation links for registered pages, excluding "Results"
            *[
                dbc.NavLink(
                    [
                        html.I(
                            className=PAGE_ICONS.get(page["name"], "bi bi-file-text"),
                            style={"marginRight": "8px"}
                        ),
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

# ───────────────────────────────
# Layout Structure
# ───────────────────────────────
app.layout = dbc.Container(
    [
        # Main content area split into Sidebar + Page container
        dbc.Row(
            [
                # Sidebar column
                dbc.Col(
                    [sidebar],
                    xs=4, sm=4, md=2, lg=2, xl=2, xxl=2
                ),

                # Page content column
                dbc.Col(
                    [dash.page_container],
                    xs=8, sm=8, md=10, lg=10, xl=10, xxl=10,
                    class_name="pt-3"
                ),
            ],
            style={"minHeight": "100vh"}
        ),

        # Footer row
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        "\u00A9 MaastrichtUniversity2025",
                        style={'fontSize': 16, 'textAlign': 'center'}
                    ),
                    class_name="p-2"
                ),
            ],
            class_name="pb-2"
        ),
    ],
    fluid=True
)

# ───────────────────────────────
# Application Entry Point
# ───────────────────────────────
if __name__ == "__main__":
    app.run(debug=False)