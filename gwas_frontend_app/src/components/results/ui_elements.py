"""
Gene Table Builders
-------------------

Utilities for constructing Dash Bootstrap tables for:
1. Genes associated with a trait.
2. Detailed NCBI gene information.

These functions return `dbc.Table` objects that can be rendered
directly in a Dash application.
"""

from typing import List, Dict, Optional
from dash import html
import dash_bootstrap_components as dbc


# ───────────────────────────────
# Gene-to-Trait Table
# ───────────────────────────────

def build_gene_table(trait_name: str, matched_genes: List[Dict]) -> dbc.Table:
    """
    Build a Bootstrap table listing genes matched to a trait.

    Args:
        trait_name: Name of the trait.
        matched_genes: List of dicts with gene info. Expected keys:
            - 'gene_name'
            - 'relation_type' (optional)

    Returns:
        A Dash Bootstrap Components Table element.
    """
    return dbc.Table(
        [
            # Table header
            html.Thead(
                html.Tr([
                    html.Th("Gene"),
                    html.Th("Relation"),
                    html.Th("Trait"),
                ])
            ),
            # Table body with one row per matched gene
            html.Tbody([
                html.Tr([
                    html.Td(gene["gene_name"]),
                    html.Td(gene.get("relation_type", "N/A")),
                    html.Td(trait_name),
                ])
                for gene in matched_genes
            ]),
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
    )


# ───────────────────────────────
# NCBI Gene Detail Table
# ───────────────────────────────

def build_ncbi_table(
    matched_genes: List[Dict],
    ncbi_map: Optional[Dict[str, Dict]] = None
) -> dbc.Table:
    """
    Build a Bootstrap table showing detailed NCBI info for matched genes.

    Args:
        matched_genes: List of dicts, each with keys 'gene_id' and 'gene_name'.
        ncbi_map: Optional dict mapping gene_id to detailed NCBI info dict.

    Returns:
        A Dash Bootstrap Components Table element.
    """
    ncbi_map = ncbi_map or {}

    # Table headers
    headers = [
        "Graph Gene", "NCBI Name", "Description", "Chromosome",
        "OtherAliases", "GenomicInfo", "Summary", "Organism"
    ]

    # Build table rows
    rows = []
    for gene in matched_genes:
        gene_id = gene.get("gene_id")
        info = ncbi_map.get(gene_id, {})

        rows.append(html.Tr([
            html.Td(gene.get("gene_name", gene_id)),
            html.Td(info.get("Name", "")),
            html.Td(info.get("Description", "")),
            html.Td(info.get("Chromosome", "")),
            html.Td(info.get("OtherAliases", "")),
            html.Td(info.get("GenomicInfo", "")),
            html.Td(info.get("Summary", "")),
            html.Td(info.get("Organism", "")),
        ]))

    return dbc.Table(
        [
            html.Thead(html.Tr([html.Th(h) for h in headers])),
            html.Tbody(rows),
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        style={"fontSize": "0.85rem"},
    )