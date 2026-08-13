"""
Module 2 -- Cleaning & Normalization.
Responsibility: deterministic cleanup that does NOT need AI --
regex-based unit normalization and abbreviation expansion, plus a hook
for fuzzy-matching manufacturer names against a reference list.

This module should be 100% correct by construction (it's just rules),
which makes it your "free" accuracy points and a safe demo moment: this
part never hallucinates.
"""
import re

# Minimal starter UOM map -- expand this against the real
# Unilog_Master_UOM_Standards file once you have it.
UOM_PATTERNS = [
    (re.compile(r'(\d)\s*(inch|inches|in\.?)\b', re.IGNORECASE), r'\1 in'),
    (re.compile(r'(\d)\s*(ft\.?|feet|foot)\b', re.IGNORECASE), r'\1 ft'),
    (re.compile(r'(\d)\s*(lbs?\.?|pounds?)\b', re.IGNORECASE), r'\1 lb'),
]

# Common abbreviation expansions seen in Part_Desc strings.
ABBREVIATIONS = {
    "SS": "Stainless Steel",
    "BSS": "Black Stainless Steel",
    "BK": "Black",
    "WH": "White",
    "GE": "GE",  # brand token, left as-is
}


def normalize_units(text: str) -> str:
    for pattern, replacement in UOM_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def clean(rows: list[dict]) -> list[dict]:
    for r in rows:
        desc = r.get("part_desc", "") or ""
        r["part_desc_normalized"] = normalize_units(desc)
        # TODO: fuzzy-match part_manuf / brand fields against the real
        # manufacturer/brand reference list with RapidFuzz once available.
        r["manufacturer_guess"] = r.get("part_manuf", "")
    return rows
