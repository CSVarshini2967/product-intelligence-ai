"""
Module 8 -- Validation Engine.
Responsibility: Deterministic validation of extracted attributes, anti-hallucination checks,
schema rules, UOM compatibility, and cross-field consistency.
"""
from typing import List, Dict, Any

VALID_UOM_MAP = {
    "Voltage Rating": {"V"},
    "Amperage Rating": {"A"},
    "Wattage": {"W"},
    "Battery Capacity": {"Ah"},
    "Horsepower": {"HP"},
    "Diameter": {"in"},
    "Thickness": {"in"},
    "Arbor Size": {"in"},
    "Sound Level": {"dBA"},
    "Max Operating Speed": {"RPM"},
    "Energy Consumption": {"kWh"},
    "Number of Teeth": {"T"},
}


def validate_row(r: Dict[str, Any]) -> Dict[str, Any]:
    """Applies all validation rules to a single product record."""
    flags = r.setdefault("flags", [])
    review_reasons = r.setdefault("review_reasons", [])

    # 1. Classification validation
    if not r.get("classpath"):
        flags.append("missing_classpath")
        review_reasons.append("Category classification missing")

    # 2. Attribute ground check & UOM validation
    attrs = r.get("extracted_attributes", [])
    for attr in attrs:
        label = attr.get("label", "")
        evidence = attr.get("evidence")
        inferred = attr.get("inferred", False)
        uom = attr.get("uom")

        # Anti-hallucination rule:
        # IF generated_value != null AND evidence == null THEN status = FAILED
        if not evidence and not inferred:
            attr["validation"] = "missing_evidence"
            attr["confidence"] = 0.3
            flags.append(f"unsupported_attr_{label}")
            review_reasons.append(f"Attribute '{label}' lacks ground evidence")
        elif inferred and not evidence:
            attr["validation"] = "unverified_inference"
            attr["confidence"] = 0.5
            flags.append(f"inferred_attr_{label}")
        else:
            attr["validation"] = "grounded"

        # UOM validity check
        if label in VALID_UOM_MAP and uom:
            if uom not in VALID_UOM_MAP[label]:
                attr["validation"] = "invalid_uom"
                attr["confidence"] = 0.2
                flags.append(f"invalid_uom_{label}_{uom}")
                review_reasons.append(f"Invalid UOM '{uom}' for attribute '{label}'")

    # 3. Manufacturer / Brand consistency check
    mfr = (r.get("manufacturer_name") or "").lower()
    brand = (r.get("brand_name") or "").lower()
    # If both present, verify they don't severely contradict
    if mfr and brand:
        # Known multi-brand parent companies are allowed
        allowed_parents = [
            "freud", "3m", "appliance", "black & decker", "schneider",
            "cooper", "signify", "acuity", "stanley", "rheem"
        ]
        is_known_parent = any(p in mfr for p in allowed_parents)
        if not is_known_parent and mfr.split()[0] not in brand and brand.split()[0] not in mfr:
            flags.append("manufacturer_brand_mismatch")
            review_reasons.append(f"Potential Manufacturer/Brand mismatch: '{r.get('manufacturer_name')}' vs '{r.get('brand_name')}'")

    # 4. Duplicate flag check
    dup_info = r.get("duplicate_info", {})
    if dup_info.get("status") in ["DUPLICATE", "POSSIBLE_DUPLICATE"]:
        review_reasons.append(f"Duplicate warning: {dup_info.get('match_reason')}")

    return r


def validate(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Runs validation engine across all products."""
    for r in rows:
        validate_row(r)
    return rows
