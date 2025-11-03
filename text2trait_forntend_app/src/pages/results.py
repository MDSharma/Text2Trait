"""
Results Page – Text2Trait
--------------------------

This page displays the Text2Trait results, including a trait-gene interaction 
graph using Cytoscape, interactive tables for matched genes, and a side panel 
for detailed gene information retrieved from NCBI.
"""

import os
from pathlib import Path
from urllib.parse import parse_qs

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from utils.data_loader import load_graph
from utils.search_utils import get_connected_subgraph, resolve_trait_and_genes, is_gene_node, is_trait_node, get_node_name
from utils.search_NCBI import set_email, fetch_multiple_nodes_info
from components.results.cytoscape_config import COSE_LAYOUT
from components.results.cytoscape_styles import build_stylesheet, RELATION_COLORS
from components.results.layout_styles import (
    GRAPH_CONTAINER_STYLE, TOOLBAR_STYLE, BUTTON_FIXED_HEIGHT_STYLE,
    SIDE_BUTTON_STYLE, SIDE_PANEL_STYLE, SIDE_PANEL_EXPANDED_STYLE,
    TABLE_CONTAINER_STYLE, TABLE_CONTAINER_EXPANDED_STYLE,
)
from components.results.ui_elements import build_gene_table, build_ncbi_table

# ───────────────────────────────
# NCBI Configuration
# ───────────────────────────────
# Ensure Entrez email is set for NCBI API usage
set_email(os.getenv("ENTREZ_EMAIL", "your.email@example.com"))

# ───────────────────────────────
# Page Registration
# ───────────────────────────────
dash.register_page(
    __name__,
    path="/results",
    name="Results",
    title="Text2Trait Results"
)

# ───────────────────────────────
# Load Graph Data
# ───────────────────────────────
script_dir = Path(__file__).resolve().parent
node_json_path = script_dir.parent / "data" / "graph_nodes_dataset.json"
edge_json_path = script_dir.parent / "data" / "graph_edges_dataset.json"
G, _ = load_graph(node_json_path, edge_json_path)


# ───────────────────────────────
# Cytoscape Elements Builder
# ───────────────────────────────
def build_cytoscape_elements(subgraph: dict, relation_colors: dict):
    """
    Build Cytoscape elements from a subgraph dict with 'nodes' and 'edges'.
    """
    elements = []

    # Nodes
    for node in subgraph["nodes"]:
        node_type = node["label"].lower()
        elements.append({
            "data": {
                "id": node["id"],
                "label": node["text"],
                "node_type": node_type,
                "source": node.get("source", "")
            },
            "classes": node_type
        })

    # Edges
    for edge in subgraph["edges"]:
        # Normalize the relation type: lowercase, strip spaces, replace spaces with underscore
        relation_class = str(edge.get("type", "")).strip().lower().replace(" ", "_")
        if relation_class not in relation_colors:
            relation_class = "default"

        edge_id = f"{edge['source']}_{edge['target']}_{relation_class}"
        label = (edge.get("type") or "N/A").replace("_", " ").capitalize()

        elements.append({
            "data": {
                "id": edge_id,
                "source": edge["source"],
                "target": edge["target"],
                "relation_type": edge.get("type", "N/A"),
                "label": label,
            },
            "classes": relation_class
        })

    return elements

