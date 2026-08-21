"""
UniHack Product Intelligence Engine -- FastAPI Backend.
Provides complete REST API endpoints for catalog enrichment, human review,
analytics, manufacturer RAG knowledge base, evaluation benchmarks, and exports.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import io
import uuid
import os
from typing import Optional, List, Dict, Any

from app.pipeline import run_pipeline
from app.schemas.models import ReviewActionRequest
from app.modules.review.service import apply_review_action, get_review_queue, get_audit_log
from app.modules.evaluation.service import run_evaluation, load_benchmark
from app.modules.enrichment.service import load_manufacturer_kb, query_rag_by_mpn

app = FastAPI(
    title="Product Intelligence AI Engine",
    description="Evidence-driven product data enrichment, validation, confidence scoring, and review platform.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):(\d+)",
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory session store for current processed datasets
_STORE: Dict[str, Dict[str, Any]] = {}
_LATEST_JOB_ID: Optional[str] = None


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Product Intelligence AI Engine",
        "version": "2.0.0"
    }


@app.post("/api/process")
async def process_csv(file: Optional[UploadFile] = File(None)):
    """
    Runs the complete 12-module intelligence pipeline on an uploaded CSV
    or uses the sample dataset if no file is uploaded.
    """
    global _LATEST_JOB_ID

    if file and file.filename:
        raw_bytes = await file.read()
        df_input = pd.read_csv(io.BytesIO(raw_bytes))
    else:
        # Default sample dataset
        sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "Unihack__Sample_Dataset_-_Input.csv")
        if os.path.exists(sample_path):
            df_input = pd.read_csv(sample_path)
        else:
            sample_appliances = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "appliances_scope.csv")
            df_input = pd.read_csv(sample_appliances)

    result = run_pipeline(df_input)
    job_id = str(uuid.uuid4())[:8]
    _LATEST_JOB_ID = job_id

    # Save output CSVs
    output_path = os.path.join(OUTPUT_DIR, f"delivery_catalog_{job_id}.csv")
    audit_path = os.path.join(OUTPUT_DIR, f"audit_evidence_{job_id}.csv")
    
    result["output_df"].to_csv(output_path, index=False)
    result["audit_df"].to_csv(audit_path, index=False)

    _STORE[job_id] = {
        "job_id": job_id,
        "rows": result["rows"],
        "summary": result["summary"],
        "rows_processed": result["rows_processed"],
        "output_path": output_path,
        "audit_path": audit_path,
    }

    return {
        "job_id": job_id,
        "rows_processed": result["rows_processed"],
        "summary": result["summary"],
        "download_url": f"/api/download/{job_id}",
        "audit_download_url": f"/api/download/{job_id}/audit",
        "sample_products": result["rows"][:20],
    }


def _get_active_rows(job_id: Optional[str] = None) -> List[Dict[str, Any]]:
    global _LATEST_JOB_ID
    target_id = job_id or _LATEST_JOB_ID
    if not target_id or target_id not in _STORE:
        # Auto-run sample dataset if not yet processed
        sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "Unihack__Sample_Dataset_-_Input.csv")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "appliances_scope.csv")
        
        df_input = pd.read_csv(sample_path)
        result = run_pipeline(df_input)
        jid = str(uuid.uuid4())[:8]
        _LATEST_JOB_ID = jid
        _STORE[jid] = {
            "job_id": jid,
            "rows": result["rows"],
            "summary": result["summary"],
            "rows_processed": result["rows_processed"],
        }
        return result["rows"]

    return _STORE[target_id]["rows"]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in _STORE:
        raise HTTPException(status_code=404, detail="Job not found")
    data = _STORE[job_id]
    return {
        "job_id": job_id,
        "rows_processed": data["rows_processed"],
        "summary": data["summary"],
        "download_url": f"/api/download/{job_id}",
        "audit_download_url": f"/api/download/{job_id}/audit",
    }


@app.get("/api/products")
def list_products(
    job_id: Optional[str] = None,
    query: Optional[str] = None,
    dept: Optional[str] = None,
    confidence_tier: Optional[str] = None,
    needs_review: Optional[bool] = None,
    duplicate_only: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    """Lists processed products with filtering, search, and pagination."""
    rows = _get_active_rows(job_id)
    filtered = rows

    if query:
        q_lower = query.lower()
        filtered = [
            r for r in filtered
            if q_lower in str(r.get("part_desc", "")).lower()
            or q_lower in str(r.get("mfg_part_num", "")).lower()
            or q_lower in str(r.get("brand_name", "")).lower()
            or q_lower in str(r.get("manufacturer_name", "")).lower()
        ]

    if dept:
        filtered = [r for r in filtered if r.get("dept", "").lower() == dept.lower()]

    if confidence_tier:
        filtered = [r for r in filtered if r.get("confidence_tier", "").upper() == confidence_tier.upper()]

    if needs_review is not None:
        filtered = [r for r in filtered if r.get("needs_review") == needs_review]

    if duplicate_only:
        filtered = [
            r for r in filtered
            if r.get("duplicate_info", {}).get("status") in ["DUPLICATE", "POSSIBLE_DUPLICATE"]
        ]

    total_count = len(filtered)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_items = filtered[start_idx:end_idx]

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size if total_count else 0,
        "products": paged_items,
    }


@app.get("/api/products/{row_id}")
def get_product_detail(row_id: int, job_id: Optional[str] = None):
    """Retrieves full Product Passport with evidence tree and confidence breakdown."""
    rows = _get_active_rows(job_id)
    for r in rows:
        if r.get("row_id") == row_id:
            return r
    raise HTTPException(status_code=404, detail=f"Product with row_id {row_id} not found")


@app.get("/api/review")
def review_queue(job_id: Optional[str] = None):
    """Returns all product items currently in the human review queue."""
    rows = _get_active_rows(job_id)
    queue = get_review_queue(rows)
    return {
        "total_in_queue": len(queue),
        "review_items": queue,
        "audit_history": get_audit_log(),
    }


@app.post("/api/review/{row_id}/action")
def review_action(row_id: int, request: ReviewActionRequest, job_id: Optional[str] = None):
    """Applies Accept, Edit, or Reject action to a product record."""
    rows = _get_active_rows(job_id)
    target_row = None
    for r in rows:
        if r.get("row_id") == row_id:
            target_row = r
            break

    if not target_row:
        raise HTTPException(status_code=404, detail="Product row not found")

    updated_row = apply_review_action(
        row=target_row,
        action=request.action,
        attribute_label=request.attribute_label,
        edited_value=request.edited_value,
        edited_uom=request.edited_uom,
        reviewer_notes=request.reviewer_notes,
    )

    return {
        "status": "success",
        "action": request.action,
        "updated_product": updated_row,
    }


def _compute_quality(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes real field-completeness and trust metrics — no fabricated numbers."""
    total = len(rows) or 1

    def pct(cond) -> float:
        return round(sum(1 for r in rows if cond(r)) / total * 100, 1)

    return {
        "field_completeness": {
            "classpath_assigned": pct(lambda r: bool(r.get("classpath")) and "Unclassified" not in r.get("classpath", "")),
            "brand_resolved": pct(lambda r: bool(r.get("brand_name"))),
            "manufacturer_resolved": pct(lambda r: bool(r.get("manufacturer_name"))),
            "mfr_url_present": pct(lambda r: bool(r.get("enrichment_mfr_url"))),
            "attributes_extracted": pct(lambda r: bool(r.get("extracted_attributes"))),
        },
        "trust_signals": {
            "fully_grounded_products": pct(
                lambda r: bool(r.get("extracted_attributes"))
                and all(a.get("validation") == "grounded" for a in r["extracted_attributes"])
            ),
            "zero_hallucination_rate": pct(
                lambda r: not any(a.get("validation") == "missing_evidence" for a in r.get("extracted_attributes", []))
            ),
        },
    }

