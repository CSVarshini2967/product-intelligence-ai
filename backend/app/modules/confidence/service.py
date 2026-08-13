"""
Module 8 -- Confidence Engine.

This is the project's core differentiator. Confidence is computed from
REAL signals gathered by earlier modules -- never invented by asking the
LLM "how sure are you 1-10", which is unreliable and easy to fake.

Signals used:
  - attr["validation"] == "grounded"      -> +1.0
  - attr["validation"] == "missing_evidence" -> +0.4
  - attr["validation"] == "unverified_inference" -> +0.2
  - manufacturer_brand_mismatch flag present -> caps row confidence at 0.5
  - no_classpath flag present -> caps row confidence at 0.3

Fields scoring below CONFIDENCE_THRESHOLD get needs_review = True and are
routed to the human review queue in the dashboard, rather than silently
auto-published.
"""

CONFIDENCE_THRESHOLD = 0.6

VALIDATION_SCORES = {
    "grounded": 1.0,
    "missing_evidence": 0.4,
    "unverified_inference": 0.2,
}


def score_confidence(rows: list[dict]) -> list[dict]:
    for r in rows:
        attrs = r.get("extracted_attributes", [])
        for attr in attrs:
            attr["confidence"] = VALIDATION_SCORES.get(attr.get("validation"), 0.0)

        if attrs:
            overall = sum(a["confidence"] for a in attrs) / len(attrs)
        else:
            overall = 0.0

        flags = r.get("flags", [])
        if "manufacturer_brand_mismatch" in flags:
            overall = min(overall, 0.5)
        if "no_classpath" in flags:
            overall = min(overall, 0.3)

        r["overall_confidence"] = round(overall, 2)
        r["needs_review"] = overall < CONFIDENCE_THRESHOLD

    return rows
