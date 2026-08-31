import json
import hashlib
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.database.db import DatabaseManager

class AuditLogger:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def _get_last_hash(self) -> str:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_hash FROM audit_logs ORDER BY audit_id DESC LIMIT 1")
            row = cursor.fetchone()
            if row and row["current_hash"]:
                return row["current_hash"]
            return "GENESIS"

    @staticmethod
    def _compute_hash(previous_hash: str,
                      timestamp: str,
                      user_action: str,
                      record_id: str,
                      agent_action: str,
                      evidence: Any,
                      decision: str,
                      confidence: float,
                      previous_state: str,
                      new_state: str,
                      human_approval: Any) -> str:
        
        ev_data = evidence
        if isinstance(evidence, str):
            try:
                ev_data = json.loads(evidence)
            except Exception:
                ev_data = evidence

        payload = {
            "previous_hash": str(previous_hash),
            "timestamp": str(timestamp),
            "user_action": str(user_action),
            "record_id": str(record_id),
            "agent_action": str(agent_action),
            "evidence": ev_data,
            "decision": str(decision),
            "confidence": float(confidence),
            "previous_state": str(previous_state),
            "new_state": str(new_state),
            "human_approval": bool(human_approval)
        }
        canonical_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def log_event(self,
                  user_action: str,
                  record_id: str,
                  agent_action: str,
                  evidence: dict,
                  decision: str,
                  confidence: float = 1.0,
                  previous_state: str = "OPEN",
                  new_state: str = "RESOLVED",
                  human_approval: bool = False) -> str:
        """
        Record tamper-evident audit entry using SHA-256 hash chaining with deterministic canonical serialization.
        """
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        prev_hash = self._get_last_hash()
        curr_hash = self._compute_hash(
            prev_hash, ts, user_action, record_id, agent_action,
            evidence, decision, confidence, previous_state, new_state, human_approval
        )

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (
                    timestamp, user_action, record_id, agent_action,
                    evidence, decision, confidence, previous_state,
                    new_state, human_approval, previous_hash, current_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts, user_action, record_id, agent_action,
                json.dumps(evidence), decision, confidence,
                previous_state, new_state, 1 if human_approval else 0,
                prev_hash, curr_hash
            ))
            conn.commit()
        return curr_hash

    def verify_audit_chain(self) -> Dict[str, Any]:
        """
        Verify cryptographic SHA-256 hash chain across all audit logs.
        Returns validation status and any detected tampering violations.
        """
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY audit_id ASC", conn)
            if df.empty:
                return {"is_valid": True, "total_events": 0, "violations": []}

            expected_prev_hash = "GENESIS"
            violations = []

            for idx, row in df.iterrows():
                audit_id = row["audit_id"]
                prev_hash = row["previous_hash"]
                curr_hash = row["current_hash"]

                if prev_hash != expected_prev_hash:
                    violations.append(f"Event #{audit_id} previous_hash mismatch: expected '{expected_prev_hash[:8]}...', found '{prev_hash[:8]}...'")

                recomputed = self._compute_hash(
                    prev_hash, row["timestamp"], row["user_action"],
                    row["record_id"], row["agent_action"], row["evidence"],
                    row["decision"], float(row["confidence"]), row["previous_state"],
                    row["new_state"], bool(row["human_approval"])
                )

                if curr_hash != recomputed:
                    violations.append(f"Event #{audit_id} current_hash tampered! Payload fields do not match cryptographic hash.")

                expected_prev_hash = curr_hash

            return {
                "is_valid": len(violations) == 0,
                "total_events": len(df),
                "violations": violations
            }

    def get_audit_logs(self, limit: int = 100) -> List[dict]:
        with self.db_manager.get_connection() as conn:
            df = pd.read_sql_query(f"SELECT * FROM audit_logs ORDER BY audit_id DESC LIMIT {limit}", conn)
            return df.to_dict("records") if not df.empty else []
