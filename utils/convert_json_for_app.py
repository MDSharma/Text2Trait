import json

# -------------------------
# Load dataset
# -------------------------
with open("dataset.json", "r") as f:
    data = json.load(f)

# Lists for storing graph structure
nodes = []   # all unique entities (span + attr)
edges = []   # all unique relations between entities

# -------------------------
# Helper structures
# -------------------------
node_lookup = {}   # (span, attr) -> node_id (ensures unique nodes)
node_counter = 1   # counter for generating node IDs like N1, N2...

edge_lookup = set()  # (source_id, target_id, rel) (ensures unique edges)


def get_node_id(span, attr):
    """
    Get or create a node ID for a (span, attr) entity.
    
    Args:
        span (str): The text of the entity (e.g., "BRCA1").
        attr (str): The attribute/type of the entity (e.g., "Gene").
    
    Returns:
        str: The node_id (e.g., "N1").
    """
    global node_counter
    key = (span, attr)

    # If this node already exists, return its ID
    if key in node_lookup:
        return node_lookup[key]

    # Otherwise, create a new node
    node_id = f"N{node_counter}"
    node_counter += 1

    node_lookup[key] = node_id
    nodes.append({
        "id": node_id,     # unique identifier
        "label": attr,     # type/category (from attr)
        "text": span       # actual entity text
    })
    return node_id


# -------------------------
# Build graph from dataset
# -------------------------
for item in data:
    pairs = item.get("pairs", [])  # get relation pairs for this sentence

    for pair in pairs:
        span_s = pair["span-s"]   # subject entity
        span_e = pair["span-e"]   # object entity
        rel = pair["rel"]         # relation type

        # Get or create node IDs for subject & object
        source_id = get_node_id(span_s["span"], span_s["attr"])
        target_id = get_node_id(span_e["span"], span_e["attr"])

        # Ensure each edge (source, target, relation) is unique
        edge_key = (source_id, target_id, rel.upper())
        if edge_key not in edge_lookup:
            edges.append({
                "type": rel.upper(),   # relation type (in uppercase for consistency)
                "source": source_id,   # from subject
                "target": target_id    # to object
            })
            edge_lookup.add(edge_key)


# -------------------------
# Run script
# -------------------------
with open("graph_nodes.json", "w") as f:
    json.dump(nodes, f, indent=2)

with open("graph_edges.json", "w") as f:
    json.dump(edges, f, indent=2)

print(f"✅ Generated {len(nodes)} nodes and {len(edges)} edges.")