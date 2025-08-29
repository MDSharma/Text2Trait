import json

def is_valid_pair(pair):
    """
    Check if a triplet pair is valid.
    Returns False if any required field is empty or '[NULL]'.
    """
    def safe_str(x):
        return str(x).strip() if isinstance(x, str) else ""
    
    rel = safe_str(pair.get("rel"))
    s_span = safe_str(pair.get("span-s", {}).get("span"))
    s_attr = safe_str(pair.get("span-s", {}).get("attr"))
    e_span = safe_str(pair.get("span-e", {}).get("span"))
    e_attr = safe_str(pair.get("span-e", {}).get("attr"))

    for val in [rel, s_span, s_attr, e_span, e_attr]:
        if val in ["", "[NULL]"]:
            return False
    return True


def filter_invalid_pairs(data):
    """
    Filter out invalid triplet pairs from a list of dicts.
    Returns a new list with only entries containing valid pairs.
    """
    print(f"🔹 Starting filtering: {len(data)} entries to check")
    filtered = []
    total_pairs_before = 0
    total_pairs_after = 0

    for entry in data:
        pairs = entry.get("pairs", [])
        total_pairs_before += len(pairs)
        valid_pairs = [p for p in pairs if is_valid_pair(p)]
        if valid_pairs:
            new_entry = entry.copy()
            new_entry["pairs"] = valid_pairs
            filtered.append(new_entry)
            total_pairs_after += len(valid_pairs)

    print(f"✅ Filtering complete:")
    print(f"   Entries before: {len(data)}, after: {len(filtered)}")
    print(f"   Triplet pairs before: {total_pairs_before}, after: {total_pairs_after}")
    return filtered


def filter_jsonl(input_file, output_file):
    """
    Read JSONL, filter invalid pairs, and write results to new JSONL.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    filtered_data = filter_invalid_pairs(data)

    with open(output_file, "w", encoding="utf-8") as f:
        for entry in filtered_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"🔹 Filtered data written to: {output_file}")