import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { TaxSummary, TaxDiscrepancyItem } from '../types';
import { StatusPill } from '../components/ui/StatusPill';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { Receipt } from 'lucide-react';

export const Tax: React.FC = () => {
  const [summary, setSummary] = useState<TaxSummary | null>(null);
  const [mismatches, setMismatches] = useState<TaxDiscrepancyItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadTaxData();
  }, []);

  const loadTaxData = async () => {
    setIsLoading(true);
    try {
      const [sumRes, mismRes] = await Promise.all([
        api.getTaxSummary(),
        api.getTaxMismatches()
      ]);
      setSummary(sumRes);
      setMismatches(mismRes.all_details || mismRes.mismatches);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !summary) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={5} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800/60 pb-4">
        <h1 className="text-xl font-bold text-slate-100 tracking-tight">Tax Matching & GST Discrepancy Engine</h1>
        <p className="text-xs text-slate-400 mt-0.5">Deterministic GST/CGST/SGST/IGST tax calculation verification comparing Recorded vs Expected Tax.</p>
      </div>

      {/* Typographic Unboxed Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-2 border-b border-slate-800/40">
        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Total Tax Lines</div>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-1 tabular-nums">{summary.total_tax_lines}</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Tax Consistency</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1 tabular-nums">{summary.match_rate_pct}%</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Tax Mismatches</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1 tabular-nums">{summary.discrepancy_count}</div>
        </div>

        <div>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Total Tax Exposure</div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-1 tabular-nums">
            ₹{summary.total_discrepancy_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Dense Tax Table */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg overflow-hidden">
        <div className="p-3.5 bg-[#090D16] border-b border-slate-800 flex items-center justify-between">
          <div className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Receipt className="w-3.5 h-3.5 text-blue-400" />
            GST Discrepancy Audit Log
          </div>
          <span className="text-xs font-mono text-slate-400">{mismatches.length} Evaluated Lines</span>
        </div>

        {mismatches.length === 0 ? (
          <EmptyState title="No Tax Discrepancies" description="All evaluated tax lines match expected GST calculations exactly." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090D16] border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="p-3 pl-4">Tax Line</th>
                  <th className="p-3">Invoice</th>
                  <th className="p-3">Customer</th>
                  <th className="p-3">Tax Type</th>
                  <th className="p-3 text-right">Taxable Amt</th>
                  <th className="p-3 text-right">Expected</th>
                  <th className="p-3 text-right">Recorded</th>
                  <th className="p-3 text-right">Difference</th>
                  <th className="p-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {mismatches.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 pl-4 font-mono text-slate-400">{item.tax_line_id}</td>
                    <td className="p-3 font-mono font-semibold text-slate-100">{item.invoice_id}</td>
                    <td className="p-3 text-slate-300">{item.customer_name}</td>
                    <td className="p-3 font-mono text-blue-400">{item.tax_type}</td>
                    <td className="p-3 text-right font-mono text-slate-300">₹{item.taxable_amount?.toLocaleString()}</td>
                    <td className="p-3 text-right font-mono text-emerald-400">₹{item.expected_tax?.toLocaleString()}</td>
                    <td className="p-3 text-right font-mono text-slate-300">₹{item.recorded_tax?.toLocaleString()}</td>
                    <td className="p-3 text-right font-mono font-bold text-rose-400">
                      ₹{item.discrepancy_amount?.toLocaleString()}
                    </td>
                    <td className="p-3 text-right">
                      <StatusPill status={item.status} />
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
