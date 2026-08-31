import React, { useEffect, useState } from 'react';
import { api } from './services/api';
import { PipelineSummaryData } from './types';
import { Navbar } from './components/layout/Navbar';
import { Sidebar, PageId } from './components/layout/Sidebar';
import { DemoModal } from './components/ui/DemoModal';
import { ControlRoom } from './pages/ControlRoom';
import { Reconciliation } from './pages/Reconciliation';
import { Exceptions } from './pages/Exceptions';
import { Settlements } from './pages/Settlements';
import { Cash } from './pages/Cash';
import { Tax } from './pages/Tax';
import { AIAnalyst } from './pages/AIAnalyst';
import { Audit } from './pages/Audit';
import { Evaluation } from './pages/Evaluation';
import { DataManagement } from './pages/DataManagement';

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>('control-room');
  const [pipelineData, setPipelineData] = useState<PipelineSummaryData | null>(null);
  const [isLoadingPipeline, setIsLoadingPipeline] = useState(true);
  const [isRunningPipeline, setIsRunningPipeline] = useState(false);
  const [pageFilter, setPageFilter] = useState<string | undefined>(undefined);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  useEffect(() => {
    loadPipeline();
  }, []);

  const loadPipeline = async () => {
    setIsLoadingPipeline(true);
    try {
      const data = await api.getDashboardSummary();
      setPipelineData(data);
    } catch (err) {
      console.error('Failed to load dashboard summary', err);
    } finally {
      setIsLoadingPipeline(false);
    }
  };

  const handleRunPipeline = async () => {
    setIsRunningPipeline(true);
    try {
      const data = await api.runPipeline();
      setPipelineData(data);
    } catch (err) {
      console.error('Failed to run controller pipeline', err);
    } finally {
      setIsRunningPipeline(false);
    }
  };

  const handleNavigateTo = (page: PageId, filter?: string) => {
    setActivePage(page);
    setPageFilter(filter);
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex flex-col font-sans">
      <Navbar
        onRunPipeline={handleRunPipeline}
        isRunningPipeline={isRunningPipeline}
        onOpenDemoModal={() => setIsDemoModalOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activePage={activePage}
          onSelectPage={(page) => {
            setActivePage(page);
            setPageFilter(undefined);
          }}
        />

        <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {activePage === 'control-room' && (
            <ControlRoom
              data={pipelineData}
              isLoading={isLoadingPipeline}
              onNavigateTo={handleNavigateTo}
            />
          )}

          {activePage === 'reconciliation' && (
            <Reconciliation initialFilter={pageFilter} />
          )}

          {activePage === 'exceptions' && (
            <Exceptions initialSeverity={pageFilter} />
          )}

          {activePage === 'settlements' && <Settlements />}

          {activePage === 'cash' && <Cash />}

          {activePage === 'tax' && <Tax />}

          {activePage === 'ai-analyst' && <AIAnalyst />}

          {activePage === 'audit' && <Audit />}

          {activePage === 'evaluation' && <Evaluation />}

          {activePage === 'data-management' && (
            <DataManagement onDataUpdated={loadPipeline} />
          )}
        </main>
      </div>

      <DemoModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
        onSelectScenario={handleNavigateTo}
      />
    </div>
  );
};

export default App;
