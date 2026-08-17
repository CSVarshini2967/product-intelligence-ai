"""
Module 11 -- Human Review Queue & Audit System.
Responsibility: Filter uncertain products/attributes needing review,
and handle Accept, Edit, Reject actions with persistent audit logging.
"""
from typing import List, Dict, Any, Optional

# In-memory store for active session review items and audit logs
_AUDIT_LOG: List[Dict[str, Any]] = []


def get_review_queue(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Returns all rows requiring human review."""
    queue = []
    for r in rows:
        if r.get("needs_review") or r.get("review_status") == "PENDING" and (r.get("overall_confidence", 1.0) < 0.75 or r.get("flags")):
            queue.append(r)
    return queue


def apply_review_action(
    row: Dict[str, Any],
    action: str,
    attribute_label: Optional[str] = None,
    edited_value: Optional[str] = None,
    edited_uom: Optional[str] = None,
    reviewer_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Applies a human action: ACCEPT, EDIT, REJECT.
    Updates the product record and records an audit log entry.
    """
    action_upper = action.upper()
    row_id = row.get("row_id")
    mpn = row.get("mfg_part_num")

    audit_entry = {
        "row_id": row_id,
        "mfg_part_num": mpn,
        "action": action_upper,
        "attribute_label": attribute_label,
        "edited_value": edited_value,
        "edited_uom": edited_uom,
        "reviewer_notes": reviewer_notes,
    }

    if action_upper == "ACCEPT":
        row["review_status"] = "ACCEPTED"
        row["needs_review"] = False
        row["overall_confidence"] = max(row.get("overall_confidence", 0.0), 0.95)
        row["confidence_tier"] = "HIGH"
        row.setdefault("confidence_reasons", []).append("✓ Approved by catalog data specialist")

    elif action_upper == "EDIT":
        row["review_status"] = "EDITED"
        row["needs_review"] = False
        row["overall_confidence"] = 1.0
        row["confidence_tier"] = "HIGH"
        row.setdefault("human_corrections", {})[attribute_label or "custom"] = edited_value

        # Update matching attribute if specified
        if attribute_label:
            for attr in row.get("extracted_attributes", []):
                if attr.get("label", "").lower() == attribute_label.lower():
                    attr["value"] = edited_value or attr["value"]
                    if edited_uom is not None:
                        attr["uom"] = edited_uom
                    attr["validation"] = "grounded"
                    attr["confidence"] = 1.0
                    attr["source"] = "human_curator"
                    break

        row.setdefault("confidence_reasons", []).append(f"✓ Human curator verified '{attribute_label}': {edited_value}")

    elif action_upper == "REJECT":
        row["review_status"] = "REJECTED"
        row["needs_review"] = False
        row["overall_confidence"] = 0.0
        row["confidence_tier"] = "LOW"
        row.setdefault("flags", []).append("human_rejected")

    _AUDIT_LOG.append(audit_entry)
    return row


def get_audit_log() -> List[Dict[str, Any]]:
    """Returns the history of all review actions performed."""
    return list(_AUDIT_LOG)
