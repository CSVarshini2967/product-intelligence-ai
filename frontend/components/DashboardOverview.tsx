"use client";

import React, { useState } from "react";
import { 
  Package, 
  ShieldCheck, 
  AlertTriangle, 
  Copy, 
  Sparkles, 
  UploadCloud, 
  ArrowRight,
  TrendingUp,
  Cpu,
  BookOpenCheck
} from "lucide-react";

interface AnalyticsData {
  total_products: number;
  high_confidence_count: number;
  medium_confidence_count: number;
  low_confidence_count: number;
  needs_review_count: number;
  duplicate_count: number;
  possible_duplicate_count: number;
  enriched_count: number;
  avg_confidence: number;
  category_distribution: Record<string, number>;
  top_brands: Record<string, number>;
}

interface DashboardOverviewProps {
  analytics: AnalyticsData | null;
  onUploadFile: (file: File) => void;
  onSelectTab: (tab: string) => void;
  loading: boolean;
}

export default function DashboardOverview({
  analytics,
  onUploadFile,
  onSelectTab,
  loading,
}: DashboardOverviewProps) {
  const [dragActive, setDragActive] = useState(false);

  const total = analytics?.total_products || 0;
  const high = analytics?.high_confidence_count || 0;
  const med = analytics?.medium_confidence_count || 0;
  const low = analytics?.low_confidence_count || 0;
  const needsRev = analytics?.needs_review_count || 0;
  const duplicates = (analytics?.duplicate_count || 0) + (analytics?.possible_duplicate_count || 0);
  const avgConf = Math.round((analytics?.avg_confidence || 0) * 100);

  const highPct = total ? Math.round((high / total) * 100) : 0;
  const medPct = total ? Math.round((med / total) * 100) : 0;
  const lowPct = total ? Math.round((low / total) * 100) : 0;

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Philosophy Alert */}
      <div className="rounded-xl bg-gradient-to-r from-indigo-950/60 via-slate-900/80 to-slate-900 border border-indigo-500/20 p-5 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          <div className="p-2.5 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 mt-0.5">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
              <span>Evidence-First Intelligence Architecture</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Guaranteed Anti-Hallucination
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
              Every extracted attribute is strictly linked to raw text evidence or manufacturer datasheet citations. 
              Unsupported or low-confidence values are deterministically routed to Human Review rather than fabricated.
            </p>
          </div>
        </div>

        <button
          onClick={() => onSelectTab("evaluation")}
          className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all shrink-0"
        >
          <span>View Benchmark Report</span>
          <ArrowRight className="w-3.5 h-3.5 text-indigo-400" />
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Processed */}
        <div className="glass-card rounded-xl p-5 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Products</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Package className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white tracking-tight">{total.toLocaleString()}</span>
            <span className="text-[11px] font-medium text-emerald-400 flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> 100% Ingested
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Full catalog records processed</div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-cyan-500"></div>
        </div>

        {/* High Confidence */}
        <div className="glass-card rounded-xl p-5 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">High Confidence (≥80%)</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white tracking-tight">{high.toLocaleString()}</span>
            <span className="text-xs font-bold text-emerald-400">{highPct}%</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Direct grounded evidence verified</div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500"></div>
        </div>

        {/* Needs Human Review */}
        <div className="glass-card rounded-xl p-5 relative overflow-hidden group cursor-pointer hover:border-amber-500/40 transition-all" onClick={() => onSelectTab("review")}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Needs Review</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-amber-300 tracking-tight">{needsRev.toLocaleString()}</span>
            <span className="text-xs font-semibold text-amber-400">Action Required</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Uncertain, duplicate, or flagged</div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-amber-500"></div>
        </div>

        {/* Duplicate Signals */}
        <div className="glass-card rounded-xl p-5 relative overflow-hidden group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Potential Duplicates</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Copy className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-extrabold text-white tracking-tight">{duplicates}</span>
            <span className="text-[11px] font-medium text-purple-400">RapidFuzz Matched</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Clustered by MPN & token similarity</div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-purple-500"></div>
        </div>
      </div>

      {/* Main Row: Confidence Tier Bar + Quick Upload Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Confidence Tier Distribution */}
        <div className="lg:col-span-2 glass-card rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">Confidence Score Distribution</h3>
              <p className="text-xs text-slate-400 mt-0.5">Computed from multi-signal point grounding, LOV taxonomy, and RAG confirmation</p>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono font-bold text-indigo-300">Catalog Avg: {avgConf}%</span>
            </div>
          </div>

          {/* Progress Stack Bar */}
          <div className="w-full h-4 bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
            <div 
              style={{ width: `${highPct}%` }} 
              className="bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-700" 
              title={`High Confidence: ${high} (${highPct}%)`}
            ></div>
            <div 
              style={{ width: `${medPct}%` }} 
              className="bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-700" 
              title={`Medium Confidence: ${med} (${medPct}%)`}
            ></div>
            <div 
              style={{ width: `${lowPct}%` }} 
              className="bg-gradient-to-r from-rose-500 to-rose-400 transition-all duration-700" 
              title={`Low Confidence: ${low} (${lowPct}%)`}
            ></div>
          </div>

          {/* Legend Details */}
          <div className="grid grid-cols-3 gap-4 pt-2 border-t border-slate-800/80">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span className="text-xs font-semibold text-slate-300">HIGH (80-100%)</span>
              </div>
              <p className="text-lg font-bold text-emerald-400">{high} <span className="text-xs font-normal text-slate-400">({highPct}%)</span></p>
              <p className="text-[11px] text-slate-500">Auto-publish eligible</p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span className="text-xs font-semibold text-slate-300">MEDIUM (50-79%)</span>
              </div>
              <p className="text-lg font-bold text-amber-400">{med} <span className="text-xs font-normal text-slate-400">({medPct}%)</span></p>
              <p className="text-[11px] text-slate-500">Minor verification needed</p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                <span className="text-xs font-semibold text-slate-300">LOW (&lt;50%)</span>
              </div>
              <p className="text-lg font-bold text-rose-400">{low} <span className="text-xs font-normal text-slate-400">({lowPct}%)</span></p>
              <p className="text-[11px] text-slate-500">Sent to human review queue</p>
            </div>
          </div>
        </div>

        {/* Upload New Catalog CSV */}
        <div 
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`glass-card rounded-xl p-6 flex flex-col items-center justify-center text-center border-2 border-dashed transition-all relative ${
            dragActive ? "border-indigo-400 bg-indigo-950/20" : "border-slate-700/80 hover:border-slate-600"
          }`}
        >
          <input
            type="file"
            id="csv-upload"
            accept=".csv"
            onChange={handleChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={loading}
          />
          <div className="w-12 h-12 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3">
            <UploadCloud className="w-6 h-6" />
          </div>
          <h4 className="text-sm font-bold text-white">Upload Catalog CSV</h4>
          <p className="text-xs text-slate-400 mt-1 max-w-[200px]">
            Drag & drop raw ERP CSV or click to browse.
          </p>
          <span className="mt-3 px-3 py-1 rounded-md bg-slate-800 text-[11px] font-semibold text-indigo-300 border border-slate-700">
            {loading ? "Running Intelligence Pipeline..." : "Select File"}
          </span>
        </div>
      </div>

      {/* Category Breakdown & Top Brands */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="glass-card rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <BookOpenCheck className="w-4 h-4 text-indigo-400" />
              <span>Taxonomy Department Breakdown</span>
            </h3>
            <span className="text-xs text-slate-400">Classified by Controlled LOV</span>
          </div>

          <div className="space-y-2.5">
            {analytics?.category_distribution && Object.entries(analytics.category_distribution).map(([cat, count]) => {
              const pct = total ? Math.round((count / total) * 100) : 0;
              return (
                <div key={cat} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium text-slate-300">{cat}</span>
                    <span className="font-mono text-slate-400">{count} ({pct}%)</span>
                  </div>
                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      style={{ width: `${pct}%` }}
                      className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full"
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Normalized Brands */}
        <div className="glass-card rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Top Canonical Brands Resolved</span>
            </h3>
            <span className="text-xs text-slate-400">Entity Resolved</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {analytics?.top_brands && Object.entries(analytics.top_brands).map(([b, count]) => (
              <div key={b} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 flex flex-col justify-between">
                <span className="text-xs font-bold text-white truncate" title={b}>{b}</span>
                <span className="text-xs font-mono text-indigo-400 mt-1">{count} items</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
