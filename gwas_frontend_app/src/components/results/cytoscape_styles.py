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
# Predefined styles for different node types in the Cytoscape graph.
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
        "background-opacity": 0.6,
        "shape": "ellipse",
    },
}

# ───────────────────────────────
# Cytoscape Stylesheet Builder
# ───────────────────────────────
# Constructs a list of style dictionaries for nodes and edges.
# Optionally highlights a clicked edge by its ID.
# def build_stylesheet(clicked_edge_id: str = None) -> list:
#     """
#     Build and return the Cytoscape stylesheet list.

#     Args:
#         clicked_edge_id: Optional ID of the edge that is clicked, to highlight it.

#     Returns:
#         List of style dictionaries for Cytoscape.
#     """
#     # Base node styles
#     stylesheet = [
#         {"selector": ".trait", "style": NODE_STYLE["trait"]},  # Trait-specific style
#         {"selector": ".gene", "style": NODE_STYLE["gene"]},    # Gene-specific style
#         {
#             "selector": "node",
#             "style": {
#                 "label": "data(label)",
#                 "width": 35,
#                 "height": 35,
#                 "font-size": 12,
#                 "text-valign": "top",
#                 "text-halign": "center",
#                 "border-width": 1,
#                 "border-color": "#000",
#             },
#         },
#         # Base edge style
#         {
#             "selector": "edge",
#             "style": {
#                 # "label": "data(label)",
#                 "curve-style": "bezier",
#                 "target-arrow-shape": "triangle",
#                 "font-size": 16,
#                 "opacity": 0.9,
#                 "text-rotation": "autorotate",
#                 "text-margin-y": -10,
#                 "color": "#000",
#             },
#         },
#     ]

#     # Highlight clicked edge if provided
#     if clicked_edge_id:
#         stylesheet.append(
#             {
#                 "selector": f'edge[id = "{clicked_edge_id}"]',
#                 "style": {
#                     # "label": "data(label)",
#                     "font-weight": "bold",
#                     "text-background-color": "#fff",
#                     "text-background-opacity": 1,
#                     "text-border-opacity": 1,
#                     "text-border-color": "#ccc",
#                     "text-border-width": 1,
#                     "z-index": 999,
#                 },
#             }
#         )

#     # Apply colors for different relation types
#     for relation, color in RELATION_COLORS.items():
#         stylesheet.append(
#             {
#                 "selector": f".{relation}",
#                 "style": {
#                     "line-color": color,
#                     "target-arrow-color": color,
#                 },
#             }
#         )

#     return stylesheet

def build_stylesheet(clicked_edge_id: str = None) -> list:
    stylesheet = [
        # Node styles
        {"selector": ".trait", "style": NODE_STYLE["trait"]},
        {"selector": ".gene", "style": NODE_STYLE["gene"]},
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

    return stylesheet
