"""
Module 7 -- Canonical Normalization.
Responsibility: Normalize attribute labels, units of measure (UOM), and values
according to master industrial taxonomy standards.
"""
from typing import List, Dict, Any

CANONICAL_LABEL_MAP = {
    "volts": "Voltage Rating",
    "voltage": "Voltage Rating",
    "amps": "Amperage Rating",
    "amperage": "Amperage Rating",
    "current": "Amperage Rating",
    "watts": "Wattage",
    "power": "Wattage",
    "dia": "Diameter",
    "dim": "Size",
    "dimensions": "Size",
    "finish": "Color",
    "sound": "Sound Level",
    "noise level": "Sound Level",
    "decibels": "Sound Level",
    "qty": "Quantity",
    "pack": "Packaging",
    "package": "Packaging",
    "teeth": "Number of Teeth",
    "tpi": "Number of Teeth",
}

CANONICAL_UOM_MAP = {
    "inch": "in",
    "inches": "in",
    "\"": "in",
    "in.": "in",
    "feet": "ft",
    "foot": "ft",
    "'": "ft",
    "ft.": "ft",
    "pounds": "lb",
    "pound": "lb",
    "lbs": "lb",
    "lbs.": "lb",
    "lb.": "lb",
    "volt": "V",
    "volts": "V",
    "v": "V",
    "amp": "A",
    "amps": "A",
    "a": "A",
    "watt": "W",
    "watts": "W",
    "w": "W",
    "dba": "dBA",
    "rpm": "RPM",
    "kw-hr": "kWh",
    "kwh": "kWh",
    "cu ft": "cu ft",
    "cf": "cu ft",
}


def normalize_attributes(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalizes labels and UOMs across all extracted attributes."""
    for r in rows:
        for attr in r.get("extracted_attributes", []):
            raw_label = (attr.get("label") or "").strip().lower()
            if raw_label in CANONICAL_LABEL_MAP:
                attr["label"] = CANONICAL_LABEL_MAP[raw_label]

            raw_uom = (attr.get("uom") or "").strip().lower()
            if raw_uom in CANONICAL_UOM_MAP:
                attr["uom"] = CANONICAL_UOM_MAP[raw_uom]

    return rows
