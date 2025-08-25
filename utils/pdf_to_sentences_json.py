import os
import spacy
import pymupdf4llm
import json
from spacy.language import Language


# -------------------------
# Custom sentence splitter
# -------------------------
@Language.component("custom_sentence_boundary")
def custom_sentence_boundary(doc):
    """
    Custom rule for sentence segmentation:
    If we encounter ".." (two consecutive dots), 
    don't treat the second dot as the start of a new sentence.
    """
    for token in doc[:-1]:
        if token.text == "." and doc[token.i + 1].text == ".":
            doc[token.i + 1].is_sent_start = False
    return doc


# -------------------------
# Step 1: PDFs -> TXT
# -------------------------
def convert_pdfs_to_sentences_separate_files(input_folder, output_folder):
    """
    Convert all PDF files in the input folder into text sentence files.
    - Extracts text from each PDF
    - Runs spaCy to split into sentences
    - Saves one .txt file per PDF with one sentence per line
    """

    # Create output folder if it doesn’t exist
    os.makedirs(output_folder, exist_ok=True)

    # Load spaCy English model
    nlp = spacy.load("en_core_web_sm")

    # Add our custom sentence rule before the parser
    nlp.add_pipe("custom_sentence_boundary", before="parser")

    # Loop through all PDF files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)

            # Extract text as markdown (better handling of layout)
            text = pymupdf4llm.to_markdown(pdf_path)

            # Replace newlines with spaces for cleaner processing
            text_no_newlines = text.replace("\n", " ")

            # Run spaCy NLP pipeline
            doc = nlp(text_no_newlines)

            # Prepare output .txt file path (same name as PDF)
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_folder, base_name + ".txt")

            # Write each sentence to a new line
            with open(output_file, "w", encoding="utf-8") as out_f:
                for sent in doc.sents:
                    sentence_text = sent.text.strip()
                    if sentence_text:  # Skip empty sentences
                        out_f.write(sentence_text + "\n")

            print(f"✅ Sentences for '{filename}' written to '{output_file}'.")


# -------------------------
# Step 2: Merge TXT -> JSON
# -------------------------
def merge_txts_to_json(input_folder, output_file):
    """
    Merge all .txt files into a single JSON file.
    - Reads sentences line by line
    - Stores them as a list of dictionaries: {"sentence": "..."}
    """

    all_sentences = []

    # Loop through all TXT files in the folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".txt"):
            txt_path = os.path.join(input_folder, filename)

            # Read file line by line
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    sentence = line.strip()
                    if sentence:
                        all_sentences.append({"sentence": sentence})

            print(f"📄 Processed TXT: {txt_path}")

    # Save all sentences into one JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_sentences, f, indent=4, ensure_ascii=False)

    print(f"\n🎉 All sentences merged into JSON: {output_file}")


# -------------------------
# Run script
# -------------------------
if __name__ == "__main__":
    input_folder_path = "GWAS_literature/inference"
    output_txt_folder = "output_inference_text"
    final_json_output = "inference.json"

    convert_pdfs_to_sentences_separate_files(input_folder_path, output_txt_folder)
    merge_txts_to_json(output_txt_folder, final_json_output)