import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, ArrowRight } from 'lucide-react';
import { PageId } from '../layout/Sidebar';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectScenario: (page: PageId, filter?: string) => void;
}

export const DemoModal: React.FC<DemoModalProps> = ({ isOpen, onClose, onSelectScenario }) => {
  const scenarios = [
    { id: 1, title: 'Exact Match', desc: '4-stage lifecycle match (Invoice -> Payment -> Settlement -> Bank)', page: 'reconciliation' as PageId, filter: 'FULLY_RECONCILED' },
    { id: 2, title: 'Partial Payment', desc: 'Underpaid invoice flagged with PARTIAL_MATCH status', page: 'reconciliation' as PageId, filter: 'PARTIAL_MATCH' },
    { id: 3, title: 'Duplicate Payment', desc: 'CRITICAL duplicate payment attempt detection', page: 'exceptions' as PageId, filter: 'CRITICAL' },
    { id: 4, title: 'Delayed Settlement', desc: 'Gateway settlement duration metric exceeding P90 threshold', page: 'settlements' as PageId },
    { id: 5, title: 'Tax Mismatch', desc: 'GST rate formula calculation mismatch audit line', page: 'tax' as PageId },
    { id: 6, title: 'Large Financial Discrepancy', desc: 'Prioritized high exposure exception requiring triage', page: 'exceptions' as PageId, filter: 'CRITICAL' },
    { id: 7, title: 'Pending Settlement', desc: 'Gateway funds in transit projected in liquidity forecast', page: 'cash' as PageId },
    { id: 8, title: 'Ambiguous Reference Conflict', desc: 'Conflicting reference identity safely flagged for refusal/review', page: 'reconciliation' as PageId, filter: 'AMBIGUOUS' },
  ];

  const handleSelect = (page: PageId, filter?: string) => {
    onSelectScenario(page, filter);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-xs z-50"
          />
          <div className="fixed inset-0 flex items-center justify-center p-4 z-50 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.96, y: -8 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: -8 }}
              transition={{ duration: 0.15 }}
              className="w-full max-w-xl bg-[#0F172A] border border-slate-800 rounded-xl shadow-2xl overflow-hidden pointer-events-auto flex flex-col"
            >
              {/* Modal Header */}
              <div className="p-4 px-6 border-b border-slate-800 flex items-center justify-between bg-[#0B0F19]">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded bg-blue-500/20 text-blue-400 flex items-center justify-center">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">Demo Mode — Test Scenarios</h3>
                    <p className="text-[11px] text-slate-400">Select a pre-configured scenario to demonstrate engine capabilities.</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Scenario List */}
              <div className="p-3 divide-y divide-slate-800/60 max-h-[70vh] overflow-y-auto">
                {scenarios.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleSelect(s.page, s.filter)}
                    className="w-full text-left p-3 rounded-lg hover:bg-slate-800/60 transition-colors flex items-center justify-between group"
                  >
                    <div className="flex items-start gap-3">
                      <span className="w-5 h-5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[11px] font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                        {s.id}
                      </span>
                      <div>
                        <div className="text-xs font-bold text-slate-200 group-hover:text-blue-400 transition-colors">
                          {s.title}
                        </div>
                        <div className="text-[11px] text-slate-400">{s.desc}</div>
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-blue-400 transition-colors shrink-0" />
                  </button>
                ))}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
