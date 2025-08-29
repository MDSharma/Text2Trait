"""
Pipeline configuration file.

Contains:
- Steps to run
- Input/output paths
- Mode settings (append/overwrite)
- Graph source option
"""

# Steps can be any subset of:
# "excel"      → Process Excel files
# "filter"     → Filter Excel triplets
# "pdf"        → Process PDF files
# "llm"        → Enrich PDF sentences with LLM
# "filter_pdf" → Filter LLM-predicted PDF triplets
# "merge_llm"  → Merge PDF triplets into Excel triplets
# "graph"      → Build graph from triplets
# "array"      → Convert JSONL → JSON array

STEPS_TO_RUN = [
    "excel", "filter", "graph", "array"
]

# Mode for handling existing files: "append" or "overwrite"
MODE_SETTINGS = {
    "excel": "overwrite",
    "pdf": "overwrite"
}

# Graph building source: "excel", "llm", or "merged"
GRAPH_SOURCE = "excel"

# Input/Output paths
PATHS = {
    "excel_input": "data/input_excels/",
    "pdf_input": "data/input_pdfs/",
    "master_triplets": "data/output/master_triplets.jsonl",
    "master_triplets_filtered": "data/output/master_triplets_filtered.jsonl",
    "master_pdfs": "data/output/master_pdfs.jsonl",
    "master_pdfs_with_triplets": "data/output/master_pdfs_with_triplets.jsonl",
    "master_pdfs_with_triplets_filtered": "data/output/master_pdfs_with_triplets_filtered.jsonl",
    "graph_nodes": "data/output/graph_nodes.json",
    "graph_edges": "data/output/graph_edges.json",
}