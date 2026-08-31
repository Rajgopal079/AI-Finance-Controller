export interface HealthSubScores {
  reconciliation: number;
  exception_exposure: number;
  settlement_delay: number;
  cash_coverage: number;
  tax_matching: number;
}

export interface HealthScore {
  overall_health_score: number;
  sub_scores: HealthSubScores;
  formula_explanation: string;
}

export interface ReconMetrics {
  total_records: number;
  matched_records: number;
  partial_matches: number;
  unmatched_records: number;
  match_rate_pct: number;
}

export interface ExceptionItem {
  id?: number;
  exception_id: string;
  invoice_id?: string;
  transaction_id?: string;
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  financial_amount: number;
  reason: string;
  status: 'OPEN' | 'UNDER_REVIEW' | 'RESOLVED' | 'REJECTED' | 'ESCALATED';
  suggested_next_step?: string;
  created_at?: string;
}

export interface SettlementMetrics {
  total_count: number;
  total_settled_amount: number;
  pending_amount: number;
  delayed_amount: number;
  success_rate_pct: number;
  gateway_breakdown: Record<string, {
    delay_rate_pct: number;
    total_amount: number;
    total_count: number;
    delayed_count: number;
  }>;
}

export interface ForecastHorizon {
  expected_inflow: number;
  expected_outflow: number;
  pending_settlements: number;
  projected_cash: number;
}

export interface CashForecastData {
  current_cash_position: number;
  pending_settlements: number;
  forecasts: {
    '7_day': ForecastHorizon;
    '14_day': ForecastHorizon;
    '30_day': ForecastHorizon;
  };
  major_drivers?: Array<{
    invoice_id: string;
    customer_name: string;
    total_amount: number;
    due_date: string;
  }>;
}

export interface PipelineSummaryData {
  health_score: HealthScore;
  recon_metrics: ReconMetrics;
  exceptions: ExceptionItem[];
  settlement_metrics: SettlementMetrics;
  cash_forecast: CashForecastData;
}

export interface ReconRecord {
  id?: number;
  reconciliation_id?: string;
  invoice_id: string;
  transaction_id?: string;
  payment_id?: string;
  settlement_id?: string;
  match_score: number;
  status: string;
  notes?: string;
  conflict_type?: string;
}

export interface RecordLifecycle {
  invoice?: Record<string, any> | null;
  payment?: Record<string, any> | null;
  settlement?: Record<string, any> | null;
  bank_transaction?: Record<string, any> | null;
}

export interface AIStatus {
  status: string;
  model_name: string;
  is_available: boolean;
  mode: string;
}

export interface AIAskResponse {
  status: string;
  answer: string;
  selected_tool?: string;
  tool_args?: Record<string, any>;
  tool_output?: any;
  evidence?: any;
  confidence: number;
}

export interface AuditLogItem {
  audit_id: string;
  timestamp: string;
  user_action: string;
  record_id: string;
  agent_action: string;
  evidence?: string;
  decision: string;
  confidence: number;
  human_approval: number;
  previous_hash: string;
  current_hash: string;
}

export interface EvaluationData {
  total_records_processed: number;
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  true_negatives: number;
  correct_matches: number;
  incorrect_matches: number;
  missed_matches: number;
  ambiguous_records: number;
  partial_matches: number;
  unmatched_records: number;
  precision: number;
  recall: number;
  f1_score: number;
  automation_rate_pct: number;
  exception_rate_pct: number;
  processing_time_seconds: number;
  throughput_records_per_sec: number;
  confusion_breakdown?: Record<string, number>;
}

export interface TaxDiscrepancyItem {
  tax_line_id: string;
  invoice_id: string;
  customer_name: string;
  tax_type: string;
  taxable_amount: number;
  expected_tax: number;
  recorded_tax: number;
  discrepancy_amount: number;
  status: string;
}

export interface TaxSummary {
  total_tax_lines: number;
  match_rate_pct: number;
  discrepancy_count: number;
  total_discrepancy_amount: number;
}

export interface DataStatus {
  counts: {
    invoices: number;
    bank_transactions: number;
    payments: number;
    settlements: number;
    tax_lines: number;
    customers: number;
    ground_truth: number;
  };
}
