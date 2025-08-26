import json

# Load JSON data from a file
with open("test_predictions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def is_valid_pair(pair):
    # Extract all relevant fields
    rel = pair.get("rel", "").strip()
    s_span = pair.get("span-s", {}).get("span", "").strip()
    s_attr = pair.get("span-s", {}).get("attr", "").strip()
    e_span = pair.get("span-e", {}).get("span", "").strip()
    e_attr = pair.get("span-e", {}).get("attr", "").strip()
    
    # Check for empty or "[NULL]" values
    if not rel or rel == "[NULL]":
        return False
    if not s_span or s_span == "[NULL]":
        return False
    if not s_attr or s_attr == "[NULL]":
        return False
    if not e_span or e_span == "[NULL]":
        return False
    if not e_attr or e_attr == "[NULL]":
        return False
    
    return True

# Filter data
filtered_data = []
for entry in data:
    valid_pairs = [p for p in entry.get("pairs", []) if is_valid_pair(p)]
    if valid_pairs:  # keep entry only if it has valid pairs
        new_entry = entry.copy()
        new_entry["pairs"] = valid_pairs
        filtered_data.append(new_entry)

# Save filtered data to a new JSON file
with open("filtered_test_predictions.json", "w", encoding="utf-8") as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=4)

print(f"Filtered {len(data)} entries down to {len(filtered_data)} entries.")