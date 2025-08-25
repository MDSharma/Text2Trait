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
    for token in doc[:-1]:
        if token.text == "." and doc[token.i + 1].text == ".":
            doc[token.i + 1].is_sent_start = False
    return doc


# -------------------------
# Step 1: PDFs -> TXT
# -------------------------
def convert_pdfs_to_sentences_separate_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("custom_sentence_boundary", before="parser")

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            text = pymupdf4llm.to_markdown(pdf_path)
            text_no_newlines = text.replace("\n", " ")

            doc = nlp(text_no_newlines)

            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_folder, base_name + ".txt")

            with open(output_file, "w", encoding="utf-8") as out_f:
                for sent in doc.sents:
                    sentence_text = sent.text.strip()
                    if sentence_text:
                        out_f.write(sentence_text + "\n")

            print(f"✅ Sentences for '{filename}' written to '{output_file}'.")


# -------------------------
# Step 2: Merge TXT -> JSON
# -------------------------
def merge_txts_to_json(input_folder, output_file):
    all_sentences = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".txt"):
            txt_path = os.path.join(input_folder, filename)

            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    sentence = line.strip()
                    if sentence:
                        all_sentences.append({"sentence": sentence})

            print(f"📄 Processed TXT: {txt_path}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_sentences, f, indent=4, ensure_ascii=False)

    print(f"\n🎉 All sentences merged into JSON: {output_file}")


# -------------------------
# Run everything
# -------------------------
if __name__ == "__main__":
    input_folder_path = "GWAS_literature/inference" # folder with your PDF files
    output_txt_folder = "output_inference_text"  # intermediate TXT files
    final_json_output = "inference.json"

    # Step 1: Convert PDFs -> sentence TXT files
    convert_pdfs_to_sentences_separate_files(input_folder_path, output_txt_folder)

    # Step 2: Merge TXT files -> final JSON
    merge_txts_to_json(output_txt_folder, final_json_output)