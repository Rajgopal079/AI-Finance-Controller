import React from 'react';
import { PipelineSummaryData } from '../types';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { StatusPill } from '../components/ui/StatusPill';
import { ShieldCheck, ArrowRight, TrendingUp, AlertTriangle, ChevronRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import { PageId } from '../components/layout/Sidebar';

interface ControlRoomProps {
  data: PipelineSummaryData | null;
  isLoading: boolean;
  onNavigateTo: (page: PageId, filter?: string) => void;
}

export const ControlRoom: React.FC<ControlRoomProps> = ({ data, isLoading, onNavigateTo }) => {
  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  const { health_score, recon_metrics, exceptions, settlement_metrics, cash_forecast } = data;

  const totalExposure = exceptions.reduce((acc, curr) => acc + (curr.financial_amount || 0), 0);
  const pendingSettlementTotal = settlement_metrics.pending_amount + settlement_metrics.delayed_amount;

  const chartData = [
    { horizon: 'Current', cash: cash_forecast.current_cash_position },
    { horizon: '7-Day', cash: cash_forecast.forecasts['7_day'].projected_cash },
    { horizon: '14-Day', cash: cash_forecast.forecasts['14_day'].projected_cash },
    { horizon: '30-Day', cash: cash_forecast.forecasts['30_day'].projected_cash },
  ];

  return (
    <div className="space-y-8">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-5 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">FINANCE OPERATIONS CONTROL ROOM</h1>
          <p className="text-xs text-slate-400 mt-1">Real-time reconciliation, exception exposure, and forward liquidity. Here's what needs attention.</p>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="px-3 py-1.5 rounded bg-[#0F172A] border border-slate-800">
            <span className="text-slate-500 font-sans">HEALTH SCORE:</span>{' '}
            <span
              className={`font-bold ${
                health_score.overall_health_score >= 85
                  ? 'text-emerald-400'
                  : health_score.overall_health_score >= 70
                  ? 'text-amber-400'
                  : 'text-rose-400'
              }`}
            >
              {health_score.overall_health_score} / 100
            </span>
          </div>
        </div>
      </div>

      {/* Primary Financial Typographic Metrics (Unboxed Layout) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 py-2 border-b border-slate-800/40">
        <div>
          <div className="text-xs font-sans font-medium text-slate-400 uppercase tracking-wider">Current Cash</div>
          <div className="text-3xl font-bold font-mono text-slate-100 mt-1 tabular-nums">
            ₹{cash_forecast.current_cash_position.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-1 font-sans">Opening Bank Position</div>
        </div>

        <div>
          <div className="text-xs font-sans font-medium text-slate-400 uppercase tracking-wider">Reconciliation Rate</div>
          <div className="text-3xl font-bold font-mono text-emerald-400 mt-1 tabular-nums">
            {recon_metrics.match_rate_pct}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1 font-sans">{recon_metrics.matched_records} / {recon_metrics.total_records} Matched</div>
        </div>

        <div>
          <div className="text-xs font-sans font-medium text-slate-400 uppercase tracking-wider">Exception Exposure</div>
          <div className="text-3xl font-bold font-mono text-rose-400 mt-1 tabular-nums">
            ₹{totalExposure.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-1 font-sans">{exceptions.length} Flagged Issues</div>
        </div>

        <div>
          <div className="text-xs font-sans font-medium text-slate-400 uppercase tracking-wider">Pending Settlements</div>
          <div className="text-3xl font-bold font-mono text-amber-400 mt-1 tabular-nums">
            ₹{pendingSettlementTotal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
          <div className="text-[10px] text-slate-500 mt-1 font-sans">In Transit Inflows</div>
        </div>
      </div>

      {/* Cash Position Trajectory Chart Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-sans font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            Cash Position Trajectory
          </div>
          <button
            onClick={() => onNavigateTo('cash')}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
          >
            Detailed Projections <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5">
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorControlCash" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="horizon" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v / 100000).toFixed(1)}L`} />
                <Tooltip
                  formatter={(val: number) => [`₹${val.toLocaleString('en-IN')}`, 'Cash Position']}
                  contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '6px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="cash" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorControlCash)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Attention Required Feed Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-sans font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Attention Required
          </div>
          <button
            onClick={() => onNavigateTo('exceptions')}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
          >
            View Exception Queue ({exceptions.length}) <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {exceptions.length === 0 ? (
          <div className="p-8 text-center text-slate-400 bg-[#0F172A] rounded-lg border border-slate-800">
            <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <div className="text-xs font-semibold text-slate-200">No Operational Exceptions</div>
            <p className="text-[11px] text-slate-500 mt-1">All financial entries reconciled cleanly across bank and payment sources.</p>
          </div>
        ) : (
          <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#080C14] border-b border-slate-800 text-slate-400 uppercase tracking-wider font-sans text-[10px]">
                <tr>
                  <th className="p-3 pl-4">Severity</th>
                  <th className="p-3">Issue</th>
                  <th className="p-3">Record ID</th>
                  <th className="p-3 text-right">Amount</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {exceptions.slice(0, 8).map((exc, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 pl-4">
                      <StatusPill status={exc.severity} />
                    </td>
                    <td className="p-3 text-slate-200 max-w-sm truncate font-medium">{exc.reason}</td>
                    <td className="p-3 font-mono text-slate-400">{exc.exception_id}</td>
                    <td className="p-3 text-right font-mono font-bold text-slate-100">
                      ₹{exc.financial_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => onNavigateTo('exceptions')}
                        className="text-blue-400 hover:text-blue-300 font-medium inline-flex items-center gap-1 text-[11px]"
                      >
                        Investigate <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
