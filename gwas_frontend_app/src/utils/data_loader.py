"""
Graph Loader
------------

Utility for loading a graph from a JSON file into a `networkx.DiGraph`.

Expected JSON structure:
{
    "nodes": [
        {"id": str, "label": str, "text": str, ...},
        ...
    ],
    "edges": [
        {"source": str, "target": str, "type": str, ...},
        ...
    ]
}

Returns:
    Tuple[nx.DiGraph, dict] → (graph object, raw JSON data)
"""

from pathlib import Path
import json
import networkx as nx
from typing import Tuple, Dict, Any, Union


# ───────────────────────────────
# Loading utility
# ───────────────────────────────

def load_graph(json_path: Union[str, Path]) -> Tuple[nx.DiGraph, Dict[str, Any]]:
    """
    Load a graph from a JSON file.

    Args:
        json_path: Path to the JSON file.

    Returns:
        A tuple:
            - NetworkX directed graph (`nx.DiGraph`)
            - Raw JSON data as a dictionary

    Raises:
        FileNotFoundError: If the provided path does not exist.
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found at: {json_path}")

    # Load raw JSON
    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes with attributes
    for node in raw.get("nodes", []):
        G.add_node(
            node["id"],
            label=node.get("label"),
            text=node.get("text")
        )

    # Add edges with type attribute
    for edge in raw.get("edges", []):
        G.add_edge(
            edge["source"],
            edge["target"],
            type=edge.get("type")
        )

    return G, raw


# ───────────────────────────────
# Script Entry Point (for testing)
# ───────────────────────────────

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    json_path = current_dir / "data" / "initial_arabiodopsis_kg.json"

    if not json_path.exists():
        raise FileNotFoundError(f"File not found: {json_path}")

    graph, data = load_graph(json_path)
    print(f"Loaded graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")

    # Print one example node and edge
    example_node = next(iter(graph.nodes(data=True)))
    print("Example node:", example_node)

    example_edge = next(iter(graph.edges(data=True)))
    print("Example edge:", example_edge)