# FINCTRL AI — Technical Architecture Specification (Phase 10)

## System Architecture Overview

FINCTRL AI operates as a local-first, evidence-driven AI Finance Controller.

```
+-----------------------------------------------------------------------+
|                       MULTI-SOURCE DATA ENTITIES                      |
| Invoices, Payments, Gateway Settlements, Bank Txns (Credit/Debit),    |
| Tax Lines, Financial Outflows, Customers, Ground Truth Dataset         |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                    DETERMINISTIC RECONCILIATION                       |
| 4-Stage Lifecycle Chain: INVOICE -> PAYMENT -> SETTLEMENT -> BANK TXN  |
| Reference Normalization (normalize_reference) & Identifier Conflict   |
| Detection (compare_reference_identity)                                |
| Score Weights: Amount 40%, Reference 30%, Date 15%, Customer 10%      |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                     EXCEPTION ENGINE & PRIORITY                       |
| Triage Priorities: CRITICAL, HIGH, MEDIUM, LOW                        |
| Discrepancies: Amount Mismatch, Partial Payment, Duplicate Payment,   |
| Tax Mismatch, Settlement Delay, Ambiguous Reference Conflict (Case 8) |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|               TOOL-USING LOCAL AI AGENT & INVESTIGATOR                |
| Ollama (llama3.2:3b) / Mock Deterministic Fallback                    |
| Controlled Tools: search_records, compare_records,                    |
| get_customer_history, get_settlement_status, get_cash_forecast,      |
| get_tax_match, get_exception_summary, get_finance_health              |
| Pydantic Schema Validation: LLMInvestigationResponse                  |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                  FINANCIAL INTELLIGENCE SUITE                         |
| Forward Cash Forecaster: Opening Balance + Credits - Debits - Outflows|
| Settlement Analytics: Calculated Duration (Mean, Median, P90)          |
| Tax-Line Matcher: Deterministic GST Rate Discrepancy Engine           |
| Finance Health Calculator: Weighted Health Score (0-100)              |
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                  HUMAN APPROVAL & AUDIT TRAIL                         |
| Human Actions: Approve, Reject, Escalate (DB Transaction Commit)      |
| Cryptographic Audit Trail: SHA-256 Hash Chaining (verify_audit_chain)|
+-----------------------------------┬-----------------------------------+
                                    │
                                    ▼
+-----------------------------------------------------------------------+
|                     STREAMLIT CONTROL ROOM UI                         |
| Control Room, Recon, Exceptions, Settlements, Cash, Tax, AI Analyst,  |
| Audit Trail, Data Management                                          |
+-----------------------------------------------------------------------+
```

## Ground-Truth Evaluation Methodology
Ground truth is created at dataset generation time and stored in `ground_truth`. Ground truth is strictly isolated from inference logic. The evaluator compares predictions against ground truth to calculate actual:
- **True Positives (TP)**: Correctly matched records.
- **False Positives (FP)**: Matches made on wrong IDs or ambiguous cases.
- **False Negatives (FN)**: Missed matchable records.
- **Precision**: `TP / (TP + FP)`
- **Recall**: `TP / (TP + FN)`
- **F1 Score**: `2 * (Precision * Recall) / (Precision + Recall)`
