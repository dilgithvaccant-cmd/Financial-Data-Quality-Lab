from financial_data_quality_lab.validator import validate


def record(**changes):
    item = {'supplier_id': 'S001', 'invoice_number': 'INV001', 'invoice_date': '2026-01-01', 'due_date': '2026-02-01', 'subtotal': '100.00', 'vat': '5.00', 'total': '105.00'}
    item.update(changes)
    return item


def test_valid_invoice():
    assert validate([record()]) == []


def test_duplicate_invoice():
    result = validate([record(), record()])
    assert sum(item['rule'] == 'duplicate_invoice' for item in result) == 2


def test_date_order():
    assert any(item['rule'] == 'date_order' for item in validate([record(due_date='2025-12-31')]))


def test_total_mismatch():
    assert any(item['rule'] == 'total_mismatch' for item in validate([record(total='100.00')]))


def test_missing_supplier():
    assert any(item['rule'] == 'required_field' for item in validate([record(supplier_id='')]))
