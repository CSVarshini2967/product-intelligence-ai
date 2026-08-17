"""
Module 1 -- Ingestion & Pre-Flight Analysis.
Responsibility: Read uploaded product data (CSV/DataFrame), validate columns,
detect and strip placeholder values, generate pre-flight telemetry, and
convert to standardized dictionary records for downstream modules.
"""
from typing import Tuple, List, Dict, Any
import pandas as pd

EXPECTED_COLUMNS = [
    "Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"
]

PLACEHOLDER_VALUES = {
    "-- Unbranded --",
    "-- No Unilog Brand --",
    "-- No DIB Brand --",
    "-- UNBRANDED --",
    "COMMODITY - UNBRANDED",
    "COMMODITY-UNBRANDED",
    "N/A",
    "n/a",
    "NA",
    "UNKNOWN",
    "Unknown",
    "NONE",
    "None",
    "none",
    "--",
    "-",
    "",
}


def clean_brand_field(val: Any) -> str:
    if val is None or pd.isna(val):
        return ""
    s = str(val).strip()
    if s in PLACEHOLDER_VALUES:
        return ""
    return s


def ingest(df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Ingest a DataFrame and produce sanitized rows along with pre-flight telemetry.
    """
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        # Fallback: if user uploaded partial columns, create missing ones
        for c in missing:
            df[c] = ""

    total_rows = len(df)
    valid_rows = 0
    invalid_rows = 0
    placeholder_count = 0
    warnings = []

    rows = []
    for i, row in df.iterrows():
        mpn = str(row.get("Mfg_Part_Num", "")).strip() if pd.notna(row.get("Mfg_Part_Num")) else ""
        desc = str(row.get("Part_Desc", "")).strip() if pd.notna(row.get("Part_Desc")) else ""
        manuf = str(row.get("Part_Manuf", "")).strip() if pd.notna(row.get("Part_Manuf")) else ""

        if not mpn and not desc:
            invalid_rows += 1
            warnings.append(f"Row {i}: Missing both Mfg_Part_Num and Part_Desc")
            continue

        valid_rows += 1

        e1_b = clean_brand_field(row.get("E1_Brand"))
        uni_b = clean_brand_field(row.get("Unilog_Brand"))
        dib_b = clean_brand_field(row.get("DIB_Brand"))

        # Count detected placeholders
        for raw_val in [row.get("E1_Brand"), row.get("Unilog_Brand"), row.get("DIB_Brand")]:
            if str(raw_val).strip() in PLACEHOLDER_VALUES:
                placeholder_count += 1

        record = {
            "row_id": int(i),
            "mfg_part_num": mpn,
            "part_desc": desc,
            "part_manuf": manuf if manuf not in PLACEHOLDER_VALUES else "",
            "e1_brand": e1_b,
            "unilog_brand": uni_b,
            "dib_brand": dib_b,
            "flags": [],
            "extracted_attributes": [],
            "confidence_reasons": [],
            "review_reasons": [],
            "needs_review": False,
            "overall_confidence": 0.0,
            "confidence_tier": "LOW",
            "review_status": "PENDING",
            "human_corrections": {},
        }
        rows.append(record)

    telemetry = {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "columns_detected": list(df.columns),
        "placeholder_brand_values_cleaned": placeholder_count,
        "warnings": warnings[:10],
    }

    return rows, telemetry
