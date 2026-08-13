"""
UniHack Product Intelligence Engine -- FastAPI backend entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import io
import uuid
import os

from app.pipeline import run_pipeline

app = FastAPI(title="UniHack Product Intelligence Engine")

# Allow the local Next.js dev servers to call this API during development.
# Port 3000 may already be occupied, so Next.js often falls back to 3001/3002.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):(\d+)",
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/process")
async def process_csv(file: UploadFile = File(...)):
    """
    Accepts an uploaded CSV (same shape as Sample_Dataset_-_Input.csv),
    runs it through the full pipeline, and returns a download link
    for the enriched output CSV.
    """
    raw_bytes = await file.read()
    df_input = pd.read_csv(io.BytesIO(raw_bytes))

    result = run_pipeline(df_input)

    job_id = str(uuid.uuid4())[:8]
    output_path = f"{OUTPUT_DIR}/enriched_{job_id}.csv"
    result["output_df"].to_csv(output_path, index=False)

    return {
        "job_id": job_id,
        "rows_processed": result["rows_processed"],
        "summary": result["summary"],
        "download_url": f"/api/download/{job_id}",
    }


@app.get("/api/download/{job_id}")
def download(job_id: str):
    path = f"{OUTPUT_DIR}/enriched_{job_id}.csv"
    return FileResponse(path, filename=f"enriched_{job_id}.csv", media_type="text/csv")
