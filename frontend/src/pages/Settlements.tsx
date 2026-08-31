import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { SettlementMetrics } from '../types';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { CreditCard, Send, HelpCircle } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export const Settlements: React.FC = () => {
  const [metrics, setMetrics] = useState<SettlementMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [question, setQuestion] = useState('Which gateway has the most delays?');
  const [qaResult, setQaResult] = useState<{ answer: string; evidence: any } | null>(null);
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    setIsLoading(true);
    try {
      const res = await api.getSettlementsSummary();
      setMetrics(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAsk = async (q?: string) => {
    const query = q || question;
    if (!query) return;
    setIsAsking(true);
    try {
      const res = await api.askSettlementQuestion(query);
      setQaResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAsking(false);
    }
  };

  if (isLoading || !metrics) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={5} />
      </div>
    );
  }

  const gatewayData = Object.entries(metrics.gateway_breakdown || {}).map(([gw, data]) => ({
    gateway: gw,
    delayRate: data.delay_rate_pct,
    totalAmount: data.total_amount
  }));

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800/60 pb-4">
        <h1 className="text-xl font-bold text-slate-100 tracking-tight">Settlement Intelligence & Analytics</h1>
        <p className="text-xs text-slate-400 mt-0.5">Payment gateway clearing performance, duration metrics, and ground-truth evidence queries.</p>
      </div>

      {/* Typographic Unboxed Metric Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-2 border-b border-slate-800/40">
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Total Settlements</div>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-1 tabular-nums">{metrics.total_count}</div>
        </div>
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Settled Amount</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1 tabular-nums">
            ₹{metrics.total_settled_amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
        </div>
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Pending / Delayed</div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-1 tabular-nums">
            ₹{(metrics.pending_amount + metrics.delayed_amount).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
        </div>
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Success Rate</div>
          <div className="text-2xl font-bold font-mono text-blue-400 mt-1 tabular-nums">{metrics.success_rate_pct}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gateway Delay Chart */}
        <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5 flex flex-col justify-between">
          <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
            <CreditCard className="w-3.5 h-3.5 text-blue-400" />
            Gateway Delay Rate %
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={gatewayData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="gateway" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} tickLine={false} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '6px', fontSize: '12px' }}
                />
                <Bar dataKey="delayRate" radius={[4, 4, 0, 0]}>
                  {gatewayData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.delayRate > 20 ? '#EF4444' : entry.delayRate > 5 ? '#F59E0B' : '#10B981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Settlement Q&A Tool */}
        <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-1 flex items-center gap-2">
              <HelpCircle className="w-3.5 h-3.5 text-purple-400" />
              Settlement Intelligence Console
            </div>
            <p className="text-xs text-slate-400">Execute grounded queries against gateway settlement records.</p>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about gateway delays..."
              className="flex-1 bg-[#090D16] border border-slate-700 rounded px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
            />
            <Button size="sm" variant="primary" onClick={() => handleAsk()} isLoading={isAsking} icon={<Send className="w-3.5 h-3.5" />}>
              Query
            </Button>
          </div>

          {qaResult && (
            <div className="p-4 rounded bg-[#090D16] border border-purple-500/30 space-y-3 text-xs">
              <div>
                <span className="text-[10px] text-purple-400 font-mono font-bold uppercase tracking-wider block">Answer</span>
                <p className="text-slate-100 font-medium">{qaResult.answer}</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider block mb-1">Source Evidence</span>
                <pre className="text-[10px] font-mono text-slate-400 bg-slate-950 p-2.5 rounded border border-slate-800 overflow-x-auto max-h-36">
                  {JSON.stringify(qaResult.evidence, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
