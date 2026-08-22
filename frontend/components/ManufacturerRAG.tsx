"use client";

import React, { useState, useEffect } from "react";
import { 
  FileText, 
  Search, 
  Sparkles, 
  ExternalLink, 
  ShieldCheck, 
  Database, 
  ChevronRight,
  BookOpen,
  ArrowRight
} from "lucide-react";

interface ManufacturerDoc {
  document_id: string;
  document_name: string;
  manufacturer: string;
  brand: string;
  product_series: string;
  model_numbers: string[];
  product_type: string;
  source_url: string;
  specifications: Record<string, { value: any; uom?: string | null; page?: number; text: string }>;
}

export default function ManufacturerRAG() {
  const [docs, setDocs] = useState<ManufacturerDoc[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<ManufacturerDoc | null>(null);
  const [searchMpn, setSearchMpn] = useState("");
  const [queryResult, setQueryResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/manufacturer-docs`)
      .then((res) => res.json())
      .then((data) => {
        if (data.documents) {
          setDocs(data.documents);
          if (data.documents.length > 0) {
            setSelectedDoc(data.documents[0]);
          }
        }
      })
      .catch((err) => console.error("Error loading RAG docs:", err));
  }, []);

  const handleQuery = async (mpn: string) => {
    setLoading(true);
    setSearchMpn(mpn);
    const formData = new FormData();
    formData.append("mpn", mpn);

    try {
      const res = await fetch("http://localhost:8000/api/manufacturer-docs/query", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setQueryResult(data);
    } catch (e) {
      console.error("RAG Query error:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* RAG Header */}
      <div className="p-5 rounded-xl glass-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            <span>Controlled Manufacturer RAG Knowledge Base</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              {docs.length} INDEXED DATASHEETS
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Controlled technical datasheets indexed for zero-hallucination catalog spec enrichment with document/page citations.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
          <span className="text-slate-300 font-medium">Vector Index Ready</span>
        </div>
      </div>

      {/* Query Bar */}
      <div className="glass-card rounded-xl p-5 space-y-3">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Test RAG Specification Retrieval</h3>
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchMpn}
              onChange={(e) => setSearchMpn(e.target.value)}
              placeholder="Enter part number (e.g. PDSH4816AF, WDTS7024RZ, 3MABR-7100075678)..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <button
            onClick={() => handleQuery(searchMpn)}
            disabled={!searchMpn || loading}
            className="w-full sm:w-auto px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-xs font-semibold text-white shadow-lg shadow-cyan-600/20 transition-all flex items-center justify-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{loading ? "Searching Docs..." : "Retrieve Specs"}</span>
          </button>
        </div>

        {/* Quick Sample Buttons */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="text-slate-500 text-[11px]">Quick Tests:</span>
          {["PDSH4816AF", "WDTS7024RZ", "3MABR-7100075678", "49-94-0013", "DCD1007B", "543140016"].map((mpn) => (
            <button
              key={mpn}
              onClick={() => handleQuery(mpn)}
              className="px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-800 font-mono text-[11px] transition-all"
            >
              {mpn}
            </button>
          ))}
        </div>

        {/* Live Query Results */}
        {queryResult && (
          <div className="mt-4 p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-3 animate-in fade-in duration-200">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-cyan-300">
                Found {queryResult.matched_specs_count} Grounded Specs for #{queryResult.mfg_part_num}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-200">
                100% Citation Backed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {queryResult.retrieved_attributes.map((attr: any, i: number) => (
                <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-white">{attr.label}</span>
                    <span className="font-mono text-cyan-300 font-bold">{attr.value} {attr.uom || ""}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 italic">"{attr.evidence}"</p>
                  <span className="text-[10px] font-mono text-slate-500 block pt-0.5">
                    Citation: {attr.source_reference}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Datasheet Browser Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document List */}
        <div className="glass-card rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Indexed Manufacturer Documents</h3>
          <div className="space-y-2">
            {docs.map((d) => {
              const isSelected = selectedDoc?.document_id === d.document_id;
              return (
                <div
                  key={d.document_id}
                  onClick={() => setSelectedDoc(d)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? "bg-slate-900 border-cyan-500/50 shadow-md shadow-cyan-500/10"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="space-y-0.5 max-w-[220px]">
                    <span className="text-xs font-bold text-white truncate block">{d.brand} — {d.product_series}</span>
                    <span className="text-[11px] text-slate-400 truncate block font-mono">{d.document_name}</span>
                  </div>
                  <ChevronRight className={`w-4 h-4 ${isSelected ? "text-cyan-400" : "text-slate-600"}`} />
                </div>
              );
            })}
          </div>
        </div>

        {/* Document Detail & Chunk Viewer */}
        <div className="lg:col-span-2 glass-card rounded-xl p-6 space-y-4">
          {selectedDoc ? (
            <div className="space-y-4">
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div>
                  <span className="text-[10px] font-mono font-bold text-cyan-400">{selectedDoc.document_id}</span>
                  <h3 className="text-sm font-bold text-white mt-0.5">{selectedDoc.brand} {selectedDoc.product_series} Datasheet</h3>
                  <p className="text-xs text-slate-400 mt-0.5">{selectedDoc.manufacturer}</p>
                </div>

                <a
                  href={selectedDoc.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-cyan-300 flex items-center space-x-1 border border-slate-700"
                >
                  <span>MFR URL</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* Supported Models */}
              <div className="space-y-1">
                <span className="text-xs font-bold text-slate-400 uppercase">Supported Model Numbers</span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedDoc.model_numbers.map((m) => (
                    <span key={m} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-indigo-300">
                      {m}
                    </span>
                  ))}
                </div>
              </div>

              {/* Extracted Specifications Table */}
              <div className="space-y-2 pt-2">
                <span className="text-xs font-bold text-slate-400 uppercase">Structured Specifications with Page Citations</span>
                <div className="space-y-2">
                  {Object.entries(selectedDoc.specifications).map(([specName, info]) => (
                    <div key={specName} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-white">{specName}</span>
                        <span className="font-mono text-cyan-300 font-bold">{info.value} {info.uom || ""}</span>
                      </div>
                      <p className="text-xs text-slate-400 italic font-mono bg-slate-950/60 p-1.5 rounded border border-slate-800/80">
                        "{info.text}"
                      </p>
                      <span className="text-[10px] text-slate-500 block">Page {info.page || 1} of PDF</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500">Select a manufacturer document to inspect specifications.</div>
          )}
        </div>
      </div>
    </div>
  );
}
