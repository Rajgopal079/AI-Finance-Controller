import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { AIStatus } from '../../types';
import { Cpu, RefreshCw, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';

interface NavbarProps {
  onRunPipeline: () => void;
  isRunningPipeline: boolean;
  onOpenDemoModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onRunPipeline,
  isRunningPipeline,
  onOpenDemoModal,
}) => {
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);

  useEffect(() => {
    api.getAIStatus().then(setAiStatus).catch(() => null);
  }, []);

  return (
    <header className="h-14 border-b border-slate-800/80 bg-[#080C14] px-6 flex items-center justify-between sticky top-0 z-30 select-none">
      <div className="flex items-center gap-3">
        <div className="w-6 h-6 rounded bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-mono font-bold text-xs">
          FC
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-bold text-slate-100 tracking-tight">FINCTRL</span>
          <span className="text-[10px] text-slate-500 uppercase tracking-wider hidden sm:inline font-sans">
            Finance Operations Controller
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Demo Mode Button */}
        <button
          onClick={onOpenDemoModal}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border border-slate-700/80 text-xs font-sans font-medium transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span>Demo Mode</span>
        </button>

        {aiStatus && (
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-xs">
            <Cpu className={`w-3.5 h-3.5 ${aiStatus.is_available ? 'text-purple-400' : 'text-amber-400'}`} />
            <span className="font-mono text-slate-300 text-[11px]">{aiStatus.model_name}</span>
            <span className={`px-1.5 py-0.2 text-[9px] font-mono font-bold rounded ${aiStatus.is_available ? 'bg-purple-500/20 text-purple-300' : 'bg-amber-500/20 text-amber-300'}`}>
              {aiStatus.is_available ? 'ONLINE' : 'FALLBACK'}
            </span>
          </div>
        )}

        <Button
          variant="primary"
          size="sm"
          onClick={onRunPipeline}
          isLoading={isRunningPipeline}
          icon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Run Controller
        </Button>
      </div>
    </header>
  );
};
