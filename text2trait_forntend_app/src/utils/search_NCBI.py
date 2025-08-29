"""
NCBI Gene / Protein / Variant Fetcher
-------------------------------------

Fetches info from NCBI using Biopython's Entrez API.
Supports:
    - Genes (by name)
    - Proteins (by accession)
    - Variants/SNPs (by rsID)
    
Includes:
    - Local JSON cache to reduce repeated queries.
    - Organism filtering for genes and proteins.
    - Safe conversion from Entrez objects to plain dicts.
"""

from pathlib import Path
import json
import time
from typing import List, Optional, Dict, Any

from Bio import Entrez

# ───────────────────────────────
# Configuration & Globals
# ───────────────────────────────

CACHE_PATH = Path(__file__).resolve().parent / "ncbi_cache.json"
_SLEEP_BETWEEN_CALLS = 0.28  # ~3 requests/sec
_ENTREZ_EMAIL_SET = False

# Load previously saved cache
def _load_cache() -> Dict[str, Any]:
    try:
        if CACHE_PATH.exists():
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_cache(cache: Dict[str, Any]):
    try:
        CACHE_PATH.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print("Warning: could not write NCBI cache:", e)

_cache: Dict[str, Any] = _load_cache()

# ───────────────────────────────
# Public Utility Functions
# ───────────────────────────────

def set_email(email: str):
    global _ENTREZ_EMAIL_SET
    Entrez.email = email
    _ENTREZ_EMAIL_SET = True

# ───────────────────────────────
# Helpers
# ───────────────────────────────

def _safe_to_python(obj: Any) -> Any:
    """Recursively convert any Biopython Entrez objects to plain Python types."""
    if isinstance(obj, dict):
        return {k: _safe_to_python(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe_to_python(v) for v in obj]
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="ignore")
    if obj is None:
        return None
    try:
        return obj.__str__()
    except Exception:
        return obj

