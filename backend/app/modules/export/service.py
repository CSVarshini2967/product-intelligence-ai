"""
Module 10 (part 1) -- Export.
Responsibility: flatten the internal row-object list back into a clean
output DataFrame, matching the shape of the real Delivery Format columns
where practical (Tier 1 fields from the plan).
"""
import pandas as pd


def build_output(rows: list[dict]) -> pd.DataFrame:
    flat_rows = []
    for r in rows:
        flat = {
            "Mfg_Part_Num": r.get("mfg_part_num"),
            "Part_Desc": r.get("part_desc"),
            "MANUFACTURER_NAME": r.get("manufacturer_name"),
            "BRAND_NAME": r.get("brand_name"),
            "Classpath": r.get("classpath"),
            "SHORT_DESC": r.get("short_desc"),
            "INVOICE_DESC": r.get("invoice_desc"),
            "MOBILE_DESC": r.get("mobile_desc"),
            "Overall_Confidence": r.get("overall_confidence"),
            "Needs_Review": r.get("needs_review"),
            "Flags": "; ".join(r.get("flags", [])),
        }
        # Flatten attributes into numbered columns, matching the real
        # ATTRIBUTE_LABEL/VALUE/UOM pattern.
        for i, attr in enumerate(r.get("extracted_attributes", []), start=1):
            flat[f"ATTRIBUTE_LABEL {i}"] = attr.get("label")
            flat[f"ATTRIBUTE_VALUE {i}"] = attr.get("value")
            flat[f"ATTRIBUTE_UOM {i}"] = attr.get("uom")
            flat[f"ATTRIBUTE_CONFIDENCE {i}"] = attr.get("confidence")
        flat_rows.append(flat)

    return pd.DataFrame(flat_rows)
