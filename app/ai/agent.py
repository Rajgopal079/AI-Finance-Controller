import json
import logging
from typing import Dict, Any, List, Optional
from app.ai.provider import LLMProvider, MockLLMProvider
from app.ai.ollama_provider import LocalOllamaProvider
from app.database.db import DatabaseManager

# Import tool functions
from app.tools.search_records import search_records
from app.tools.compare_records import compare_records
from app.tools.customer_history import get_customer_history

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """You are FINCTRL AI, an intelligent tool-using Finance Controller Assistant.
Your task is to analyze user financial questions and select the appropriate database tool to answer accurately.

Available Tools:
1. `search_records(query)`: Search invoices or bank transactions by keyword or ID.
2. `compare_records(invoice_id, transaction_id)`: Compare specific invoice and transaction evidence.
3. `get_customer_history(customer_id)`: Retrieve customer billing, payment history, and balance.
4. `get_settlement_status()`: Get gateway settlement metrics and delays.
5. `get_cash_forecast()`: Get forward cash position and 7/14/30-day forecasts.
6. `get_tax_match()`: Get GST tax reconciliation status and discrepancies.
7. `get_exception_summary()`: Get summary of current flagged exceptions.
8. `get_finance_health()`: Get overall Finance Health Score (0-100).

Respond in JSON format:
{
  "selected_tool": "<tool_name>",
  "tool_args": { ... },
  "reasoning": "<why this tool was selected>"
}
"""

class ToolUsingFinanceAgent:
    def __init__(self, db_manager: DatabaseManager = None, provider: Optional[LLMProvider] = None):
        self.db = db_manager or DatabaseManager()
        self.provider = provider or LocalOllamaProvider()
        if not self.provider.is_available():
            self.provider = MockLLMProvider()

    def process_query(self, user_question: str) -> Dict[str, Any]:
        """
        Process user query by selecting and executing DB tools, then summarizing evidence.
        """
        q_lower = user_question.lower()

        # Step 1: Tool Selection via LLM or Intent Router
        if self.provider.is_available() and not isinstance(self.provider, MockLLMProvider):
            raw = self.provider.generate(AGENT_SYSTEM_PROMPT, f"User Question: {user_question}")
            tool_call = self._parse_tool_call(raw, q_lower)
        else:
            tool_call = self._deterministic_tool_router(q_lower)

        tool_name = tool_call.get("selected_tool", "search_records")
        args = tool_call.get("tool_args", {})

        # Step 2: Execute Tool
        tool_output = self._execute_tool(tool_name, args, q_lower)

        # Step 3: Summarize Evidence
        if isinstance(self.provider, MockLLMProvider):
            fallback_msg = "(Local AI offline — displaying ground-truth tool execution results directly)"
            answer = f"Found tool results for '{tool_name}'. {fallback_msg}"
        else:
            sum_prompt = f"User Question: {user_question}\n\nTool Output ({tool_name}):\n{json.dumps(tool_output, indent=2)[:1500]}\n\nSummarize the answer clearly grounded in the tool output."
            answer = self.provider.generate("You are FINCTRL AI. Synthesize an exact financial answer grounded strictly in the tool output.", sum_prompt)

        return {
            "question": user_question,
            "selected_tool": tool_name,
            "tool_args": args,
            "tool_output": tool_output,
            "answer": answer,
            "is_ai_online": self.provider.is_available() and not isinstance(self.provider, MockLLMProvider)
        }

    def _parse_tool_call(self, raw_text: str, q_lower: str) -> dict:
        try:
            clean = raw_text.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            return json.loads(clean)
        except Exception:
            return self._deterministic_tool_router(q_lower)

    def _deterministic_tool_router(self, q_lower: str) -> dict:
        if "cash" in q_lower or "forecast" in q_lower or "position" in q_lower:
            return {"selected_tool": "get_cash_forecast", "tool_args": {}}
        elif "settlement" in q_lower or "gateway" in q_lower or "delay" in q_lower:
            return {"selected_tool": "get_settlement_status", "tool_args": {}}
        elif "tax" in q_lower or "gst" in q_lower:
            return {"selected_tool": "get_tax_match", "tool_args": {}}
        elif "exception" in q_lower or "unresolved" in q_lower or "exposure" in q_lower:
            return {"selected_tool": "get_exception_summary", "tool_args": {}}
        elif "health" in q_lower or "score" in q_lower:
            return {"selected_tool": "get_finance_health", "tool_args": {}}
        elif "cust-" in q_lower or "customer" in q_lower:
            return {"selected_tool": "get_customer_history", "tool_args": {"customer_id": "CUST-1000"}}
        else:
            return {"selected_tool": "search_records", "tool_args": {"query": q_lower}}

    def _execute_tool(self, tool_name: str, args: dict, q_lower: str) -> Any:
        from app.finance.settlements import SettlementAnalyzer
        from app.finance.cash_forecast import ForwardCashForecaster
        from app.finance.tax_matching import TaxLineMatcher
        from app.reconciliation.matcher import ReconciliationEngine

        if tool_name == "get_cash_forecast":
            return ForwardCashForecaster(self.db).generate_forecast()
        elif tool_name == "get_settlement_status":
            return SettlementAnalyzer(self.db).get_settlement_metrics()
        elif tool_name == "get_tax_match":
            return TaxLineMatcher(self.db).run_tax_matching()
        elif tool_name == "get_exception_summary":
            exc_df = self.db.get_table_df("exceptions")
            return exc_df.to_dict("records") if not exc_df.empty else []
        elif tool_name == "get_customer_history":
            cid = args.get("customer_id", "CUST-1000")
            return get_customer_history(cid, self.db)
        elif tool_name == "compare_records":
            inv_id = args.get("invoice_id", "INV-1001")
            txn_id = args.get("transaction_id", "TXN-8001")
            return compare_records(inv_id, txn_id, self.db)
        else:
            q = args.get("query", q_lower)
            return search_records(q, self.db)
