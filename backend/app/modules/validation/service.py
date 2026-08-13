"""
Module 7 -- Validation Engine.

Responsibility: deterministically check every extracted value. This is
core to the "constrained, not creative" requirement -- a value that isn't
grounded should be flagged, never silently shipped.

Checks applied (expand these against real LOV/UOM files once available):
  1. Was the attribute's evidence field present? (non-null evidence = can verify)
  2. Manufacturer/Brand mismatch check (the real ground truth itself has
     one of these -- e.g. Manufacturer="Rheem Manufacturing" but
     Brand="FRIGIDAIRE" on one row -- so this is a genuinely useful check,
     not a hypothetical).
  3. Classification succeeded (Module 3 didn't fail).
"""


def validate(rows: list[dict]) -> list[dict]:
    for r in rows:
        flags = r.setdefault("flags", [])

        if not r.get("classpath"):
            flags.append("no_classpath")

        for attr in r.get("extracted_attributes", []):
            if attr.get("inferred") and not attr.get("evidence"):
                attr["validation"] = "unverified_inference"
            elif attr.get("evidence"):
                attr["validation"] = "grounded"
            else:
                attr["validation"] = "missing_evidence"

        # Simple manufacturer/brand sanity check -- if both are present but
        # look nothing alike, flag for human review rather than silently
        # trusting the model's pairing.
        mfr = (r.get("manufacturer_name") or "").lower()
        brand = (r.get("brand_name") or "").lower()
        if mfr and brand and mfr.split()[0] not in brand and brand.split()[0] not in mfr:
            flags.append("manufacturer_brand_mismatch")

    return rows
