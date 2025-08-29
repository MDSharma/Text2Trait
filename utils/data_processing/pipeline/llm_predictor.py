"""
LLM Predictor module.

Reads PDF sentences and enriches them with triplets using OpenAI GPT.
Supports batching and incremental appending to JSONL.
"""

import json
import time
from openai import OpenAI
from pipeline.json_writer import append_jsonl, read_jsonl

def call_llm_api(prompt, api_key, model="gpt-4o-mini", max_retries=3, sleep_time=2):
    """
    Calls OpenAI API with retry mechanism (new SDK).
    """
    client = OpenAI(api_key=api_key)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ LLM API call failed (attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(sleep_time)

    raise RuntimeError("LLM API call failed after retries.")


def enrich_with_triplets(input_file, output_file, batch_size=5, custom_prompt=None, api_key=None):
    """
    Enrich PDF sentences with triplets using LLM.
    - input_file: JSONL file with {"sentence": "..."} entries
    - output_file: JSONL file to append triplet predictions
    - batch_size: number of sentences per API call
    - custom_prompt: user-defined prompt template, with {sentences} placeholder
    - api_key: OpenAI API key
    """

    all_sentences = read_jsonl(input_file)
    print(f"🔹 Total sentences to process: {len(all_sentences)}")

    # Already processed sentences (avoid duplicates)
    try:
        existing_data = read_jsonl(output_file)
        existing_sentences = {entry["sentence"] for entry in existing_data}
        print(f"ℹ️ Found {len(existing_sentences)} sentences already in output, skipping duplicates")
    except FileNotFoundError:
        existing_sentences = set()
        print(f"ℹ️ Output file not found. Creating new JSONL: {output_file}")

    # Filter out sentences already processed
    sentences_to_process = [s for s in all_sentences if s["sentence"] not in existing_sentences]
    print(f"🔹 Sentences remaining for LLM enrichment: {len(sentences_to_process)}")

    # Process in batches
    for i in range(0, len(sentences_to_process), batch_size):
        batch = sentences_to_process[i:i+batch_size]
        batch_texts = [f"{j+1}. {entry['sentence']}" for j, entry in enumerate(batch)]
        batch_prompt = custom_prompt.format(sentences="\n".join(batch_texts)) if custom_prompt else "\n".join(batch_texts)

        print(f"⏳ Processing batch {i//batch_size + 1} ({len(batch)} sentences)...")
        llm_output = call_llm_api(batch_prompt, api_key)

        # Expecting JSON from LLM; try parsing
        try:
            predictions = json.loads(llm_output)
        except json.JSONDecodeError:
            print("⚠️ Failed to parse LLM output as JSON. Skipping batch.")
            print(f"Output: {llm_output}")
            continue

        # Append batch predictions to output JSONL
        append_jsonl(output_file, predictions)
        print(f"✅ Batch {i//batch_size + 1} appended ({len(predictions)} entries)")

    print(f"\n🎉 LLM enrichment complete. Output saved to {output_file}")