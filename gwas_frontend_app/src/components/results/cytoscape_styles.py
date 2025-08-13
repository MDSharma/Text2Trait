RELATION_COLORS = {
    "ASSOCIATED_WITH": "#7fb0d6",
    "CAUSES": "#e88b8b",
    "CONTRIBUTES_TO": "#ffc680",
    "ENCODES": "#8fcf8f",
    "HAS_MEASUREMENT": "#c5a6dd",
    "IDENTIFIED_IN": "#c99589",
    "IS_A": "#ef9ed6",
    "LOCATED_IN": "#b0b0b0",
    "NOT_ASSOCIATED_WITH": "#e2e269",
    "PART_OF": "#73d3dd",
    "REGULATES": "#b7d1eb",
    "USED_IN": "#f4a6c8",
    "default": "#cbdbe2",
}

NODE_STYLE = {
    "trait": {
        "background-color": "#67e7da",
        "background-image": "url('/assets/trait_icon.png')",
        "background-fit": "contain",
        "background-clip": "node",
        "background-opacity": 0.6,
        "shape": "ellipse",
        "text-border-color": "#333",
        "text-margin-y": -10,
        "text-halign": "center",
        "text-valign": "top",
    },
    "gene": {
        "background-color": "#2283D3",
        "background-image": "url('/assets/gene_icon.png')",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.6,
        "shape": "ellipse",
    },
}


def build_stylesheet(clicked_edge_id: str = None) -> list:
    """
    Build and return the Cytoscape stylesheet list.

    Args:
        clicked_edge_id: Optional ID of the edge that is clicked, to highlight it.

    Returns:
        List of style dictionaries for Cytoscape.
    """
    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "width": 25,
                "height": 25,
                "font-size": 8,
                "text-valign": "top",
                "text-halign": "center",
                "border-width": 1,
                "border-color": "#000",
            },
        },
        {"selector": ".trait", "style": NODE_STYLE["trait"]},
        {"selector": ".gene", "style": NODE_STYLE["gene"]},
        {
            "selector": "edge",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "font-size": 10,
                "opacity": 0.9,
                "label": "data(label)",
                "text-rotation": "autorotate",
                "text-margin-y": -10,
                "color": "#000",
            },
        },
    ]

    if clicked_edge_id:
        stylesheet.append(
            {
                "selector": f'edge[id = "{clicked_edge_id}"]',
                "style": {
                    "label": "data(hover_label)",
                    "font-weight": "bold",
                    "text-background-color": "#fff",
                    "text-background-opacity": 1,
                    "text-border-opacity": 1,
                    "text-border-color": "#ccc",
                    "text-border-width": 1,
                    "z-index": 999,
                },
            }
        )

    for relation, color in RELATION_COLORS.items():
        stylesheet.append(
            {
                "selector": f".{relation}",
                "style": {
                    "line-color": color,
                    "target-arrow-color": color,
                },
            }
        )

    return stylesheet