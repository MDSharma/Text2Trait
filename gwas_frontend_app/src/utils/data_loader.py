"""
Graph Loader (Two-File Version)
-------------------------------

Utility for loading a graph from **two JSON files** (nodes and edges) into a `networkx.DiGraph`.

Expected JSON structure:
- Nodes file:
[
    {"id": str, "label": str, "text": str, ...},
    ...
]
- Edges file:
[
    {"source": str, "target": str, "type": str, ...},
    ...
]

Returns:
    Tuple[nx.DiGraph, dict] → (graph object, combined raw JSON data)
"""

from pathlib import Path
import json
import networkx as nx
from typing import Tuple, Dict, Any, Union


def load_graph(nodes_path: Union[str, Path], edges_path: Union[str, Path]) -> Tuple[nx.DiGraph, Dict[str, Any]]:
    """
    Load a knowledge graph from separate JSON files for nodes and edges.

    Args:
        nodes_path: Path to the JSON file containing nodes.
        edges_path: Path to the JSON file containing edges.

    Returns:
        - nx.DiGraph: A directed graph with nodes and edges loaded from files.
        - dict: Combined raw JSON data in the format {"nodes": [...], "edges": [...]}.

    Raises:
        FileNotFoundError: If either nodes or edges file is missing.
    """
    # Ensure paths are Path objects
    nodes_path = Path(nodes_path)
    edges_path = Path(edges_path)

    # Verify files exist
    if not nodes_path.exists():
        raise FileNotFoundError(f"Nodes file not found: {nodes_path}")
    if not edges_path.exists():
        raise FileNotFoundError(f"Edges file not found: {edges_path}")

    # Load JSON content
    with nodes_path.open("r", encoding="utf-8") as f:
        nodes = json.load(f)

    with edges_path.open("r", encoding="utf-8") as f:
        edges = json.load(f)

    # Combine into a single raw dictionary (like old single-file format)
    raw = {"nodes": nodes, "edges": edges}

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes with attributes
    for node in nodes:
        node_id = node["id"]
        attr = dict(node)
        # Ensure expected keys exist
        attr.setdefault("label", None)
        attr.setdefault("text", None)
        G.add_node(node_id, **attr)

    # Add edges with attributes
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        edge_attr = dict(edge)
        edge_attr.setdefault("type", None)
        # Remove source and target from attributes (they are part of the edge itself)
        edge_attr.pop("source", None)
        edge_attr.pop("target", None)
        G.add_edge(source, target, **edge_attr)

    return G, raw


# ───────────────────────────────
# Script Entry Point (for testing)
# ───────────────────────────────
if __name__ == "__main__":
    # Current script directory
    current_dir = Path(__file__).resolve().parent
    data_dir = current_dir.parent / "data"
    nodes_file = data_dir / "graph_nodes.json"
    edges_file = data_dir / "graph_edges.json"

    # Load graph from two files
    graph, raw_data = load_graph(nodes_file, edges_file)
    print(f"Graph loaded with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
