import sqlite3
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from app.core.config import config

class DatabaseManager:
    def __init__(self, db_path: str = config.db_path):
        self.db_path = db_path
        self._shared_conn = None
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
        self.init_db()

    def get_connection(self):
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT,
                historical_payment_behavior TEXT,
                average_payment_delay INTEGER,
                risk_level TEXT
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                customer_id TEXT,
                customer_name TEXT,
                invoice_date TEXT,
                due_date TEXT,
                amount REAL,
                currency TEXT,
                tax_amount REAL,
                total_amount REAL,
                status TEXT,
                reference TEXT
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_transactions (
                transaction_id TEXT PRIMARY KEY,
                transaction_date TEXT,
                amount REAL,
                currency TEXT,
                description TEXT,
                reference TEXT,
                account_id TEXT,
                transaction_type TEXT
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                invoice_id TEXT,
                customer_id TEXT,
                payment_date TEXT,
                amount REAL,
                payment_method TEXT,
                reference TEXT,
                status TEXT
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS settlements (
                settlement_id TEXT PRIMARY KEY,
                payment_id TEXT,
                settlement_date TEXT,
                settled_amount REAL,
                gateway TEXT,
                settlement_status TEXT,
                bank_reference TEXT
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tax_lines (
                tax_line_id TEXT PRIMARY KEY,
                invoice_id TEXT,
                tax_type TEXT,
                taxable_amount REAL,
                tax_rate REAL,
                expected_tax REAL,
                recorded_tax REAL
            )""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_outflows (
                outflow_id TEXT PRIMARY KEY,
                category TEXT,
                amount REAL,
                due_date TEXT,
                recipient TEXT,
                status TEXT
            )""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ground_truth (
                invoice_id TEXT PRIMARY KEY,
                true_payment_id TEXT,
                true_transaction_id TEXT,
                true_settlement_id TEXT,
                case_type TEXT,
                expected_relationship TEXT
            )""")
            
            cursor.execute("DROP TABLE IF EXISTS reconciliations")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reconciliations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT,
                payment_id TEXT,
                settlement_id TEXT,
                transaction_id TEXT,
                status TEXT,
                match_score REAL,
                evidence TEXT,
                conflicts TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS exceptions (
                exception_id TEXT PRIMARY KEY,
                severity TEXT,
                type TEXT,
                financial_amount REAL,
                related_records TEXT,
                evidence TEXT,
                reason TEXT,
                confidence REAL,
                suggested_next_step TEXT,
                status TEXT,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            
            cursor.execute("DROP TABLE IF EXISTS audit_logs")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_action TEXT,
                record_id TEXT,
                agent_action TEXT,
                evidence TEXT,
                decision TEXT,
                confidence REAL,
                previous_state TEXT,
                new_state TEXT,
                human_approval INTEGER,
                previous_hash TEXT,
                current_hash TEXT
            )""")
            conn.commit()

    def clear_all(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for table in ["customers", "invoices", "bank_transactions", "payments", "settlements", "tax_lines", "financial_outflows", "ground_truth", "reconciliations", "exceptions", "audit_logs"]:
                cursor.execute(f"DELETE FROM {table}")
            conn.commit()

    def load_dataset(self, dataset_dict: Dict[str, List[dict]]):
        self.clear_all()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for cust in dataset_dict.get("customers", []):
                cursor.execute("INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?)",
                               (cust["customer_id"], cust["customer_name"], cust["historical_payment_behavior"], cust["average_payment_delay"], cust["risk_level"]))
                
            for inv in dataset_dict.get("invoices", []):
                cursor.execute("INSERT OR REPLACE INTO invoices VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                               (inv["invoice_id"], inv["customer_id"], inv["customer_name"], inv["invoice_date"], inv["due_date"], inv["amount"], inv["currency"], inv["tax_amount"], inv["total_amount"], inv["status"], inv["reference"]))
                
            for txn in dataset_dict.get("bank_transactions", []):
                cursor.execute("INSERT OR REPLACE INTO bank_transactions VALUES (?,?,?,?,?,?,?,?)",
                               (txn["transaction_id"], txn["transaction_date"], txn["amount"], txn["currency"], txn["description"], txn["reference"], txn["account_id"], txn.get("transaction_type", "CREDIT")))
                
            for pay in dataset_dict.get("payments", []):
                cursor.execute("INSERT OR REPLACE INTO payments VALUES (?,?,?,?,?,?,?,?)",
                               (pay["payment_id"], pay["invoice_id"], pay["customer_id"], pay["payment_date"], pay["amount"], pay["payment_method"], pay["reference"], pay["status"]))
                
            for stl in dataset_dict.get("settlements", []):
                cursor.execute("INSERT OR REPLACE INTO settlements VALUES (?,?,?,?,?,?,?)",
                               (stl["settlement_id"], stl["payment_id"], stl["settlement_date"], stl["settled_amount"], stl["gateway"], stl["settlement_status"], stl["bank_reference"]))
                
            for tax in dataset_dict.get("tax_lines", []):
                cursor.execute("INSERT OR REPLACE INTO tax_lines VALUES (?,?,?,?,?,?,?)",
                               (tax["tax_line_id"], tax["invoice_id"], tax["tax_type"], tax["taxable_amount"], tax["tax_rate"], tax["expected_tax"], tax["recorded_tax"]))
                               
            for out in dataset_dict.get("financial_outflows", []):
                cursor.execute("INSERT OR REPLACE INTO financial_outflows VALUES (?,?,?,?,?,?)",
                               (out["outflow_id"], out["category"], out["amount"], out["due_date"], out["recipient"], out.get("status", "PENDING")))

            for gt in dataset_dict.get("ground_truth", []):
                cursor.execute("INSERT OR REPLACE INTO ground_truth VALUES (?,?,?,?,?,?)",
                               (gt["invoice_id"], gt.get("true_payment_id"), gt.get("true_transaction_id"), gt.get("true_settlement_id"), gt["case_type"], gt["expected_relationship"]))

            conn.commit()

    def get_table_df(self, table_name: str) -> pd.DataFrame:
        with self.get_connection() as conn:
            return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
