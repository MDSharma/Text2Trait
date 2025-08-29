import json
import os

def append_jsonl(file_path, data):
    """
    Append a list of dicts to a JSON Lines file.
    Each dict is written as one line.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"✅ Appended {len(data)} entries to {file_path}")

def read_jsonl(file_path):
    """
    Read a JSON Lines file into a list of dicts.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def jsonl_to_json_array(jsonl_file, json_file):
    data = read_jsonl(jsonl_file)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Converted JSONL '{jsonl_file}' → JSON array '{json_file}', total entries: {len(data)}")

def merge_jsonl_files(target_file, source_file):
    source_data = read_jsonl(source_file)
    append_jsonl(target_file, source_data)
    print(f"✅ Merged {len(source_data)} entries from '{source_file}' into '{target_file}'")