"""Deterministic accounts payable data quality checks."""
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation


def validate(records):
    """Return findings with row numbers, rule IDs and explanations."""
    findings = []
    keys = Counter((r.get('supplier_id', '').strip(), r.get('invoice_number', '').strip()) for r in records)
    for index, record in enumerate(records, 1):
        supplier = record.get('supplier_id', '').strip()
        invoice = record.get('invoice_number', '').strip()
        if not supplier or not invoice:
            findings.append({'row': index, 'rule': 'required_field', 'detail': 'Supplier ID and invoice number are required'})
        if supplier and invoice and keys[(supplier, invoice)] > 1:
            findings.append({'row': index, 'rule': 'duplicate_invoice', 'detail': 'Repeated supplier/invoice key'})
        try:
            invoice_date = date.fromisoformat(record.get('invoice_date', ''))
            due_date = date.fromisoformat(record.get('due_date', ''))
            if due_date < invoice_date:
                findings.append({'row': index, 'rule': 'date_order', 'detail': 'Due date precedes invoice date'})
        except ValueError:
            findings.append({'row': index, 'rule': 'invalid_date', 'detail': 'Dates must use YYYY-MM-DD'})
        try:
            subtotal = Decimal(record.get('subtotal', ''))
            vat = Decimal(record.get('vat', ''))
            total = Decimal(record.get('total', ''))
            if abs(subtotal + vat - total) > Decimal('0.01'):
                findings.append({'row': index, 'rule': 'total_mismatch', 'detail': 'Subtotal plus VAT differs from total'})
        except InvalidOperation:
            findings.append({'row': index, 'rule': 'invalid_amount', 'detail': 'Amounts must be decimal numbers'})
    return findings
