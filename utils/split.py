import json
import random
import os


def split_json(input_file, output_dir, train_ratio=0.7, dev_ratio=0.2, test_ratio=0.1, seed=42):
    """
    Split a JSON dataset into train/dev/test subsets.
    
    Args:
        input_file (str): Path to the input JSON file (list of items).
        output_dir (str): Directory where split files will be saved.
        train_ratio (float): Fraction of data for training set.
        dev_ratio (float): Fraction of data for development/validation set.
        test_ratio (float): Fraction of data for test set.
        seed (int): Random seed for reproducibility.
    """

    # Ensure ratios add up to 1 (within floating point tolerance)
    assert abs((train_ratio + dev_ratio + test_ratio) - 1.0) < 1e-6, \
        "Ratios must sum to 1"

    # Load the dataset from JSON
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Shuffle the dataset so splits are randomized
    random.seed(seed)       # fix random seed for reproducibility
    random.shuffle(data)

    # Compute index boundaries for splits
    n = len(data)
    train_end = int(n * train_ratio)       # end index for training
    dev_end = train_end + int(n * dev_ratio)  # end index for development

    # Slice into subsets
    train_data = data[:train_end]
    dev_data = data[train_end:dev_end]
    test_data = data[dev_end:]

    # Ensure the output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Save train/dev/test JSON files with pretty formatting
    with open(os.path.join(output_dir, "train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=4, ensure_ascii=False)

    with open(os.path.join(output_dir, "dev.json"), "w", encoding="utf-8") as f:
        json.dump(dev_data, f, indent=4, ensure_ascii=False)

    with open(os.path.join(output_dir, "test.json"), "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4, ensure_ascii=False)

    # Print summary
    print(f"✅ Done! Wrote {len(train_data)} train, {len(dev_data)} dev, {len(test_data)} test examples.")


# -------------------------
# Run script
# -------------------------
# This will read dataset/dataset.json, shuffle it,
# split it into train/dev/test, and save results inside dataset/ folder.
split_json("dataset/dataset.json", "dataset/")