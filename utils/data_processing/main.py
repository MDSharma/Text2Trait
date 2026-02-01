"""
Main pipeline script for processing Text2Trait and literature data.

Workflow:
1. Process Excel files → master_triplets.jsonl
2. Filter Excel triplets → master_triplets_filtered.jsonl
3. Process PDF files → master_pdfs.jsonl
4. LLM enrichment of PDF sentences → master_pdfs_with_triplets.jsonl
5. Filter LLM PDF triplets → master_pdfs_with_triplets_filtered.jsonl
6. Merge PDF triplets into filtered Excel triplets
7. Build graph from chosen triplets source (Excel, LLM, or merged)
8. Convert JSONL → JSON array for downstream use

Incremental behavior:
- LLM enrichment appends new predictions instead of overwriting
- Merging only appends new filtered PDF triplets
"""

from pipeline.excel_reader import write_excel_jsonl
from pipeline.pdf_reader import write_pdf_jsonl
from pipeline.filter import filter_jsonl
from pipeline.graph_builder import build_graph_from_dataset, write_graph
from pipeline.json_writer import read_jsonl, jsonl_to_json_array, merge_jsonl_files
from pipeline.llm_predictor import enrich_with_triplets
from config import STEPS_TO_RUN, MODE_SETTINGS, GRAPH_SOURCE, PATHS, LLM_SETTINGS

# -------------------------
# Track which source was last processed
processed_source = None

# -------------------------
# Step 1: Excel → master_triplets.jsonl
if "excel" in STEPS_TO_RUN:
    print("\n🔹 Processing Excel files (triplets)...")
    write_excel_jsonl(PATHS["excel_input"], PATHS["master_triplets"], mode=MODE_SETTINGS["excel"])
    processed_source = "excel"

# -------------------------
# Step 2: PDF → master_pdfs.jsonl
if "pdf" in STEPS_TO_RUN:
    print("\n🔹 Processing PDF files (sentences)...")
    write_pdf_jsonl(PATHS["pdf_input"], PATHS["master_pdfs"], mode=MODE_SETTINGS["pdf"])
    processed_source = "pdf" if processed_source != "excel" else processed_source

# -------------------------
# Step 3: Filter Excel triplets
master_data = []
if "filter" in STEPS_TO_RUN and processed_source == "excel":
    print("\n🔹 Filtering invalid Excel triplets...")
    filter_jsonl(PATHS["master_triplets"], PATHS["master_triplets_filtered"])
    master_data = read_jsonl(PATHS["master_triplets_filtered"])
elif processed_source == "pdf":
    print("\n⚠️ Skipping filtering: only applies to Excel triplets")

# -------------------------
# Step 4: LLM enrichment (PDF sentences)
if "llm" in STEPS_TO_RUN and processed_source == "pdf":
    print("\n🔹 Enriching PDF sentences with LLM triplets...")
    enrich_with_triplets(
        input_file=PATHS["master_pdfs"],
        output_file=PATHS["master_pdfs_with_triplets"],
        batch_size=LLM_SETTINGS["batch_size"],
        custom_prompt=LLM_SETTINGS["custom_prompt"],
        api_key=LLM_SETTINGS["api_key"]
    )
    processed_source = "llm"

# -------------------------
# Step 5: Filter LLM PDF triplets
if "filter_pdf" in STEPS_TO_RUN and processed_source == "llm":
    print("\n🔹 Filtering invalid PDF LLM triplets...")
    filter_jsonl(PATHS["master_pdfs_with_triplets"], PATHS["master_pdfs_with_triplets_filtered"])

# -------------------------
# Step 6: Merge PDF triplets into filtered Excel triplets
if "merge_llm" in STEPS_TO_RUN:
    print("\n🔹 Merging filtered PDF triplets into filtered Excel triplets...")
    merge_jsonl_files(
        target_file=PATHS["master_triplets_filtered"],
        source_file=PATHS["master_pdfs_with_triplets_filtered"]
    )
    master_data = read_jsonl(PATHS["master_triplets_filtered"])

# -------------------------
# Step 7: Build graph
if "graph" in STEPS_TO_RUN:
    if GRAPH_SOURCE == "excel":
        print("\n🔹 Building graph from Excel triplets only...")
        graph_data = read_jsonl(PATHS["master_triplets_filtered"])
    elif GRAPH_SOURCE == "llm":
        print("\n🔹 Building graph from LLM PDF triplets only...")
        graph_data = read_jsonl(PATHS["master_pdfs_with_triplets_filtered"])
    elif GRAPH_SOURCE == "merged":
        print("\n🔹 Building graph from merged triplets...")
        graph_data = read_jsonl(PATHS["master_triplets_filtered"])
    else:
        raise ValueError(f"Unknown graph source: {GRAPH_SOURCE}")

    nodes, edges = build_graph_from_dataset(graph_data)
    write_graph(PATHS["graph_nodes"], PATHS["graph_edges"], nodes, edges)

# -------------------------
# Step 8: Convert JSONL → JSON array
if "array" in STEPS_TO_RUN:
    if GRAPH_SOURCE in ["excel", "merged"]:
        jsonl_to_json_array(PATHS["master_triplets_filtered"], "data/output/master_triplets_filtered_array.json")
    elif GRAPH_SOURCE == "llm":
        jsonl_to_json_array(PATHS["master_pdfs_with_triplets_filtered"], "data/output/master_pdfs_with_triplets_filtered_array.json")

print("\n🎉 Pipeline completed successfully!")