def _normalize_gene_doc(ds: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Entrez gene DocumentSummary to simple dict."""
    out: Dict[str, Any] = {
        "Name": ds.get("Name", "") or "",
        "Description": ds.get("Description", "") or "",
        "Chromosome": ds.get("Chromosome", "") or "",
        "OtherAliases": ds.get("OtherAliases", "") or "",
        "Summary": ds.get("Summary", "") or "",
        "raw": ds
    }

    organism = ds.get("Organism", {})
    if isinstance(organism, dict):
        out["Organism"] = organism.get("ScientificName", "") or ""
    else:
        out["Organism"] = str(organism) or ""

    genomic = ds.get("GenomicInfo", []) or []
    gi_list = []
    for g in genomic:
        acc = g.get("ChrAccVer", "")
        start = g.get("ChrStart", "")
        stop = g.get("ChrStop", "")
        strand = g.get("ChrStrand", "")
        loc_parts = []
        if acc:
            loc_parts.append(acc)
        if start != "" and stop != "":
            loc_parts.append(f"{start}-{stop}")
        if strand != "":
            loc_parts.append(f"strand={strand}")
        gi_str = ":".join([loc_parts[0]]) + (
            " " + " ".join(loc_parts[1:]) if len(loc_parts) > 1 else ""
        ) if loc_parts else ""
        gi_list.append(gi_str)
    out["GenomicInfo"] = "; ".join([s for s in gi_list if s])
    return out

def _normalize_protein_doc(ds: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Entrez protein DocumentSummary to simple dict with custom fields."""
    out: Dict[str, Any] = {
        "AccessionVersion": ds.get("AccessionVersion", "") or "",
        "Description": ds.get("Title", "") or "",
        "Organism": "",
        "SequenceLength": ds.get("Length", "") or "",
        "raw": ds
    }

    organism = ds.get("Organism", {})
    if isinstance(organism, dict):
        out["Organism"] = organism.get("ScientificName", "") or ""
    else:
        out["Organism"] = str(organism) or ""

    return out

# ───────────────────────────────
# Fetch Functions
# ───────────────────────────────

def fetch_gene_info_by_name(name: str, organism: Optional[str] = None) -> Dict[str, Any]:
    if organism is None:
        organism = "txid4081[Organism:exp]"

    query = f"{name}[Gene] AND {organism}"

    if not _ENTREZ_EMAIL_SET and not getattr(Entrez, "email", None):
        Entrez.email = "your.email@example.com"

    handle = Entrez.esearch(db="gene", term=query, retmax=5)
    try:
        record = Entrez.read(handle, validate=False)
    finally:
        handle.close()

    idlist = record.get("IdList", []) or []
    if not idlist:
        return {"query": name, "not_found": True}

    handle = Entrez.esummary(db="gene", id=",".join(idlist))
    try:
        doc = Entrez.read(handle, validate=False)
    finally:
        handle.close()

    docs = _safe_to_python(doc.get("DocumentSummarySet", {}).get("DocumentSummary", []))
    best_doc = None
    for d in docs:
        if d.get("Name", "").lower() == name.lower():
            best_doc = d
            break
    if best_doc is None and docs:
        best_doc = docs[0]
    if best_doc is None:
        return {"query": name, "not_found": True}

    result = _normalize_gene_doc(best_doc)
    result["query"] = name
    time.sleep(_SLEEP_BETWEEN_CALLS)
    return result

def fetch_protein_info(name: str, organism: Optional[str] = None) -> Dict[str, Any]:
    key = f"protein:{name}"
    if key in _cache:
        return _cache[key]

    if organism is None:
        organism = "txid4081[Organism:exp]"

    query = f'{name} AND {organism}'
    print("NCBI protein search query:", query)

    if not _ENTREZ_EMAIL_SET and not getattr(Entrez, "email", None):
        Entrez.email = "your.email@example.com"

    handle = Entrez.esearch(db="protein", term=query, retmax=5)
    try:
        record = Entrez.read(handle, validate=False)
    finally:
        handle.close()

    record_dict = _safe_to_python(record)
    idlist = record_dict.get("IdList", []) or []
    if not idlist:
        return {"query": name, "not_found": True}

    handle = Entrez.esummary(db="protein", id=",".join(idlist))
    try:
        doc = Entrez.read(handle, validate=False)
    finally:
        handle.close()

    doc_normalized = _safe_to_python(doc)

    docs = []
    if isinstance(doc_normalized, dict):
        docs = doc_normalized.get("DocumentSummarySet", {}).get("DocumentSummary", [])
    elif isinstance(doc_normalized, list):
        docs = doc_normalized

    best_doc = None
    for d in docs:
        if d.get("AccessionVersion", "").split(".")[0].lower() == name.split(".")[0].lower():
            best_doc = d
            break
    if best_doc is None and docs:
        best_doc = docs[0]
    if best_doc is None:
        return {"query": name, "not_found": True}

    result = _normalize_protein_doc(best_doc)
    result["query"] = name

    _cache[key] = result
    _save_cache(_cache)
    time.sleep(_SLEEP_BETWEEN_CALLS)
    return result

def fetch_multiple_nodes_info(
    nodes: List[Dict[str, str]],
    organism: Optional[str] = None
) -> List[Dict[str, Any]]:
    results = []
    for node in nodes:
        node_type = node.get("type", "gene")
        name_or_id = node.get("name")
        node_id = node.get("id") or name_or_id
        try:
            if node_type == "gene":
                info = fetch_gene_info_by_name(name_or_id, organism)

            elif node_type == "protein":
                info = fetch_protein_info(name_or_id, organism)
            else:
                info = {"not_found": True, "query": name_or_id, "type": node_type}

            info["_key"] = f"{node_type}:{node_id}"
            info["graph_id"] = node_id
            info["graph_name"] = name_or_id
            results.append(info)
        except Exception as e:
            results.append({
                "_key": f"{node_type}:{name_or_id}",
                "not_found": True,
                "error": str(e)
            })
            
    return results