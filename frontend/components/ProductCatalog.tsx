"use client";

import React, { useState } from "react";
import { 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  ShieldCheck, 
  AlertTriangle, 
  Layers, 
  FileText, 
  ExternalLink,
  Copy,
  Tag
} from "lucide-react";
import ProductPassportModal from "./ProductPassportModal";

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

interface ProductCatalogProps {
  products: ProductRecord[];
  totalProducts: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedDept: string;
  onDeptChange: (d: string) => void;
  selectedTier: string;
  onTierChange: (t: string) => void;
  needsReviewOnly: boolean;
  onNeedsReviewChange: (val: boolean) => void;
}

export default function ProductCatalog({
  products,
  totalProducts,
  currentPage,
  onPageChange,
  searchQuery,
  onSearchChange,
  selectedDept,
  onDeptChange,
  selectedTier,
  onTierChange,
  needsReviewOnly,
  onNeedsReviewChange,
}: ProductCatalogProps) {
  const [selectedProduct, setSelectedProduct] = useState<ProductRecord | null>(null);

  const totalPages = Math.ceil(totalProducts / 25) || 1;

  const departments = [
    "All Departments",
    "Appliances",
    "Abrasives",
    "Power Tools",
    "Building Materials",
    "Electrical & Lighting",
    "Safety & PPE",
    "Hardware & Hand Tools"
  ];

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="glass-card rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search part #, description, brand..."
            className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
          />
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Department Select */}
          <select
            value={selectedDept}
            onChange={(e) => onDeptChange(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            {departments.map((d) => (
              <option key={d} value={d === "All Departments" ? "" : d}>
                {d}
              </option>
            ))}
          </select>

          {/* Confidence Tier Select */}
          <select
            value={selectedTier}
            onChange={(e) => onTierChange(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Tiers</option>
            <option value="HIGH">High (≥80%)</option>
            <option value="MEDIUM">Medium (50-79%)</option>
            <option value="LOW">Low (&lt;50%)</option>
          </select>

          {/* Review Filter Button */}
          <button
            onClick={() => onNeedsReviewChange(!needsReviewOnly)}
            className={`px-3 py-2 rounded-lg text-xs font-semibold border transition-all flex items-center gap-1.5 ${
              needsReviewOnly
                ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-white"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Needs Review</span>
          </button>
        </div>
      </div>

      {/* Catalog Table */}
      <div className="glass-card rounded-xl overflow-hidden shadow-xl border border-slate-800/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider border-b border-slate-800 font-bold">
              <tr>
                <th className="py-3 px-4">Part #</th>
                <th className="py-3 px-4">Raw Description & Normalized Title</th>
                <th className="py-3 px-4">Canonical Brand</th>
                <th className="py-3 px-4">Taxonomy Classpath</th>
                <th className="py-3 px-4">Grounded Attributes</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {products.map((p) => {
                const confPct = Math.round(p.overall_confidence * 100);
                const tier = p.confidence_tier || "LOW";

                return (
                  <tr 
                    key={p.row_id} 
                    onClick={() => setSelectedProduct(p)}
                    className="hover:bg-slate-900/50 cursor-pointer transition-colors group"
                  >
                    {/* MPN */}
                    <td className="py-3.5 px-4 font-mono font-bold text-indigo-400 whitespace-nowrap">
                      {p.mfg_part_num}
                    </td>

                    {/* Description & Product Name */}
                    <td className="py-3.5 px-4 max-w-xs sm:max-w-sm">
                      <div className="font-semibold text-white group-hover:text-indigo-300 transition-colors truncate" title={p.product_name || p.part_desc}>
                        {p.product_name || p.part_desc}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate mt-0.5" title={p.part_desc}>
                        {p.part_desc}
                      </div>
                    </td>

                    {/* Brand */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="font-semibold text-slate-200">{p.brand_name || "Unbranded"}</span>
                      {p.manufacturer_name && (
                        <span className="block text-[10px] text-slate-500 truncate max-w-[120px]" title={p.manufacturer_name}>
                          {p.manufacturer_name}
                        </span>
                      )}
                    </td>

                    {/* Classpath */}
                    <td className="py-3.5 px-4 max-w-[180px]">
                      <span className="text-[11px] text-slate-400 line-clamp-1" title={p.classpath || ""}>
                        {p.fine || p.class_name || p.classpath || "Unclassified"}
                      </span>
                    </td>

                    {/* Grounded Attributes pill summary */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1 max-w-[160px]">
                        {p.extracted_attributes.slice(0, 2).map((a, i) => (
                          <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">
                            {a.label}: {a.value}
                          </span>
                        ))}
                        {p.extracted_attributes.length > 2 && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-950/60 text-indigo-300 font-mono font-bold">
                            +{p.extracted_attributes.length - 2} more
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Confidence Meter */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <span className={`text-[11px] font-bold ${tier === "HIGH" ? "text-emerald-400" : tier === "MEDIUM" ? "text-amber-400" : "text-rose-400"}`}>
                          {confPct}%
                        </span>
                        <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            style={{ width: `${confPct}%` }}
                            className={`h-full ${tier === "HIGH" ? "bg-emerald-400" : tier === "MEDIUM" ? "bg-amber-400" : "bg-rose-400"}`}
                          ></div>
                        </div>
                      </div>
                    </td>

                    {/* Action */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedProduct(p);
                        }}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-indigo-600 text-slate-400 hover:text-white transition-all inline-flex items-center space-x-1 text-[11px] font-semibold px-2.5"
                      >
                        <span>Passport</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })}

              {products.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    No matching products found. Try adjusting your search query or filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing <span className="text-white font-semibold">{products.length}</span> of <span className="text-white font-semibold">{totalProducts}</span> catalog records
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => onPageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-white px-2">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Product Passport Detail Modal */}
      {selectedProduct && (
        <ProductPassportModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
    </div>
  );
}
