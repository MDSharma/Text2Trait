from pathlib import Path
import json
import networkx as nx
from typing import Tuple, Dict, Any, Union

def load_graph(json_path: Union[str, Path]) -> Tuple[nx.DiGraph, Dict[str, Any]]:
    """
    Load a graph from a JSON file and return a NetworkX DiGraph plus raw data.
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found at: {json_path}")

    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    G = nx.DiGraph()

    for node in raw.get("nodes", []):
        node_id = node["id"]
        G.add_node(node_id,
                   label=node.get("label"),
                   text=node.get("text"))

    for edge in raw.get("edges", []):
        src = edge["source"]
        tgt = edge["target"]
        etype = edge.get("type")
        G.add_edge(src, tgt, type=etype)

    return G, raw


if __name__ == "__main__":
    # Smoke-test: load from relative path
    current_dir = Path(__file__).resolve().parent
    json_path = current_dir / "data" / "gwas_kg.json"
    if not json_path.exists():
      raise FileNotFoundError(f"File not found: {json_path}")

    graph, data = load_graph(json_path)
    print(f"Loaded graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")

    # print one example:
    example_node = next(iter(graph.nodes(data=True)))
    print("Example node:", example_node)
    example_edge = next(iter(graph.edges(data=True)))
    print("Example edge:", example_edge)
