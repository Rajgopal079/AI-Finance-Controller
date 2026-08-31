import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { AIStatus, AIAskResponse } from '../types';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { Bot, Send, Terminal, Cpu, Database } from 'lucide-react';

export const AIAnalyst: React.FC = () => {
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<AIStatus | null>(null);
  const [response, setResponse] = useState<AIAskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    api.getAIStatus().then(setStatus).catch(() => null);
  }, []);

  const sampleQuestions = [
    "What's driving today's exceptions?",
    "Which unresolved issue has the largest exposure?",
    "How much cash is expected in the next 7 days?",
    "Which gateway has the longest settlement time?",
    "Show me tax mismatches."
  ];

  const handleAsk = async (q?: string) => {
    const prompt = q || query;
    if (!prompt) return;
    setIsLoading(true);
    setQuery(prompt);
    try {
      const res = await api.askAIAgent(prompt);
      setResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/60 pb-4 gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">FINCTRL ANALYST</h1>
          <p className="text-xs text-slate-400 mt-0.5">Ask questions about your financial operations grounded in database tool execution.</p>
        </div>

        {status && (
          <div className="flex items-center gap-2 font-mono text-xs text-slate-400 bg-[#0F172A] px-3 py-1.5 rounded border border-slate-800">
            <Cpu className={`w-3.5 h-3.5 ${status.is_available ? 'text-purple-400' : 'text-amber-400'}`} />
            <span>MODEL:</span> <span className="text-purple-300 font-bold">{status.model_name}</span>
          </div>
        )}
      </div>

      {/* Suggested Questions Pills */}
      <div className="space-y-2">
        <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest">Suggested Queries</div>
        <div className="flex flex-wrap gap-2">
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(q)}
              className="text-xs px-3 py-1.5 rounded bg-[#0F172A] hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors font-sans"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Query Bar */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="flex gap-3"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask questions about financial operations..."
            className="flex-1 bg-[#090D16] border border-slate-700 rounded px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500 font-mono"
          />
          <Button
            type="submit"
            variant="primary"
            isLoading={isLoading}
            className="bg-purple-600 hover:bg-purple-500 border-purple-500"
            icon={<Send className="w-3.5 h-3.5" />}
          >
            Execute Query
          </Button>
        </form>
      </div>

      {/* Answer & Source Data Section */}
      {isLoading ? (
        <LoadingSkeleton rows={5} />
      ) : response ? (
        <div className="space-y-4">
          {/* Prominent Answer */}
          <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-6 space-y-3">
            <div className="flex items-center justify-between text-xs font-mono text-purple-400 font-bold uppercase tracking-wider">
              <span className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-purple-400" />
                Analyst Response
              </span>
              <span className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded text-[10px]">
                Confidence: {(response.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-sm text-slate-100 leading-relaxed whitespace-pre-wrap font-sans">
              {response.answer}
            </p>
          </div>

          {/* Source Data Block */}
          <div className="bg-[#0F172A] border border-slate-800 rounded-lg p-5 space-y-3">
            <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-blue-400" />
              Source Data Transparency
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs font-mono text-slate-300">
              <div className="p-2.5 rounded bg-[#090D16] border border-slate-800">
                <span className="text-slate-500 text-[10px] block">TOOL USED</span>
                <span className="text-purple-300 font-bold">{response.selected_tool || 'search_records'}</span>
              </div>
              <div className="p-2.5 rounded bg-[#090D16] border border-slate-800">
                <span className="text-slate-500 text-[10px] block">TOOL ARGS</span>
                <span className="text-slate-300">{JSON.stringify(response.tool_args || {})}</span>
              </div>
            </div>

            {response.tool_output && (
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Inspected Records Evidence JSON</span>
                <pre className="text-[10px] font-mono text-slate-300 bg-[#090D16] p-3.5 rounded border border-slate-800 overflow-x-auto max-h-64">
                  {JSON.stringify(response.tool_output, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
