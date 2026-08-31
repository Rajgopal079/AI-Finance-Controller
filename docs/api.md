# FINCTRL AI — FastAPI REST Endpoints & Contracts

## Base URL
`http://localhost:8000/api`

---

## 1. Control Room & Dashboard
### `GET /api/dashboard/summary`
Returns top KPI metrics, overall finance health score, sub-scores, and priority exception feed.

### `POST /api/dashboard/run-pipeline`
Triggers `FinanceController.run_controller_pipeline()` and updates system state.

---

## 2. Reconciliation Engine
### `GET /api/reconciliation/summary`
Returns total records count, match rate percentage, matched records count, partial match count, and unmatched count.

### `GET /api/reconciliation/records`
Query parameters: `status`, `page`, `limit`.
Returns paginated reconciliation records with matched invoice and bank transaction details.

### `GET /api/reconciliation/records/{record_id}`
Returns 4-stage lifecycle breakdown (Invoice -> Payment -> Settlement -> Bank Txn) with match score and calculated evidence notes.

### `POST /api/reconciliation/run`
Re-runs deterministic multi-stage matching engine.

---

## 3. Exception Triage & Investigation
### `GET /api/exceptions`
Query parameters: `severity`, `status`.
Returns list of open and historical exceptions with severity, type, exposure amount, reason, and status.

### `GET /api/exceptions/{exception_id}`
Returns details for a specific exception record.

### `POST /api/exceptions/{exception_id}/investigate`
Executes `FinanceController.investigate_exception_by_id(exception_id)` via local Ollama LLM or fallback investigator.

### `POST /api/exceptions/{exception_id}/approve`
Updates exception status to `RESOLVED` with user action `HUMAN_APPROVAL` and updates database.

### `POST /api/exceptions/{exception_id}/reject`
Updates exception status to `REJECTED` with user action `HUMAN_REJECTION`.

### `POST /api/exceptions/{exception_id}/escalate`
Updates exception status to `ESCALATED` with user action `HUMAN_ESCALATION`.

### `POST /api/exceptions/{exception_id}/resolve`
Updates exception status to `RESOLVED` with user action `HUMAN_RESOLUTION`.

---

## 4. Settlement Intelligence
### `GET /api/settlements/summary`
Returns total count, settled amount, pending amount, delayed amount, success rate %, and gateway breakdown.

### `GET /api/settlements`
Returns settlement records.

### `POST /api/settlements/ask`
Request Body: `{ "question": "..." }`
Answers settlement query using `SettlementAnalyzer.answer_settlement_question()`.

---

## 5. Forward Cash Forecast
### `GET /api/cash/current`
Returns current bank cash position, pending gateway settlements, and expected inflows.

### `GET /api/cash/forecast`
Returns 7D, 14D, 30D projected cash amounts and major forecast driver receivables.

---

## 6. Tax-Line Matcher
### `GET /api/tax/summary`
Returns total tax lines, match rate %, discrepancy count, total discrepancy amount.

### `GET /api/tax/mismatches`
Returns tax discrepancy records with expected tax vs recorded tax comparison.

---

## 7. AI Analyst
### `POST /api/ai/ask`
Request Body: `{ "question": "..." }`
Calls `ToolUsingFinanceAgent.process_query()` and returns selected tool, tool arguments, answer, raw tool output, and confidence.

### `GET /api/ai/status`
Returns Ollama model availability and online status.

---

## 8. Audit Trail
### `GET /api/audit`
Returns last 200 audit trail events with SHA-256 hashes and human approval metadata.

### `GET /api/audit/verify`
Runs `AuditLogger.verify_audit_chain()` and returns verification result and violation log if tampered.

---

## 9. System Evaluation
### `GET /api/evaluation/latest`
Returns system metrics: Precision, Recall, F1 Score, TP, FP, FN, TN, Automation Rate %, Throughput.

### `POST /api/evaluation/run`
Executes evaluation pipeline against Ground Truth data.

---

## 10. Data Management
### `GET /api/data/status`
Returns database record counts across invoices, bank transactions, payments, settlements, and tax lines.

### `POST /api/data/load-demo`
Loads 100-record demo dataset.

### `POST /api/data/load-benchmark`
Loads 500-record benchmark dataset.

### `POST /api/data/generate`
Request Body: `{ "count": 150, "seed": 42 }`
Generates and loads custom synthetic data.

### `POST /api/data/reset`
Clears database tables.
