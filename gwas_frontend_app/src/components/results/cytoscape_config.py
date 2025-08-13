"""
Cytoscape Layouts
-----------------

Predefined layout configurations for Cytoscape graphs.
Layout parameters:
    - name: Layout algorithm name
    - idealEdgeLength: Preferred length of edges
    - nodeRepulsion: Repulsive force between nodes
    - gravity: Global gravity to pull nodes toward center
    - numIter: Number of iterations to run
    - componentSpacing: Minimum spacing between disconnected components
    - padding: Padding around the graph
"""

from typing import Dict, Any

# ───────────────────────────────
# Cytoscape layout configuration
# ───────────────────────────────

COSE_LAYOUT: Dict[str, Any] = {
    "name": "cose",
    "idealEdgeLength": 150,
    "nodeRepulsion": 800_000,
    "gravity": 80,
    "numIter": 1000,
    "componentSpacing": 100,
    "padding": 50
}