import json

nodes = []
edges = []
node_lookup = {}
node_counter = 1
edge_lookup = set()


def get_node_id(span, attr, source=None):
    """
    Get or create a unique node ID for an entity (span + attr).
    Includes optional 'source' field.
    """
    global node_counter
    key = (span, attr)

    if key in node_lookup:
        return node_lookup[key]

    node_id = f"N{node_counter}"
    node_counter += 1
    node_lookup[key] = node_id

    node_data = {
        "id": node_id,
        "label": attr,
        "text": span
    }
    if source:
        node_data["source"] = source

    nodes.append(node_data)
    return node_id


def build_graph_from_dataset(data):
    """
    Build graph nodes and edges from a list of triplet dicts.
    Propagates 'source' from sentence level to relevant nodes.
    """
    global nodes, edges, node_lookup, node_counter, edge_lookup
    nodes = []
    edges = []
    node_lookup = {}
    node_counter = 1
    edge_lookup = set()

    total_edges = 0

    for item in data:
        source_link = item.get("source", None)
        for pair in item.get("pairs", []):
            s = pair["span-s"]
            e = pair["span-e"]
            rel = pair["rel"]

            source_id = get_node_id(s["span"], s["attr"], source=source_link)
            target_id = get_node_id(e["span"], e["attr"], source=source_link)

            edge_key = (source_id, target_id, rel.upper())
            if edge_key not in edge_lookup:
                edges.append({
                    "type": rel.upper(),
                    "source": source_id,
                    "target": target_id
                })
                edge_lookup.add(edge_key)
                total_edges += 1

    print(f"🔹 Graph building complete:")
    print(f"   Nodes created: {len(nodes)}")
    print(f"   Edges created: {total_edges}")

    return nodes, edges


def write_graph(nodes_file, edges_file, nodes_data, edges_data):
    """
    Write nodes and edges to JSON files.
    """
    with open(nodes_file, "w", encoding="utf-8") as f:
        json.dump(nodes_data, f, indent=2)

    with open(edges_file, "w", encoding="utf-8") as f:
        json.dump(edges_data, f, indent=2)

    print(f"🔹 Graph saved: {nodes_file} and {edges_file}")