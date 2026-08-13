"""
Straight-line pipeline orchestrator.

This is intentionally a plain Python function calling each module's
service function in order -- NOT a LangGraph agent. With ~9 fixed
sequential stages and no branching logic needed, an explicit orchestrator
is easier to debug live during a demo and has zero extra dependency risk.
(If you outgrow this -- e.g. need retries, parallel branches, or dynamic
routing between modules -- that's the point where LangGraph starts to
earn its keep. Not before.)
"""
import pandas as pd

from app.modules.ingestion.service import ingest
from app.modules.cleaning.service import clean
from app.modules.classification.service import classify
from app.modules.extraction.service import extract_attributes
from app.modules.enrichment.service import enrich
from app.modules.validation.service import validate
from app.modules.confidence.service import score_confidence
from app.modules.generation.service import generate_descriptions
from app.modules.export.service import build_output


def run_pipeline(df_input: pd.DataFrame) -> dict:
    rows = ingest(df_input)
    rows = clean(rows)
    rows = classify(rows)
    rows = extract_attributes(rows)
    rows = enrich(rows)
    rows = validate(rows)
    rows = score_confidence(rows)
    rows = generate_descriptions(rows)
    output_df = build_output(rows)

    summary = {
        "total_rows": len(rows),
        "needs_review": sum(1 for r in rows if r.get("needs_review")),
        "avg_confidence": (
            sum(r.get("overall_confidence", 0) for r in rows) / len(rows) if rows else 0
        ),
    }

    return {"output_df": output_df, "rows_processed": len(rows), "summary": summary}
