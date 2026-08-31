import pandas as pd
from typing import Tuple, List, Dict
from pydantic import ValidationError
from app.data.schemas import (
    InvoiceSchema, BankTransactionSchema, PaymentSchema,
    SettlementSchema, TaxLineSchema, CustomerSchema
)
from app.core.exceptions import DataValidationError

class DataValidator:
    @staticmethod
    def validate_invoices(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        errors = []
        valid_rows = []
        required_cols = {"invoice_id", "customer_id", "customer_name", "invoice_date", "due_date", "amount", "total_amount"}
        missing = required_cols - set(df.columns)
        if missing:
            raise DataValidationError(f"Invoices DataFrame missing columns: {missing}")
            
        for idx, row in df.iterrows():
            try:
                item = InvoiceSchema(**row.to_dict())
                valid_rows.append(item.model_dump())
            except ValidationError as e:
                errors.append(f"Row {idx} Invoice validation error: {e}")
        return pd.DataFrame(valid_rows), errors

    @staticmethod
    def validate_bank_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        errors = []
        valid_rows = []
        required_cols = {"transaction_id", "transaction_date", "amount", "description"}
        missing = required_cols - set(df.columns)
        if missing:
            raise DataValidationError(f"Bank Transactions missing columns: {missing}")
            
        for idx, row in df.iterrows():
            try:
                item = BankTransactionSchema(**row.to_dict())
                valid_rows.append(item.model_dump())
            except ValidationError as e:
                errors.append(f"Row {idx} BankTxn validation error: {e}")
        return pd.DataFrame(valid_rows), errors
