"""
12-Stage Pipeline Orchestrator.
Calls each module's service function in deterministic order, collects
stage latencies, builds both Delivery Format and Audit DataFrames,
and summarizes catalog quality metrics.
"""
import time
import pandas as pd
from typing import Dict, Any, List

from app.modules.ingestion.service import ingest
from app.modules.cleaning.service import clean
from app.modules.deduplication.service import deduplicate
from app.modules.classification.service import classify
from app.modules.extraction.service import extract_attributes
from app.modules.enrichment.service import enrich
from app.modules.normalization.service import normalize_attributes
from app.modules.validation.service import validate
from app.modules.confidence.service import score_confidence
from app.modules.generation.service import generate_descriptions
from app.modules.export.service import build_output, build_audit_export


def run_pipeline(df_input: pd.DataFrame) -> Dict[str, Any]:
    stage_latencies: Dict[str, float] = {}

    # Stage 1: Ingestion & Pre-flight
    t0 = time.time()
    rows, preflight_telemetry = ingest(df_input)
    stage_latencies["Ingestion"] = round(time.time() - t0, 4)

    # Stage 2: Cleaning
    t0 = time.time()
    rows = clean(rows)
    stage_latencies["Cleaning"] = round(time.time() - t0, 4)

    # Stage 3: De-duplication
    t0 = time.time()
    rows = deduplicate(rows)
    stage_latencies["Deduplication"] = round(time.time() - t0, 4)

    # Stage 4: Taxonomy Classification
    t0 = time.time()
    rows = classify(rows)
    stage_latencies["Classification"] = round(time.time() - t0, 4)

    # Stage 5: Attribute Extraction
    t0 = time.time()
    rows = extract_attributes(rows)
    stage_latencies["Extraction"] = round(time.time() - t0, 4)

    # Stage 6: Manufacturer RAG Enrichment
    t0 = time.time()
    rows = enrich(rows)
    stage_latencies["Enrichment"] = round(time.time() - t0, 4)

    # Stage 7: Canonical Normalization
    t0 = time.time()
    rows = normalize_attributes(rows)
    stage_latencies["Normalization"] = round(time.time() - t0, 4)

    # Stage 8: Validation Engine
    t0 = time.time()
    rows = validate(rows)
    stage_latencies["Validation"] = round(time.time() - t0, 4)

    # Stage 9: Confidence Engine
    t0 = time.time()
    rows = score_confidence(rows)
    stage_latencies["Confidence"] = round(time.time() - t0, 4)

    # Stage 10: Description Generation
    t0 = time.time()
    rows = generate_descriptions(rows)
    stage_latencies["Generation"] = round(time.time() - t0, 4)

    # Stage 11: Export DataFrames
    t0 = time.time()
    output_df = build_output(rows)
    audit_df = build_audit_export(rows)
    stage_latencies["Export"] = round(time.time() - t0, 4)

    # Summary Statistics
    total_rows = len(rows)
    high_conf = sum(1 for r in rows if r.get("confidence_tier") == "HIGH")
    med_conf = sum(1 for r in rows if r.get("confidence_tier") == "MEDIUM")
    low_conf = sum(1 for r in rows if r.get("confidence_tier") == "LOW")
    needs_rev = sum(1 for r in rows if r.get("needs_review"))
    enriched_count = sum(1 for r in rows if r.get("enrichment_applied"))
    dup_count = sum(1 for r in rows if r.get("duplicate_info", {}).get("status") == "DUPLICATE")
    possible_dup_count = sum(1 for r in rows if r.get("duplicate_info", {}).get("status") == "POSSIBLE_DUPLICATE")
    
    avg_conf = (
        sum(r.get("overall_confidence", 0.0) for r in rows) / total_rows if total_rows else 0.0
    )

    summary = {
        "total_rows": total_rows,
        "high_confidence_count": high_conf,
        "medium_confidence_count": med_conf,
        "low_confidence_count": low_conf,
        "needs_review_count": needs_rev,
        "enriched_count": enriched_count,
        "duplicate_count": dup_count,
        "possible_duplicate_count": possible_dup_count,
        "avg_confidence": round(avg_conf, 2),
        "preflight_telemetry": preflight_telemetry,
        "stage_latencies": stage_latencies,
    }

    return {
        "output_df": output_df,
        "audit_df": audit_df,
        "rows": rows,
        "rows_processed": total_rows,
        "summary": summary,
    }
