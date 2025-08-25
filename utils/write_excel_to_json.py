import pandas as pd
import json
import os


def excel_to_json(excel_file):
    """
    Convert a single Excel file into JSON data.
    - Each Excel sheet is processed
    - Expected columns: Sentence ID, Sentence, Span-S, Relation, Span-E
    - Groups rows by Sentence ID to collect entity pairs and relations
    """

    # Load Excel file (can have multiple sheets)
    xls = pd.ExcelFile(excel_file)
    all_sentences = []

    # Iterate through all sheets in the Excel file
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        # Required column names to validate structure
        required_cols = [
            "Sentence ID", "Sentence", 
            "Span-S (text)", "Span-S (attr)", 
            "Relation", 
            "Span-E (text)", "Span-E (attr)"
        ]
        # Check if all required columns exist in the sheet
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(
                    f"Missing column '{col}' in sheet '{sheet_name}' of file '{excel_file}'"
                )

        # Group rows by Sentence ID (since multiple pairs may belong to one sentence)
        for sentence_id, group in df.groupby("Sentence ID"):
            # Take the actual sentence text (same across group)
            sentence_text = group["Sentence"].iloc[0]

            # Collect all span-relation-span pairs for this sentence
            pairs = []
            for _, row in group.iterrows():
                pair = {
                    "span-s": {
                        "span": row["Span-S (text)"],   # Subject span text
                        "attr": row["Span-S (attr)"]    # Subject attribute
                    },
                    "rel": row["Relation"],            # Relation between spans
                    "span-e": {
                        "span": row["Span-E (text)"],   # Object span text
                        "attr": row["Span-E (attr)"]    # Object attribute
                    }
                }
                pairs.append(pair)

            # Store sentence + all its pairs
            all_sentences.append({
                "sentence": sentence_text,
                "pairs": pairs
            })

    return all_sentences


def merge_excels_to_json(input_folder, output_file):
    """
    Process all Excel files in a folder and save one merged JSON file.
    - Calls excel_to_json() for each file
    - Aggregates all sentences into one dataset
    """

    all_data = []

    # Iterate over all Excel files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".xlsx"):  # Only process .xlsx files
            excel_path = os.path.join(input_folder, filename)

            # Convert the Excel to JSON-like structure
            json_data = excel_to_json(excel_path)

            # Merge into master list
            all_data.extend(json_data)

            print(f"📄 Processed: {excel_path}")

    # Save one merged JSON file with all sentences + pairs
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Merged JSON written to {output_file}")


# -------------------------
# Run script
# -------------------------
# Convert all Excel files inside "training_xlsx/" into one JSON dataset.
merge_excels_to_json("training_xlsx/", "dataset.json")