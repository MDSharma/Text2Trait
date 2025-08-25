import json

# Load your dataset
with open("dataset.json", "r") as f:
    data = json.load(f)

nodes = []
edges = []

# Prevent duplicate nodes
node_lookup = {}  # Maps (span, attr) -> node_id
node_counter = 1

# Prevent duplicate edges
edge_lookup = set()  # Stores (source_id, target_id, rel)

def get_node_id(span, attr):
    """
    Return the node_id for a given (span, attr) combination.
    Creates a new node if it doesn't exist yet.
    """
    global node_counter
    key = (span, attr)
    if key in node_lookup:
        return node_lookup[key]

    node_id = f"N{node_counter}"
    node_counter += 1

    node_lookup[key] = node_id
    nodes.append({
        "id": node_id,
        "label": attr,
        "text": span
    })
    return node_id

# Process each sentence and its pairs
for item in data:
    pairs = item.get("pairs", [])
    for pair in pairs:
        span_s = pair["span-s"]
        span_e = pair["span-e"]
        rel = pair["rel"]

        source_id = get_node_id(span_s["span"], span_s["attr"])
        target_id = get_node_id(span_e["span"], span_e["attr"])

        edge_key = (source_id, target_id, rel.upper())
        if edge_key not in edge_lookup:
            edges.append({
                "type": rel.upper(),
                "source": source_id,
                "target": target_id
            })
            edge_lookup.add(edge_key)

# Save nodes and edges
with open("graph_nodes.json", "w") as f:
    json.dump(nodes, f, indent=2)

with open("graph_edges.json", "w") as f:
    json.dump(edges, f, indent=2)

print(f"Generated {len(nodes)} nodes and {len(edges)} edges.")