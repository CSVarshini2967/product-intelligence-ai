"""
Module 6 -- Enrichment (from manufacturer sources).

SCOPE NOTE: live web scraping/RAG against manufacturer sites is fragile
and slow to demo reliably, and the brief's sourcing rules restrict you to
manufacturer-owned sources only. For the hackathon build, this module is
a clean pass-through / pluggable stub -- wire in real retrieval only if
core modules (3-9) are fully working with time to spare.

If you DO build this out: keep it retrieval-only (fetch + extract from a
known manufacturer URL), never free-generation, and feed extracted values
back through the same evidence/inferred schema as Module 5 so the
Confidence Engine treats it consistently.
"""


def enrich(rows: list[dict]) -> list[dict]:
    for r in rows:
        r.setdefault("enrichment_source", None)
        r.setdefault("enrichment_applied", False)
        # TODO (stretch goal): fetch MFR URL / Ref URL content for rows with
        # low attribute coverage and merge results here, same evidence schema.
    return rows
