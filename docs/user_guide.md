# FINCTRL AI — User Guide & Judge Demo Walkthrough (Phase 10)

## Judge / Demo Story Scenarios

1. **CASE 1: Exact Match** → Automatically reconciled across 4-stage lifecycle (`INVOICE` -> `PAYMENT` -> `SETTLEMENT` -> `BANK`).
2. **CASE 2: Partial Payment** → ₹7,500 underpayment flagged as `PARTIAL_PAYMENT` exception with balance request recommendation.
3. **CASE 3: Duplicate Payment** → High-priority exception flagging dual RTGS payments for identical invoice.
4. **CASE 4: Delayed Settlement** → Settlement intelligence highlights Stripe/gateway delay.
5. **CASE 5: Tax Mismatch** → Tax matcher detects GST rate/amount discrepancy.
6. **CASE 6: Large Financial Discrepancy** → ₹8.5L unidentified deposit escalated to senior controller.
7. **CASE 7: Pending Settlements** → Forecast engine includes pending releases without double counting.
8. **CASE 8: Ambiguous Reference Conflict (Refusal Case)** → Reference contains conflicting invoice ID (`INV-1136` vs `INV-1011`). The system **REFUSES** to force a match and marks it `AMBIGUOUS`.

---

## 🎬 120-Second Judge Demo Sequence

1. **Launch Dashboard**: Run `streamlit run app/main.py`.
2. **Control Room Overview**: Observe live **Finance Health Score**, KPI metrics, and **Attention Required** exception feed.
3. **Execute Controller Loop**: Click `🚀 Run Finance Controller Loop`.
4. **Inspect 4-Stage Reconciliation**: Open `🔄 Reconciliation` to see `FULLY_RECONCILED`, `PARTIAL_PAYMENT`, and `AMBIGUOUS` lifecycle tags.
5. **Demonstrate Case 8 Refusal**: Note how conflicting references are flagged as `AMBIGUOUS` with explicit conflict explanations.
6. **Tool-Using AI Agent**: Open `🤖 Ask the Finance Controller` and ask: *"Which unresolved invoice has the largest financial exposure?"*. Watch the agent select `get_exception_summary()` and summarize the DB evidence.
7. **Human Approval Persistence**: Open `🚨 Exception Triage`, click `✅ Approve`, then refresh the page to prove DB transaction persistence.
8. **Cryptographic Audit Verification**: Open `📜 Audit Trail` and click `🛡️ Verify Audit Chain Integrity` to run SHA-256 hash verification.
