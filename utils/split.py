import json
import random
import os

def split_json(input_file, output_dir, train_ratio=0.7, dev_ratio=0.2, test_ratio=0.1, seed=42):
    # Ensure ratios sum to 1
    assert abs((train_ratio + dev_ratio + test_ratio) - 1.0) < 1e-6, "Ratios must sum to 1"

    # Load data
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Shuffle for randomness (seed for reproducibility)
    random.seed(seed)
    random.shuffle(data)

    # Compute split sizes
    n = len(data)
    train_end = int(n * train_ratio)
    dev_end = train_end + int(n * dev_ratio)

    train_data = data[:train_end]
    dev_data = data[train_end:dev_end]
    test_data = data[dev_end:]

    # Make sure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Save splits
    with open(os.path.join(output_dir, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=4, ensure_ascii=False)

    with open(os.path.join(output_dir, "dev.json"), "w", encoding="utf-8") as f:
        json.dump(dev_data, f, indent=4, ensure_ascii=False)

    with open(os.path.join(output_dir, "test.json"), "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Done! Wrote {len(train_data)} train, {len(dev_data)} dev, {len(test_data)} test examples.")


# Example usage:
split_json("dataset/dataset.json", "dataset/")
