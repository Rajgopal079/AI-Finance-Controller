import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { CashForecastData } from '../types';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { TrendingUp, Calendar, ArrowRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

export const Cash: React.FC = () => {
  const [data, setData] = useState<CashForecastData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedHorizon, setSelectedHorizon] = useState<'7_day' | '14_day' | '30_day'>('30_day');

  useEffect(() => {
    loadForecast();
  }, []);

  const loadForecast = async () => {
    setIsLoading(true);
    try {
      const res = await api.getCashForecast();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={5} />
      </div>
    );
  }

  const chartData = [
    { horizon: 'Current', cash: data.current_cash_position },
    { horizon: '7-Day', cash: data.forecasts['7_day'].projected_cash },
    { horizon: '14-Day', cash: data.forecasts['14_day'].projected_cash },
    { horizon: '30-Day', cash: data.forecasts['30_day'].projected_cash },
  ];

  const currentHorizonData = data.forecasts[selectedHorizon];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-4 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Forward Cash Forecaster</h1>
          <p className="text-xs text-slate-400 mt-0.5">Deterministic forward liquidity trajectory based on bank opening cash, receivables, and pending settlements.</p>
        </div>

        {/* Horizon Segmented Control */}
        <div className="flex items-center bg-[#0F172A] p-1 rounded border border-slate-800">
          {(['7_day', '14_day', '30_day'] as const).map((h) => (
            <button
              key={h}
              onClick={() => setSelectedHorizon(h)}
              className={`px-3 py-1 rounded text-xs font-mono font-bold transition-colors ${
                selectedHorizon === h
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {h.replace('_day', 'D').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Large Typographic Cash Headline */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 py-2 border-b border-slate-800/40">
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Current Cash</div>
          <div className="text-3xl font-bold font-mono text-slate-100 mt-1 tabular-nums">
            ₹{(data.current_cash_position / 100000).toFixed(2)}L
          </div>
          <div className="text-[10px] text-slate-500 font-mono">₹{data.current_cash_position.toLocaleString('en-IN')}</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Projected {selectedHorizon.replace('_day', 'D')} Cash</div>
          <div className="text-3xl font-bold font-mono text-emerald-400 mt-1 tabular-nums">
            ₹{(currentHorizonData.projected_cash / 100000).toFixed(2)}L
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Forecast Horizon Target</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Expected Inflows</div>
          <div className="text-3xl font-bold font-mono text-blue-400 mt-1 tabular-nums">
            ₹{(currentHorizonData.expected_inflow / 100000).toFixed(2)}L
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Outstanding Receivables</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Pending Settlements</div>
          <div className="text-3xl font-bold font-mono text-amber-400 mt-1 tabular-nums">
            ₹{(data.pending_settlements / 100000).toFixed(2)}L
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Gateway In Transit</div>
        </div>
      </div>

      {/* Large Trajectory Chart */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5">
        <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
          <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
          Projected Cash Trajectory (INR)
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCashPage" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="horizon" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={(v) => `₹${(v / 100000).toFixed(1)}L`} />
              <Tooltip
                formatter={(val: number) => [`₹${val.toLocaleString('en-IN')}`, 'Projected Cash']}
                contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', borderRadius: '6px', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="cash" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorCashPage)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Driver Receivables Section */}
      <div className="space-y-3">
        <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
          Expected Inflow Driver Receivables
        </div>

        {!data.major_drivers || data.major_drivers.length === 0 ? (
          <div className="p-6 text-center text-slate-400 text-xs bg-[#0F172A] rounded-lg border border-slate-800">
            No unpaid receivables driving cash forecasts.
          </div>
        ) : (
          <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090D16] border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="p-3 pl-4">Invoice ID</th>
                  <th className="p-3">Customer</th>
                  <th className="p-3">Due Date</th>
                  <th className="p-3 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {data.major_drivers.map((driver, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 pl-4 font-mono font-semibold text-slate-100">{driver.invoice_id}</td>
                    <td className="p-3 text-slate-300">{driver.customer_name}</td>
                    <td className="p-3 font-mono text-slate-400">{driver.due_date}</td>
                    <td className="p-3 text-right font-mono font-bold text-emerald-400">
                      ₹{driver.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
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
