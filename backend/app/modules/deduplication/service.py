"""
Module 3 -- De-duplication.
Responsibility: Detect potential duplicate products using exact Mfg_Part_Num,
normalized alphanumeric part numbers, and RapidFuzz description similarity.
Classifies into DUPLICATE, POSSIBLE_DUPLICATE, and UNIQUE.
"""
import re
from typing import List, Dict, Any
from rapidfuzz import fuzz


def normalize_part_number(mpn: str) -> str:
    """Strip all hyphens, spaces, dots for alphanumeric matching."""
    if not mpn:
        return ""
    return re.sub(r'[^A-Z0-9]', '', str(mpn).upper())


def deduplicate(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans the product list and computes duplicate signals.
    Does NOT delete records; classifies status and attaches cluster IDs.
    """
    seen_exact_mpn: Dict[str, int] = {}
    seen_norm_mpn: Dict[str, int] = {}

    for i, r in enumerate(rows):
        mpn = str(r.get("mfg_part_num", "")).strip()
        norm_mpn = normalize_part_number(mpn)
        desc = str(r.get("part_desc", "")).strip()

        dup_status = "UNIQUE"
        sim_score = 0.0
        reason = None
        cluster_id = None

        # 1. Exact Part Number check
        if mpn and mpn in seen_exact_mpn:
            orig_idx = seen_exact_mpn[mpn]
            dup_status = "DUPLICATE"
            sim_score = 1.0
            cluster_id = f"CLUST-EXACT-{norm_mpn}"
            reason = f"Exact Mfg_Part_Num match with row {orig_idx}"
        elif norm_mpn and norm_mpn in seen_norm_mpn:
            # 2. Normalized alphanumeric check
            orig_idx = seen_norm_mpn[norm_mpn]
            dup_status = "DUPLICATE"
            sim_score = 0.98
            cluster_id = f"CLUST-NORM-{norm_mpn}"
            reason = f"Normalized part number match with row {orig_idx}"
        else:
            # 3. Fuzzy similarity against previous 50 items (sliding window for efficiency)
            window_start = max(0, i - 50)
            best_sim = 0.0
            best_match_idx = -1

            for prev_idx in range(window_start, i):
                prev_row = rows[prev_idx]
                prev_desc = str(prev_row.get("part_desc", "")).strip()
                
                # Check description token set ratio
                ratio = fuzz.token_set_ratio(desc.lower(), prev_desc.lower())
                if ratio > best_sim:
                    best_sim = ratio
                    best_match_idx = prev_idx

            if best_sim >= 95.0:
                dup_status = "DUPLICATE"
                sim_score = round(best_sim / 100.0, 2)
                cluster_id = f"CLUST-FUZZ-{best_match_idx}"
                reason = f"High description similarity ({best_sim:.0f}%) with row {best_match_idx}"
            elif best_sim >= 85.0:
                dup_status = "POSSIBLE_DUPLICATE"
                sim_score = round(best_sim / 100.0, 2)
                cluster_id = f"CLUST-POSS-{best_match_idx}"
                reason = f"Possible duplicate ({best_sim:.0f}% similarity) with row {best_match_idx}"

        if mpn:
            seen_exact_mpn[mpn] = i
        if norm_mpn:
            seen_norm_mpn[norm_mpn] = i

        r["duplicate_info"] = {
            "status": dup_status,
            "cluster_id": cluster_id,
            "similarity_score": sim_score,
            "match_reason": reason,
        }

        if dup_status == "DUPLICATE":
            r.setdefault("flags", []).append("duplicate_detected")
        elif dup_status == "POSSIBLE_DUPLICATE":
            r.setdefault("flags", []).append("possible_duplicate")

    return rows
