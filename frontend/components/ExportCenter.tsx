"use client";

import React from "react";
import { 
  DownloadCloud, 
  FileSpreadsheet, 
  ShieldCheck, 
  Database, 
  Sparkles, 
  ExternalLink,
  Layers,
  FileCode
} from "lucide-react";

interface ExportCenterProps {
  jobId: string | null;
  totalRows: number;
}

export default function ExportCenter({ jobId, totalRows }: ExportCenterProps) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const downloadCatalogUrl = jobId
    ? `${API_BASE}/api/download/${jobId}`
    : `${API_BASE}/api/download/default`;

const downloadAuditUrl = jobId
    ? `${API_BASE}/api/download/${jobId}/audit`
    : `${API_BASE}/api/download/default/audit`;

  return (
    <div className="space-y-6">
      {/* Export Hub Header */}
      <div className="p-5 rounded-xl glass-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            <span>Catalog & Intelligence Export Hub</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              COMMERCE READY
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Download your enriched catalog formatted for target distributor specifications or full intelligence audit logs.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="font-mono text-slate-400">Job ID:</span>
          <span className="font-mono text-indigo-400 font-bold">{jobId || "Active Session"}</span>
        </div>
      </div>

      {/* Export Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Delivery Format Catalog CSV */}
        <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-5 border-t-4 border-t-indigo-500 shadow-xl">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <FileSpreadsheet className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                150+ COLUMNS
              </span>
            </div>

            <h3 className="text-base font-bold text-white">Final Delivery Format Catalog CSV</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Standardized catalog matching the exact schema requirements: Classpath, Product Name, INVOICE_DESC (40 char), MOBILE_DESC, LONG_DESC1, ITEM_FEATURES_1..20, and ATTRIBUTE_LABEL/VALUE/UOM columns.
            </p>

            <div className="space-y-1 pt-2 text-xs text-slate-300">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Zero hallucinated values included</span>
              </div>
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-indigo-400" />
                <span>Includes {totalRows} processed records</span>
              </div>
            </div>
          </div>

          <a
            href={downloadCatalogUrl}
            download="enriched_catalog_delivery_format.csv"
            className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all active:scale-95"
          >
            <DownloadCloud className="w-4 h-4" />
            <span>Download Delivery Catalog CSV</span>
          </a>
        </div>

        {/* Card 2: Intelligence & Audit Trail CSV */}
        <div className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-5 border-t-4 border-t-cyan-500 shadow-xl">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <FileCode className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                EXPLAINABILITY AUDIT
              </span>
            </div>

            <h3 className="text-base font-bold text-white">Intelligence & Evidence Audit CSV</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every single extracted attribute linked directly with raw substring evidence, source origin, extraction method, confidence score, validation status, and human review decision.
            </p>

            <div className="space-y-1 pt-2 text-xs text-slate-300">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span>Complete data provenance & RAG citations</span>
              </div>
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-purple-400" />
                <span>Auditable for enterprise compliance</span>
              </div>
            </div>
          </div>

          <a
            href={downloadAuditUrl}
            download="catalog_intelligence_audit_evidence.csv"
            className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 font-bold text-xs shadow-lg flex items-center justify-center space-x-2 transition-all active:scale-95"
          >
            <DownloadCloud className="w-4 h-4" />
            <span>Download Audit & Evidence CSV</span>
          </a>
        </div>
      </div>
    </div>
  );
}
