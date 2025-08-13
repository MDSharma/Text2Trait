"""
Index Page – GWAS-P
-------------------

This page provides a browsable index of:
    - All traits in the knowledge graph.
    - All trait–gene pairs.

Users can click "View Results" links to navigate directly to the results page
for a specific trait or trait–gene combination.
"""

import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc
from urllib.parse import urlencode
from pathlib import Path

from utils.data_loader import load_graph
from utils.search_utils import (
    get_trait_name,
    get_all_trait_gene_pairs,
    get_all_traits
)


# ───────────────────────────────
# Page Registration
# ───────────────────────────────
dash.register_page(
    __name__,
    path="/index",
    name="Index",
    title="Index"
)


# ───────────────────────────────
# Load Graph Data
# ───────────────────────────────
script_dir = Path(__file__).resolve().parent
json_path = script_dir.parent / "data" / "initial_arabiodopsis_kg.json"
G, _ = load_graph(json_path)


# ───────────────────────────────
# Helper Functions
# ───────────────────────────────
def make_link(trait_id: str = None, gene_id: str = None) -> str:
    """
    Construct a URL to the results page with optional trait and gene parameters.
    """
    params = {}
    if trait_id:
        params["trait"] = trait_id
    if gene_id:
        params["gene"] = gene_id
    return f"/results?{urlencode(params)}"


# Shared DataTable styles
shared_styles = {
    "table": {
        "overflowX": "auto",
        "border": "1px solid #dee2e6",
        "borderRadius": "0.25rem",
        "fontFamily": "'Helvetica Neue', Helvetica, Arial, sans-serif",
        "fontSize": "0.95rem",
        "backgroundColor": "#ffffff",
    },
    "header": {
        "backgroundColor": "#f1f3f5",
        "fontWeight": "bold",
        "borderBottom": "2px solid #dee2e6",
        "fontFamily": "'Helvetica Neue', Helvetica, Arial, sans-serif",
        "color": "#212529",
        "padding": "0.75rem",
        "textAlign": "left",
    },
    "cell": {
        "padding": "0.70rem",
        "textAlign": "left",
        "borderBottom": "1px solid #dee2e6",
        "fontFamily": "'Helvetica Neue', Helvetica, Arial, sans-serif",
        "color": "#212529",
    },
    "conditional": [
        {
            "if": {"column_id": "Link"},
            "verticalAlign": "middle",
            "paddingTop": "1.8rem",
        },
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#f8f9fa",
        },
        {
            "if": {"state": "active"},
            "backgroundColor": "#d1ecf1",
            "border": "1px solid #b8daff",
        },
        {
            "if": {"state": "selected"},
            "backgroundColor": "#cce5ff",
            "border": "1px solid #b8daff",
        },
    ]
}


# ───────────────────────────────
# Table Generators
# ───────────────────────────────
def generate_traits_tab() -> dash_table.DataTable:
    """
    Create a DataTable listing all traits in the graph, each linking to results.
    """
    data = [
        {
            "Trait": get_trait_name(G, trait_id),
            "Link": f"[View Results]({make_link(trait_id=trait_id)})"
        }
        for trait_id in get_all_traits(G)
    ]

    return dash_table.DataTable(
        columns=[
            {"name": "Trait", "id": "Trait"},
            {"name": "Link", "id": "Link", "presentation": "markdown"},
        ],
        data=data,
        page_size=10,
        sort_action="native",
        filter_action="none",
        style_table=shared_styles["table"],
        style_header=shared_styles["header"],
        style_cell=shared_styles["cell"],
        style_data_conditional=shared_styles["conditional"],
        markdown_options={"html": True},
    )


def generate_trait_gene_tab() -> dash_table.DataTable:
    """
    Create a DataTable listing all trait–gene pairs in the graph, each linking to results.
    """
    pairs = get_all_trait_gene_pairs(G)
    data = [
        {
            "Trait": trait_name,
            "Gene": gene_name,
            "Link": f"[View Results]({make_link(trait_id=trait_id, gene_id=gene_id)})"
        }
        for trait_id, trait_name, gene_id, gene_name in pairs
    ]

    return dash_table.DataTable(
        columns=[
            {"name": "Trait", "id": "Trait"},
            {"name": "Gene", "id": "Gene"},
            {"name": "Link", "id": "Link", "presentation": "markdown"},
        ],
        data=data,
        page_size=10,
        sort_action="native",
        filter_action="none",
        style_table=shared_styles["table"],
        style_header=shared_styles["header"],
        style_cell=shared_styles["cell"],
        style_data_conditional=shared_styles["conditional"],
        markdown_options={"html": True},
    )


# ───────────────────────────────
# Page Layout
# ───────────────────────────────
layout = dbc.Container([
    html.H2("GWAS-P Knowledge Graph Explorer", className="my-4"),
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(generate_traits_tab(), label="Traits"),
                dbc.Tab(generate_trait_gene_tab(), label="Traits & Genes"),
            ])
        ])
    ])
], fluid=True)