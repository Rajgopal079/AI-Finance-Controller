import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { EvaluationData } from '../types';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { Play, Target, Gauge } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export const Evaluation: React.FC = () => {
  const [data, setData] = useState<EvaluationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    loadEval();
  }, []);

  const loadEval = async () => {
    setIsLoading(true);
    try {
      const res = await api.getLatestEvaluation();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunEval = async () => {
    setIsRunning(true);
    try {
      const res = await api.runEvaluation();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  };

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={6} />
      </div>
    );
  }

  const confusionData = [
    { name: 'True Positives (TP)', count: data.true_positives, fill: '#10B981' },
    { name: 'True Negatives (TN)', count: data.true_negatives, fill: '#3B82F6' },
    { name: 'False Positives (FP)', count: data.false_positives, fill: '#EF4444' },
    { name: 'False Negatives (FN)', count: data.false_negatives, fill: '#F59E0B' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-4 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-100 tracking-tight">System Evaluation & Benchmarks</h1>
            <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono text-[10px] font-bold">
              SYNTHETIC BENCHMARK
            </span>
          </div>
          <p className="text-xs text-slate-400">Evaluate multi-stage deterministic reconciliation and AI predictions against synthetic Ground Truth data.</p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleRunEval}
          isLoading={isRunning}
          icon={<Play className="w-3.5 h-3.5" />}
        >
          Run System Evaluation
        </Button>
      </div>

      {/* Typographic Metric Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-2 border-b border-slate-800/40">
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">F1 Score</div>
          <div className="text-3xl font-bold font-mono text-emerald-400 mt-1 tabular-nums">
            {(data.f1_score * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Harmonic Mean</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Precision</div>
          <div className="text-3xl font-bold font-mono text-blue-400 mt-1 tabular-nums">
            {(data.precision * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-slate-500 font-mono">TP / (TP + FP)</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Recall</div>
          <div className="text-3xl font-bold font-mono text-purple-400 mt-1 tabular-nums">
            {(data.recall * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-slate-500 font-mono">TP / (TP + FN)</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Automation Rate</div>
          <div className="text-3xl font-bold font-mono text-amber-400 mt-1 tabular-nums">
            {data.automation_rate_pct}%
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Hands-Free Reconciled</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Chart */}
        <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5">
          <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Target className="w-3.5 h-3.5 text-emerald-400" />
            Confusion Breakdown
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confusionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#64748B" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '6px', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {confusionData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Operational Metrics Panel */}
        <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5 space-y-4">
          <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Gauge className="w-3.5 h-3.5 text-blue-400" />
            Performance & Throughput Metrics
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between p-3 rounded bg-[#090D16] border border-slate-800">
              <span className="text-slate-400">Total Evaluated Records</span>
              <span className="text-slate-100 font-bold">{data.total_records_processed}</span>
            </div>
            <div className="flex justify-between p-3 rounded bg-[#090D16] border border-slate-800">
              <span className="text-slate-400">Throughput Speed</span>
              <span className="text-emerald-400 font-bold">{data.throughput_records_per_sec} rec/sec</span>
            </div>
            <div className="flex justify-between p-3 rounded bg-[#090D16] border border-slate-800">
              <span className="text-slate-400">Execution Time</span>
              <span className="text-slate-200">{data.processing_time_seconds}s</span>
            </div>
            <div className="flex justify-between p-3 rounded bg-[#090D16] border border-slate-800">
              <span className="text-slate-400">Ambiguous Cases</span>
              <span className="text-amber-400 font-bold">{data.ambiguous_records}</span>
            </div>
            <div className="flex justify-between p-3 rounded bg-[#090D16] border border-slate-800">
              <span className="text-slate-400">Exception Rate</span>
              <span className="text-rose-400 font-bold">{data.exception_rate_pct}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
