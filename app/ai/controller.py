import logging
import json
from typing import Dict, Any, List
from app.database.db import DatabaseManager
from app.reconciliation.matcher import ReconciliationEngine
from app.reconciliation.exception_engine import ExceptionEngine
from app.ai.investigator import AIInvestigator
from app.ai.agent import ToolUsingFinanceAgent
from app.finance.settlements import SettlementAnalyzer
from app.finance.cash_forecast import ForwardCashForecaster
from app.finance.tax_matching import TaxLineMatcher
from app.finance.health_score import FinanceHealthCalculator
from app.audit.logger import AuditLogger

logger = logging.getLogger(__name__)

class FinanceController:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.recon_engine = ReconciliationEngine(self.db)
        self.exception_engine = ExceptionEngine(self.db)
        self.investigator = AIInvestigator()
        self.agent = ToolUsingFinanceAgent(self.db, self.investigator.provider)
        self.settlement_analyzer = SettlementAnalyzer(self.db)
        self.cash_forecaster = ForwardCashForecaster(self.db)
        self.tax_matcher = TaxLineMatcher(self.db)
        self.audit_logger = AuditLogger(self.db)

    def run_controller_pipeline(self) -> Dict[str, Any]:
        """
        Runs the end-to-end Finance Controller pipeline:
        RECONCILIATION -> EXCEPTION DETECTION -> HEALTH SCORE -> FORECAST -> TAX -> SETTLEMENTS
        """
        # Step 1: Deterministic 4-Stage Reconciliation
        recon_metrics = self.recon_engine.run_reconciliation()

        # Step 2: Exception Engine & Priority Triage
        exceptions = self.exception_engine.generate_exceptions(recon_metrics)

        # Step 3: Settlement Analysis
        settlement_metrics = self.settlement_analyzer.get_settlement_metrics()

        # Step 4: Tax Line Matching
        tax_metrics = self.tax_matcher.run_tax_matching()

        # Step 5: Cash Forecast
        cash_metrics = self.cash_forecaster.generate_forecast()

        # Step 6: Health Score
        health = FinanceHealthCalculator.calculate(
            recon_metrics=recon_metrics,
            settlement_metrics=settlement_metrics,
            tax_metrics=tax_metrics,
            total_records=recon_metrics.get("total_records", 0),
            exception_count=len(exceptions)
        )

        # Log system run in tamper-evident audit log
        self.audit_logger.log_event(
            user_action="RUN_FINANCE_CONTROLLER",
            record_id="BATCH-PIPELINE",
            agent_action="EXECUTED_PIPELINE",
            evidence={"recon_match_rate": recon_metrics.get("match_rate_pct"), "exceptions_found": len(exceptions)},
            decision=f"Batch process completed with Health Score {health['overall_health_score']}/100.",
            confidence=1.0,
            previous_state="UNPROCESSED",
            new_state="RECONCILED",
            human_approval=False
        )

        return {
            "health_score": health,
            "recon_metrics": recon_metrics,
            "exceptions": exceptions,
            "settlement_metrics": settlement_metrics,
            "tax_metrics": tax_metrics,
            "cash_forecast": cash_metrics
        }

    def update_exception_status(self, exception_id: str, new_status: str, user_action: str) -> bool:
        """
        Update exception status with database transaction commit for human approval persistence.
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE exceptions SET status = ? WHERE exception_id = ?", (new_status, exception_id))
            conn.commit()

        self.audit_logger.log_event(
            user_action=user_action,
            record_id=exception_id,
            agent_action=f"UPDATED_STATUS_TO_{new_status}",
            evidence={"exception_id": exception_id, "new_status": new_status},
            decision=f"Human action '{user_action}' updated exception '{exception_id}' to status '{new_status}'.",
            confidence=1.0,
            previous_state="OPEN",
            new_state=new_status,
            human_approval=True
        )
        return True

    def investigate_exception_by_id(self, exception_id: str) -> Dict[str, Any]:
        exc_df = self.db.get_table_df("exceptions")
        match = exc_df[exc_df["exception_id"] == exception_id].to_dict("records") if not exc_df.empty else []
        if not match:
            return {"error": f"Exception ID '{exception_id}' not found"}

        exc = match[0]
        try:
            exc["evidence"] = json.loads(exc["evidence"])
        except Exception:
            pass

        ai_response = self.investigator.investigate_exception(exc)
        return ai_response.model_dump()
