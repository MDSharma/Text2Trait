import pandas as pd
import os
from pipeline.json_writer import append_jsonl

def doi_to_url(doi_str):
    """
    Convert a DOI string to a clickable URL and clean non-breaking spaces.
    """
    doi_str = doi_str.replace("\u00a0", " ").strip()
    if doi_str.lower().startswith("doi:"):
        doi_str = doi_str[4:].strip()
    return f"https://doi.org/{doi_str}"

def excel_to_json(excel_file):
    """
    Convert a single Excel file into JSON-like data with triplets.
    Each row represents a sentence + entity-relation pairs.
    Adds 'source' field from DOI/link column.
    """
    print(f"⏳ Processing Excel file: {excel_file}")
    xls = pd.ExcelFile(excel_file)
    all_sentences = []

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Initialize sheet sentence counter
        sheet_sentence_count = 0

        # Extract first non-empty link from the sheet
        if "Link" in df.columns and not df["Link"].dropna().empty:
            raw_link = df["Link"].dropna().iloc[0]
            source_link = doi_to_url(raw_link)
        else:
            source_link = ""

        for sentence_id, group in df.groupby("Sentence ID"):
            sentence_text = group["Sentence"].iloc[0]

            pairs = []
            for _, row in group.iterrows():
                pairs.append({
                    "span-s": {"span": row["Span-S (text)"], "attr": row["Span-S (attr)"]},
                    "rel": row["Relation"],
                    "span-e": {"span": row["Span-E (text)"], "attr": row["Span-E (attr)"]}
                })

            all_sentences.append({
                "sentence": sentence_text,
                "pairs": pairs,
                "source": source_link
            })
            sheet_sentence_count += 1

        print(f"     ✅ Sheet '{sheet_name}' processed: {sheet_sentence_count} sentences")

    print(f"🔹 Total sentences extracted from Excel '{excel_file}': {len(all_sentences)}")
    return all_sentences


def merge_excels(input_folder):
    """
    Read all Excel files in the folder and convert to a list of triplet dicts.
    """
    all_data = []
    excel_files = [f for f in os.listdir(input_folder) if f.endswith(".xlsx")]
    print(f"Found {len(excel_files)} Excel files in '{input_folder}'.")

    for filename in excel_files:
        excel_path = os.path.join(input_folder, filename)
        file_data = excel_to_json(excel_path)
        all_data.extend(file_data)
        print(f"📄 Processed Excel: {filename}, total sentences: {len(file_data)}")

    print(f"🔹 Total sentences from all Excel files: {len(all_data)}")
    return all_data


def write_excel_jsonl(input_folder, output_file, mode="append"):
    """
    Convert all Excel files in a folder and write to JSONL.
    mode="append" -> add to existing file
    mode="overwrite" -> overwrite existing file
    """
    if mode == "overwrite" and os.path.exists(output_file):
        os.remove(output_file)
        print(f"🗑️ Cleared existing Excel JSONL: {output_file}")

    data = merge_excels(input_folder)
    print(f"{'Appending' if mode=='append' else 'Writing'} {len(data)} sentences to JSONL: {output_file}")
    append_jsonl(output_file, data)