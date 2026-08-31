import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ExceptionItem } from '../types';
import { StatusPill } from '../components/ui/StatusPill';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { AlertTriangle, Bot, CheckCircle, XCircle, ShieldAlert, Filter } from 'lucide-react';

interface ExceptionsProps {
  initialSeverity?: string;
}

export const Exceptions: React.FC<ExceptionsProps> = ({ initialSeverity }) => {
  const [exceptions, setExceptions] = useState<ExceptionItem[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<string>(initialSeverity || 'ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('OPEN,UNDER_REVIEW,ESCALATED');
  const [isLoading, setIsLoading] = useState(true);

  const [aiAnalysis, setAiAnalysis] = useState<Record<string, any>>({});
  const [investigatingId, setInvestigatingId] = useState<string | null>(null);

  useEffect(() => {
    loadExceptions();
  }, [selectedSeverity, selectedStatus]);

  const loadExceptions = async () => {
    setIsLoading(true);
    try {
      const res = await api.getExceptions(
        selectedSeverity === 'ALL' ? undefined : selectedSeverity,
        selectedStatus === 'ALL' ? undefined : selectedStatus
      );
      setExceptions(res.exceptions);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInvestigate = async (id: string) => {
    setInvestigatingId(id);
    try {
      const res = await api.investigateException(id);
      setAiAnalysis((prev) => ({ ...prev, [id]: res }));
    } catch (err) {
      console.error(err);
    } finally {
      setInvestigatingId(null);
    }
  };

  const handleAction = async (id: string, action: 'approve' | 'reject' | 'escalate' | 'resolve') => {
    try {
      if (action === 'approve') await api.approveException(id);
      if (action === 'reject') await api.rejectException(id);
      if (action === 'escalate') await api.escalateException(id);
      if (action === 'resolve') await api.resolveException(id);
      await loadExceptions();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-4 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Exception Triage & Human Approval</h1>
          <p className="text-xs text-slate-400 mt-0.5">Investigate flagged financial exposure with evidence-backed local AI reasoning.</p>
        </div>

        {/* Severity Filter Toolbar */}
        <div className="flex items-center gap-1.5 overflow-x-auto">
          <Filter className="w-3.5 h-3.5 text-slate-500 mr-1 shrink-0" />
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              className={`px-2.5 py-1 rounded text-[11px] font-mono uppercase tracking-wider transition-colors shrink-0 ${
                selectedSeverity === sev
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold'
                  : 'text-slate-400 hover:text-slate-200 border border-transparent'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : exceptions.length === 0 ? (
        <EmptyState title="No Open Exceptions" description="All financial entries are reconciled. No pending exceptions in triage queue." />
      ) : (
        <div className="space-y-4">
          {exceptions.map((exc) => {
            const ai = aiAnalysis[exc.exception_id];
            const isBusy = investigatingId === exc.exception_id;

            return (
              <div
                key={exc.exception_id}
                className="bg-[#0F172A] border border-slate-800/80 rounded-lg p-5 space-y-4 hover:border-slate-700/80 transition-colors"
              >
                {/* Exception Summary Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/60 pb-3">
                  <div className="flex items-center gap-3">
                    <StatusPill status={exc.severity} />
                    <span className="font-mono text-xs font-bold text-slate-100">{exc.exception_id}</span>
                    <span className="text-xs text-slate-400 font-mono">• {exc.type}</span>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right font-mono">
                      <span className="text-[10px] text-slate-500 uppercase block">Exposure Amount</span>
                      <span className="text-sm font-bold text-rose-400 tabular-nums">
                        ₹{exc.financial_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <StatusPill status={exc.status} />
                  </div>
                </div>

                {/* Reason Explanation */}
                <p className="text-xs text-slate-300 leading-relaxed font-sans">{exc.reason}</p>

                {/* AI Reasoning Panel */}
                {ai && (
                  <div className="p-4 rounded bg-[#090D16] border border-purple-500/30 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-purple-300 font-bold font-mono text-[11px]">
                        <Bot className="w-3.5 h-3.5" />
                        FINCTRL Analyst Reasoning
                      </div>
                      <span className="text-[10px] font-mono text-purple-400 bg-purple-500/20 px-2 py-0.5 rounded">
                        Confidence: {(ai.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-slate-200 text-xs">{ai.reason}</p>
                    {ai.recommended_action && (
                      <div className="text-[11px] font-mono text-purple-300">
                        <span className="text-slate-500">Recommended:</span> {ai.recommended_action}
                      </div>
                    )}
                  </div>
                )}

                {/* Action Buttons Toolbar */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleInvestigate(exc.exception_id)}
                    isLoading={isBusy}
                    icon={<Bot className="w-3.5 h-3.5 text-purple-400" />}
                  >
                    {ai ? 'Re-run Investigation' : 'Investigate via AI'}
                  </Button>

                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleAction(exc.exception_id, 'approve')}
                      icon={<CheckCircle className="w-3.5 h-3.5" />}
                    >
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => handleAction(exc.exception_id, 'reject')}
                      icon={<XCircle className="w-3.5 h-3.5" />}
                    >
                      Reject
                    </Button>
                    <Button
                      size="sm"
                      variant="warning"
                      onClick={() => handleAction(exc.exception_id, 'escalate')}
                      icon={<ShieldAlert className="w-3.5 h-3.5" />}
                    >
                      Escalate
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
