"""
Module 9 -- Description Generator.

Responsibility: build the standard description formats from VALIDATED
attributes only, using simple templates -- not free LLM generation. This
directly avoids the brief's stated failure mode: "a fluent description
made of invented values scores zero." A description built from a
template + validated fields can never contain a spec that wasn't already
checked by Modules 7-8.
"""


def _attr_value(attrs: list[dict], label: str) -> str:
    for a in attrs:
        if a["label"].lower() == label.lower() and a.get("validation") != "missing_evidence":
            uom = f" {a['uom']}" if a.get("uom") else ""
            return f"{a['value']}{uom}"
    return ""


def generate_descriptions(rows: list[dict]) -> list[dict]:
    for r in rows:
        brand = r.get("brand_name") or ""
        mpn = r.get("mfg_part_num") or ""
        attrs = r.get("extracted_attributes", [])

        material = _attr_value(attrs, "Material")
        size = _attr_value(attrs, "Size")

        parts = [p for p in [brand, mpn, material, size] if p]
        r["short_desc"] = ", ".join(parts) if parts else r.get("part_desc", "")
        r["invoice_desc"] = (r["short_desc"][:40]).upper()
        r["mobile_desc"] = r["short_desc"][:80]
    return rows
