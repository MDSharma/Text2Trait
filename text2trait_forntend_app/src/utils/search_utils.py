"""
Search & Subgraph Utilities
---------------------------

Provides:
    - Fuzzy search for traits (and optionally genes).
    - Expansion: return all connected nodes + edges (all relations).
    - Helpers to convert into Cytoscape elements.
"""

from typing import List, Tuple, Dict, Optional
import networkx as nx
from rapidfuzz import process, fuzz


# ───────────────────────────────
# Node Type Checks
# ───────────────────────────────

def is_trait_node(node_data: dict) -> bool:
    return node_data.get("label") in {"Trait", "Trait / Phenotype"}


def is_gene_node(node_data: dict) -> bool:
    return node_data.get("label") == "Gene"


# ───────────────────────────────
# Name Helpers
# ───────────────────────────────

def get_node_name(G: nx.DiGraph, node_id: str) -> str:
    return G.nodes[node_id].get("text", node_id)


# ───────────────────────────────
# Fuzzy Matching
# ───────────────────────────────

def find_best_traits(
    graph: nx.DiGraph,
    trait_query: str,
    limit: int = 5,
    min_score: int = 70,
    scorer=fuzz.WRatio
) -> List[Tuple[str, float]]:
    """Fuzzy match trait nodes by text."""
    trait_nodes = {
        n_id: data.get("text", n_id)
        for n_id, data in graph.nodes(data=True)
        if is_trait_node(data)
    }

    matches = process.extract(
        query=trait_query,
        choices=trait_nodes,
        scorer=scorer,
        limit=limit
    )

    return [(node_id, score) for _, score, node_id in matches if score >= min_score]


# ───────────────────────────────
# Trait + Gene Resolution
# ───────────────────────────────

def resolve_trait_and_genes(
    graph: nx.DiGraph,
    trait_query: str,
    gene_query: Optional[str] = None,
    min_score: int = 70
) -> Optional[Dict]:
    """
    Resolve trait (fuzzy) and optionally filter to a specific gene.
    Returns:
        {
            "trait_id": str,
            "trait_name": str,
            "matched_genes": [ { "gene_id": str, "gene_name": str } ]
        }
    """
    # Find trait
    if trait_query in graph.nodes and is_trait_node(graph.nodes[trait_query]):
        trait_id = trait_query
    else:
        matches = find_best_traits(graph, trait_query, min_score=min_score)
        if not matches:
            return None
        trait_id, _ = matches[0]

    trait_name = get_node_name(graph, trait_id)

    # Find all connected genes
    candidate_genes = []
    for neighbor in set(graph.predecessors(trait_id)) | set(graph.successors(trait_id)):
        if is_gene_node(graph.nodes[neighbor]):
            candidate_genes.append({
                "gene_id": neighbor,
                "gene_name": get_node_name(graph, neighbor)
            })

    # Filter if gene_query provided
    matched_genes = candidate_genes
    if gene_query and candidate_genes:
        # Direct match by ID
        if gene_query in {g["gene_id"] for g in candidate_genes}:
            matched_genes = [g for g in candidate_genes if g["gene_id"] == gene_query]
        else:
            # Fuzzy match by gene name
            gene_dict = {g["gene_id"]: g["gene_name"] for g in candidate_genes}
            best_match = process.extractOne(gene_query, gene_dict, scorer=fuzz.WRatio)
            if best_match and best_match[1] >= min_score:
                best_id = best_match[2]
                matched_genes = [g for g in candidate_genes if g["gene_id"] == best_id]
            else:
                matched_genes = []

    return {
        "trait_id": trait_id,
        "trait_name": trait_name,
        "matched_genes": matched_genes
    }


# ───────────────────────────────
# Subgraph Expansion (ALL relations)
# ───────────────────────────────

def get_connected_subgraph(graph: nx.DiGraph, focus_nodes: List[str]) -> Dict[str, list]:
    """
    Return all nodes + edges connected to the focus nodes (trait + matched genes).
    Includes ALL relation types.
    """
    connected_nodes = set(focus_nodes)
    connected_edges = []

    for n in focus_nodes:
        for neighbor in graph.successors(n):
            connected_nodes.add(neighbor)
            connected_edges.append((n, neighbor, graph.get_edge_data(n, neighbor)))
        for neighbor in graph.predecessors(n):
            connected_nodes.add(neighbor)
            connected_edges.append((neighbor, n, graph.get_edge_data(neighbor, n)))

    # Build dict
    nodes_data = [
        {
            "id": nid,
            "label": graph.nodes[nid].get("label", "unknown"),
            "text": get_node_name(graph, nid),
            "source": graph.nodes[nid].get("source", "")
        }
        for nid in connected_nodes
    ]
    edges_data = [
        {"source": src, "target": tgt, **(edata or {})}
        for src, tgt, edata in connected_edges
    ]

    return {"nodes": nodes_data, "edges": edges_data}