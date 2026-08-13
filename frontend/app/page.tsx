"use client";

import { useState } from "react";

type ProcessResult = {
  job_id: string;
  rows_processed: number;
  summary: {
    total_rows: number;
    needs_review: number;
    avg_confidence: number;
  };
  download_url: string;
};

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/api/process`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data: ProcessResult = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-50 flex flex-col items-center px-6 py-16">
      <div className="max-w-xl w-full">
        <h1 className="text-2xl font-semibold text-neutral-900">
          Product Intelligence Engine
        </h1>
        <p className="text-neutral-500 mt-1 mb-8">
          Upload a raw catalog CSV. Every field is validated and scored —
          nothing is shipped without evidence.
        </p>

        <div className="border border-dashed border-neutral-300 rounded-lg p-8 bg-white">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-neutral-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-neutral-900 file:text-white file:text-sm hover:file:bg-neutral-700"
          />
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="mt-4 w-full rounded-md bg-neutral-900 text-white py-2 text-sm font-medium disabled:opacity-40"
          >
            {loading ? "Processing…" : "Run enrichment pipeline"}
          </button>
        </div>

        {error && (
          <p className="mt-4 text-sm text-red-600">Error: {error}</p>
        )}

        {result && (
          <div className="mt-8 bg-white border border-neutral-200 rounded-lg p-6">
            <h2 className="font-medium text-neutral-900">Done</h2>
            <dl className="mt-3 grid grid-cols-2 gap-y-2 text-sm">
              <dt className="text-neutral-500">Rows processed</dt>
              <dd className="text-neutral-900 text-right">{result.rows_processed}</dd>

              <dt className="text-neutral-500">Needs human review</dt>
              <dd className="text-neutral-900 text-right">
                {result.summary.needs_review} / {result.summary.total_rows}
              </dd>

              <dt className="text-neutral-500">Avg. confidence</dt>
              <dd className="text-neutral-900 text-right">
                {(result.summary.avg_confidence * 100).toFixed(0)}%
              </dd>
            </dl>

            <a
              href={`${API_BASE}${result.download_url}`}
              className="mt-4 inline-block text-sm text-neutral-900 underline underline-offset-2"
            >
              Download enriched CSV
            </a>
          </div>
        )}
      </div>
    </main>
  );
}
