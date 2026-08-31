import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { AIStatus } from '../../types';
import {
  LayoutDashboard,
  RefreshCw,
  AlertTriangle,
  CreditCard,
  TrendingUp,
  Receipt,
  Bot,
  ShieldCheck,
  BarChart3,
  Database
} from 'lucide-react';

export type PageId =
  | 'control-room'
  | 'reconciliation'
  | 'exceptions'
  | 'settlements'
  | 'cash'
  | 'tax'
  | 'ai-analyst'
  | 'audit'
  | 'evaluation'
  | 'data-management';

interface SidebarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onSelectPage }) => {
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);

  useEffect(() => {
    api.getAIStatus().then(setAiStatus).catch(() => null);
  }, []);

  const groups: Array<{
    title: string;
    items: Array<{ id: PageId; label: string; icon: React.ReactNode }>;
  }> = [
    {
      title: 'CONTROL',
      items: [
        { id: 'control-room', label: 'Overview', icon: <LayoutDashboard className="w-3.5 h-3.5" /> },
        { id: 'reconciliation', label: 'Reconciliation', icon: <RefreshCw className="w-3.5 h-3.5" /> },
        { id: 'exceptions', label: 'Exceptions', icon: <AlertTriangle className="w-3.5 h-3.5" /> },
        { id: 'settlements', label: 'Settlements', icon: <CreditCard className="w-3.5 h-3.5" /> },
        { id: 'cash', label: 'Cash', icon: <TrendingUp className="w-3.5 h-3.5" /> },
        { id: 'tax', label: 'Tax', icon: <Receipt className="w-3.5 h-3.5" /> },
      ],
    },
    {
      title: 'INTELLIGENCE',
      items: [
        { id: 'ai-analyst', label: 'AI Analyst', icon: <Bot className="w-3.5 h-3.5" /> },
        { id: 'audit', label: 'Audit', icon: <ShieldCheck className="w-3.5 h-3.5" /> },
        { id: 'evaluation', label: 'Evaluation', icon: <BarChart3 className="w-3.5 h-3.5" /> },
      ],
    },
    {
      title: 'SYSTEM',
      items: [
        { id: 'data-management', label: 'Data Management', icon: <Database className="w-3.5 h-3.5" /> },
      ],
    },
  ];

  return (
    <aside className="w-56 border-r border-slate-800/80 bg-[#080C14] flex flex-col justify-between shrink-0 select-none">
      <div className="p-3 space-y-5">
        {groups.map((group, idx) => (
          <div key={idx} className="space-y-1">
            <div className="px-2.5 py-1 text-[10px] font-sans font-bold text-slate-500 uppercase tracking-widest">
              {group.title}
            </div>
            {group.items.map((item) => {
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectPage(item.id)}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded text-xs font-sans font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600/10 text-blue-400 font-semibold border-l-2 border-blue-500 pl-2'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* Bottom Status Indicator */}
      <div className="p-3 border-t border-slate-800/60">
        <div className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-slate-900/60 text-[11px]">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              aiStatus?.is_available ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
            }`}
          />
          <div className="flex-1 truncate">
            <span className="text-slate-300 font-mono text-[10px] block truncate">
              {aiStatus?.model_name || 'llama3.2:3b'}
            </span>
            <span className="text-[9px] text-slate-500 font-mono uppercase">
              {aiStatus?.is_available ? 'ONLINE' : 'FALLBACK'}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
