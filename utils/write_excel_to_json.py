import pandas as pd
import json
import os

def excel_to_json(excel_file):
    """Convert a single Excel file into JSON data."""
    xls = pd.ExcelFile(excel_file)
    all_sentences = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        required_cols = [
            "Sentence ID", "Sentence", 
            "Span-S (text)", "Span-S (attr)", 
            "Relation", 
            "Span-E (text)", "Span-E (attr)"
        ]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' in sheet '{sheet_name}' of file '{excel_file}'")

        for sentence_id, group in df.groupby("Sentence ID"):
            sentence_text = group["Sentence"].iloc[0]

            pairs = []
            for _, row in group.iterrows():
                pair = {
                    "span-s": {
                        "span": row["Span-S (text)"],
                        "attr": row["Span-S (attr)"]
                    },
                    "rel": row["Relation"],
                    "span-e": {
                        "span": row["Span-E (text)"],
                        "attr": row["Span-E (attr)"]
                    }
                }
                pairs.append(pair)

            all_sentences.append({
                "sentence": sentence_text,
                "pairs": pairs
            })

    return all_sentences


def merge_excels_to_json(input_folder, output_file):
    """Process all Excel files in a folder and save one merged JSON file."""
    all_data = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".xlsx"):
            excel_path = os.path.join(input_folder, filename)
            json_data = excel_to_json(excel_path)
            all_data.extend(json_data)  # merge everything into one list
            print(f"Processed: {excel_path}")

    # Save one merged JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Merged JSON written to {output_file}")


# Example usage:
merge_excels_to_json("training_xlsx/", "dataset.json")