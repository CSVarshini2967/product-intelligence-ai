"""
Pydantic schemas and data models for Product Intelligence AI.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ExtractedAttribute(BaseModel):
    label: str
    value: str
    uom: Optional[str] = None
    evidence: Optional[str] = None
    source: str = "Part_Desc"  # "Part_Desc", "Mfg_Part_Num", "Part_Manuf", "manufacturer_datasheet", "inferred"
    method: str = "regex_rule"  # "regex_rule", "dictionary_lookup", "gemini_llm", "manufacturer_rag"
    inferred: bool = False
    confidence: float = 1.0  # 0.0 to 1.0
    validation: str = "grounded"  # "grounded", "missing_evidence", "unverified_inference", "failed"
    source_reference: Optional[str] = None  # e.g., document name or URL if from RAG


class DuplicateInfo(BaseModel):
    status: str = "UNIQUE"  # "UNIQUE", "POSSIBLE_DUPLICATE", "DUPLICATE"
    cluster_id: Optional[str] = None
    similarity_score: float = 0.0
    match_reason: Optional[str] = None


class ProductRecord(BaseModel):
    row_id: int
    mfg_part_num: str
    part_desc: str
    part_manuf: Optional[str] = None
    e1_brand: Optional[str] = None
    unilog_brand: Optional[str] = None
    dib_brand: Optional[str] = None
    
    # Normalized & Cleaned fields
    part_desc_normalized: Optional[str] = None
    manufacturer_name: Optional[str] = None
    brand_name: Optional[str] = None
    trade_name: Optional[str] = None
    sku: Optional[str] = None
    part_number: Optional[str] = None
    
    # Taxonomy / Classification
    dept: Optional[str] = None
    class_name: Optional[str] = None
    fine: Optional[str] = None
    classpath: Optional[str] = None
    classification_confidence: float = 1.0
    classification_reason: Optional[str] = None
    
    # De-duplication
    duplicate_info: DuplicateInfo = Field(default_factory=DuplicateInfo)
    
    # Attributes & Enrichment
    extracted_attributes: List[ExtractedAttribute] = Field(default_factory=list)
    enrichment_applied: bool = False
    enrichment_source: Optional[str] = None
    enrichment_doc_refs: List[str] = Field(default_factory=list)
    
    # Validation & Confidence
    overall_confidence: float = 0.0
    confidence_tier: str = "LOW"  # "HIGH", "MEDIUM", "LOW"
    confidence_reasons: List[str] = Field(default_factory=list)
    needs_review: bool = False
    review_reasons: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)
    
    # Descriptions
    product_name: Optional[str] = None
    short_desc: Optional[str] = None
    invoice_desc: Optional[str] = None
    mobile_desc: Optional[str] = None
    long_desc1: Optional[str] = None
    retail_desc: Optional[str] = None
    marketing_description: Optional[str] = None
    item_features: List[str] = Field(default_factory=list)
    
    # Human Review Status
    review_status: str = "PENDING"  # "PENDING", "ACCEPTED", "EDITED", "REJECTED"
    human_corrections: Dict[str, Any] = Field(default_factory=dict)


class ReviewActionRequest(BaseModel):
    action: str  # "ACCEPT", "EDIT", "REJECT"
    attribute_label: Optional[str] = None
    edited_value: Optional[str] = None
    edited_uom: Optional[str] = None
    reviewer_notes: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: str  # "PROCESSING", "COMPLETED", "FAILED"
    progress: float = 0.0
    current_stage: str = ""
    rows_processed: int = 0
    total_rows: int = 0
    summary: Dict[str, Any] = Field(default_factory=dict)
    stage_latencies: Dict[str, float] = Field(default_factory=dict)
    download_url: Optional[str] = None
    audit_download_url: Optional[str] = None
