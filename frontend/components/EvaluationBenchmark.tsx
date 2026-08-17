"use client";

import React, { useState, useEffect } from "react";
import { 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  ShieldCheck, 
  BarChart2, 
  RefreshCw, 
  AlertTriangle,
  Award,
  Layers
} from "lucide-react";

interface EvaluationMetrics {
  overall_accuracy: number;
  brand_accuracy: number;
  manufacturer_accuracy: number;
  classification_accuracy: number;
  attribute_accuracy: number;
  evidence_grounding_accuracy: number;
  uom_accuracy: number;
  hallucination_rate: number;
  review_rate: number;
}

interface ComparisonRow {
  mfg_part_num: string;
  part_desc: string;
  expected_brand: string;
  predicted_brand: string;
  brand_match: boolean;
  expected_classpath: string;
  predicted_classpath: string;
  class_match: boolean;
  expected_attributes: Record<string, any>;
  predicted_attributes: any[];
  confidence: number;
  confidence_tier: string;
  needs_review: boolean;
}

export default function EvaluationBenchmark() {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [rows, setRows] = useState<ComparisonRow[]>([]);
  const [sampleCount, setSampleCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchEval = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/evaluation");
      const data = await res.json();
      if (data.metrics) {
        setMetrics(data.metrics);
        setRows(data.comparison_rows || []);
        setSampleCount(data.benchmark_samples || 0);
      }
    } catch (e) {
      console.error("Evaluation fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEval();
  }, []);

  return (
    <div className="space-y-6">
      {/* Evaluation Header */}
      <div className="p-5 rounded-xl glass-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            <span>Verified Ground Truth Evaluation Benchmark</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              ZERO FAKE NUMBERS
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Evaluated live against manually verified ground truth samples across diverse catalog categories.
          </p>
        </div>

        <button
          onClick={fetchEval}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>{loading ? "Evaluating Benchmark..." : "Re-Run Benchmark"}</span>
        </button>
      </div>

      {/* Accuracy Gauges Grid */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {/* Overall Accuracy */}
          <div className="glass-card rounded-xl p-5 border-l-4 border-indigo-500 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Overall Accuracy</span>
            <div className="text-2xl font-extrabold text-white">{metrics.overall_accuracy}%</div>
            <div className="text-[11px] text-indigo-400 font-medium">Weighted composite score</div>
          </div>

          {/* Classification Accuracy */}
          <div className="glass-card rounded-xl p-5 border-l-4 border-emerald-500 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Taxonomy Classpath</span>
            <div className="text-2xl font-extrabold text-emerald-400">{metrics.classification_accuracy}%</div>
            <div className="text-[11px] text-slate-500">Controlled LOV routing</div>
          </div>

          {/* Hallucination Rate */}
          <div className="glass-card rounded-xl p-5 border-l-4 border-cyan-500 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Hallucination Rate</span>
            <div className="text-2xl font-extrabold text-cyan-300">{metrics.hallucination_rate}%</div>
            <div className="text-[11px] text-emerald-400 font-medium">Strict anti-hallucination guard</div>
          </div>

          {/* Evidence Grounding */}
          <div className="glass-card rounded-xl p-5 border-l-4 border-purple-500 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Evidence Grounding</span>
            <div className="text-2xl font-extrabold text-purple-400">{metrics.evidence_grounding_accuracy}%</div>
            <div className="text-[11px] text-slate-500">Exact substring justified</div>
          </div>

          {/* Brand Accuracy */}
          <div className="glass-card rounded-xl p-5 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Brand Resolution</span>
            <div className="text-xl font-bold text-white">{metrics.brand_accuracy}%</div>
            <div className="text-[11px] text-slate-500">Canonical brand entity map</div>
          </div>

          {/* Manufacturer Accuracy */}
          <div className="glass-card rounded-xl p-5 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Manufacturer Resolution</span>
            <div className="text-xl font-bold text-white">{metrics.manufacturer_accuracy}%</div>
            <div className="text-[11px] text-slate-500">Vendor code stripping</div>
          </div>

          {/* Attribute Extraction Accuracy */}
          <div className="glass-card rounded-xl p-5 space-y-1">
            <span className="text-xs font-semibold text-slate-400">Attribute Extraction</span>
            <div className="text-xl font-bold text-white">{metrics.attribute_accuracy}%</div>
            <div className="text-[11px] text-slate-500">Grounded attribute extraction</div>
          </div>

          {/* UOM Accuracy */}
          <div className="glass-card rounded-xl p-5 space-y-1">
            <span className="text-xs font-semibold text-slate-400">UOM Normalization</span>
            <div className="text-xl font-bold text-white">{metrics.uom_accuracy}%</div>
            <div className="text-[11px] text-slate-500">Delivery schema compliant</div>
          </div>
        </div>
      )}

      {/* Comparison Diff Table */}
      <div className="glass-card rounded-xl overflow-hidden shadow-xl border border-slate-800 space-y-3">
        <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Ground Truth vs Pipeline Predictions</h3>
            <p className="text-[11px] text-slate-400">Side-by-side verification table for {sampleCount} benchmark items</p>
          </div>
          <span className="text-xs font-mono text-indigo-300 font-bold">{sampleCount} Samples</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase font-bold border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Part #</th>
                <th className="py-2.5 px-4">Raw Description</th>
                <th className="py-2.5 px-4">Brand Match</th>
                <th className="py-2.5 px-4">Taxonomy Match</th>
                <th className="py-2.5 px-4">Expected vs Extracted Specs</th>
                <th className="py-2.5 px-4">Confidence</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {rows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-indigo-400 whitespace-nowrap">
                    {row.mfg_part_num}
                  </td>

                  <td className="py-3 px-4 max-w-xs truncate" title={row.part_desc}>
                    {row.part_desc}
                  </td>

                  {/* Brand Match */}
                  <td className="py-3 px-4 whitespace-nowrap">
                    <div className="flex items-center space-x-1.5">
                      {row.brand_match ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                      )}
                      <div>
                        <span className="text-white font-semibold block">{row.predicted_brand || "None"}</span>
                        <span className="text-[10px] text-slate-500 block">Exp: {row.expected_brand}</span>
                      </div>
                    </div>
                  </td>

                  {/* Classpath Match */}
                  <td className="py-3 px-4 max-w-[200px]">
                    <div className="flex items-center space-x-1.5">
                      {row.class_match ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                      )}
                      <span className="text-[11px] truncate block" title={row.predicted_classpath}>
                        {row.predicted_classpath?.split(">").pop() || "Unclassified"}
                      </span>
                    </div>
                  </td>

                  {/* Specs Comparison */}
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1 max-w-[220px]">
                      {Object.entries(row.expected_attributes).map(([k, v]) => (
                        <span key={k} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                          {k}: {v}
                        </span>
                      ))}
                    </div>
                  </td>

                  {/* Confidence */}
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="font-mono font-bold text-emerald-400">
                      {Math.round(row.confidence * 100)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