@app.get("/api/analytics")
def analytics(job_id: Optional[str] = None):
    """Returns catalog intelligence analytics, category distributions, and KPI metrics."""
    rows = _get_active_rows(job_id)
    total = len(rows)
    high = sum(1 for r in rows if r.get("confidence_tier") == "HIGH")
    med = sum(1 for r in rows if r.get("confidence_tier") == "MEDIUM")
    low = sum(1 for r in rows if r.get("confidence_tier") == "LOW")
    needs_rev = sum(1 for r in rows if r.get("needs_review"))
    dups = sum(1 for r in rows if r.get("duplicate_info", {}).get("status") == "DUPLICATE")
    poss_dups = sum(1 for r in rows if r.get("duplicate_info", {}).get("status") == "POSSIBLE_DUPLICATE")
    enriched = sum(1 for r in rows if r.get("enrichment_applied"))

    # Category distribution
    categories: Dict[str, int] = {}
    for r in rows:
        d = r.get("dept") or "Unclassified"
        categories[d] = categories.get(d, 0) + 1

    # Brand distribution
    brands: Dict[str, int] = {}
    for r in rows:
        b = r.get("brand_name") or "Unbranded"
        brands[b] = brands.get(b, 0) + 1

    avg_conf = (sum(r.get("overall_confidence", 0.0) for r in rows) / total) if total else 0.0

    return {
        "total_products": total,
        "high_confidence_count": high,
        "medium_confidence_count": med,
        "low_confidence_count": low,
        "needs_review_count": needs_rev,
        "duplicate_count": dups,
        "possible_duplicate_count": poss_dups,
        "enriched_count": enriched,
        "avg_confidence": round(avg_conf, 2),
        "category_distribution": categories,
        "top_brands": dict(sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]),
        "quality": _compute_quality(rows),
    }


@app.get("/api/evaluation")
def evaluate():
    """Runs evaluation benchmark against verified ground truth and returns real metrics."""
    return run_evaluation()


@app.get("/api/manufacturer-docs")
def list_mfr_docs():
    """Lists all structured datasheets in the manufacturer knowledge base."""
    docs = load_manufacturer_kb()
    return {
        "total_documents": len(docs),
        "documents": docs,
    }


@app.post("/api/manufacturer-docs/query")
def query_mfr_doc(mpn: str = Form(...)):
    """Retrieves missing specs for a part number from the manufacturer RAG knowledge base."""
    docs = load_manufacturer_kb()
    specs = query_rag_by_mpn(mpn, docs)
    return {
        "mfg_part_num": mpn,
        "matched_specs_count": len(specs),
        "retrieved_attributes": specs,
    }


@app.get("/api/download/{job_id}")
def download_catalog(job_id: str):
    path = os.path.join(OUTPUT_DIR, f"delivery_catalog_{job_id}.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=f"delivery_catalog_{job_id}.csv", media_type="text/csv")


@app.get("/api/download/{job_id}/audit")
def download_audit(job_id: str):
    path = os.path.join(OUTPUT_DIR, f"audit_evidence_{job_id}.csv")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=f"audit_evidence_{job_id}.csv", media_type="text/csv")
