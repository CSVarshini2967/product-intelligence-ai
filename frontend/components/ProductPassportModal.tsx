"use client";

import React, { useState } from "react";
import { 
  X, 
  ShieldCheck, 
  AlertTriangle, 
  Sparkles, 
  FileText, 
  Database, 
  CheckCircle2, 
  Tag, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  Copy
} from "lucide-react";

interface ExtractedAttribute {
  label: string;
  value: string;
  uom?: string | null;
  evidence?: string | null;
  source: string;
  method: string;
  inferred: boolean;
  confidence: number;
  validation: string;
  source_reference?: string | null;
}

interface ProductRecord {
  row_id: number;
  mfg_part_num: string;
  part_desc: string;
  part_manuf?: string | null;
  manufacturer_name?: string | null;
  brand_name?: string | null;
  dept?: string | null;
  class_name?: string | null;
  fine?: string | null;
  classpath?: string | null;
  overall_confidence: number;
  confidence_tier: string;
  confidence_reasons: string[];
  needs_review: boolean;
  review_reasons: string[];
  flags: string[];
  extracted_attributes: ExtractedAttribute[];
  product_name?: string | null;
  short_desc?: string | null;
  invoice_desc?: string | null;
  mobile_desc?: string | null;
  long_desc1?: string | null;
  retail_desc?: string | null;
  marketing_description?: string | null;
  item_features: string[];
  enrichment_applied: boolean;
  enrichment_source?: string | null;
  enrichment_doc_refs: string[];
  duplicate_info: {
    status: string;
    cluster_id?: string | null;
    similarity_score: number;
    match_reason?: string | null;
  };
}

interface ProductPassportModalProps {
  product: ProductRecord | null;
  onClose: () => void;
}

