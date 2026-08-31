import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { AuditLogItem } from '../types';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { ShieldCheck, CheckCircle2, Hash, ShieldAlert } from 'lucide-react';

export const Audit: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; events_verified: number; violations: string[] } | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    setIsLoading(true);
    try {
      const res = await api.getAuditLogs(200);
      setLogs(res.logs);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const res = await api.verifyAuditChain();
      setVerifyResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-4 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Audit Trail & Chain Verification</h1>
          <p className="text-xs text-slate-400 mt-0.5">SHA-256 hash-chained log tracking automated decisions, AI investigations, and human approvals.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-[#0F172A] border border-slate-800 text-xs font-mono">
            <span className="text-slate-500">AUDIT INTEGRITY:</span>
            {verifyResult ? (
              verifyResult.valid ? (
                <span className="text-emerald-400 font-bold flex items-center gap-1">✓ VERIFIED</span>
              ) : (
                <span className="text-rose-400 font-bold flex items-center gap-1">✕ VIOLATION</span>
              )
            ) : (
              <span className="text-slate-300 font-bold">UNCHECKED</span>
            )}
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={handleVerify}
            isLoading={isVerifying}
            className="bg-emerald-600 hover:bg-emerald-500 border-emerald-500"
            icon={<ShieldCheck className="w-3.5 h-3.5" />}
          >
            Verify Integrity
          </Button>
        </div>
      </div>

      {verifyResult && (
        <div
          className={`p-3.5 rounded border text-xs font-mono flex items-center gap-3 ${
            verifyResult.valid
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
          }`}
        >
          {verifyResult.valid ? <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" /> : <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />}
          <div>
            {verifyResult.valid
              ? `${verifyResult.events_verified} sequential events verified. Hash chain unbroken.`
              : `${verifyResult.violations.length} hash violations detected in log chain.`}
          </div>
        </div>
      )}

      {/* Audit Log Table */}
      <div className="bg-[#0F172A] border border-slate-800/80 rounded-lg overflow-hidden">
        <div className="p-3.5 bg-[#090D16] border-b border-slate-800 flex items-center justify-between">
          <div className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Hash className="w-3.5 h-3.5 text-blue-400" />
            Audit Trail ({logs.length} Logged Events)
          </div>
        </div>

        {isLoading ? (
          <LoadingSkeleton rows={6} />
        ) : logs.length === 0 ? (
          <EmptyState title="No Audit Logs" description="No system audit events logged yet." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090D16] border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="p-3 pl-4">Timestamp</th>
                  <th className="p-3">User Action</th>
                  <th className="p-3">Record ID</th>
                  <th className="p-3">Agent Action</th>
                  <th className="p-3">Decision</th>
                  <th className="p-3 text-right">Human Approval</th>
                  <th className="p-3 text-right">SHA-256 Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {logs.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-3 pl-4 font-mono text-slate-400 text-[11px]">{item.timestamp}</td>
                    <td className="p-3 font-semibold text-slate-200">{item.user_action}</td>
                    <td className="p-3 font-mono text-blue-400">{item.record_id}</td>
                    <td className="p-3 text-slate-300">{item.agent_action}</td>
                    <td className="p-3 text-slate-200">{item.decision}</td>
                    <td className="p-3 text-right font-mono">
                      {item.human_approval ? (
                        <span className="text-emerald-400 font-bold">YES</span>
                      ) : (
                        <span className="text-slate-500">NO</span>
                      )}
                    </td>
                    <td className="p-3 text-right font-mono text-[10px] text-slate-400 truncate max-w-xs" title={item.current_hash}>
                      {item.current_hash ? `${item.current_hash.slice(0, 14)}...` : '—'}
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
