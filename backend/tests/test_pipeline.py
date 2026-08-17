"""
Automated unit and integration test suite for Product Intelligence AI.
"""
import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.pipeline import run_pipeline
from app.modules.ingestion.service import ingest
from app.modules.cleaning.service import clean
from app.modules.classification.service import classify
from app.modules.extraction.service import extract_attributes
from app.modules.deduplication.service import deduplicate
from app.modules.validation.service import validate
from app.modules.confidence.service import score_confidence
from app.modules.review.service import apply_review_action, get_review_queue
from app.modules.evaluation.service import run_evaluation


class TestProductIntelligencePipeline(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame([
            {
                "Mfg_Part_Num": "3MABR-7100075678",
                "Part_Desc": "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "Part_Manuf": "Jam Industrial Supply LLC (JAMIN)"
            },
            {
                "Mfg_Part_Num": "PDSH4816AF",
                "Part_Desc": "PDSH4816AF Dishwasher SS - Display Only",
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "Part_Manuf": "Appliance Dealers Cooperative (APPDE)"
            },
            {
                "Mfg_Part_Num": "49-94-0013",
                "Part_Desc": '49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc',
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "Part_Manuf": "Milwaukee Accessory (4031)"
            },
            {
                "Mfg_Part_Num": "49-94-0013",
                "Part_Desc": '49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc',
                "E1_Brand": "-- Unbranded --",
                "Unilog_Brand": "-- No Unilog Brand --",
                "DIB_Brand": "-- No DIB Brand --",
                "Part_Manuf": "Milwaukee Accessory (4031)"
            }
        ])

    def test_ingestion_strips_placeholders(self):
        rows, telemetry = ingest(self.sample_df)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["e1_brand"], "")
        self.assertEqual(rows[0]["unilog_brand"], "")
        self.assertGreater(telemetry["placeholder_brand_values_cleaned"], 0)

    def test_cleaning_resolves_canonical_entities(self):
        rows, _ = ingest(self.sample_df)
        cleaned = clean(rows)
        self.assertEqual(cleaned[0]["brand_name"], "3M")
        self.assertEqual(cleaned[2]["brand_name"], "Milwaukee")
        self.assertEqual(cleaned[2]["manufacturer_name"], "Milwaukee Electric Tool Corp")

    def test_deduplication_detects_exact_duplicates(self):
        rows, _ = ingest(self.sample_df)
        cleaned = clean(rows)
        deduped = deduplicate(cleaned)
        self.assertEqual(deduped[3]["duplicate_info"]["status"], "DUPLICATE")

    def test_classification_routes_categories(self):
        rows, _ = ingest(self.sample_df)
        cleaned = clean(rows)
        classified = classify(cleaned)
        self.assertIn("Dishwashers", classified[1]["classpath"])
        self.assertIn("Cut-Off Wheels", classified[2]["classpath"])

    def test_extraction_attaches_evidence(self):
        rows, _ = ingest(self.sample_df)
        cleaned = clean(rows)
        classified = classify(cleaned)
        extracted = extract_attributes(classified)
        
        attrs_3m = extracted[0]["extracted_attributes"]
        labels = [a["label"] for a in attrs_3m]
        self.assertIn("Grit", labels)
        self.assertIn("Quantity", labels)
        
        for a in attrs_3m:
            self.assertIsNotNone(a.get("evidence"))
            self.assertEqual(a.get("validation"), "grounded")

    def test_human_review_action(self):
        rows, _ = ingest(self.sample_df)
        cleaned = clean(rows)
        classified = classify(cleaned)
        extracted = extract_attributes(classified)
        validated = validate(extracted)
        scored = score_confidence(validated)
        
        target = scored[0]
        updated = apply_review_action(target, action="ACCEPT", reviewer_notes="Looks great")
        self.assertEqual(updated["review_status"], "ACCEPTED")
        self.assertFalse(updated["needs_review"])

    def test_evaluation_benchmark_runs(self):
        eval_result = run_evaluation(run_pipeline)
        self.assertEqual(eval_result["status"], "success")
        self.assertIn("overall_accuracy", eval_result["metrics"])
        self.assertGreater(eval_result["metrics"]["overall_accuracy"], 70.0)


if __name__ == "__main__":
    unittest.main()