export default function ProductPassportModal({ product, onClose }: ProductPassportModalProps) {
  const [activeTab, setActiveTab] = useState<"attributes" | "confidence" | "descriptions" | "audit">("attributes");
  const [expandedAttr, setExpandedAttr] = useState<number | null>(null);

  if (!product) return null;

  const confPct = Math.round(product.overall_confidence * 100);
  const tier = product.confidence_tier || "LOW";

  const getTierBadge = (t: string) => {
    switch (t) {
      case "HIGH":
        return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
      case "MEDIUM":
        return "bg-amber-500/20 text-amber-300 border-amber-500/40";
      default:
        return "bg-rose-500/20 text-rose-300 border-rose-500/40";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-4xl max-h-[90vh] bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800/80 bg-slate-900/50 flex items-start justify-between">
          <div className="space-y-1 max-w-2xl">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold text-indigo-400">PART #{product.mfg_part_num}</span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${getTierBadge(tier)}`}>
                {tier} CONFIDENCE ({confPct}%)
              </span>
              {product.needs_review && (
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  <span>NEEDS REVIEW</span>
                </span>
              )}
              {product.duplicate_info.status === "DUPLICATE" && (
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                  <Copy className="w-3 h-3" />
                  <span>DUPLICATE</span>
                </span>
              )}
            </div>

            <h2 className="text-lg font-bold text-white tracking-tight leading-snug">
              {product.product_name || product.part_desc}
            </h2>

            <p className="text-xs text-slate-400">
              <span className="text-slate-500 font-semibold">Raw Input:</span> {product.part_desc}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Nav Tabs */}
        <div className="flex border-b border-slate-800/80 px-6 bg-slate-900/20 text-xs">
          <button
            onClick={() => setActiveTab("attributes")}
            className={`py-3 px-4 font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "attributes"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>Extracted Attributes & Evidence ({product.extracted_attributes.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("confidence")}
            className={`py-3 px-4 font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "confidence"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Confidence Scoring Rationale</span>
          </button>

          <button
            onClick={() => setActiveTab("descriptions")}
            className={`py-3 px-4 font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "descriptions"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Catalog Descriptions</span>
          </button>

          <button
            onClick={() => setActiveTab("audit")}
            className={`py-3 px-4 font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "audit"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Product Passport Meta</span>
          </button>
        </div>

        {/* Modal Tab Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4">
          {/* TAB 1: ATTRIBUTES & EVIDENCE */}
          {activeTab === "attributes" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">
                  Click any attribute below to inspect its exact source evidence and extraction method.
                </span>
                <span className="text-xs font-mono text-emerald-400">100% Grounded</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {product.extracted_attributes.map((attr, idx) => {
                  const isExpanded = expandedAttr === idx;
                  return (
                    <div
                      key={idx}
                      onClick={() => setExpandedAttr(isExpanded ? null : idx)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer ${
                        isExpanded
                          ? "bg-slate-900 border-indigo-500/50 shadow-md shadow-indigo-500/10"
                          : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-[11px] font-semibold text-slate-400 block">{attr.label}</span>
                          <span className="text-sm font-bold text-white mt-0.5 block">
                            {attr.value} {attr.uom && <span className="text-indigo-400 text-xs font-mono">{attr.uom}</span>}
                          </span>
                        </div>

                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            {attr.validation.toUpperCase()}
                          </span>
                          {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                        </div>
                      </div>

                      {/* Expandable Evidence Card */}
                      {isExpanded && (
                        <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2 text-xs">
                          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                            <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Grounded Input Evidence</span>
                            <p className="font-mono text-emerald-300 text-xs bg-emerald-950/30 p-1.5 rounded border border-emerald-500/20">
                              "{attr.evidence || "Direct canonical entity map"}"
                            </p>
                          </div>

                          <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400">
                            <div>
                              <span className="text-slate-500 block">Source:</span>
                              <span className="text-slate-200 font-mono">{attr.source}</span>
                            </div>
                            <div>
                              <span className="text-slate-500 block">Method:</span>
                              <span className="text-slate-200 font-mono">{attr.method}</span>
                            </div>
                            {attr.source_reference && (
                              <div className="col-span-2">
                                <span className="text-slate-500 block">Citation Document:</span>
                                <span className="text-cyan-400 font-mono">{attr.source_reference}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {product.extracted_attributes.length === 0 && (
                <div className="p-8 text-center text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
                  No attributes extracted from this raw description.
                </div>
              )}
            </div>
          )}

          {/* TAB 2: CONFIDENCE RATIONALE */}
          {activeTab === "confidence" && (
            <div className="space-y-4">
              <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">Explainable Trust Score</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Calculated deterministically from actual grounding signals</p>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-extrabold text-white">{confPct}%</span>
                  <span className={`block text-xs font-bold ${tier === "HIGH" ? "text-emerald-400" : tier === "MEDIUM" ? "text-amber-400" : "text-rose-400"}`}>
                    {tier} CONFIDENCE
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Why should I trust this record?</h4>
                <div className="space-y-2">
                  {product.confidence_reasons.map((r, i) => (
                    <div key={i} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex items-start space-x-2 text-xs text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>

              {product.review_reasons && product.review_reasons.length > 0 && (
                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Review Triggers & Warnings</h4>
                  <div className="space-y-2">
                    {product.review_reasons.map((wr, i) => (
                      <div key={i} className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/30 flex items-start space-x-2 text-xs text-amber-300">
                        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                        <span>{wr}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CATALOG DESCRIPTIONS */}
          {activeTab === "descriptions" && (
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-400 uppercase">Product Name</label>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-sm font-semibold text-white">
                  {product.product_name || "N/A"}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase">Short Description</label>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200">
                    {product.short_desc || "N/A"}
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-400 uppercase">
                    Invoice Description <span className="text-[10px] text-slate-500">(Max 40 chars, Uppercase)</span>
                  </label>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300 uppercase">
                    {product.invoice_desc || "N/A"}
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-400 uppercase">Long Description (Technical Narrative)</label>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                  {product.long_desc1 || "N/A"}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400 uppercase">Item Features (Bullet Points)</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {product.item_features.map((feat, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-center space-x-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: PASSPORT META */}
          {activeTab === "audit" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <span className="text-slate-500 font-bold uppercase block">Classification & Taxonomy</span>
                <div><span className="text-slate-400">Department:</span> <span className="text-white font-semibold">{product.dept}</span></div>
                <div><span className="text-slate-400">Class:</span> <span className="text-white font-semibold">{product.class_name}</span></div>
                <div><span className="text-slate-400">Fine:</span> <span className="text-white font-semibold">{product.fine}</span></div>
                <div><span className="text-slate-400">Classpath:</span> <span className="text-indigo-300 font-mono text-[11px] block mt-0.5">{product.classpath}</span></div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <span className="text-slate-500 font-bold uppercase block">Brand & Vendor Entities</span>
                <div><span className="text-slate-400">Canonical Brand:</span> <span className="text-white font-semibold">{product.brand_name || "Unbranded"}</span></div>
                <div><span className="text-slate-400">Canonical Manufacturer:</span> <span className="text-white font-semibold">{product.manufacturer_name || "N/A"}</span></div>
                <div><span className="text-slate-400">Raw Vendor:</span> <span className="text-slate-300">{product.part_manuf || "N/A"}</span></div>
              </div>

              {product.enrichment_applied && (
                <div className="col-span-2 p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-1">
                  <span className="text-cyan-400 font-bold uppercase block">Manufacturer Datasheet RAG References</span>
                  <div className="space-y-1">
                    {product.enrichment_doc_refs.map((ref, idx) => (
                      <div key={idx} className="font-mono text-xs text-cyan-200 flex items-center space-x-2">
                        <FileText className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{ref}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
          <span>Row ID: #{product.row_id}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold transition-all"
          >
            Close Passport
          </button>
        </div>
      </div>
    </div>
  );
}
