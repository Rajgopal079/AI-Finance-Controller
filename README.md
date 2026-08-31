# FINCTRL AI — Autonomous Finance Operations Controller

FINCTRL AI is a local-first, evidence-driven Finance Operations Controller. It features an immutable, frozen finance engine providing multi-source reconciliation, exception triage, forward cash forecasting, gateway settlement intelligence, GST tax matching, and SHA-256 tamper-evident audit logging.

This repository features a **FastAPI REST backend adapter** and a **React + TypeScript + Vite enterprise frontend** with Framer Motion and Tailwind CSS.

---

## 🏛️ System Architecture

```
┌──────────────────────────────────┐
│      REACT + TYPESCRIPT UI       │
│  (Vite + Tailwind + Motion)      │
└────────────────┬─────────────────┘
                 │ REST / JSON (http://localhost:5173 -> http://localhost:8000)
                 ▼
┌──────────────────────────────────┐
│           FASTAPI API            │
│       (Backend REST Adapter)     │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│      FROZEN FINCTRL CORE         │
│  - Multi-Stage Matcher           │
│  - Exception Engine              │
│  - Forward Cash Forecaster       │
│  - Tax Discrepancy Engine        │
│  - SHA-256 Audit Logger          │
│  - ToolUsingFinanceAgent (AI)    │
└────────┬─────────────────┬───────┘
         │                 │
         ▼                 ▼
┌─────────────────┐ ┌──────────────┐
│ SQLite Database │ │  Local AI    │
│  (finctrl.db)   │ │ llama3.2:3b  │
└─────────────────┘ └──────────────┘
```

---

## 🚀 Quick Startup Guide

### 1. Backend (FastAPI API)
```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
- **API URL**: `http://localhost:8000/api`
- **Swagger Documentation**: `http://localhost:8000/docs`

### 2. Frontend (React + TypeScript + Vite)
```bash
cd frontend
npm install
npm run dev
```
- **React App**: `http://localhost:5173`

---

## 🧪 Testing & Verification

### Run Full Test Suite (33 Backend & API Tests)
```bash
pytest
```

### Build Production Frontend Bundle
```bash
cd frontend
npm run build
```

---

## 🎯 8 Judge Demo Test Scenarios
The React Control Room UI includes a dedicated quick-navigation bar for demonstrating all 8 judge test scenarios:
1. **CASE 1 — Exact Match**: Clean 4-stage lifecycle reconciliation (`Invoice -> Payment -> Settlement -> Bank Txn`).
2. **CASE 2 — Partial Payment**: Payment amount less than invoice total flagged with `PARTIAL_MATCH`.
3. **CASE 3 — Duplicate Payment**: Multiple payment attempts flagged with `CRITICAL` duplicate exception.
4. **CASE 4 — Delayed Settlement**: Gateway settlement duration exceeding threshold.
5. **CASE 5 — Tax Mismatch**: Recorded GST line tax differing from rate formula.
6. **CASE 6 — Large Financial Discrepancy**: High exposure financial discrepancy prioritized in feed.
7. **CASE 7 — Pending Settlement**: Gateway funds in transit projected in 7D/14D/30D forward cash.
8. **CASE 8 — Ambiguous Reference Conflict**: Conflicting reference IDs safely flagged for human approval.

---

## 📜 Legacy Streamlit UI
The original Streamlit application remains available under `legacy_streamlit/`:
```bash
streamlit run legacy_streamlit/main.py
```
