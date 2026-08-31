import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DataStatus } from '../types';
import { PageHeader } from '../components/layout/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { Database, FileCode, Zap, RefreshCw, Trash2 } from 'lucide-react';

interface DataManagementProps {
  onDataUpdated: () => void;
}

export const DataManagement: React.FC<DataManagementProps> = ({ onDataUpdated }) => {
  const [status, setStatus] = useState<DataStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [customCount, setCustomCount] = useState(150);
  const [isWorking, setIsWorking] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setIsLoading(true);
    try {
      const res = await api.getDataStatus();
      setStatus(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadDemo = async () => {
    setIsWorking(true);
    try {
      await api.loadDemoData();
      await loadStatus();
      onDataUpdated();
    } catch (err) {
      console.error(err);
    } finally {
      setIsWorking(false);
    }
  };

  const handleLoadBenchmark = async () => {
    setIsWorking(true);
    try {
      await api.loadBenchmarkData();
      await loadStatus();
      onDataUpdated();
    } catch (err) {
      console.error(err);
    } finally {
      setIsWorking(false);
    }
  };

  const handleGenerateCustom = async () => {
    setIsWorking(true);
    try {
      await api.generateCustomData(customCount);
      await loadStatus();
      onDataUpdated();
    } catch (err) {
      console.error(err);
    } finally {
      setIsWorking(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Are you sure you want to clear all SQLite tables?")) return;
    setIsWorking(true);
    try {
      await api.resetData();
      await loadStatus();
      onDataUpdated();
    } catch (err) {
      console.error(err);
    } finally {
      setIsWorking(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Management & Synthetic Benchmarks"
        subtitle="Load pre-generated benchmark datasets (100 or 500 records), generate custom scenarios, or reset SQLite storage."
      />

      {/* Dataset Actions Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-5 flex flex-col justify-between space-y-4 border-l-4 border-l-blue-500">
          <div>
            <div className="flex items-center gap-2 text-sm font-bold text-slate-100 mb-1">
              <FileCode className="w-4 h-4 text-blue-400" />
              100-Record Demo Dataset
            </div>
            <p className="text-xs text-slate-400">
              Quick demonstration dataset containing exact matches, partial payments, duplicates, and tax mismatches.
            </p>
          </div>
          <Button
            variant="primary"
            onClick={handleLoadDemo}
            isLoading={isWorking}
            className="w-full justify-center"
          >
            Load 100 Demo Dataset
          </Button>
        </Card>

        <Card className="p-5 flex flex-col justify-between space-y-4 border-l-4 border-l-purple-500">
          <div>
            <div className="flex items-center gap-2 text-sm font-bold text-slate-100 mb-1">
              <Zap className="w-4 h-4 text-purple-400" />
              500-Record Benchmark Dataset
            </div>
            <p className="text-xs text-slate-400">
              Full stress-testing benchmark dataset with comprehensive ground-truth cases and edge-case exceptions.
            </p>
          </div>
          <Button
            variant="primary"
            onClick={handleLoadBenchmark}
            isLoading={isWorking}
            className="w-full justify-center bg-purple-600 hover:bg-purple-500 border-purple-500"
          >
            Load 500 Benchmark Dataset
          </Button>
        </Card>

        <Card className="p-5 flex flex-col justify-between space-y-4 border-l-4 border-l-amber-500">
          <div>
            <div className="flex items-center gap-2 text-sm font-bold text-slate-100 mb-1">
              <RefreshCw className="w-4 h-4 text-amber-400" />
              Custom Generator
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-slate-400">Count:</span>
              <input
                type="number"
                min="50"
                max="1000"
                value={customCount}
                onChange={(e) => setCustomCount(Number(e.target.value))}
                className="w-24 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-100 focus:outline-none"
              />
            </div>
          </div>
          <Button
            variant="secondary"
            onClick={handleGenerateCustom}
            isLoading={isWorking}
            className="w-full justify-center"
          >
            Generate & Load
          </Button>
        </Card>
      </div>

      {/* Database Entity Status Table */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-400" />
            Current SQLite Storage Record Counts
          </div>
          <Button size="sm" variant="danger" onClick={handleReset} isLoading={isWorking} icon={<Trash2 className="w-3.5 h-3.5" />}>
            Reset Database
          </Button>
        </div>

        {isLoading || !status ? (
          <LoadingSkeleton rows={4} />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 text-center">
            {Object.entries(status.counts).map(([table, count]) => (
              <div key={table} className="p-3 rounded bg-slate-900 border border-slate-800">
                <div className="text-[10px] font-mono text-slate-400 uppercase">{table.replace('_', ' ')}</div>
                <div className="text-xl font-bold font-mono text-slate-100 mt-1">{count}</div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
