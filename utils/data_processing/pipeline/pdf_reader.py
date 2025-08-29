import os
import spacy
import pymupdf4llm
from pipeline.json_writer import append_jsonl

def convert_pdfs_to_sentences(input_folder):
    """
    Convert all PDF files in a folder into a list of sentence dicts:
    {"sentence": "..."}.
    Uses spaCy for sentence splitting.
    """
    nlp = spacy.load("en_core_web_sm")
    all_sentences = []

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDF files in '{input_folder}'.")

    for filename in pdf_files:
        pdf_path = os.path.join(input_folder, filename)

        # Extract text from PDF as markdown
        print(f"⏳ Extracting text from: {filename}")
        text = pymupdf4llm.to_markdown(pdf_path)
        text = text.replace("\n", " ")

        # Run spaCy NLP for sentence segmentation
        doc = nlp(text)
        num_sentences = 0
        for sent in doc.sents:
            sentence_text = sent.text.strip()
            if sentence_text:
                all_sentences.append({"sentence": sentence_text})
                num_sentences += 1

        print(f"✅ {filename}: extracted {num_sentences} sentences")

    print(f"🔹 Total sentences extracted from PDFs: {len(all_sentences)}")
    return all_sentences


def merge_pdf_sentences(input_folder):
    """
    Wrapper function for consistency with Excel module.
    Returns a list of sentence dicts.
    """
    return convert_pdfs_to_sentences(input_folder)


def write_pdf_jsonl(input_folder, output_file, mode="append"):
    """
    Convert all PDFs in a folder and write to JSONL.
    mode="append" -> add to existing file
    mode="overwrite" -> overwrite existing file
    """
    if mode == "overwrite" and os.path.exists(output_file):
        os.remove(output_file)
        print(f"🗑️ Cleared existing PDF JSONL: {output_file}")

    data = merge_pdf_sentences(input_folder)
    print(f"{'Appending' if mode=='append' else 'Writing'} {len(data)} sentences to JSONL: {output_file}")
    append_jsonl(output_file, data)