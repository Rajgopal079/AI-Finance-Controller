import axios from 'axios';
import {
  PipelineSummaryData,
  ReconMetrics,
  ReconRecord,
  RecordLifecycle,
  ExceptionItem,
  SettlementMetrics,
  CashForecastData,
  TaxSummary,
  TaxDiscrepancyItem,
  AIStatus,
  AIAskResponse,
  AuditLogItem,
  EvaluationData,
  DataStatus
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Dashboard
  getDashboardSummary: async (): Promise<PipelineSummaryData> => {
    const res = await client.get('/dashboard/summary');
    return res.data.data;
  },
  runPipeline: async (): Promise<PipelineSummaryData> => {
    const res = await client.post('/dashboard/run-pipeline');
    return res.data.data;
  },

  // Reconciliation
  getReconSummary: async (): Promise<ReconMetrics> => {
    const res = await client.get('/reconciliation/summary');
    return res.data.data;
  },
  getReconRecords: async (status?: string): Promise<{ count: number; records: ReconRecord[] }> => {
    const res = await client.get('/reconciliation/records', { params: { status } });
    return res.data;
  },
  getReconRecordDetail: async (recordId: string): Promise<{ reconciliation: ReconRecord; lifecycle: RecordLifecycle }> => {
    const res = await client.get(`/reconciliation/records/${recordId}`);
    return res.data;
  },
  runReconciliation: async (): Promise<ReconMetrics> => {
    const res = await client.post('/reconciliation/run');
    return res.data.data;
  },
  resetReconciliation: async (): Promise<void> => {
    await client.post('/reconciliation/reset');
  },

  // Exceptions
  getExceptions: async (severity?: string, status?: string): Promise<{ count: number; exceptions: ExceptionItem[] }> => {
    const res = await client.get('/exceptions', { params: { severity, status } });
    return res.data;
  },
  getExceptionDetail: async (id: string): Promise<ExceptionItem> => {
    const res = await client.get(`/exceptions/${id}`);
    return res.data.exception;
  },
  investigateException: async (id: string): Promise<any> => {
    const res = await client.post(`/exceptions/${id}/investigate`);
    return res.data.investigation;
  },
  approveException: async (id: string): Promise<void> => {
    await client.post(`/exceptions/${id}/approve`);
  },
  rejectException: async (id: string): Promise<void> => {
    await client.post(`/exceptions/${id}/reject`);
  },
  escalateException: async (id: string): Promise<void> => {
    await client.post(`/exceptions/${id}/escalate`);
  },
  resolveException: async (id: string): Promise<void> => {
    await client.post(`/exceptions/${id}/resolve`);
  },

  // Settlements
  getSettlementsSummary: async (): Promise<SettlementMetrics> => {
    const res = await client.get('/settlements/summary');
    return res.data.data;
  },
  getSettlements: async (): Promise<any[]> => {
    const res = await client.get('/settlements');
    return res.data.settlements;
  },
  askSettlementQuestion: async (question: string): Promise<{ answer: string; evidence: any }> => {
    const res = await client.post('/settlements/ask', { question });
    return res.data.data;
  },

  // Cash
  getCurrentCash: async (): Promise<any> => {
    const res = await client.get('/cash/current');
    return res.data;
  },
  getCashForecast: async (): Promise<CashForecastData> => {
    const res = await client.get('/cash/forecast');
    return res.data.data;
  },

  // Tax
  getTaxSummary: async (): Promise<TaxSummary> => {
    const res = await client.get('/tax/summary');
    return res.data.data;
  },
  getTaxMismatches: async (): Promise<{ count: number; mismatches: TaxDiscrepancyItem[]; all_details: TaxDiscrepancyItem[] }> => {
    const res = await client.get('/tax/mismatches');
    return res.data;
  },

  // AI Analyst
  askAIAgent: async (question: string): Promise<AIAskResponse> => {
    const res = await client.post('/ai/ask', { question });
    return res.data;
  },
  getAIStatus: async (): Promise<AIStatus> => {
    const res = await client.get('/ai/status');
    return res.data;
  },

  // Audit
  getAuditLogs: async (limit = 200): Promise<{ count: number; logs: AuditLogItem[] }> => {
    const res = await client.get('/audit', { params: { limit } });
    return res.data;
  },
  verifyAuditChain: async (): Promise<{ valid: boolean; events_verified: number; violations: string[] }> => {
    const res = await client.get('/audit/verify');
    return res.data;
  },

  // Evaluation
  getLatestEvaluation: async (): Promise<EvaluationData> => {
    const res = await client.get('/evaluation/latest');
    return res.data.data;
  },
  runEvaluation: async (): Promise<EvaluationData> => {
    const res = await client.post('/evaluation/run');
    return res.data.data;
  },

  // Data Management
  getDataStatus: async (): Promise<DataStatus> => {
    const res = await client.get('/data/status');
    return res.data;
  },
  loadDemoData: async (): Promise<void> => {
    await client.post('/data/load-demo');
  },
  loadBenchmarkData: async (): Promise<void> => {
    await client.post('/data/load-benchmark');
  },
  generateCustomData: async (count: number, seed = 42): Promise<void> => {
    await client.post('/data/generate', { count, seed });
  },
  resetData: async (): Promise<void> => {
    await client.post('/data/reset');
  }
};
