"""
Module 6 -- Manufacturer RAG & Datasheet Enrichment.
Responsibility: Retrieve verified catalog attributes from controlled manufacturer
datasheets and technical documents.
Every enriched attribute contains:
  - source = "manufacturer_datasheet"
  - source_reference = Document name & Page
  - method = "manufacturer_rag"
  - validation = "grounded"
  - confidence = 0.98
"""
import os
import json
import glob
from typing import List, Dict, Any

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "manufacturer_docs")


def load_manufacturer_kb() -> List[Dict[str, Any]]:
    """Loads all structured manufacturer datasheets from data/manufacturer_docs."""
    kb_docs = []
    norm_path = os.path.normpath(DOCS_DIR)
    if not os.path.exists(norm_path):
        return kb_docs

    for file_path in glob.glob(os.path.join(norm_path, "*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                kb_docs.append(data)
        except Exception:
            continue
    return kb_docs


def query_rag_by_mpn(mpn: str, kb_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Finds matching manufacturer datasheet and returns missing specs."""
    if not mpn:
        return []

    norm_mpn = mpn.upper().replace("-", "").strip()
    matched_specs = []

    for doc in kb_docs:
        models = [m.upper().replace("-", "").strip() for m in doc.get("model_numbers", [])]
        if any(norm_mpn in m or m in norm_mpn for m in models):
            doc_name = doc.get("document_name", "manufacturer_datasheet.pdf")
            doc_url = doc.get("source_url", "")          
            specs = doc.get("specifications", {})
            for attr_name, spec_info in specs.items():
                matched_specs.append({
                    "label": attr_name,
                    "value": str(spec_info["value"]),
                    "uom": spec_info.get("uom"),
                    "evidence": spec_info.get("text", f"{attr_name}: {spec_info['value']}"),
                    "source": "manufacturer_datasheet",
                    "method": "manufacturer_rag",
                    "inferred": False,
                    "confidence": 0.98,
                    "validation": "grounded",
                    "source_reference": f"{doc_name} (p. {spec_info.get('page', 1)})",
                    "mfr_url": doc_url,                   
                })
            break

    return matched_specs


def enrich(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans products and enriches missing attributes from manufacturer knowledge base.
    """
    kb_docs = load_manufacturer_kb()

    for r in rows:
        mpn = r.get("mfg_part_num", "")
        rag_attrs = query_rag_by_mpn(mpn, kb_docs)

        existing_labels = {a["label"].lower() for a in r.get("extracted_attributes", [])}
        added_count = 0
        doc_refs = set()

        for rag_attr in rag_attrs:
            if rag_attr["label"].lower() not in existing_labels:
                r["extracted_attributes"].append(rag_attr)
                existing_labels.add(rag_attr["label"].lower())
                added_count += 1
                if rag_attr.get("source_reference"):
                    doc_refs.add(rag_attr["source_reference"])

        if added_count > 0:
            r["enrichment_applied"] = True
            r["enrichment_source"] = "Manufacturer Datasheet RAG"
            r["enrichment_doc_refs"] = list(doc_refs)
            r["enrichment_mfr_url"] = rag_attrs[0].get("mfr_url", "")
            r.setdefault("confidence_reasons", []).append(f"✓ Enriched {added_count} attributes from manufacturer datasheet RAG")
        else:
            r["enrichment_applied"] = False
            r["enrichment_source"] = None
            r["enrichment_doc_refs"] = []
            r["enrichment_mfr_url"] = ""
    return rows
