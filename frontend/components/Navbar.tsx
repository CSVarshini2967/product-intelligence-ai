"use client";

import React from "react";
import { 
  Layers, 
  Activity, 
  Database, 
  CheckCircle2, 
  FileSearch, 
  BarChart3, 
  Download,
  Sparkles,
  RefreshCw
} from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onRunPipeline: () => void;
  loading: boolean;
  needsReviewCount: number;
}

export default function Navbar({
  activeTab,
  setActiveTab,
  onRunPipeline,
  loading,
  needsReviewCount,
}: NavbarProps) {
  const tabs = [
    { id: "overview", label: "Executive Dashboard", icon: BarChart3 },
    { id: "pipeline", label: "Pipeline Monitor", icon: Activity },
    { id: "catalog", label: "Product Catalog", icon: Database },
    { 
      id: "review", 
      label: "Review Queue", 
      icon: CheckCircle2,
      badge: needsReviewCount > 0 ? needsReviewCount : undefined 
    },
    { id: "rag", label: "Manufacturer RAG", icon: FileSearch },
    { id: "evaluation", label: "Accuracy Benchmark", icon: Sparkles },
    { id: "export", label: "Export Hub", icon: Download },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Tagline */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Layers className="w-5 h-5 text-indigo-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">Product Intelligence</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">AI</span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Industrial Catalog Standardization & Enrichment</p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-3">
            <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Zero-Hallucination Guardrails Active</span>
            </div>

            <button
              onClick={onRunPipeline}
              disabled={loading}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all active:scale-95 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Processing Pipeline..." : "Run Intelligence Pipeline"}</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 overflow-x-auto py-2 scrollbar-none border-t border-slate-800/40">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-slate-500"}`} />
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span className="ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