# ───────────────────────────────
# Page Layout
# ───────────────────────────────
layout = html.Div([

    # URL & State Stores
    dcc.Location(id="url"),
    dcc.Store(id="cyto-elements-store"),
    dcc.Store(id="table-visible", data=False),
    dcc.Store(id="side-panel-visible", data=False),
    dcc.Store(id="ncbi-store", data={}),
    dcc.Store(id="graph-loaded", data=False),
    dcc.Store(id="timer-done", data=False),
    dcc.Interval(id="loading-timer", interval=2000, n_intervals=0, max_intervals=1),

    # ──────────────── Loading Modal ────────────────
    dbc.Modal(
        [
            dbc.ModalBody(
                html.Div([
                    dbc.Spinner(size="lg", color="primary", type="border"),
                    html.Div(
                        "Loading the network...",
                        style={"marginTop": "10px", "fontWeight": "bold"}
                    )
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "height": "100%",
                    "textAlign": "center"
                })
            )
        ],
        id="loading-modal",
        is_open=True,
        backdrop=True,
        centered=True,
        keyboard=False,
        fullscreen=True
    ),

    # ──────────────── Toolbar ────────────────
    dbc.Card(
        dbc.CardBody(
            dbc.Row([
                dbc.Col(dbc.Button(
                    ["Reset ", html.I(className="bi bi-arrow-clockwise")],
                    id="reset-graph", color="primary", size="sm",
                    className="w-100", style=BUTTON_FIXED_HEIGHT_STYLE
                ), width=2),

                dbc.Col(dbc.Button(
                    ["Zoom ", html.I(className="bi bi-zoom-in")],
                    id="zoom-in", size="sm", className="w-100", style=BUTTON_FIXED_HEIGHT_STYLE
                ), width=2),

                dbc.Col(dbc.Button(
                    ["Zoom ", html.I(className="bi bi-zoom-out")],
                    id="zoom-out", size="sm", className="w-100", style=BUTTON_FIXED_HEIGHT_STYLE
                ), width=2),

                dbc.Col(dbc.Button(
                    "Show Table", id="toggle-table", size="sm",
                    className="w-100", style=BUTTON_FIXED_HEIGHT_STYLE
                ), width=3),

                dbc.Col(dbc.Button(
                    "Download PNG", id="download-png", color="success", size="sm",
                    className="w-100", style=BUTTON_FIXED_HEIGHT_STYLE
                ), width=3),
            ], className="g-2")
        ),
        className="mt-2 mb-2 pb-2",
        style=TOOLBAR_STYLE
    ),

    # ──────────────── Graph & Side Panels ────────────────
    html.Div([

        # Graph & Table Container
        html.Div([
            cyto.Cytoscape(
                id="graph-output",
                layout=COSE_LAYOUT,
                style={"width": "100%", "height": "100%"},
                elements=[],
                stylesheet=build_stylesheet(),
                userZoomingEnabled=True,
                userPanningEnabled=True,
                minZoom=0.3,
                maxZoom=2.5,
                zoom=1.4,
                tapEdgeData=True
            ),

            html.Div([
                dbc.Tabs([
                    dbc.Tab(label="Trait Matches", tab_id="trait_matches"),
                    dbc.Tab(label="Gene Descriptions", tab_id="gene_descriptions"),
                ], id="table-tab-selector", active_tab="trait_matches"),
                html.Div(id="table-content")
            ], id="gene-table-container", style=TABLE_CONTAINER_STYLE)
        ], style=GRAPH_CONTAINER_STYLE),

        # Side Panel
        html.Div([
            dbc.Button("Quick info", id="toggle-side-panel", size="sm", style=SIDE_BUTTON_STYLE),

            html.Div([
                dbc.Button("\u00d7", id="close-side-panel", size="sm"),
                html.Div(id="side-panel-inner-content", style={"paddingTop": "15px"})
            ], id="side-panel-content", style={"position": "relative", "height": "100%", "width": "100%"})
        ], id="side-panel", style=SIDE_PANEL_STYLE)

    ], style={"display": "flex", "position": "relative", "height": "100%"})
])



# ───────────────────────────────
# Callbacks
# ───────────────────────────────
# Timer completion callback
@callback(
    Output("timer-done", "data"),
    Input("loading-timer", "n_intervals"),
    prevent_initial_call=True
)
def finish_timer(_):
    """Mark the loading timer as done after the interval."""
    return True


# Loading modal visibility callback
@callback(
    Output("loading-modal", "is_open"),
    Input("graph-loaded", "data"),
    Input("timer-done", "data")
)
def update_modal(graph_loaded, timer_done):
    """
    Keep the loading modal open until both the graph is loaded
    and the loading timer has completed.
    """
    return not (graph_loaded and timer_done)


@callback(
    Output("cyto-elements-store", "data"),
    Output("graph-output", "elements"),
    Output("graph-output", "stylesheet"),
    Output("graph-loaded", "data"),
    Input("url", "search"),
    prevent_initial_call=True
)
def load_graph_elements(search):
    if not search:
        return [], [], build_stylesheet(), True

    try:
        params = parse_qs(search[1:])
        trait = params.get("trait", [None])[0]
        gene = params.get("gene", [None])[0]

        if not trait:
            return [], [], build_stylesheet(), True

        result = resolve_trait_and_genes(G, trait, gene)
        if not result:
            return [], [], build_stylesheet(), True

        focus_nodes = [result["trait_id"]] + [g["gene_id"] for g in result["matched_genes"]]

        subgraph = get_connected_subgraph(G, focus_nodes)
        elements = build_cytoscape_elements(subgraph, RELATION_COLORS)

        all_displayed_nodes = []
        for n in subgraph["nodes"]:
            node_id = n["id"]
            node_data = G.nodes[node_id]
            label = node_data.get("label", "unknown")

            if is_gene_node(node_data):
                node_type = "gene"
                node_name = get_node_name(G, node_id)
            elif label.lower() == "protein":
                node_type = "protein"
                node_name = node_data.get("text", node_id)
            elif is_trait_node(node_data):
                node_type = "trait"
                node_name = get_node_name(G, node_id)
            else:
                node_type = "other"
                node_name = node_data.get("text", node_id)

            all_displayed_nodes.append({
                "id": node_id,
                "name": node_name,
                "type": node_type
            })

        return {
            "elements": elements,
            "matched_genes": result["matched_genes"],
            "all_displayed_nodes": all_displayed_nodes,
            "trait_id": result["trait_id"],
            "trait_name": result["trait_name"]
        }, elements, build_stylesheet(), True

    except Exception as e:
        print("Error in load_graph_elements:", e)
        return [], [], build_stylesheet(), True


