"""
Module 1 -- Ingestion.
Responsibility: read the uploaded CSV, validate expected columns, convert
to a list of plain dicts ("row objects") that every downstream module
reads and writes to. Keeping this a plain dict (not a class) keeps every
module decoupled -- any module can add new keys without touching others.
"""
import pandas as pd

EXPECTED_COLUMNS = [
    "Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf"
]

PLACEHOLDER_VALUES = {"-- Unbranded --", "-- No Unilog Brand --", "-- No DIB Brand --"}


def ingest(df: pd.DataFrame) -> list[dict]:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Uploaded CSV is missing expected columns: {missing}")

    rows = []
    for i, row in df.iterrows():
        record = {
            "row_id": i,
            "mfg_part_num": row["Mfg_Part_Num"],
            "part_desc": row["Part_Desc"],
            "part_manuf": row["Part_Manuf"],
        }
        # Strip placeholder brand values immediately -- treat as genuinely empty,
        # not as a real brand string, per the solution guide's explicit warning.
        for src_col, key in [("E1_Brand", "e1_brand"), ("Unilog_Brand", "unilog_brand"),
                              ("DIB_Brand", "dib_brand")]:
            val = row.get(src_col)
            record[key] = "" if val in PLACEHOLDER_VALUES or pd.isna(val) else val
        rows.append(record)
    return rows
