# Product Intelligence AI — Master Platform

**Evidence-Driven B2B Product Intelligence, Extraction, Validation & Enrichment Platform**

Built for Industrial & B2B Commerce Product Catalogs.

---

## Key Differentiators & Philosophy

1. **Evidence First**: Every single extracted or generated attribute is strictly tied to exact substring evidence from input descriptions or verified citations from manufacturer datasheets.
2. **Zero-Hallucination Guarantee**: If an attribute is missing and unsupported by evidence, it is kept `null` or routed to Human Review rather than fabricated.
3. **Deterministic Extraction Before Generative AI**: Deterministic regex pattern matching, controlled LOV taxonomies, and canonical dictionary mappings execute first for 100% accuracy, complemented by structured Gemini AI for semantic inference.
4. **Signal-Based Explainable Confidence**: Transparent scoring derived from real evidence signals (+30 pts evidence, +20 pts LOV match, +25 pts manufacturer RAG, +10 pts canonical norm, +5 pts validation) with human-readable "Why should I trust this?" rationale.
5. **Human-in-the-Loop Review Queue**: Low-confidence, duplicate, or flagged records are managed in an interactive review queue with Accept, Edit, and Reject workflows with persistent audit history.
6. **Live Evaluation Engine**: Evaluates live accuracy against a verified ground truth benchmark with zero fake numbers.
7. **Dual-Level Commerce Exports**: Produces both the 150+ column **Standard Delivery Format CSV** and the **Intelligence Audit Evidence CSV**.

---

## 12-Module Pipeline Architecture

```
Raw Product Input (CSV)
        ↓
1. Ingestion & Pre-Flight Analysis (Clean placeholders, compute telemetry)
        ↓
2. Data Cleaning (Deterministic abbreviation expansion, vendor code stripping)
        ↓
3. RapidFuzz De-duplication (Exact, normalized, and fuzzy token similarity)
        ↓
4. Controlled Taxonomy Classification (LOV Department > Class > Fine > Classpath)
        ↓
5. Hybrid Attribute Extraction (Deterministic regex rules + structured Gemini AI)
        ↓
6. Manufacturer RAG Enrichment (Controlled datasheet knowledge base retrieval)
        ↓
7. Canonical Normalization (Standard labels & UOM harmonization)
        ↓
8. Anti-Hallucination Validation (Cross-field sanity & evidence checks)
        ↓
9. Signal-Based Confidence Engine (Transparent points, HIGH/MEDIUM/LOW tiers)
        ↓
10. Validated Description Generation (Product Name, Short, Invoice [40 char], Mobile, Long, Features)
        ↓
11. Human Review Queue (Accept, Edit, Reject workflow with audit log)
        ↓
12. Evaluation Engine & Dual-Level Export (Delivery Format CSV + Audit Evidence CSV)
```

---

## Getting Started

### 1. Start Backend (FastAPI)

```bash
cd backend
# Create or activate virtual environment
.\venv\Scripts\activate

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: http://localhost:8000/docs

### 2. Start Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000 to interact with the Product Intelligence Dashboard.

---

## Running Automated Tests & Benchmarks

### Run Unit Tests
```bash
cd backend
.\venv\Scripts\python -m unittest discover tests
```

### Run Pipeline Smoke Test & Ground Truth Evaluation
```bash
cd backend
.\venv\Scripts\python smoke_test.py
```

---

## API Endpoints

- `GET /health` — Service health check
- `POST /api/process` — Ingest CSV, run 12-stage pipeline, return job summary and download links
- `GET /api/jobs/{job_id}` — Get job execution status and stage latencies
- `GET /api/products` — Filterable, searchable, and paginated product catalog
- `GET /api/products/{row_id}` — Full Product Passport with evidence tree and confidence breakdown
- `GET /api/review` — Retrieve items in human review queue
- `POST /api/review/{row_id}/action` — Apply Accept, Edit, or Reject action
- `GET /api/analytics` — KPI metrics, confidence tier breakdown, and department distribution
- `GET /api/evaluation` — Run live evaluation benchmark against verified ground truth
- `GET /api/manufacturer-docs` — Browse indexed manufacturer datasheets
- `POST /api/manufacturer-docs/query` — Query manufacturer knowledge base for grounded specs
- `GET /api/download/{job_id}` — Download Final Delivery Format Catalog CSV (150+ columns)
- `GET /api/download/{job_id}/audit` — Download Intelligence & Audit Evidence CSV
