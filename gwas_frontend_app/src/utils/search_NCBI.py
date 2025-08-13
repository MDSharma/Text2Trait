# All avaible inforrmations:
# Name:
# Description:
# Status:
# CurrentID:
# Chromosome:
# GeneticSource:
# MapLocation:
# OtherAliases:
# OtherDesignations:
# NomenclatureSymbol:
# NomenclatureName:
# NomenclatureStatus:
# Mim:
# GenomicInfo:
# GeneWeight:
# Summary:
# ChrSort:
# ChrStart:
# Organism:
# LocationHist:

"""
Helper for fetching Gene summaries from NCBI using Biopython Entrez.

Provides:
- set_email(email)             # set Entrez.email once at app start
- fetch_gene_info_by_geneid(id)
- fetch_gene_info_by_name(name, organism=None)
- fetch_multiple_genes_info(names, organism=None) -> list of dicts

Returned dict contains the selected fields:
  Name, Description, Chromosome, OtherAliases, GenomicInfo, Summary, Organism, GeneID, query, raw
The module also keeps a small JSON cache on disk at the same folder (ncbi_cache.json).
"""

from pathlib import Path
import json
import time
from typing import List, Optional, Dict, Any

from Bio import Entrez

# Path for a small local cache to avoid repeated queries during development
CACHE_PATH = Path(__file__).resolve().parent / "ncbi_cache.json"
_SLEEP_BETWEEN_CALLS = 0.3  # ~3 requests/sec (be polite)

_ENTREZ_EMAIL_SET = False

def set_email(email: str):
    """Set the Entrez email used for queries (NCBI requires this)."""
    global _ENTREZ_EMAIL_SET
    Entrez.email = email
    _ENTREZ_EMAIL_SET = True

# --- simple persistent cache helpers ---
def _load_cache() -> Dict[str, Any]:
    try:
        if CACHE_PATH.exists():
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_cache(cache: Dict[str, Any]):
    try:
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("Warning: could not write NCBI cache:", e)

_cache: Dict[str, Any] = _load_cache()

# --- normalization helper ---
def _normalize_docsummary(ds: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a DocumentSummary (esummary) entry into a JSON-serializable dict with the fields you requested."""
    out: Dict[str, Any] = {}
    # NCBI's DocumentSummary often includes 'Id' (string), 'Name', 'Description', ...
    out["GeneID"] = str(ds.get("Id", "")) or str(ds.get("GeneID", "")) or ""
    out["Name"] = ds.get("Name", "") or ""
    out["Description"] = ds.get("Description", "") or ""
    out["Chromosome"] = ds.get("Chromosome", "") or ""
    out["OtherAliases"] = ds.get("OtherAliases", "") or ""
    # GenomicInfo is a list of dicts; produce a concise representation
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
        gi_str = ":".join([loc_parts[0]]) + (" " + " ".join(loc_parts[1:]) if len(loc_parts) > 1 else "") if loc_parts else ""
        gi_list.append(gi_str)
    out["GenomicInfo"] = "; ".join([s for s in gi_list if s])
    out["Summary"] = ds.get("Summary", "") or ""
    organism = ds.get("Organism", {})
    if isinstance(organism, dict):
        out["Organism"] = organism.get("ScientificName", "") or ""
    else:
        out["Organism"] = str(organism) or ""
    out["raw"] = ds
    return out

# --- public fetching functions ---
def fetch_gene_info_by_geneid(gene_id: str) -> Dict[str, Any]:
    """
    Fetch summary for a given GeneID from NCBI (esummary).
    Uses simple disk cache keyed by the gene_id.
    """
    global _cache
    key = f"gid:{gene_id}"
    if key in _cache:
        return _cache[key]

    if not _ENTREZ_EMAIL_SET and not getattr(Entrez, "email", None):
        Entrez.email = "your.email@example.com"

    handle = Entrez.esummary(db="gene", id=str(gene_id))
    try:
        doc = Entrez.read(handle)
    finally:
        handle.close()

    docs = doc.get("DocumentSummarySet", {}).get("DocumentSummary", []) or []
    if not docs:
        result = {"GeneID": gene_id, "not_found": True}
    else:
        result = _normalize_docsummary(docs[0])
    _cache[key] = result
    _save_cache(_cache)
    time.sleep(_SLEEP_BETWEEN_CALLS)
    return result

def fetch_gene_info_by_name(name: str, organism: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for gene by name (and optional organism). Returns best matching gene's summary.
    Defaults to plants if organism not provided.
    """
    if organism is None:
        organism = "txid33090[Organism:exp]"  # plant filter by default

    query = f"{name}[Gene] AND {organism}"

    if not _ENTREZ_EMAIL_SET and not getattr(Entrez, "email", None):
        Entrez.email = "your.email@example.com"

    handle = Entrez.esearch(db="gene", term=query, retmax=5)
    try:
        record = Entrez.read(handle)
    finally:
        handle.close()

    idlist = record.get("IdList", []) or []
    if not idlist:
        return {"query": name, "not_found": True}

    # Fetch summaries for candidates
    handle = Entrez.esummary(db="gene", id=",".join(idlist))
    try:
        doc = Entrez.read(handle)
    finally:
        handle.close()

    docs = doc.get("DocumentSummarySet", {}).get("DocumentSummary", [])
    best_doc = None
    # Pick exact name match first
    for d in docs:
        if d.get("Name", "").lower() == name.lower():
            best_doc = d
            break
    # fallback to first if no exact match
    if best_doc is None and docs:
        best_doc = docs[0]

    if best_doc is None:
        return {"query": name, "not_found": True}

    result = _normalize_docsummary(best_doc)
    result["query"] = name
    time.sleep(_SLEEP_BETWEEN_CALLS)
    return result

def fetch_multiple_genes_info(names: List[str], organism: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch info for multiple gene names (sequentially, with polite pauses).
    Returns a list of info dicts in the same order as 'names'. Each item will contain 'query'.
    """
    results = []
    for name in names:
        try:
            info = fetch_gene_info_by_name(name, organism)
            results.append(info)
        except Exception as e:
            results.append({"query": name, "error": str(e)})
    return results