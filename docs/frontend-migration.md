# FINCTRL AI — Frontend Migration & API Layer Specification

## 1. Existing Architecture

```
                               ┌────────────────────────────────┐
                               │     FINCTRL STREAMLIT UI       │
                               │     (Legacy UI Interface)      │
                               └───────────────┬────────────────┘
                                               │ (Direct Python Calls)
                                               ▼
                               ┌────────────────────────────────┐
                               │       FinanceController        │
                               │    (Central Orchestrator)      │
                               └───────┬───────────────┬────────┘
                                       │               │
            ┌──────────────────────────┴────┐     ┌────┴──────────────────────────┐
            │                               │     │                               │
            ▼                               ▼     ▼                               ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
│ ReconciliationEngine │  │ SettlementEngine │  │  CashForecaster  │  │     TaxMatcher      │
│ - MultiStageMatcher  │  │ & Delay Analyzer │  │ & Projections    │  │ & Discrepancy Engine│
│ - DuplicateDetector  │  └──────────────────┘  └──────────────────┘  └─────────────────────┘
│ - ExceptionEngine    │
└──────────────────────┘
            │                               │     │                               │
            └──────────────────────────┬────┴─────┴───────────────────────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │          DatabaseManager          │
                     │         (SQLite Database)         │
                     └─────────────────┬─────────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │ AuditLogger & ToolUsingAgent (AI) │
                     │ (SHA-256 Chain & Local Ollama)    │
                     └───────────────────────────────────┘
```

---

## 2. Existing UI Functionality & User Actions

| Page / Section | Current Streamlit Functionality | User Actions Available |
|---|---|---|
| **Control Room (Dashboard)** | Displays overall Finance Health Score (0-100), sub-scores breakdown bar chart, top KPIs (Records, Match Rate %, Exception Count, Pending Settlements, Current Cash, 30-Day Proj Cash), and Priority Exception Feed. | - Run Finance Controller Loop button<br>- Refresh / view live operational status |
| **Reconciliation** | Lists reconciled records comparing Invoices vs Bank Txns & Payments. Shows status badges (MATCHED, PARTIAL_MATCH, UNMATCHED/MISSING), match score (0-1.0), calculated evidence notes, and JSON details for invoice and bank txn. | - Filter by Status<br>- Expand detail view for invoice and transaction records |
| **Exception Triage** | Displays open exceptions card list with color-coded severity badges (CRITICAL, HIGH, MEDIUM, LOW), financial exposure amount, and issue reason. Provides evidence-backed local AI investigation for selected exception. | - Filter by Severity & Status<br>- Trigger AI Investigation per exception<br>- Approve (sets status RESOLVED, logs HUMAN_APPROVAL)<br>- Reject (sets status REJECTED, logs HUMAN_REJECTION)<br>- Escalate (sets status ESCALATED, logs HUMAN_ESCALATION) |
| **Settlements** | Displays settlement KPI summary (Total count, Settled amount, Pending/delayed amount, Success rate %), gateway delay percentage breakdown chart (Razorpay, Stripe, PineLabs, etc.), and Settlement Q&A tool. | - Enter text question for Settlement Q&A Agent<br>- View grounding evidence JSON |
| **Forward Cash** | Displays cash metrics (Current Cash, Pending Settlements, 30-Day Inflows), cash projection trajectory line chart (Current, 7D, 14D, 30D), and major cash driver receivables table. | - View 7-day, 14-day, 30-day projected cash<br>- Inspect cash forecast drivers |
| **Tax Matching** | Displays tax summary metrics (Total tax lines, Tax matched rate %, Discrepancies count, Total discrepancy amount ₹), and full table of tax line discrepancies comparing Expected vs Recorded GST/CGST/SGST/IGST tax. | - Inspect invoice-level tax discrepancy details |
| **AI Analyst** | Provides a natural language interface to the `ToolUsingFinanceAgent`. Answers financial operations questions using database tools and outputs selected tool name, tool arguments, structured answer, and raw DB evidence. | - Submit natural language queries (e.g., "Which unresolved invoice has largest exposure?")<br>- View selected DB tool, arguments, and returned evidence |
| **Audit Trail** | Shows full immutable SHA-256 hash-chained audit log of system decisions, AI investigations, and human approvals. Supports cryptographic verification of hash chain integrity. | - Verify Audit Chain Integrity button<br>- Download Audit Trail CSV |
| **Data Management** | Displays current database entity counts (Invoices, Bank Txns, Payments, Settlements, Tax Lines). Allows loading predefined datasets or generating custom synthetic data. | - Load Demo Dataset (100 Records)<br>- Load Benchmark Dataset (500 Records)<br>- Generate Custom Dataset (50-1000 records) |

