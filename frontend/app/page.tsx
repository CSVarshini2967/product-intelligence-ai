"use client";

import React, { useState, useEffect, useCallback } from "react";
import Navbar from "@/components/Navbar";
import DashboardOverview from "@/components/DashboardOverview";
import PipelineMonitor from "@/components/PipelineMonitor";
import ProductCatalog from "@/components/ProductCatalog";
import ReviewQueue from "@/components/ReviewQueue";
import ManufacturerRAG from "@/components/ManufacturerRAG";
import EvaluationBenchmark from "@/components/EvaluationBenchmark";
import ExportCenter from "@/components/ExportCenter";

const API_BASE = "http://localhost:8000";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [loading, setLoading] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);

  // Analytics & Summary State
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [stageLatencies, setStageLatencies] = useState<Record<string, number>>({});
  const [preflightTelemetry, setPreflightTelemetry] = useState<any | null>(null);

  // Products Table State
  const [products, setProducts] = useState<any[]>([]);
  const [totalProducts, setTotalProducts] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedDept, setSelectedDept] = useState<string>("");
  const [selectedTier, setSelectedTier] = useState<string>("");
  const [needsReviewOnly, setNeedsReviewOnly] = useState<boolean>(false);

  // Review Queue State
  const [reviewItems, setReviewItems] = useState<any[]>([]);

  // Fetch Analytics Summary
  const fetchAnalytics = useCallback(async (jid?: string) => {
    try {
      const url = jid ? `${API_BASE}/api/analytics?job_id=${jid}` : `${API_BASE}/api/analytics`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (e) {
      console.error("Failed to load analytics:", e);
    }
  }, []);

  // Fetch Filtered Product Catalog
  const fetchProducts = useCallback(async (
    page = 1,
    query = "",
    dept = "",
    tier = "",
    reviewOnly = false,
    jid?: string
  ) => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: "25",
      });
      if (query) params.append("query", query);
      if (dept) params.append("dept", dept);
      if (tier) params.append("confidence_tier", tier);
      if (reviewOnly) params.append("needs_review", "true");
      if (jid) params.append("job_id", jid);

      const res = await fetch(`${API_BASE}/api/products?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setProducts(data.products || []);
        setTotalProducts(data.total || 0);
      }
    } catch (e) {
      console.error("Failed to load products:", e);
    }
  }, []);

  // Fetch Review Queue Items
  const fetchReviewQueue = useCallback(async (jid?: string) => {
    try {
      const url = jid ? `${API_BASE}/api/review?job_id=${jid}` : `${API_BASE}/api/review`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setReviewItems(data.review_items || []);
      }
    } catch (e) {
      console.error("Failed to load review queue:", e);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchAnalytics();
    fetchProducts(currentPage, searchQuery, selectedDept, selectedTier, needsReviewOnly);
    fetchReviewQueue();
  }, [fetchAnalytics, fetchProducts, fetchReviewQueue, currentPage, searchQuery, selectedDept, selectedTier, needsReviewOnly]);

  // Run Pipeline Trigger
  const handleRunPipeline = async (uploadedFile?: File) => {
    setLoading(true);
    const formData = new FormData();
    if (uploadedFile) {
      formData.append("file", uploadedFile);
    }

    try {
      const res = await fetch(`${API_BASE}/api/process`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Processing failed with status ${res.status}`);
      const data = await res.json();
      setJobId(data.job_id);

      if (data.summary) {
        setStageLatencies(data.summary.stage_latencies || {});
        setPreflightTelemetry(data.summary.preflight_telemetry || null);
      }

      await fetchAnalytics(data.job_id);
      await fetchProducts(1, "", "", "", false, data.job_id);
      await fetchReviewQueue(data.job_id);
      setCurrentPage(1);
      setSearchQuery("");
      setSelectedDept("");
      setSelectedTier("");
      setNeedsReviewOnly(false);
    } catch (e) {
      console.error("Error executing pipeline:", e);
    } finally {
      setLoading(false);
    }
  };

  // Human Review Action (Accept / Edit / Reject)
  const handleReviewAction = async (
    rowId: number,
    action: "ACCEPT" | "EDIT" | "REJECT",
    payload?: { label?: string; value?: string; uom?: string; notes?: string }
  ) => {
    try {
      const res = await fetch(`${API_BASE}/api/review/${rowId}/action${jobId ? `?job_id=${jobId}` : ""}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action,
          attribute_label: payload?.label,
          edited_value: payload?.value,
          edited_uom: payload?.uom,
          reviewer_notes: payload?.notes,
        }),
      });

      if (res.ok) {
        // Refresh items
        await fetchReviewQueue(jobId || undefined);
        await fetchAnalytics(jobId || undefined);
        await fetchProducts(currentPage, searchQuery, selectedDept, selectedTier, needsReviewOnly, jobId || undefined);
      }
    } catch (e) {
      console.error("Failed to apply review action:", e);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunPipeline={() => handleRunPipeline()}
        loading={loading}
        needsReviewCount={analytics?.needs_review_count || 0}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "overview" && (
          <DashboardOverview
            analytics={analytics}
            onUploadFile={(file) => handleRunPipeline(file)}
            onSelectTab={(t) => setActiveTab(t)}
            loading={loading}
          />
        )}

        {activeTab === "pipeline" && (
          <PipelineMonitor
            totalRows={analytics?.total_products || 0}
            stageLatencies={stageLatencies}
            preflightTelemetry={preflightTelemetry}
          />
        )}

        {activeTab === "catalog" && (
          <ProductCatalog
            products={products}
            totalProducts={totalProducts}
            currentPage={currentPage}
            onPageChange={(p) => setCurrentPage(p)}
            searchQuery={searchQuery}
            onSearchChange={(q) => {
              setSearchQuery(q);
              setCurrentPage(1);
            }}
            selectedDept={selectedDept}
            onDeptChange={(d) => {
              setSelectedDept(d);
              setCurrentPage(1);
            }}
            selectedTier={selectedTier}
            onTierChange={(t) => {
              setSelectedTier(t);
              setCurrentPage(1);
            }}
            needsReviewOnly={needsReviewOnly}
            onNeedsReviewChange={(val) => {
              setNeedsReviewOnly(val);
              setCurrentPage(1);
            }}
          />
        )}

        {activeTab === "review" && (
          <ReviewQueue
            reviewItems={reviewItems}
            onAction={handleReviewAction}
            loading={loading}
          />
        )}

        {activeTab === "rag" && <ManufacturerRAG />}

        {activeTab === "evaluation" && <EvaluationBenchmark />}

        {activeTab === "export" && (
          <ExportCenter
            jobId={jobId}
            totalRows={analytics?.total_products || 0}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Product Intelligence AI &copy; 2026 — Evidence-First Industrial Data Enrichment Engine</span>
          <div className="flex items-center space-x-4">
            <span className="text-slate-400">Zero Hallucinations Guarantee</span>
            <span className="text-indigo-400 font-mono">FastAPI + Next.js</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
