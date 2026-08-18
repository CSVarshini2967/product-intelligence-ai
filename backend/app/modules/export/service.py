"""
Module -- Export Engine.
Responsibility: Produce dual-level export formats:
  A. Final Catalog Delivery Format CSV (matching all 150+ columns of the target schema)
  B. Intelligence / Audit Output CSV (linking every attribute to evidence, source, method, confidence, validation)
"""
import pandas as pd
from typing import List, Dict, Any
SKU_BASE = 1_000_001
DELIVERY_FORMAT_COLUMNS = [
    "MFR URL", "Ref URL 1", "Ref URL 2", "Ref URL 3", "Ref URL 4", "Ref URL 5",
    "PART_NUMBER", "Dept", "Class", "Fine", "SKU - MY_PART_NUMBER",
    "Mfg_Part_Num", "Part_Desc", "E1_Brand", "Unilog_Brand", "DIB_Brand", "Part_Manuf",
    "MANUFACTURER_NAME", "BRAND_NAME", "TRADE_NAME", "MANUFACTURER_PART_NUMBER", "ALTERNATE_PART_NUMBER",
    "Classpath", "MOBILE_DESC", "INVOICE_DESC", "SHORT_DESC", "LONG_DESC1", "RETAIL_DESC", "MARKETING_DESCRIPTION",
    "ITEM_FEATURES_1", "ITEM_FEATURES_2", "ITEM_FEATURES_3", "ITEM_FEATURES_4", "ITEM_FEATURES_5",
    "ITEM_FEATURES_6", "ITEM_FEATURES_7", "ITEM_FEATURES_8", "ITEM_FEATURES_9", "ITEM_FEATURES_10",
    "ITEM_FEATURES_11", "ITEM_FEATURES_12", "ITEM_FEATURES_13", "ITEM_FEATURES_14", "ITEM_FEATURES_15",
    "ITEM_FEATURES_16", "ITEM_FEATURES_17", "ITEM_FEATURES_18", "ITEM_FEATURES_19", "ITEM_FEATURES_20",
    "With", "Standard/Approvals", "Prop 65", "Application", "Includes", "Product Name",
]

# Generate numbered attribute columns (ATTRIBUTE_LABEL 1..50, ATTRIBUTE_VALUE 1..50, ATTRIBUTE_UOM 1..50)
for i in range(1, 51):
    DELIVERY_FORMAT_COLUMNS.extend([f"ATTRIBUTE_LABEL {i}", f"ATTRIBUTE_VALUE {i}", f"ATTRIBUTE_UOM {i}"])

DELIVERY_FORMAT_COLUMNS.extend([
    "UPC", "EAN", "GTIN", "UNSPSC", "Warranty", "List Price", "Selling Qty", "Selling UOM", "Standard Packaging Information",
    "LENGTH", "LENGTH_UOM", "HEIGHT", "HEIGHT_UOM", "WIDTH", "WIDTH_UOM", "WEIGHT", "WEIGHT_UOM", "VOLUME", "VOLUME_UOM",
    "Product Image", "Alternate Image 1", "Alternate Image 2", "Alternate Image 3", "Alternate Image 4",
    "SDS", "SDS_1", "Warranty Information", "Catalog", "Specification Sheet", "Instruction/Installation Manual",
    "Service Manual", "Owners/User Manual", "Line Drawing", "MTR", "RoHS", "Full Engineering Drawing",
    "Energy Star Guide", "Technical Bulletin", "Submittal", "Compatibility Chart", "Size Chart",
    "Product Label/Insert", "Video Link", "Video Link 1", "Country Of Origin", "Discontinued", "Actual Image (Yes/No)"
])