---

## 3. Existing Backend Functionality & Business Logic

1. **Reconciliation Engine**: Multi-stage deterministic matching (Exact match on reference/amount/date, fuzzy string match, normalized reference, duplicate payment detection, tax mismatch detection, partial payment detection).
2. **Exception Triage Engine**: Categorizes unmatched/discrepant records into severity buckets (CRITICAL, HIGH, MEDIUM, LOW), calculates exposure amount, assigns suggested next steps.
3. **Settlement Intelligence**: Evaluates gateway-level settlement durations, delay rates, pending vs settled amounts, and answers settlement natural language queries.
4. **Cash Forecaster**: Rule-based forward liquidity projections incorporating opening bank cash position, expected unpaid invoice receivables (30D), and pending gateway settlements.
5. **Tax Matching Engine**: Validates recorded tax vs expected tax rates (CGST, SGST, IGST, GST) and logs discrepancy amounts.
6. **Finance Health Score**: Weighted aggregate scoring formula evaluating Reconciliation Rate, Exception Exposure, Settlement Delay Rate, Cash Coverage, and Tax Matching Rate.
7. **ToolUsingFinanceAgent**: Natural language AI agent connected to local Ollama (`llama3.2:3b`) with deterministic tool execution fallback.
8. **Audit Trail Logger**: SHA-256 hash-chained immutable event log recording all user actions, AI investigations, and human approvals with cryptographic verification (`verify_audit_chain`).
9. **System Evaluator**: Benchmark metrics calculating True Positives (TP), False Positives (FP), False Negatives (FN), True Negatives (TN), Precision, Recall, F1 Score, Throughput, and Automation Rate against synthetic Ground Truth data.

---

## 4. Required API Endpoints & Request/Response Contracts

### Dashboard API
- `GET /api/dashboard/summary`
  - Returns: `health_score` (overall + sub_scores), `recon_metrics`, `exceptions_summary` (count, total exposure, priority items), `settlement_summary`, `cash_summary`
- `POST /api/dashboard/run-pipeline`
  - Triggers `FinanceController.run_controller_pipeline()` and returns updated summary metrics.

### Reconciliation API
- `GET /api/reconciliation/summary`
  - Returns: total records, matched count, partial count, unmatched count, match rate %
- `GET /api/reconciliation/records?status={status}&page={page}&limit={limit}`
  - Returns list of reconciliation records with matched invoice, bank transaction, match score, status, and evidence notes.
- `GET /api/reconciliation/records/{record_id}`
  - Returns complete invoice, payment, settlement, and bank transaction lifecycle details for a single record.
- `POST /api/reconciliation/run`
  - Re-executes multi-stage reconciliation engine.
- `POST /api/reconciliation/reset`
  - Resets reconciliation tables.

### Exceptions API
- `GET /api/exceptions?severity={severity}&status={status}`
  - Returns list of financial exception records with severity, type, exposure amount, status, and reason.
- `GET /api/exceptions/{exception_id}`
  - Returns single exception detail with related records.
- `POST /api/exceptions/{exception_id}/investigate`
  - Calls `FinanceController.investigate_exception_by_id(exception_id)` using local Ollama AI / fallback.
- `POST /api/exceptions/{exception_id}/approve`
  - Updates exception status to `RESOLVED` with user action `HUMAN_APPROVAL`.
- `POST /api/exceptions/{exception_id}/reject`
  - Updates exception status to `REJECTED` with user action `HUMAN_REJECTION`.
- `POST /api/exceptions/{exception_id}/escalate`
  - Updates exception status to `ESCALATED` with user action `HUMAN_ESCALATION`.
- `POST /api/exceptions/{exception_id}/resolve`
  - Updates exception status to `RESOLVED` with user action `HUMAN_RESOLUTION`.

