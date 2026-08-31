import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ReconRecord, RecordLifecycle } from '../types';
import { StatusPill } from '../components/ui/StatusPill';
import { Drawer } from '../components/ui/Drawer';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { Filter, ArrowRight, CheckCircle2, AlertCircle, HelpCircle, XCircle } from 'lucide-react';

interface ReconciliationProps {
  initialFilter?: string;
}

export const Reconciliation: React.FC<ReconciliationProps> = ({ initialFilter }) => {
  const [records, setRecords] = useState<ReconRecord[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>(initialFilter || 'ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<ReconRecord | null>(null);
  const [lifecycle, setLifecycle] = useState<RecordLifecycle | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  useEffect(() => {
    loadRecords();
  }, [statusFilter]);

  const loadRecords = async () => {
    setIsLoading(true);
    try {
      const res = await api.getReconRecords(statusFilter === 'ALL' ? undefined : statusFilter);
      setRecords(res.records);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectRecord = async (record: ReconRecord) => {
    setSelectedRecord(record);
    setIsLoadingDetail(true);
    try {
      const res = await api.getReconRecordDetail(record.invoice_id);
      setLifecycle(res.lifecycle);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const statuses = ['ALL', 'FULLY_RECONCILED', 'PARTIAL_MATCH', 'AMBIGUOUS', 'MISSING_BANK_TRANSACTION'];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-4 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Multi-Source Reconciliation Engine</h1>
          <p className="text-xs text-slate-400 mt-0.5">Deterministic 4-stage matching comparing Invoices vs Gateway Payments & Bank Transactions.</p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto">
          <Filter className="w-3.5 h-3.5 text-slate-500 mr-1 shrink-0" />
          {statuses.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-2.5 py-1 rounded text-[11px] font-mono uppercase tracking-wider transition-colors shrink-0 ${
                statusFilter === s
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
              }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={8} />
      ) : records.length === 0 ? (
        <EmptyState title="No Reconciliation Records" description="No reconciled records match the selected status filter." />
      ) : (
        <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090D16] border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="p-3 pl-4">Status</th>
                  <th className="p-3">Invoice</th>
                  <th className="p-3">Payment</th>
                  <th className="p-3">Settlement</th>
                  <th className="p-3">Bank Txn</th>
                  <th className="p-3 text-right">Score</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {records.map((row, idx) => (
                  <tr
                    key={idx}
                    onClick={() => handleSelectRecord(row)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="p-3 pl-4">
                      <StatusPill status={row.status} />
                    </td>
                    <td className="p-3 font-mono font-semibold text-slate-100">{row.invoice_id}</td>
                    <td className="p-3 font-mono text-slate-300">{row.payment_id || '—'}</td>
                    <td className="p-3 font-mono text-slate-300">{row.settlement_id || '—'}</td>
                    <td className="p-3 font-mono text-slate-300">{row.transaction_id || '—'}</td>
                    <td className="p-3 text-right font-mono font-bold">
                      <span className={row.match_score >= 0.85 ? 'text-emerald-400' : row.match_score >= 0.5 ? 'text-amber-400' : 'text-rose-400'}>
                        {row.match_score.toFixed(2)}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <span className="text-blue-400 hover:underline font-medium text-[11px]">Inspect →</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4-Stage Lifecycle Detail Drawer */}
      <Drawer
        isOpen={!!selectedRecord}
        onClose={() => {
          setSelectedRecord(null);
          setLifecycle(null);
        }}
        title={`Reconciliation Trail: ${selectedRecord?.invoice_id}`}
        subtitle={`Deterministic Score: ${selectedRecord?.match_score.toFixed(2)} | Status: ${selectedRecord?.status}`}
      >
        {selectedRecord && (
          <div className="space-y-6">
            {/* Visual Horizontal Lifecycle Stepper */}
            <div className="p-4 rounded-lg bg-[#090D16] border border-slate-800 space-y-3">
              <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                FINANCIAL LIFECYCLE TRAIL
              </div>
              <div className="grid grid-cols-4 gap-2 text-center text-[11px]">
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                  <div className="font-bold text-slate-200">Invoice</div>
                  <div className="text-emerald-400 text-[10px] mt-1 font-mono">✓ Created</div>
                </div>
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                  <div className="font-bold text-slate-200">Payment</div>
                  <div className="text-[10px] mt-1 font-mono">
                    {lifecycle?.payment ? <span className="text-emerald-400">✓ Received</span> : <span className="text-amber-400">⚠ Missing</span>}
                  </div>
                </div>
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                  <div className="font-bold text-slate-200">Settlement</div>
                  <div className="text-[10px] mt-1 font-mono">
                    {lifecycle?.settlement ? <span className="text-emerald-400">✓ Settled</span> : <span className="text-amber-400">⚠ Pending</span>}
                  </div>
                </div>
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                  <div className="font-bold text-slate-200">Bank Txn</div>
                  <div className="text-[10px] mt-1 font-mono">
                    {lifecycle?.bank_transaction ? <span className="text-emerald-400">✓ Matched</span> : <span className="text-rose-400">✕ Unmatched</span>}
                  </div>
                </div>
              </div>
            </div>

            {/* Calculated Evidence Notes */}
            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-blue-200">
              <div className="font-bold uppercase tracking-wider text-[10px] text-blue-400 mb-1">
                Matching Evidence Notes
              </div>
              <p>{selectedRecord.notes}</p>
            </div>

            {/* Record Inspector JSON Cards */}
            {isLoadingDetail ? (
              <LoadingSkeleton rows={4} />
            ) : (
              <div className="space-y-4">
                {lifecycle?.invoice && (
                  <div className="p-4 rounded-lg bg-[#090D16] border border-slate-800 space-y-2">
                    <div className="text-xs font-bold text-slate-300 flex items-center justify-between">
                      <span>Invoice Entity</span>
                      <span className="font-mono text-emerald-400">₹{lifecycle.invoice.total_amount?.toLocaleString()}</span>
                    </div>
                    <pre className="text-[10px] font-mono text-slate-400 bg-[#090D16] p-3 rounded border border-slate-800 overflow-x-auto">
                      {JSON.stringify(lifecycle.invoice, null, 2)}
                    </pre>
                  </div>
                )}

                {lifecycle?.bank_transaction && (
                  <div className="p-4 rounded-lg bg-[#090D16] border border-slate-800 space-y-2">
                    <div className="text-xs font-bold text-slate-300 flex items-center justify-between">
                      <span>Bank Transaction Entity</span>
                      <span className="font-mono text-emerald-400">₹{lifecycle.bank_transaction.amount?.toLocaleString()}</span>
                    </div>
                    <pre className="text-[10px] font-mono text-slate-400 bg-[#090D16] p-3 rounded border border-slate-800 overflow-x-auto">
                      {JSON.stringify(lifecycle.bank_transaction, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};
