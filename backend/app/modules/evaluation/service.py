"""
Module 12 -- Evaluation Engine & Accuracy Benchmark.
Responsibility: Run evaluation against verified ground truth benchmark dataset.
Calculates REAL metrics:
  - Overall Field Accuracy (%)
  - Brand Accuracy (%)
  - Manufacturer Accuracy (%)
  - Classification Accuracy (%)
  - Attribute Extraction Accuracy (%)
  - Evidence Accuracy (%)
  - Hallucination Rate (%)
  - Human Review Rate (%)
"""
import os
import json
import pandas as pd
from typing import Dict, Any, List

BENCHMARK_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "reference", "benchmark_ground_truth.json"
)


def load_benchmark() -> List[Dict[str, Any]]:
    """Loads verified benchmark ground truth items."""
    norm_path = os.path.normpath(BENCHMARK_PATH)
    if not os.path.exists(norm_path):
        return []
    with open(norm_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _compute_evidence_grounding(processed_rows: List[Dict[str, Any]]) -> float:
    """
    Real evidence-grounding metric: of all extracted attributes across the
    benchmark run, what fraction have validation == 'grounded' (i.e. backed
    by an exact substring match rather than an unverified inference)?
    """
    total = 0
    grounded = 0
    for row in processed_rows:
        for attr in row.get("extracted_attributes", []):
            total += 1
            if attr.get("validation") == "grounded":
                grounded += 1
    if total == 0:
        return 0.0
    return round((grounded / total) * 100.0, 1)


def _compute_uom_accuracy(processed_rows: List[Dict[str, Any]], benchmark_items: List[Dict[str, Any]]) -> float:
    """
    Real UOM metric: for every ground-truth attribute that specifies a uom,
    check whether the pipeline's predicted attribute (matched by label) has
    the same normalized uom.
    """
    total = 0
    correct = 0
    for i, gt in enumerate(benchmark_items):
        pred = processed_rows[i] if i < len(processed_rows) else {}
        pred_attrs_by_label = {
            a.get("label", "").lower(): a for a in pred.get("extracted_attributes", [])
        }
        gt_uoms = gt.get("expected_uoms", {})
        for label, expected_uom in gt_uoms.items():
            if not expected_uom:
                continue
            total += 1
            pred_attr = pred_attrs_by_label.get(label.lower())
            if pred_attr and (pred_attr.get("uom") or "").strip().lower() == expected_uom.strip().lower():
                correct += 1
    if total == 0:
        return 0.0
    return round((correct / total) * 100.0, 1)


def run_evaluation(pipeline_func=None) -> Dict[str, Any]:
    """
    Evaluates the current pipeline against the verified ground truth benchmark.
    """
    if pipeline_func is None:
        from app.pipeline import run_pipeline
        pipeline_func = run_pipeline

    benchmark_items = load_benchmark()
    if not benchmark_items:
        return {
            "status": "error",
            "message": "Benchmark dataset not found",
            "metrics": {},
            "comparison_rows": []
        }

    # Convert benchmark to input DataFrame
    # Convert benchmark to input DataFrame.
    # IMPORTANT: Part_Manuf must be the RAW distributor/vendor string exactly
    # as it appears in production data (e.g. "Appliance Dealers Cooperative
    # (APPDE)"), never the expected_manufacturer answer -- feeding the answer
    # in silently inflates brand/manufacturer accuracy. Run migrate_benchmark.py
    # first to add "raw_part_manuf" to each benchmark item.
    input_records = []
    for item in benchmark_items:
        raw_manuf = item.get("raw_part_manuf")
        if raw_manuf is None:
            raise ValueError(
                f"Benchmark item {item.get('mfg_part_num')} is missing 'raw_part_manuf'. "
                "Run migrate_benchmark.py to add the real distributor string before "
                "evaluating, or brand/manufacturer accuracy will be invalid."
            )
        input_records.append({
            "Mfg_Part_Num": item.get("mfg_part_num", ""),
            "Part_Desc": item.get("part_desc", ""),
            "E1_Brand": item.get("raw_e1_brand", "-- Unbranded --"),
            "Unilog_Brand": "-- No Unilog Brand --",
            "DIB_Brand": item.get("raw_dib_brand", "-- No DIB Brand --"),
            "Part_Manuf": raw_manuf,
        })

    df_input = pd.DataFrame(input_records)
    pipeline_result = pipeline_func(df_input)
    processed_rows = pipeline_result.get("rows", [])

    # Evaluate each field
    total_samples = len(benchmark_items)
    brand_correct = 0
    mfr_correct = 0
    class_correct = 0
    attr_correct = 0
    total_expected_attrs = 0
    hallucinated_count = 0
    review_count = 0
    comparison_rows = []

    for i, gt in enumerate(benchmark_items):
        pred = processed_rows[i] if i < len(processed_rows) else {}
        
        # 1. Brand check
        gt_brand = (gt.get("expected_brand") or "").lower()
        pred_brand = (pred.get("brand_name") or "").lower()
        b_match = gt_brand == pred_brand or gt_brand in pred_brand or pred_brand in gt_brand
        if b_match and pred_brand:
            brand_correct += 1

        # 2. Manufacturer check
        gt_mfr = (gt.get("expected_manufacturer") or "").lower()
        pred_mfr = (pred.get("manufacturer_name") or "").lower()
        m_match = gt_mfr in pred_mfr or pred_mfr in gt_mfr or not gt_mfr
        if m_match and pred_mfr:
            mfr_correct += 1

        # 3. Classpath check
        gt_class = (gt.get("expected_classpath") or "").lower()
        pred_class = (pred.get("classpath") or "").lower()
        c_match = gt_class == pred_class or (gt_class.split(">")[-1] in pred_class)
        if c_match:
            class_correct += 1

        # 4. Attribute checks
        gt_attrs = gt.get("expected_attributes", {})
        total_expected_attrs += len(gt_attrs)
        pred_attrs = {a.get("label", "").lower(): a.get("value", "").lower() for a in pred.get("extracted_attributes", [])}
        
        matched_attrs_count = 0
        for exp_k, exp_v in gt_attrs.items():
            exp_k_lower = exp_k.lower()
            exp_v_lower = str(exp_v).lower()
            if exp_k_lower in pred_attrs:
                pred_v = pred_attrs[exp_k_lower]
                if exp_v_lower in pred_v or pred_v in exp_v_lower:
                    attr_correct += 1
                    matched_attrs_count += 1

        # 5. Hallucination check
        # An attribute is a hallucination if it has no evidence and is unverified
        for a in pred.get("extracted_attributes", []):
            if a.get("validation") == "missing_evidence":
                hallucinated_count += 1

        if pred.get("needs_review"):
            review_count += 1

        comparison_rows.append({
            "mfg_part_num": gt.get("mfg_part_num"),
            "part_desc": gt.get("part_desc"),
            "expected_brand": gt.get("expected_brand"),
            "predicted_brand": pred.get("brand_name"),
            "brand_match": b_match,
            "expected_classpath": gt.get("expected_classpath"),
            "predicted_classpath": pred.get("classpath"),
            "class_match": c_match,
            "expected_attributes": gt_attrs,
            "predicted_attributes": pred.get("extracted_attributes", []),
            "confidence": pred.get("overall_confidence", 0.0),
            "confidence_tier": pred.get("confidence_tier", "LOW"),
            "needs_review": pred.get("needs_review", False),
        })

    brand_acc = round((brand_correct / total_samples) * 100.0, 1) if total_samples else 0.0
    mfr_acc = round((mfr_correct / total_samples) * 100.0, 1) if total_samples else 0.0
    class_acc = round((class_correct / total_samples) * 100.0, 1) if total_samples else 0.0
    attr_acc = round((attr_correct / total_expected_attrs) * 100.0, 1) if total_expected_attrs else 0.0
    evidence_grounding_accuracy = _compute_evidence_grounding(processed_rows)
    uom_accuracy = _compute_uom_accuracy(processed_rows, benchmark_items)
    overall_acc = round((brand_acc * 0.25 + mfr_acc * 0.15 + class_acc * 0.30 + attr_acc * 0.30), 1)
    hallucination_rate = round((hallucinated_count / max(1, total_expected_attrs)) * 100.0, 1)
    review_rate = round((review_count / total_samples) * 100.0, 1) if total_samples else 0.0

    return {
        "status": "success",
        "benchmark_samples": total_samples,
        "metrics": {
            "overall_accuracy": overall_acc,
            "brand_accuracy": brand_acc,
            "manufacturer_accuracy": mfr_acc,
            "classification_accuracy": class_acc,
            "attribute_accuracy": attr_acc,
            "evidence_grounding_accuracy": evidence_grounding_accuracy,
            "uom_accuracy": uom_accuracy,
            "hallucination_rate": hallucination_rate,
            "review_rate": review_rate,
        },
        "comparison_rows": comparison_rows
    }
