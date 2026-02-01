"""
Index Page – Text2Trait
------------------------

This page provides a browsable index of:
    - All traits in the knowledge graph.
    - All trait–gene pairs.

Users can select a species and click "View Results" links to navigate directly 
to the results page for a specific trait or trait–gene combination.
"""

import dash
from dash import html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from urllib.parse import urlencode
from pathlib import Path
import networkx as nx

from utils.data_loader import load_graph, load_graph_by_species
from utils.search_utils import (
    get_node_name,
    is_trait_node,
    is_gene_node
)
from utils.species_config import get_available_species_from_data

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
data_dir = script_dir.parent / "data"
node_json_path = data_dir / "graph_nodes_dataset.json"
edge_json_path = data_dir / "graph_edges_dataset.json"
G, _ = load_graph(node_json_path, edge_json_path)
AVAILABLE_SPECIES = get_available_species_from_data(data_dir)

# ───────────────────────────────
# Helper Functions
# ───────────────────────────────
def make_link(trait_id: str = None, gene_id: str = None, species: str = "all") -> str:
    """Construct a URL to the results page with optional trait, gene, and species parameters."""
    params = {}
    if trait_id:
        params["trait"] = trait_id
    if gene_id:
        params["gene"] = gene_id
    if species:
        params["species"] = species
    return f"/results?{urlencode(params)}"


def get_all_traits(graph: nx.DiGraph):
    """Return all trait node IDs in the graph."""
    return [nid for nid, data in graph.nodes(data=True) if is_trait_node(data)]


def get_all_trait_gene_pairs(graph: nx.DiGraph):
    """
    Return all trait–gene pairs as (trait_id, trait_name, gene_id, gene_name).
    Here we assume genes are connected to traits via any edge.
    """
    pairs = []
    for trait_id in get_all_traits(graph):
        trait_name = get_node_name(graph, trait_id)
        # check neighbors for genes
        for neighbor in set(graph.predecessors(trait_id)) | set(graph.successors(trait_id)):
            if is_gene_node(graph.nodes[neighbor]):
                pairs.append((trait_id, trait_name, neighbor, get_node_name(graph, neighbor)))
    return pairs

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
def generate_traits_tab(graph: nx.DiGraph, species: str = "all") -> dash_table.DataTable:
    """Create a DataTable listing all traits in the graph, each linking to results."""
    data = [
        {
            "Trait": get_node_name(graph, trait_id),
            "Link": f"[View Results]({make_link(trait_id=trait_id, species=species)})"
        }
        for trait_id in get_all_traits(graph)
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


def generate_trait_gene_tab(graph: nx.DiGraph, species: str = "all") -> dash_table.DataTable:
    """Create a DataTable listing all trait–gene pairs in the graph, each linking to results."""
    pairs = get_all_trait_gene_pairs(graph)
    data = [
        {
            "Trait": trait_name,
            "Gene": gene_name,
            "Link": f"[View Results]({make_link(trait_id=trait_id, gene_id=gene_id, species=species)})"
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
    html.H2("Text2Trait Knowledge Graph Explorer", className="my-4"),
    
    # Species selector
    dbc.Row([
        dbc.Col([
            html.Label("Select Species:", style={"fontWeight": "bold"}),
            dcc.Dropdown(
                id="index-species-dropdown",
                options=AVAILABLE_SPECIES,
                value="all",
                clearable=False,
            ),
        ], width=4)
    ], className="mb-3"),
    
    # Tables
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Traits", tab_id="traits"),
                dbc.Tab(label="Traits & Genes", tab_id="trait_genes"),
            ], id="index-tabs", active_tab="traits"),
            html.Div(id="index-table-content")
        ])
    ])
], fluid=True)


# ───────────────────────────────
# Callbacks
# ───────────────────────────────
@callback(
    Output("index-table-content", "children"),
    Input("index-tabs", "active_tab"),
    Input("index-species-dropdown", "value"),
)
def update_index_tables(active_tab, species):
    """Update the displayed table based on the active tab and selected species."""
    try:
        # Load the appropriate graph based on species
        try:
            graph, _ = load_graph_by_species(species, data_dir)
        except FileNotFoundError:
            # Fall back to default graph if species-specific files don't exist
            graph = G
        
        if active_tab == "traits":
            return generate_traits_tab(graph, species)
        elif active_tab == "trait_genes":
            return generate_trait_gene_tab(graph, species)
    except Exception as e:
        return html.Div(f"Error loading data: {str(e)}", style={"color": "red"})
    
    return html.Div("No data available")