"""
Module 9 -- Signal-Based Explainable Confidence Engine.
Responsibility: Compute transparent confidence scores from real signals
rather than LLM self-rating. Produces an explainable breakdown of why
each score was assigned.
"""
from typing import List, Dict, Any

HIGH_THRESHOLD = 0.80
MEDIUM_THRESHOLD = 0.50


def score_single_product(r: Dict[str, Any]) -> Dict[str, Any]:
    """Computes transparent confidence score and explainability breakdown."""
    attrs = r.get("extracted_attributes", [])
    flags = r.get("flags", [])
    reasons: List[str] = []

    # Score components (out of 100 points)
    score_points = 0.0

    # 1. Attribute Grounding Signal (up to 35 points)
    if attrs:
        grounded_count = sum(1 for a in attrs if a.get("validation") == "grounded")
        ratio = grounded_count / len(attrs)
        score_points += ratio * 35.0
        if ratio == 1.0:
            reasons.append(f"✓ All {len(attrs)} attributes verified with direct input evidence (+35 pts)")
        else:
            reasons.append(f"✓ {grounded_count}/{len(attrs)} attributes grounded in source text (+{ratio*35:.1f} pts)")
    else:
        reasons.append("⚠ No specific attributes extracted from input text")

    # 2. Controlled Taxonomy Classification (up to 20 points)
    if r.get("classpath") and "unclassified_fallback" not in flags:
        score_points += 20.0
        reasons.append("✓ Mapped to controlled industrial taxonomy LOV (+20 pts)")
    else:
        score_points += 5.0
        reasons.append("⚠ General unclassified taxonomy category (+5 pts)")

    # 3. Manufacturer RAG Enrichment Signal (up to 25 points)
    if r.get("enrichment_applied"):
        score_points += 25.0
        doc_refs = r.get("enrichment_doc_refs", [])
        ref_str = f" from {', '.join(doc_refs)}" if doc_refs else ""
        reasons.append(f"✓ Verified and enriched via manufacturer datasheet RAG{ref_str} (+25 pts)")
    else:
        score_points += 15.0  # Base standard catalog record

    # 4. Brand & Manufacturer Verification (up to 15 points)
    brand = r.get("brand_name")
    mfr = r.get("manufacturer_name")
    if brand and mfr and "manufacturer_brand_mismatch" not in flags:
        score_points += 15.0
        reasons.append(f"✓ Canonical Brand ('{brand}') & Manufacturer ('{mfr}') resolved (+15 pts)")
    elif brand or mfr:
        score_points += 8.0
        reasons.append(f"✓ Entity identified: {brand or mfr} (+8 pts)")
    else:
        reasons.append("⚠ Unidentified brand/manufacturer (0 pts)")

    # 5. Validation Cleanliness (up to 5 points)
    if not flags:
        score_points += 5.0
        reasons.append("✓ Zero validation warnings or schema conflicts (+5 pts)")

    # Penalties
    if "manufacturer_brand_mismatch" in flags:
        score_points -= 20.0
        reasons.append("✗ Penalty: Potential manufacturer/brand discrepancy (-20 pts)")
    if "missing_classpath" in flags or "unclassified_fallback" in flags:
        score_points -= 15.0
        reasons.append("✗ Penalty: Ambiguous category classification (-15 pts)")
    if "duplicate_detected" in flags:
        reasons.append("⚠ Duplicate record detected in catalog")

    # Final normalized score (0.0 to 1.0)
    final_score = max(0.0, min(1.0, score_points / 100.0))
    rounded_score = round(final_score, 2)

    # Determine Tier
    if rounded_score >= HIGH_THRESHOLD:
        tier = "HIGH"
    elif rounded_score >= MEDIUM_THRESHOLD:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    # Route to review if low confidence, ungrounded, or validation errors
    needs_review = (
        rounded_score < 0.70
        or bool(r.get("review_reasons"))
        or "manufacturer_brand_mismatch" in flags
        or "duplicate_detected" in flags
    )

    r["overall_confidence"] = rounded_score
    r["confidence_tier"] = tier
    r["confidence_reasons"] = reasons
    r["needs_review"] = needs_review

    return r


def score_confidence(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scores confidence and builds explainability reasons for all products."""
    for r in rows:
        score_single_product(r)
    return rows
