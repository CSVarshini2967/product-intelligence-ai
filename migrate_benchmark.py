
import json
import os

BENCHMARK_PATH = os.path.join(
    os.path.dirname(__file__), "backend", "data", "reference", "benchmark_ground_truth.json"
)

# Real raw values pulled directly from the production sample input CSV,
# keyed by mfg_part_num. These are the actual messy vendor-code strings
# ("Company Name (CODE)") and brand columns as they exist pre-cleaning --
# NOT the clean expected_brand/expected_manufacturer answers.
RAW_OVERRIDES = {
    "PDSH4816AF":        {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "WDTS7024RZ":        {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "KDFM404KPS":        {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "PDT715SYVFS":       {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "LDPH5554D":         {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "KDTS424SBE":        {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "DF7004WE":          {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "FF7011WN":          {"raw_part_manuf": "Appliance Dealers Cooperative (APPDE)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "3MABR-7100075678":  {"raw_part_manuf": "Jam Industrial Supply LLC (JAMIN)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "3MABR-7100045865":  {"raw_part_manuf": "Jam Industrial Supply LLC (JAMIN)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "3MABR-7100048736":  {"raw_part_manuf": "Jam Industrial Supply LLC (JAMIN)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "DCB518ASTS06G":     {"raw_part_manuf": "Freud Inc (2435)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "DBD090094101F":     {"raw_part_manuf": "Freud Inc (2435)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "49-94-0013":        {"raw_part_manuf": "Milwaukee Accessory (4031)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "49-94-0101":        {"raw_part_manuf": "Milwaukee Accessory (4031)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "-- No DIB Brand --"},
    "543140016":         {"raw_part_manuf": "U S Lumber (3073)", "raw_e1_brand": "TREX", "raw_dib_brand": "-- No DIB Brand --"},
    "543140412":         {"raw_part_manuf": "U S Lumber (3073)", "raw_e1_brand": "TREX", "raw_dib_brand": "-- No DIB Brand --"},
    "ADB15516CS":        {"raw_part_manuf": "Parksite (6151)", "raw_e1_brand": "TIMBERTECH", "raw_dib_brand": "-- No DIB Brand --"},
    "65-1224":           {"raw_part_manuf": "Satco Prod Inc (5573)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "Satco"},
    "576355":            {"raw_part_manuf": "Phillips Lighting (5831)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "Philips"},
    "DCD1007B":          {"raw_part_manuf": "Black & Decker/dewlt (2585)", "raw_e1_brand": "-- Unbranded --", "raw_dib_brand": "DEWALT"},
}


def main():
    norm_path = os.path.normpath(BENCHMARK_PATH)
    if not os.path.exists(norm_path):
        raise FileNotFoundError(
            f"Benchmark file not found at {norm_path}. "
            "Check BENCHMARK_PATH matches your actual data/reference/ location."
        )

    with open(norm_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    patched = 0
    missing = []
    for item in items:
        mpn = item.get("mfg_part_num")
        override = RAW_OVERRIDES.get(mpn)
        if override is None:
            missing.append(mpn)
            continue
        item["raw_part_manuf"] = override["raw_part_manuf"]
        item["raw_e1_brand"] = override["raw_e1_brand"]
        item["raw_dib_brand"] = override["raw_dib_brand"]
        patched += 1

    with open(norm_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Patched {patched}/{len(items)} benchmark items with raw_* fields.")
    if missing:
        print(f"WARNING: no raw-field override found for: {missing}")
        print("Add these to RAW_OVERRIDES before evaluating, or they'll raise ValueError in run_evaluation().")


if __name__ == "__main__":
    main()