@callback(
    Output("ncbi-store", "data"),
    Input("cyto-elements-store", "data"),
    prevent_initial_call=True
)
def fetch_ncbi_data(data):
    if not data:
        return {}

    nodes_to_fetch = []

    for g in data.get("matched_genes", []):
        nodes_to_fetch.append({
            "name": g.get("gene_name"),
            "type": "gene",
            "id": g.get("gene_id")
        })

    for n in data.get("all_displayed_nodes", []):
        node_type = n.get("type")
        node_id = n.get("id")
        node_name = n.get("name")

        if any(nf["id"] == node_id and nf["type"] == node_type for nf in nodes_to_fetch):
            continue


        if node_type in {"gene", "protein"}:
            nodes_to_fetch.append({
                "name": node_name,
                "type": node_type,
                "id": node_id
            })
    if not nodes_to_fetch:
        return {}

    try:
        ncbi_results = fetch_multiple_nodes_info(nodes_to_fetch)
        ncbi_map = {info["_key"]: info for info in ncbi_results}
        return ncbi_map

    except Exception as e:
        print("Error fetching NCBI data:", e)
        return {}


# Zoom in/out callback
@callback(
    Output("graph-output", "zoom"),
    Input("zoom-in", "n_clicks"),
    Input("zoom-out", "n_clicks"),
    State("graph-output", "zoom"),
    prevent_initial_call=True
)
def zoom_graph(zoom_in_clicks, zoom_out_clicks, current_zoom):
    """Adjust the Cytoscape graph zoom level based on user clicks."""
    triggered_id = dash.callback_context.triggered_id
    if triggered_id == "zoom-in":
        return min(current_zoom + 0.2, 2.5)
    elif triggered_id == "zoom-out":
        return max(current_zoom - 0.2, 0.3)
    return current_zoom


# Graph PNG download callback
@callback(
    Output("graph-output", "generateImage"),
    Input("download-png", "n_clicks"),
    prevent_initial_call=True
)
def download_graph(n_clicks):
    """Trigger download of the current Cytoscape graph as PNG."""
    return {"type": "png", "action": "download"}


# Toggle table visibility callback
@callback(
    Output("table-visible", "data"),
    Output("toggle-table", "children"),
    Input("toggle-table", "n_clicks"),
    State("table-visible", "data"),
    prevent_initial_call=True
)
def toggle_table(n_clicks, currently_visible):
    """Show or hide the gene table and update button label."""
    return (False, "Show Table") if currently_visible else (True, "Hide Table")


