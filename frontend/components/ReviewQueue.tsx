"use client";

import React, { useState } from "react";
import { 
  CheckCircle2, 
  Edit3, 
  XCircle, 
  AlertTriangle, 
  ShieldAlert, 
  Sparkles, 
  Clock, 
  UserCheck,
  ChevronDown,
  ChevronUp,
  Tag
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
}

interface ProductRecord {
  row_id: number;
  mfg_part_num: string;
  part_desc: string;
  part_manuf?: string | null;
  manufacturer_name?: string | null;
  brand_name?: string | null;
  classpath?: string | null;
  overall_confidence: number;
  confidence_tier: string;
  needs_review: boolean;
  review_reasons: string[];
  flags: string[];
  extracted_attributes: ExtractedAttribute[];
  review_status: string;
}

interface ReviewQueueProps {
  reviewItems: ProductRecord[];
  onAction: (rowId: number, action: "ACCEPT" | "EDIT" | "REJECT", payload?: { label?: string; value?: string; uom?: string; notes?: string }) => Promise<void>;
  loading: boolean;
}

export default function ReviewQueue({
  reviewItems,
  onAction,
  loading,
}: ReviewQueueProps) {
  const [editingRow, setEditingRow] = useState<number | null>(null);
  const [editLabel, setEditLabel] = useState("");
  const [editValue, setEditValue] = useState("");
  const [editUom, setEditUom] = useState("");
  const [notes, setNotes] = useState("");
  const [actionInProgress, setActionInProgress] = useState<number | null>(null);

  const handleEditOpen = (p: ProductRecord) => {
    setEditingRow(p.row_id);
    const firstAttr = p.extracted_attributes[0];
    if (firstAttr) {
      setEditLabel(firstAttr.label);
      setEditValue(firstAttr.value);
      setEditUom(firstAttr.uom || "");
    } else {
      setEditLabel("Brand");
      setEditValue(p.brand_name || "");
      setEditUom("");
    }
    setNotes("");
  };

  const handleEditSubmit = async (rowId: number) => {
    setActionInProgress(rowId);
    await onAction(rowId, "EDIT", {
      label: editLabel,
      value: editValue,
      uom: editUom || undefined,
      notes,
    });
    setEditingRow(null);
    setActionInProgress(null);
  };

  const handleQuickAction = async (rowId: number, action: "ACCEPT" | "REJECT") => {
    setActionInProgress(rowId);
    await onAction(rowId, action);
    setActionInProgress(null);
  };

  return (
    <div className="space-y-6">
      {/* Review Queue Header */}
      <div className="p-5 rounded-xl glass-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            <span>Human-in-the-Loop Review Queue</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {reviewItems.length} PENDING AUDITS
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Review uncertain classifications, low-confidence extractions, or duplicate warnings. Human decisions are logged to the audit trail.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
          <span className="text-slate-300 font-medium">Auto-Tuned Routing Active</span>
        </div>
      </div>

      {/* Review Items Grid */}
      <div className="space-y-4">
        {reviewItems.map((p) => {
          const isEditing = editingRow === p.row_id;
          const isBusy = actionInProgress === p.row_id;
          const confPct = Math.round(p.overall_confidence * 100);

          return (
            <div
              key={p.row_id}
              className={`glass-card rounded-xl p-5 border transition-all space-y-4 ${
                p.review_status === "ACCEPTED"
                  ? "border-emerald-500/40 bg-emerald-950/10"
                  : p.review_status === "REJECTED"
                  ? "border-rose-500/40 bg-rose-950/10 opacity-60"
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              {/* Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-mono font-bold text-indigo-400">#{p.mfg_part_num}</span>
                  <span className="text-xs font-bold text-slate-200">{p.brand_name || "Unbranded"}</span>
                  <span className="text-[11px] text-slate-500 hidden sm:inline">{p.manufacturer_name}</span>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-[11px] font-mono font-bold text-amber-400">
                    Confidence: {confPct}%
                  </span>
                  <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold border border-slate-700">
                    {p.review_status}
                  </span>
                </div>
              </div>

              {/* Raw Input vs Review Reason */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="space-y-1">
                  <span className="text-[10px] font-bold uppercase text-slate-500 block">Raw Catalog Description</span>
                  <p className="text-slate-300 font-mono bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                    {p.part_desc}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] font-bold uppercase text-amber-400 block">Review Triggers</span>
                  <div className="space-y-1">
                    {p.review_reasons && p.review_reasons.length > 0 ? (
                      p.review_reasons.map((r, i) => (
                        <div key={i} className="text-amber-300 bg-amber-950/30 p-1.5 rounded border border-amber-500/20 flex items-center gap-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-400" />
                          <span>{r}</span>
                        </div>
                      ))
                    ) : (
                      <div className="text-slate-400 italic">Score below auto-acceptance threshold (75%)</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Extracted Attributes Summary */}
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold uppercase text-slate-500 block">Extracted Specs & Grounding</span>
                <div className="flex flex-wrap gap-2">
                  {p.extracted_attributes.map((a, i) => (
                    <div key={i} className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-center space-x-2">
                      <span className="text-slate-400 font-semibold">{a.label}:</span>
                      <span className="text-white font-bold">{a.value} {a.uom || ""}</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
                        "{a.evidence || "Mapped"}"
                      </span>
                    </div>
                  ))}
                  {p.extracted_attributes.length === 0 && (
                    <span className="text-xs text-slate-500 italic">No attributes extracted.</span>
                  )}
                </div>
              </div>

              {/* Inline Edit Form */}
              {isEditing && (
                <div className="p-4 rounded-xl bg-slate-900 border border-indigo-500/40 space-y-3 animate-in fade-in duration-150">
                  <h4 className="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Curate Product Attribute</span>
                  </h4>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="text-slate-400 block mb-1">Attribute Label</label>
                      <input
                        type="text"
                        value={editLabel}
                        onChange={(e) => setEditLabel(e.target.value)}
                        placeholder="e.g. Grit, Material"
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-white"
                      />
                    </div>
                    <div>
                      <label className="text-slate-400 block mb-1">Corrected Value</label>
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        placeholder="e.g. P180, Steel"
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-white"
                      />
                    </div>
                    <div>
                      <label className="text-slate-400 block mb-1">UOM (Optional)</label>
                      <input
                        type="text"
                        value={editUom}
                        onChange={(e) => setEditUom(e.target.value)}
                        placeholder="e.g. V, in, dBA"
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-white"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-end space-x-2 pt-2">
                    <button
                      onClick={() => setEditingRow(null)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleEditSubmit(p.row_id)}
                      disabled={isBusy}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow"
                    >
                      Save Correction
                    </button>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-800/80">
                <button
                  onClick={() => handleQuickAction(p.row_id, "REJECT")}
                  disabled={isBusy}
                  className="px-3.5 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 text-xs font-semibold flex items-center gap-1.5 transition-all"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Reject</span>
                </button>

                <button
                  onClick={() => handleEditOpen(p)}
                  disabled={isBusy}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-all"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>Edit Values</span>
                </button>

                <button
                  onClick={() => handleQuickAction(p.row_id, "ACCEPT")}
                  disabled={isBusy}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 flex items-center gap-1.5 transition-all"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Approve & Accept</span>
                </button>
              </div>
            </div>
          );
        })}

        {reviewItems.length === 0 && (
          <div className="p-12 text-center glass-card rounded-2xl space-y-3">
            <UserCheck className="w-12 h-12 text-emerald-400 mx-auto" />
            <h3 className="text-base font-bold text-white">Review Queue Clean</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              All catalog records meet high confidence standards or have already been reviewed and approved by data specialists.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
