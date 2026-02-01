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
from typing import Tuple, Dict, Any, Union, Optional


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


def load_graph_by_species(species: str, data_dir: Union[str, Path]) -> Tuple[nx.DiGraph, Dict[str, Any]]:
    """
    Load a knowledge graph for a specific species.
    
    Args:
        species: Species identifier (NCBI taxon ID like "3702", or "all")
        data_dir: Directory containing the data files
        
    Returns:
        - nx.DiGraph: A directed graph with nodes and edges loaded from files.
        - dict: Combined raw JSON data in the format {"nodes": [...], "edges": [...]}.
        
    Raises:
        FileNotFoundError: If either nodes or edges file is missing.
    """
    from utils.species_config import get_species_data_paths
    
    data_dir = Path(data_dir)
    nodes_path, edges_path = get_species_data_paths(species, data_dir)
    
    return load_graph(nodes_path, edges_path)


def load_all_species_graphs(data_dir: Union[str, Path]) -> Tuple[nx.DiGraph, Dict[str, Any], List[str]]:
    """
    Load and merge graphs from all available species.
    
    This function discovers all species-specific data files, loads them,
    and merges them into a single graph. Each node and edge is tagged
    with its species of origin.
    
    Args:
        data_dir: Directory containing the data files
        
    Returns:
        - nx.DiGraph: Combined graph with all species
        - dict: Combined raw JSON data with species metadata
        - list: List of species taxon IDs included in the graph
    """
    from utils.species_config import get_all_available_species, get_species_data_paths
    
    data_dir = Path(data_dir)
    available_species = get_all_available_species(data_dir)
    
    if not available_species:
        # Fall back to default dataset if no species-specific files found
        G, raw = load_graph(
            data_dir / "graph_nodes_dataset.json",
            data_dir / "graph_edges_dataset.json"
        )
        return G, raw, []
    
    # Create combined graph
    combined_graph = nx.DiGraph()
    all_nodes = []
    all_edges = []
    
    for taxon_id in available_species:
        nodes_path, edges_path = get_species_data_paths(taxon_id, data_dir)
        
        try:
            # Load the species-specific graph
            with nodes_path.open("r", encoding="utf-8") as f:
                nodes = json.load(f)
            
            with edges_path.open("r", encoding="utf-8") as f:
                edges = json.load(f)
            
            # Add species metadata to nodes
            for node in nodes:
                node_with_species = dict(node)
                node_with_species["species"] = taxon_id
                node_id = node_with_species["id"]
                
                # Use species-prefixed IDs to avoid conflicts
                species_node_id = f"{taxon_id}_{node_id}"
                node_with_species["id"] = species_node_id
                node_with_species["original_id"] = node_id
                
                # Add node to graph
                combined_graph.add_node(species_node_id, **node_with_species)
                all_nodes.append(node_with_species)
            
            # Add species metadata to edges
            for edge in edges:
                edge_with_species = dict(edge)
                edge_with_species["species"] = taxon_id
                
                # Update source and target to use species-prefixed IDs
                source = f"{taxon_id}_{edge['source']}"
                target = f"{taxon_id}_{edge['target']}"
                
                edge_attr = dict(edge_with_species)
                edge_attr.pop("source", None)
                edge_attr.pop("target", None)
                
                # Add edge to graph
                combined_graph.add_edge(source, target, **edge_attr)
                
                # Store for raw data
                edge_with_species["source"] = source
                edge_with_species["target"] = target
                all_edges.append(edge_with_species)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load species {taxon_id}: {e}")
            continue
    
    raw = {"nodes": all_nodes, "edges": all_edges}
    return combined_graph, raw, available_species


# ───────────────────────────────
# Script Entry Point (for testing)
# ───────────────────────────────
# if __name__ == "__main__":
#     # Current script directory
#     current_dir = Path(__file__).resolve().parent
#     data_dir = current_dir.parent / "data"
#     nodes_file = data_dir / "graph_nodes.json"
#     edges_file = data_dir / "graph_edges.json"

#     # Load graph from two files
#     graph, raw_data = load_graph(nodes_file, edges_file)
#     print(f"Graph loaded with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
