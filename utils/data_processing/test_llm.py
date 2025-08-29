"""
Test LLM enrichment on a small batch of PDF sentences.
"""

from pipeline.llm_predictor import enrich_with_triplets
from pipeline.json_writer import read_jsonl
from config import PATHS
import json

# -------------------------
# Test settings
# -------------------------
API_KEY = ""  # <-- Put your OpenAI API key here
BATCH_SIZE = 2  # small batch for testing

# Simple prompt for testing
CUSTOM_PROMPT = """
The task is to analyse sentences according to schema I developed.
We want to prepare dataset that we can use to do a NER task.
That is why we have to find according entities and relations to create training set.
This is the schema:
Entities: Gene: gene Regulator: [transcription_factor, regulator] Variant: [variant, SNP, polymorphism, mutation], Protein: protein, Trait: phenotype Enzyme: enzyme Organism: organism;
Relations: "is_a" "part_of" "inheres_in" "develops_from" “is_related_to” "is_not_related_to" “increases” “decreases” “may_influence” “may_not_influence” “disrupts” “influences” “does_not_influence”;
Return a JSON list of objects with the format:
[
  {{
    "sentence": "...",
    "pairs": [
      {{
        "span-s": {{"span": "...", "attr": "..."}},
        "rel": "...",
        "span-e": {{"span": "...", "attr": "..."}}
      }}
    ]
  }}
]
Sentences:
{sentences}
"""

# -------------------------
# Read first few sentences only
pdf_sentences = read_jsonl(PATHS["test_inference"])
test_sentences = pdf_sentences[:5]  # first 5 sentences for testing

# Save them temporarily to a small JSONL
TEST_INPUT_FILE = "data/output/test_master_llm.jsonl"
from pipeline.json_writer import append_jsonl
with open(TEST_INPUT_FILE, "w", encoding="utf-8") as f:
    for entry in test_sentences:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# -------------------------
# Run LLM enrichment
TEST_OUTPUT_FILE = "data/output/test_inference_llm.jsonl"

enrich_with_triplets(
    input_file=TEST_INPUT_FILE,
    output_file=TEST_OUTPUT_FILE,
    batch_size=BATCH_SIZE,
    custom_prompt=CUSTOM_PROMPT,
    api_key=API_KEY
)

print(f"✅ Test LLM enrichment complete. Output in: {TEST_OUTPUT_FILE}")
