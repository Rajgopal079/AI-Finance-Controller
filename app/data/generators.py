import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
from app.data.schemas import (
    CustomerSchema, InvoiceSchema, BankTransactionSchema,
    PaymentSchema, SettlementSchema, TaxLineSchema,
    FinancialOutflowSchema, GroundTruthSchema
)

CUSTOMER_NAMES = [
    "Apex Tech Solutions", "BlueSky Retailers", "Cipher Cloud Systems",
    "Delta Logistics Ltd", "Echo Media Group", "Frontier Global",
    "GreenGrid Energy", "Horizon Healthcare", "InfiniSoft Labs",
    "Jupiter Traders", "Krypton Infra", "Lumina Enterprises",
    "Nexus Electronics", "OmniCorp India", "Prism Biotech"
]

GATEWAYS = ["Razorpay", "Stripe", "PineLabs", "HDFC_Direct"]

class SyntheticDataGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        
    def generate(self, count: int = 100) -> Dict[str, List[dict]]:
        """
        Generate synthetic financial datasets with explicit ground-truth relationships and edge cases.
        Count represents the base number of invoices.
        """
        random.seed(self.seed)
        base_date = datetime(2026, 8, 1)
        
        customers = []
        for i, name in enumerate(CUSTOMER_NAMES):
            cid = f"CUST-{1000 + i}"
            behavior = random.choice(["PROMPT", "PROMPT", "OCCASIONAL_DELAY", "CHRONIC_DELAY", "PARTIAL"])
            delay = 0 if behavior == "PROMPT" else random.randint(3, 20)
            risk = "LOW" if behavior == "PROMPT" else ("MEDIUM" if behavior == "OCCASIONAL_DELAY" else "HIGH")
            customers.append(CustomerSchema(
                customer_id=cid,
                customer_name=name,
                historical_payment_behavior=behavior,
                average_payment_delay=delay,
                risk_level=risk
            ).model_dump())
            
        invoices = []
        bank_txns = []
        payments = []
        settlements = []
        tax_lines = []
        outflows = []
        ground_truth = []
        
        txn_counter = 8000
        pay_counter = 5000
        settle_counter = 3000
        tax_counter = 9000
        outflow_counter = 7000

        # Generate Outflows (Vendor payments, Payroll, Tax payments, Expenses)
        outflow_categories = [
            ("VENDOR_PAYMENT", "AWS Cloud Services", 125000.0, 5),
            ("PAYROLL", "Engineering Payroll", 450000.0, 10),
            ("TAX_PAYMENT", "GST Advance Tax", 95000.0, 15),
            ("OPERATING_EXPENSE", "Office Facility Lease", 80000.0, 20)
        ]
        for idx, (cat, recip, o_amt, o_day) in enumerate(outflow_categories):
            o_date = (base_date + timedelta(days=o_day)).strftime("%Y-%m-%d")
            oid = f"OUT-{outflow_counter + idx}"
            outflows.append(FinancialOutflowSchema(
                outflow_id=oid,
                category=cat,
                amount=o_amt,
                due_date=o_date,
                recipient=recip,
                status="PENDING"
            ).model_dump())
            # Add corresponding debit bank transaction for past outflows
            bank_txns.append(BankTransactionSchema(
                transaction_id=f"TXN-DEBIT-{idx+1}",
                transaction_date=o_date,
                amount=o_amt,
                currency="INR",
                description=f"DEBIT OUTFLOW {cat} TO {recip}",
                reference=f"REF-OUT-{idx+1}",
                account_id="ACC-101",
                transaction_type="DEBIT"
            ).model_dump())

        # Main Invoices & 4-Stage Lifecycles
        for i in range(1, count + 1):
            inv_id = f"INV-{1000 + i}"
            cust = random.choice(customers)
            cname = cust["customer_name"]
            cid = cust["customer_id"]
            
            inv_days_offset = random.randint(0, 25)
            inv_date = base_date + timedelta(days=inv_days_offset)
            due_date = inv_date + timedelta(days=30)
            
            # Cases
            if i == 1:
                base_amount = 100000.0
                case_type = "EXACT_MATCH"
            elif i == 2:
                base_amount = 50000.0
                case_type = "PARTIAL_PAYMENT"
            elif i == 3:
                base_amount = 240000.0
                case_type = "DUPLICATE"
            elif i == 4:
                base_amount = 180000.0
                case_type = "SETTLEMENT_DELAY"
            elif i == 5:
                base_amount = 50000.0
                case_type = "TAX_MISMATCH"
            elif i == 6:
                base_amount = 850000.0
                case_type = "HIGH_VALUE_DISCREPANCY"
            elif i == 7:
                base_amount = 120000.0
                case_type = "UNMATCHED"
            elif i == 8:
                base_amount = 75000.0
                case_type = "AMBIGUOUS_CONFLICT" # CASE 8: Reference conflict!
            else:
                base_amount = round(random.choice([15000, 25000, 45000, 60000, 120000, 250000]), 2)
                case_type = random.choice([
                    "EXACT_MATCH", "EXACT_MATCH", "EXACT_MATCH", "EXACT_MATCH",
                    "PARTIAL_PAYMENT", "DUPLICATE", "SETTLEMENT_DELAY", "TAX_MISMATCH",
                    "AMBIGUOUS_CONFLICT", "UNMATCHED"
                ])

            tax_rate = 0.18
            tax_amount = round(base_amount * tax_rate, 2)
            total_amount = round(base_amount + tax_amount, 2)
            ref_str = f"REF-{inv_id}-{cname[:3].upper()}"

            inv_status = "PAID" if case_type in ["EXACT_MATCH", "TAX_MISMATCH", "SETTLEMENT_DELAY"] else "UNPAID"
            if case_type == "PARTIAL_PAYMENT":
                inv_status = "PARTIAL"

            invoices.append(InvoiceSchema(
                invoice_id=inv_id,
                customer_id=cid,
                customer_name=cname,
                invoice_date=inv_date.strftime("%Y-%m-%d"),
                due_date=due_date.strftime("%Y-%m-%d"),
                amount=base_amount,
                currency="INR",
                tax_amount=tax_amount,
                total_amount=total_amount,
                status=inv_status,
                reference=ref_str
            ).model_dump())

            # Tax Line
            recorded_tax = tax_amount
            if case_type == "TAX_MISMATCH":
                recorded_tax = round(tax_amount - 300.0 if tax_amount >= 300 else tax_amount * 0.8, 2)

            tax_lines.append(TaxLineSchema(
                tax_line_id=f"TAX-{tax_counter + i}",
                invoice_id=inv_id,
                tax_type="GST_18",
                taxable_amount=base_amount,
                tax_rate=0.18,
                expected_tax=tax_amount,
                recorded_tax=recorded_tax
            ).model_dump())

            pay_date = inv_date + timedelta(days=random.randint(1, 10))
            txn_date = pay_date + timedelta(days=random.randint(1, 4)) # actual settlement delay delta

            # 4-stage lifecycle ground truth tracking
            true_pid = None
            true_txnid = None
            true_stlid = None

            if case_type == "EXACT_MATCH":
                true_pid = f"PAY-{pay_counter + i}"
                true_txnid = f"TXN-{txn_counter + i}"
                true_stlid = f"STL-{settle_counter + i}"

                payments.append(PaymentSchema(
                    payment_id=true_pid, invoice_id=inv_id, customer_id=cid,
                    payment_date=pay_date.strftime("%Y-%m-%d"), amount=total_amount,
                    payment_method="NEFT", reference=ref_str, status="COMPLETED"
                ).model_dump())

                bank_txns.append(BankTransactionSchema(
                    transaction_id=true_txnid, transaction_date=txn_date.strftime("%Y-%m-%d"),
                    amount=total_amount, currency="INR", description=f"NEFT CREDIT {ref_str} FROM {cname}",
                    reference=ref_str, account_id="ACC-101", transaction_type="CREDIT"
                ).model_dump())

                settlements.append(SettlementSchema(
                    settlement_id=true_stlid, payment_id=true_pid,
                    settlement_date=pay_date.strftime("%Y-%m-%d"), settled_amount=total_amount,
                    gateway="Razorpay", settlement_status="SETTLED", bank_reference=f"BANK-REF-{true_txnid}"
                ).model_dump())

            elif case_type == "PARTIAL_PAYMENT":
                actual_paid = round(total_amount - 7500.0 if total_amount > 7500 else total_amount * 0.7, 2)
                true_pid = f"PAY-{pay_counter + i}"
                true_txnid = f"TXN-{txn_counter + i}"

                payments.append(PaymentSchema(
                    payment_id=true_pid, invoice_id=inv_id, customer_id=cid,
                    payment_date=pay_date.strftime("%Y-%m-%d"), amount=actual_paid,
                    payment_method="NEFT", reference=ref_str, status="COMPLETED"
                ).model_dump())

                bank_txns.append(BankTransactionSchema(
                    transaction_id=true_txnid, transaction_date=txn_date.strftime("%Y-%m-%d"),
                    amount=actual_paid, currency="INR", description=f"PARTIAL REMITTANCE {ref_str}",
                    reference=ref_str, account_id="ACC-101", transaction_type="CREDIT"
                ).model_dump())

            elif case_type == "DUPLICATE":
                true_pid = f"PAY-{pay_counter + i}-A"
                true_txnid = f"TXN-{txn_counter + i}-A"

                payments.append(PaymentSchema(
                    payment_id=true_pid, invoice_id=inv_id, customer_id=cid,
                    payment_date=pay_date.strftime("%Y-%m-%d"), amount=total_amount,
                    payment_method="RTGS", reference=ref_str, status="COMPLETED"
                ).model_dump())
                payments.append(PaymentSchema(
                    payment_id=f"PAY-{pay_counter + i}-B", invoice_id=inv_id, customer_id=cid,
                    payment_date=pay_date.strftime("%Y-%m-%d"), amount=total_amount,
                    payment_method="RTGS", reference=ref_str, status="COMPLETED"
                ).model_dump())

                bank_txns.append(BankTransactionSchema(
                    transaction_id=true_txnid, transaction_date=txn_date.strftime("%Y-%m-%d"),
                    amount=total_amount, currency="INR", description=f"RTGS CREDIT {ref_str}",
                    reference=ref_str, account_id="ACC-101", transaction_type="CREDIT"
                ).model_dump())

            elif case_type == "SETTLEMENT_DELAY":
                true_pid = f"PAY-{pay_counter + i}"
                true_stlid = f"STL-{settle_counter + i}"

                payments.append(PaymentSchema(
                    payment_id=true_pid, invoice_id=inv_id, customer_id=cid,
                    payment_date=pay_date.strftime("%Y-%m-%d"), amount=total_amount,
                    payment_method="UPI", reference=ref_str, status="COMPLETED"
                ).model_dump())

                settlements.append(SettlementSchema(
                    settlement_id=true_stlid, payment_id=true_pid,
                    settlement_date=pay_date.strftime("%Y-%m-%d"), settled_amount=total_amount,
                    gateway="Stripe", settlement_status="DELAYED", bank_reference="PENDING_GATEWAY_RELEASE"
                ).model_dump())

            elif case_type == "AMBIGUOUS_CONFLICT":
                # CASE 8: Reference conflict! Transaction amount matches, customer matches, date is close,
                # BUT transaction reference contains INV-1136 instead of INV-1008!
                conflicting_ref = f"REF-INV-1136-{cname[:3].upper()}"
                true_txnid = f"TXN-AMB-{txn_counter + i}"

                bank_txns.append(BankTransactionSchema(
                    transaction_id=true_txnid, transaction_date=txn_date.strftime("%Y-%m-%d"),
                    amount=total_amount, currency="INR", description=f"TRANSFER WITH CONFLICTING REF {conflicting_ref}",
                    reference=conflicting_ref, account_id="ACC-101", transaction_type="CREDIT"
                ).model_dump())

            elif case_type == "HIGH_VALUE_DISCREPANCY":
                true_txnid = f"TXN-{txn_counter + i}"
                bank_txns.append(BankTransactionSchema(
                    transaction_id=true_txnid, transaction_date=txn_date.strftime("%Y-%m-%d"),
                    amount=850000.0, currency="INR", description=f"UNIDENTIFIED BULK DEPOSIT {cname[:5]}",
                    reference=f"UNKNOWN-{i}", account_id="ACC-101", transaction_type="CREDIT"
                ).model_dump())

            elif case_type == "TAX_MISMATCH":
                true_pid = f"PAY-{pay_counter + i}"
                true_txnid = f"TXN-{txn_counter + i}"
                payments.append(PaymentSchema(
                    payment_id=true_pid, invoice_id=inv_id, customer_id=cid,
                    payment_date=pay_date.strftime("%Y-%m-%d"), amount=total_amount,
                    payment_method="NEFT", reference=ref_str, status="COMPLETED"
                ).model_dump())
                bank_txns.append(BankTransactionSchema(
                    transaction_id=true_txnid, transaction_date=txn_date.strftime("%Y-%m-%d"),
                    amount=total_amount, currency="INR", description=f"NEFT CREDIT {ref_str}",
                    reference=ref_str, account_id="ACC-101", transaction_type="CREDIT"
                ).model_dump())

            # Store Ground Truth
            ground_truth.append(GroundTruthSchema(
                invoice_id=inv_id,
                true_payment_id=true_pid,
                true_transaction_id=true_txnid,
                true_settlement_id=true_stlid,
                case_type=case_type,
                expected_relationship=f"Invoice {inv_id} ground truth type is {case_type}."
            ).model_dump())

        return {
            "customers": customers,
            "invoices": invoices,
            "bank_transactions": bank_txns,
            "payments": payments,
            "settlements": settlements,
            "tax_lines": tax_lines,
            "financial_outflows": outflows,
            "ground_truth": ground_truth
        }
