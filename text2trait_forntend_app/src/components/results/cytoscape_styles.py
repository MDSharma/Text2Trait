# ───────────────────────────────
# Relation Colors
# ───────────────────────────────
# Mapping of edge relation types to their respective colors for visualization.
RELATION_COLORS = {
    "is_a": "#ef9ed6",
    "part_of": "#73d3dd",
    "develops_from": "#ffc680",
    "is_related_to": "#7fb0d6",
    "is_not_related_to": "#e2e269",
    "increases": "#8fcf8f",
    "decreases": "#e88b8b",
    "influences": "#b7d1eb",
    "does_not_influence": "#f4a6c8",
    "may_influence": "#cbdbe2",
    "may_not_influence": "#d0d0d0",
    "disrupts": "#c99589",
    "default": "#cbdbe2",
}


# ───────────────────────────────
# Node Style Definitions
# ───────────────────────────────
NODE_STYLE = {
    "trait": {
        "background-color": "#67e7da",
        "background-image": "url('/assets/trait_icon.png')",
        "background-fit": "contain",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
        "text-border-color": "#333",
        "text-margin-y": -10,
        "text-halign": "center",
        "text-valign": "top",
        "text-background-color": "#b3f2d1",
        "text-background-opacity": 0.6,
        "text-border-color": "#67e7da",
        "text-border-width": 1,
        "text-border-opacity": 1,
    },
    "gene": {
        "background-color": "#2283D3",
        "background-image": "url('/assets/gene_icon.png')",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "regulator": {
        "background-color": "#1abc9c",
        "background-image": "url('/assets/regulator_icon.png')",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "variant": {
        "background-color": "#f39c12",
        # "background-image": "url('/assets/variant_icon.png')",
        "background-fit": "contain",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "protein": {
        "background-color": "#8e44ad",
        # "background-image": "url('/assets/protein_icon.png')",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "enzyme": {
        "background-color": "#27ae60",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "qtl": {
        "background-color": "#e67e22",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "coordinates": {
        "background-color": "#34495e",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
    "metabolite": {
        "background-color": "#d35400",
        "background-fit": "cover",
        "background-clip": "node",
        "background-opacity": 0.5,
        "shape": "ellipse",
    },
}

# ───────────────────────────────
# Cytoscape Stylesheet Builder
# ───────────────────────────────
def build_stylesheet(clicked_edge_id: str = None) -> list:
    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "width": 35,
                "height": 35,
                "font-size": 12,
                "text-valign": "top",
                "text-halign": "center",
                "border-width": 1,
                "border-color": "#000",
            },
        },

        # Base edge style (labels hidden)
        {
            "selector": "edge",
            "style": {
                "label": "",
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "font-size": 16,
                "opacity": 0.9,
                "text-rotation": "autorotate",
                "text-margin-y": -10,
                "color": "#000",
            },
        },

        # Show label when edge is clicked/selected
        {
            "selector": "edge:selected",
            "style": {
                "label": "data(label)",
                "text-background-color": "transparent",
                "text-background-opacity": 0,
                "text-border-color": "transparent",
                "text-border-width": 0,
                "text-border-opacity": 0,
                "text-margin-y": -20,
                "z-index": 999,
            },
        }
    ]

    # Optional: emphasize a clicked edge by ID if passed explicitly
    if clicked_edge_id:
        stylesheet.append(
            {
                "selector": f'edge[id = "{clicked_edge_id}"]',
                "style": {
                    "font-weight": "bold",
                    "line-color": "#000",
                    "target-arrow-color": "#000",
                    "z-index": 1000,
                },
            }
        )

    # Relation-specific colors
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

    # Node styles
    for node_type in NODE_STYLE:
        stylesheet.append({"selector": f".{node_type}", "style": NODE_STYLE[node_type]})

    return stylesheet