### Settlements API
- `GET /api/settlements/summary`
  - Returns total count, total settled amount, pending amount, delayed amount, success rate %, gateway breakdown (delay rates & amounts).
- `GET /api/settlements`
  - Returns list of settlement records.
- `POST /api/settlements/ask`
  - Body: `{ "question": "..." }`
  - Calls `settlement_analyzer.answer_settlement_question()` and returns answer and grounding evidence.

### Cash API
- `GET /api/cash/current`
  - Returns current cash position, pending settlements, expected inflows/outflows.
- `GET /api/cash/forecast`
  - Returns 7-day, 14-day, and 30-day cash projections and list of major forecast driver receivables.

### Tax API
- `GET /api/tax/summary`
  - Returns total tax lines, match rate %, discrepancy count, total discrepancy amount.
- `GET /api/tax/mismatches`
  - Returns list of tax discrepancies with expected tax, recorded tax, difference, status, and evidence.

### AI Analyst API
- `POST /api/ai/ask`
  - Body: `{ "question": "..." }`
  - Calls `ToolUsingFinanceAgent.process_query()` and returns selected tool, tool arguments, answer, raw tool output, and confidence.
- `GET /api/ai/status`
  - Returns model name, availability status (`is_available`), and provider type.

### Audit API
- `GET /api/audit?limit=200`
  - Returns audit log entries with SHA-256 hashes, user action, record id, decision, actor, confidence, and timestamp.
- `GET /api/audit/verify`
  - Calls `AuditLogger.verify_audit_chain()` and returns `{ "valid": bool, "total_events": int, "violations": [] }`.

### Evaluation API
- `GET /api/evaluation/latest`
  - Returns precision, recall, F1 score, TP, FP, FN, TN, automation rate %, exception rate %, throughput, and confusion matrix breakdown.
- `POST /api/evaluation/run`
  - Triggers system evaluation benchmark.

### Data Management API
- `GET /api/data/status`
  - Returns current database entity counts (invoices, bank_transactions, payments, settlements, tax_lines).
- `POST /api/data/load-demo`
  - Loads 100-record demo dataset into SQLite.
- `POST /api/data/load-benchmark`
  - Loads 500-record benchmark dataset into SQLite.
- `POST /api/data/generate`
  - Body: `{ "count": 150, "seed": 42 }`
  - Generates and loads custom synthetic dataset.
- `POST /api/data/reset`
  - Clears database tables.

---

## 5. Target Frontend Pages (React + TypeScript + Vite)

1. **Control Room (`/`)**: Main KPI dashboard with Finance Health Score, Cash position, Reconciliation Rate, Pending Settlements, Exception Exposure, and Priority Attention feed.
2. **Reconciliation (`/reconciliation`)**: Detailed reconciliation table with status badges, match scores, filters, and interactive row drawer for 4-stage lifecycle visualization (Invoice -> Payment -> Settlement -> Bank Txn).
3. **Exception Investigation (`/exceptions`)**: Split-view triage interface (Left: Financial evidence & details, Right: AI investigation reasoning with confidence & approval buttons).
4. **Settlement Intelligence (`/settlements`)**: Gateway performance cards, delay metrics chart, and natural language settlement Q&A interface with grounding evidence viewer.
5. **Forward Cash (`/cash`)**: Liquidity KPI metrics, 7D/14D/30D forecast area chart, and major forecast driver receivables breakdown.
6. **Tax Matching (`/tax`)**: GST/CGST/SGST/IGST audit metrics and detailed discrepancy list showing expected vs recorded tax differences.
7. **AI Analyst (`/ai-analyst`)**: Premium internal finance query tool with suggested query pills, tool execution transparency, and evidence drawer.
8. **Audit Trail (`/audit`)**: Timeline-style audit viewer with SHA-256 verification status indicator and single-click chain verification.
9. **Evaluation & Benchmarks (`/evaluation`)**: Confusion matrix, TP/FP/FN/TN metrics, Precision/Recall/F1 cards, throughput graphs, and synthetic benchmark runner.
10. **Data Management (`/data-management`)**: Dataset loader buttons (100 demo, 500 benchmark, custom count) and database table status meters.
