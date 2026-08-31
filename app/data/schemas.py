from datetime import date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class CustomerSchema(BaseModel):
    customer_id: str
    customer_name: str
    historical_payment_behavior: str  # e.g., "PROMPT", "OCCASIONAL_DELAY", "CHRONIC_DELAY", "PARTIAL"
    average_payment_delay: int  # days
    risk_level: str  # "LOW", "MEDIUM", "HIGH"

class InvoiceSchema(BaseModel):
    invoice_id: str
    customer_id: str
    customer_name: str
    invoice_date: str
    due_date: str
    amount: float
    currency: str = "INR"
    tax_amount: float
    total_amount: float
    status: str = "UNPAID"  # "PAID", "UNPAID", "PARTIAL", "OVERDUE"
    reference: str

class BankTransactionSchema(BaseModel):
    transaction_id: str
    transaction_date: str
    amount: float
    currency: str = "INR"
    description: str
    reference: str
    account_id: str = "ACC-101"
    transaction_type: str = "CREDIT"  # "CREDIT", "DEBIT"

class PaymentSchema(BaseModel):
    payment_id: str
    invoice_id: Optional[str] = None
    customer_id: str
    payment_date: str
    amount: float
    payment_method: str = "NEFT"  # "NEFT", "RTGS", "UPI", "CREDIT_CARD"
    reference: str
    status: str = "COMPLETED"

class SettlementSchema(BaseModel):
    settlement_id: str
    payment_id: str
    settlement_date: str
    settled_amount: float
    gateway: str = "Razorpay"  # "Razorpay", "Stripe", "PineLabs", "HDFC_Direct"
    settlement_status: str = "SETTLED"  # "SETTLED", "PENDING", "DELAYED", "FAILED"
    bank_reference: str

class TaxLineSchema(BaseModel):
    tax_line_id: str
    invoice_id: str
    tax_type: str  # "GST_18", "GST_12", "GST_5", "CGST_SGST", "IGST"
    taxable_amount: float
    tax_rate: float
    expected_tax: float
    recorded_tax: float

class FinancialOutflowSchema(BaseModel):
    outflow_id: str
    category: str  # "VENDOR_PAYMENT", "PAYROLL", "TAX_PAYMENT", "OPERATING_EXPENSE"
    amount: float
    due_date: str
    recipient: str
    status: str = "PENDING"

class GroundTruthSchema(BaseModel):
    invoice_id: str
    true_payment_id: Optional[str] = None
    true_transaction_id: Optional[str] = None
    true_settlement_id: Optional[str] = None
    case_type: str  # "EXACT_MATCH", "PARTIAL_PAYMENT", "DUPLICATE", "SETTLEMENT_DELAY", "TAX_MISMATCH", "HIGH_VALUE_DISCREPANCY", "AMBIGUOUS_CONFLICT", "UNMATCHED"
    expected_relationship: str

class ReconciledPair(BaseModel):
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    settlement_id: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str  # "FULLY_RECONCILED", "PARTIAL_PAYMENT", "INVOICE_PAYMENT_MISMATCH", "PAYMENT_SETTLEMENT_MISMATCH", "SETTLEMENT_BANK_MISMATCH", "MISSING_PAYMENT", "MISSING_SETTLEMENT", "MISSING_BANK_TRANSACTION", "AMBIGUOUS"
    match_score: float
    evidence: dict
    conflicts: List[str] = []
    notes: Optional[str] = None

class ExceptionRecord(BaseModel):
    exception_id: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    type: str
    financial_amount: float
    related_records: dict
    evidence: dict
    reason: str
    confidence: float
    suggested_next_step: str
    status: str = "OPEN"  # "OPEN", "UNDER_REVIEW", "RESOLVED", "REJECTED", "ESCALATED"
    risk_level: str = "MEDIUM"
