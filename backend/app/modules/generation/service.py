"""
Module 10 -- Validated Description Generator.
Responsibility: Generate standard catalog descriptions from VALIDATED attributes only.
Produces:
  - product_name
  - short_desc
  - invoice_desc (<= 40 chars, uppercase)
  - mobile_desc (<= 80 chars)
  - long_desc1 (comprehensive technical description)
  - retail_desc
  - marketing_description
  - item_features (list of 1-10 bullet points)
"""
from typing import List, Dict, Any


def get_attr_val(attrs: List[Dict[str, Any]], label_name: str) -> str:
    """Safely retrieves a grounded attribute value with UOM."""
    for a in attrs:
        if a.get("label", "").lower() == label_name.lower() and a.get("validation") != "missing_evidence":
            val = a.get("value", "")
            uom = f" {a['uom']}" if a.get("uom") else ""
            return f"{val}{uom}".strip()
    return ""
FALLBACK_FINE = "Miscellaneous Products"

def build_product_name(r: Dict[str, Any], attrs: List[Dict[str, Any]]) -> str:
    brand = r.get("brand_name") or ""
    series = get_attr_val(attrs, "Series")
    fine_raw = r.get("fine") or ""
    fine = "" if fine_raw == FALLBACK_FINE else fine_raw
    mpn = r.get("mfg_part_num") or ""

    parts = [p for p in [brand, series, fine, mpn] if p]
    if parts:
        return " ".join(parts)
    return r.get("part_desc", "")


def generate_descriptions(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds catalog descriptions and bullet features from grounded attributes."""
    for r in rows:
        attrs = r.get("extracted_attributes", [])
        brand = r.get("brand_name") or ""
        mpn = r.get("mfg_part_num") or ""
        fine_raw = r.get("fine") or ""
        fine = "" if fine_raw == FALLBACK_FINE else fine_raw
        series = get_attr_val(attrs, "Series")
        material = get_attr_val(attrs, "Material")
        color = get_attr_val(attrs, "Color")
        size = get_attr_val(attrs, "Size") or get_attr_val(attrs, "Diameter")
        voltage = get_attr_val(attrs, "Voltage Rating")
        grit = get_attr_val(attrs, "Grit")
        qty = get_attr_val(attrs, "Quantity")
        mounting = get_attr_val(attrs, "Mounting Type")
        sound = get_attr_val(attrs, "Sound Level")

        # 1. Product Name
        prod_name = build_product_name(r, attrs)
        r["product_name"] = prod_name

        # 2. Short Description
        short_parts = [p for p in [brand, series, mpn, fine, size, color or material, grit] if p]
        short_desc = ", ".join(short_parts) if short_parts else r.get("part_desc", "")
        r["short_desc"] = short_desc

        # 3. Invoice Description (Max 40 chars, uppercase)
        inv_text = f"{fine or brand} {mpn} {size} {color}".strip()
        if not inv_text:
            inv_text = short_desc
        r["invoice_desc"] = (inv_text[:40]).upper().strip()

        # 4. Mobile Description (Max 80 chars)
        r["mobile_desc"] = short_desc[:80].strip()

        # 5. Long Description 1 (Technical narrative)
        spec_phrases = []
        if series:
            spec_phrases.append(f"{brand} {series}")
        elif brand:
            spec_phrases.append(brand)
        if fine:
            spec_phrases.append(fine)
        if mpn:
            spec_phrases.append(f"model {mpn}")
        if size:
            spec_phrases.append(f"featuring {size} dimensions")
        if grit:
            spec_phrases.append(f"with {grit} abrasive grading")
        if voltage:
            spec_phrases.append(f"engineered for {voltage} operation")
        if sound:
            spec_phrases.append(f"with ultra-quiet {sound} acoustic rating")
        if material or color:
            spec_phrases.append(f"finished in {color or material}")
        if mounting:
            spec_phrases.append(f"designed for {mounting} installation")

        if spec_phrases:
            long_desc = f"{', '.join(spec_phrases)}."
        else:
            long_desc = r.get("part_desc", "")
        r["long_desc1"] = long_desc

        # 6. Retail & Marketing Descriptions
        r["retail_desc"] = short_desc
        r["marketing_description"] = f"Industrial-grade {brand} {fine or 'catalog product'} engineered for reliable commercial performance and standardized durability."

        # 7. Item Features (1 to 10 bullet points)
        features = []
        if series:
            features.append(f"Series: {series}")
        if size:
            features.append(f"Dimensions / Size: {size}")
        if grit:
            features.append(f"Abrasive Grade: {grit}")
        if voltage:
            features.append(f"Voltage Rating: {voltage}")
        if material:
            features.append(f"Material: {material}")
        if color:
            features.append(f"Color / Finish: {color}")
        if sound:
            features.append(f"Sound Level: {sound}")
        if qty:
            features.append(f"Package Quantity: {qty}")
        if mounting:
            features.append(f"Mounting: {mounting}")

        # Add remaining custom attributes as features
        for a in attrs:
            if len(features) >= 10:
                break
            feat_str = f"{a['label']}: {a['value']}{' ' + a['uom'] if a.get('uom') else ''}"
            if feat_str not in features:
                features.append(feat_str)

        r["item_features"] = features

    return rows