# Side panel toggle and content update callback
@callback(
    Output("side-panel", "style"),
    Output("toggle-side-panel", "style"),
    Output("side-panel-visible", "data"),
    Output("side-panel-inner-content", "children"),
    Input("toggle-side-panel", "n_clicks"),
    Input("close-side-panel", "n_clicks"),
    Input("graph-output", "tapNodeData"),
    State("side-panel-visible", "data"),
    State("ncbi-store", "data"),
    prevent_initial_call=True
)
def toggle_side_panel(toggle_clicks, close_clicks, tap_node_data, is_visible, ncbi_store):
    """
    Manage side panel state: toggle visibility and update content when a node is clicked.
    Does NOT open for 'trait' nodes.
    Shows entity type at the top, paper link if available, and info for supported node types.
    """
    ctx = dash.callback_context.triggered_id
    base_button_style = SIDE_BUTTON_STYLE

    # Node tapped in graph
    if ctx == "graph-output" and tap_node_data:

        node_type = tap_node_data.get("node_type", "")
        node_id = tap_node_data.get("id")
        source_link = tap_node_data.get("source", "")

        # Do NOT open side panel for traits
        if node_type == "trait":
            return SIDE_PANEL_STYLE, base_button_style, False, ""

        # Look up info from ncbi_store (if available)
        info = (ncbi_store or {}).get(f"{node_type}:{node_id}", {})

        # Default content: show entity type at top
        content_children = [
            html.H5(f"{node_type.capitalize()}"),
            html.Hr(),
        ]

        # Build content depending on node type
        if node_type == "gene":
            gene_fields = ["Description", "Chromosome", "OtherAliases", "GenomicInfo", "Summary", "Organism"]
            if all(not info.get(f, "").strip() for f in gene_fields):
                content_children += [html.P("Information will be added soon.")]
            else:
                content_children += [
                    html.P([html.Strong("Description: "), html.Span(info.get("Description", ""))]),
                    html.P([html.Strong("Chromosome: "), html.Span(info.get("Chromosome", ""))]),
                    html.P([html.Strong("Other Aliases: "), html.Span(info.get("OtherAliases", ""))]),
                    html.P([html.Strong("Genomic Info: "), html.Span(info.get("GenomicInfo", ""))]),
                    html.P([html.Strong("Summary: "), html.Span(info.get("Summary", ""))]),
                    html.P([html.Strong("Organism: "), html.Span(info.get("Organism", ""))]),
                ]
        elif node_type == "protein":
            protein_fields = ["AccessionVersion", "Organism", "SequenceLength", "Description"]
            if all(not str(info.get(f, "")).strip() for f in protein_fields):
                content_children += [html.P("Information will be added soon.")]
            else:
                content_children += [
                    html.P([html.Strong("AccessionVersion: "), html.Span(info.get("AccessionVersion", ""))]),
                    html.P([html.Strong("Description: "), html.Span(info.get("Description", ""))]),
                    html.P([html.Strong("Sequence Length: "), html.Span(info.get("SequenceLength", ""))]),
                ]
        else:
            content_children += [html.P("Information will be added soon.")]

        # Always append the paper link (if available)
        if source_link:
            content_children += [
                html.Hr(),
                html.P([
                    html.Strong("Source: "),
                    html.A("View Paper", href=source_link, target="_blank", style={"color": "blue"})
                ])
            ]

        return SIDE_PANEL_EXPANDED_STYLE, {**base_button_style, "display": "none"}, True, html.Div(
            content_children, style={"padding": "10px", "maxHeight": "85vh", "overflowY": "auto"}
        )

    # Toggle button clicked
    if ctx == "toggle-side-panel":
        if not is_visible:
            return SIDE_PANEL_EXPANDED_STYLE, {**base_button_style, "display": "none"}, True, html.Div([
                html.H5("Currently empty..."),
                html.P("Click a node to see more details.")
            ], style={"padding": "10px"})
        else:
            return SIDE_PANEL_STYLE, base_button_style, False, ""

    # Close button clicked
    if ctx == "close-side-panel" and is_visible:
        return SIDE_PANEL_STYLE, base_button_style, False, ""

    return SIDE_PANEL_STYLE, base_button_style, False, ""


# Sync table container style with side panel visibility
@callback(
    Output("gene-table-container", "style"),
    Input("side-panel-visible", "data"),
    Input("table-visible", "data"),
    prevent_initial_call=True
)
def sync_table_style(side_panel_visible, table_visible):
    """Adjust gene table container style dynamically based on side panel and table visibility."""
    style = TABLE_CONTAINER_STYLE.copy()
    if table_visible:
        if side_panel_visible:
            style.update(TABLE_CONTAINER_EXPANDED_STYLE)
        else:
            style.update({
                "marginRight": "0",
                "width": "100%",
                "height": "300px",
                "padding": "10px",
            })
    else:
        style.update({
            "height": "0px",
            "padding": "0px",
            "width": "100%",
            "marginRight": "0",
        })
    return style


# Update table content based on active tab
@callback(
    Output("table-content", "children"),
    Input("table-tab-selector", "active_tab"),
    Input("table-visible", "data"),
    Input("cyto-elements-store", "data"),
    State("url", "search"),
    State("ncbi-store", "data"),
    prevent_initial_call=True
)
def update_table(tab, table_visible, elements_data, search, ncbi_store):
    """
    Render gene table or gene descriptions depending on the selected tab,
    table visibility, and available data. Only genes connected to the trait
    are displayed in the bottom table. Variants and proteins are not shown here.
    """
    if not table_visible or not elements_data or not search:
        return ""

    elements = elements_data.get("elements", []) if isinstance(elements_data, dict) else []
    trait_name = elements_data.get("trait_name") if isinstance(elements_data, dict) else None
    trait_id = elements_data.get("trait_id") if isinstance(elements_data, dict) else None

    if not trait_id:
        return ""

    # Only consider edges pointing to the trait
    gene_relations = {
        el["data"]["source"]: el["data"].get("relation_type", "N/A")
        for el in elements
        if el.get("data", {}).get("target") == trait_id
    }

    # Include only genes connected to the trait
    matched_genes = [
        {
            "gene_id": el["data"]["id"],
            "gene_name": el["data"]["label"],
            "relation_type": gene_relations.get(el["data"]["id"], "N/A")
        }
        for el in elements
        if el.get("classes") == "gene" and el["data"]["id"] in gene_relations
    ]

    if tab == "trait_matches" and trait_name:
        return build_gene_table(trait_name, matched_genes)
    elif tab == "gene_descriptions":
        if not ncbi_store:
            return html.Div("Loading gene descriptions...", style={"fontStyle": "italic"})
        return build_ncbi_table(matched_genes, ncbi_store, node_type="gene")

    return ""