def build_output(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """Builds the 150+ column Final Delivery Catalog DataFrame."""
    formatted_rows = []

    for r in rows:
        row_dict = {col: "" for col in DELIVERY_FORMAT_COLUMNS}

        # Core identifiers
        row_dict["PART_NUMBER"] = r.get("mfg_part_num", "")
        row_dict["Dept"] = r.get("dept", "")
        row_dict["Class"] = r.get("class_name", "")
        row_dict["Fine"] = r.get("fine", "")
        row_dict["SKU - MY_PART_NUMBER"] = str(SKU_BASE + int(r.get("row_id", 0)))
        row_dict["Mfg_Part_Num"] = r.get("mfg_part_num", "")
        row_dict["Part_Desc"] = r.get("part_desc", "")
        row_dict["E1_Brand"] = r.get("e1_brand", "")
        row_dict["Unilog_Brand"] = r.get("unilog_brand", "")
        row_dict["DIB_Brand"] = r.get("dib_brand", "")
        row_dict["Part_Manuf"] = r.get("part_manuf", "")
        row_dict["MANUFACTURER_NAME"] = r.get("manufacturer_name", "")
        row_dict["BRAND_NAME"] = r.get("brand_name", "")
        row_dict["MANUFACTURER_PART_NUMBER"] = r.get("mfg_part_num", "")
        row_dict["Classpath"] = r.get("classpath", "")

        # Descriptions
        row_dict["Product Name"] = r.get("product_name", "")
        row_dict["MOBILE_DESC"] = r.get("mobile_desc", "")
        row_dict["INVOICE_DESC"] = r.get("invoice_desc", "")
        row_dict["SHORT_DESC"] = r.get("short_desc", "")
        row_dict["LONG_DESC1"] = r.get("long_desc1", "")
        row_dict["RETAIL_DESC"] = r.get("retail_desc", "")
        row_dict["MARKETING_DESCRIPTION"] = r.get("marketing_description", "")

        # Item Features (up to 20)
        features = r.get("item_features", [])
        for f_idx, feat in enumerate(features[:20], start=1):
            row_dict[f"ITEM_FEATURES_{f_idx}"] = feat

        # Numbered Attributes (up to 50)
        attrs = r.get("extracted_attributes", [])
        for a_idx, attr in enumerate(attrs[:50], start=1):
            row_dict[f"ATTRIBUTE_LABEL {a_idx}"] = attr.get("label", "")
            row_dict[f"ATTRIBUTE_VALUE {a_idx}"] = attr.get("value", "")
            row_dict[f"ATTRIBUTE_UOM {a_idx}"] = attr.get("uom", "") or ""

        # Assets & Specs
        doc_refs = r.get("enrichment_doc_refs", [])
        if doc_refs:
            row_dict["Specification Sheet"] = doc_refs[0]
            row_dict["Actual Image (Yes/No)"] = "Yes"
        row_dict["MFR URL"] = r.get("enrichment_mfr_url", "")
        formatted_rows.append(row_dict)

    return pd.DataFrame(formatted_rows, columns=DELIVERY_FORMAT_COLUMNS)


def build_audit_export(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Builds the Intelligence & Audit DataFrame where each row represents
    an extracted attribute linked with evidence, method, confidence, and validation.
    """
    audit_records = []

    for r in rows:
        row_id = r.get("row_id")
        mpn = r.get("mfg_part_num")
        desc = r.get("part_desc")
        overall_conf = r.get("overall_confidence", 0.0)
        tier = r.get("confidence_tier", "LOW")
        rev_status = r.get("review_status", "PENDING")
        flags = "; ".join(r.get("flags", []))

        attrs = r.get("extracted_attributes", [])
        if attrs:
            for attr in attrs:
                audit_records.append({
                    "Product_ID": row_id,
                    "Mfg_Part_Num": mpn,
                    "Part_Desc": desc,
                    "Attribute_Label": attr.get("label"),
                    "Attribute_Value": attr.get("value"),
                    "Attribute_UOM": attr.get("uom", ""),
                    "Evidence": attr.get("evidence", ""),
                    "Source": attr.get("source", ""),
                    "Method": attr.get("method", ""),
                    "Inferred": attr.get("inferred", False),
                    "Attribute_Confidence": attr.get("confidence", 1.0),
                    "Overall_Confidence": overall_conf,
                    "Confidence_Tier": tier,
                    "Validation_Status": attr.get("validation", ""),
                    "Review_Status": rev_status,
                    "Source_Reference": attr.get("source_reference", ""),
                    "System_Flags": flags,
                })
        else:
            # Entry for items without extracted attributes
            audit_records.append({
                "Product_ID": row_id,
                "Mfg_Part_Num": mpn,
                "Part_Desc": desc,
                "Attribute_Label": "None",
                "Attribute_Value": "None",
                "Attribute_UOM": "",
                "Evidence": "",
                "Source": "Part_Desc",
                "Method": "none",
                "Inferred": False,
                "Attribute_Confidence": 0.0,
                "Overall_Confidence": overall_conf,
                "Confidence_Tier": tier,
                "Validation_Status": "no_attributes",
                "Review_Status": rev_status,
                "Source_Reference": "",
                "System_Flags": flags,
            })

    return pd.DataFrame(audit_records)
