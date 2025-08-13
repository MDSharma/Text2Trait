from typing import List, Tuple, Dict, Optional
import networkx as nx
from rapidfuzz import process, fuzz

# Relations considered to indicate influence between genes and traits
INFLUENCE_RELATIONS = {"ASSOCIATED_WITH",
                       "CAUSES",
                       "CONTRIBUTES_TO",
                       "ENCODES",
                       "HAS_MEASUREMENT",
                       "IDENTIFIED_IN",
                       "IS_A",
                       "LOCATED_IN",
                       "NOT_ASSOCIATED_WITH",
                       "PART_OF",
                       "REGULATES",
                       "USED_IN"}
# Acceptable labels for trait nodes
TRAIT_LABELS = {"Trait", "Trait / Phenotype"}

def is_trait_node(node_data: dict) -> bool:
    return node_data.get("label") in TRAIT_LABELS

def is_gene_node(node_data: dict) -> bool:
    return node_data.get("label") == "Gene"

def get_trait_name(G: nx.DiGraph, node_id: str) -> str:
    return G.nodes[node_id].get("text", node_id)

def get_gene_name(G: nx.DiGraph, node_id: str) -> str:
    return G.nodes[node_id].get("text", node_id)

def get_all_traits(G: nx.DiGraph) -> List[str]:
    return [n_id for n_id, data in G.nodes(data=True) if is_trait_node(data)]

def get_all_genes(G: nx.DiGraph) -> List[str]:
    return [n_id for n_id, data in G.nodes(data=True) if is_gene_node(data)]

def find_best_traits(
    graph: nx.DiGraph,
    trait_query: str,
    limit: int = 5,
    min_score: int = 70,
    scorer=fuzz.WRatio
) -> List[Tuple[str, float]]:
    trait_nodes = {
        n_id: data["text"]
        for n_id, data in graph.nodes(data=True)
        if is_trait_node(data)
    }

    matches = process.extract(
        query=trait_query,
        choices=trait_nodes,
        scorer=scorer,
        limit=limit
    )

    return [
        (node_id, score)
        for _, score, node_id in matches
        if score >= min_score
    ]

def get_genes_influencing_trait(
    graph: nx.DiGraph,
    trait_query: str,
    gene_query: Optional[str] = None,
    match_limit: int = 1,
    min_score: int = 70,
    scorer=fuzz.WRatio
) -> Optional[Dict]:
    # Resolve trait by ID or fuzzy name match
    if trait_query in graph.nodes and is_trait_node(graph.nodes[trait_query]):
        trait_id = trait_query
    else:
        matches = find_best_traits(graph, trait_query, limit=match_limit, min_score=min_score, scorer=scorer)
        if not matches:
            return None
        trait_id, _ = matches[0]

    trait_name = get_trait_name(graph, trait_id)
    matched_genes = []

    # Check gene → trait
    for gene_id in graph.predecessors(trait_id):
        if is_gene_node(graph.nodes[gene_id]):
            edge_data = graph.get_edge_data(gene_id, trait_id)
            if edge_data.get("type") in INFLUENCE_RELATIONS:
                matched_genes.append({
                    "gene_id": gene_id,
                    "gene_name": get_gene_name(graph, gene_id),
                    "relation_type": edge_data["type"],
                    "direction": "gene → trait"
                })

    # Check trait → gene
    for gene_id in graph.successors(trait_id):
        if is_gene_node(graph.nodes[gene_id]):
            edge_data = graph.get_edge_data(trait_id, gene_id)
            if edge_data.get("type") in INFLUENCE_RELATIONS:
                matched_genes.append({
                    "gene_id": gene_id,
                    "gene_name": get_gene_name(graph, gene_id),
                    "relation_type": edge_data["type"],
                    "direction": "trait → gene"
                })

    # Filter by gene if provided
    if gene_query:
        if not matched_genes:
            return {
                "trait_id": trait_id,
                "trait_name": trait_name,
                "matched_genes": []
            }

        # Direct match by ID
        if gene_query in {g["gene_id"] for g in matched_genes}:
            matched_genes = [g for g in matched_genes if g["gene_id"] == gene_query]
        else:
            # Fuzzy match by name
            gene_dict = {g["gene_id"]: g["gene_name"] for g in matched_genes}
            best_match = process.extractOne(gene_query, gene_dict, scorer=scorer)

            if best_match and best_match[1] >= min_score:
                best_id = best_match[2]
                matched_genes = [g for g in matched_genes if g["gene_id"] == best_id]
            else:
                matched_genes = []

    return {
        "trait_id": trait_id,
        "trait_name": trait_name,
        "matched_genes": matched_genes
    }

def get_all_trait_gene_pairs(G: nx.DiGraph) -> List[Tuple[str, str, str, str]]:
    """
    Returns a list of (trait_id, trait_name, gene_id, gene_name)
    for all trait-gene pairs connected by influence relations.
    """
    pairs = []
    for trait_id in get_all_traits(G):
        trait_name = get_trait_name(G, trait_id)
        result = get_genes_influencing_trait(G, trait_id)
        if result:
            for gene in result["matched_genes"]:
                pairs.append((trait_id, trait_name, gene["gene_id"], gene["gene_name"]))
    return pairs