"""Version 0.2 synthetic accounting and reconciliation benchmark.

This is a controlled experiment, not UAE VAT compliance advice.
"""
import argparse
import csv
import json
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

RULES = (
    'required_field', 'duplicate_invoice', 'date_order', 'invalid_date',
    'total_mismatch', 'invalid_amount', 'vat_rate_mismatch',
    'payment_mismatch', 'missing_payment_reference', 'missing_ledger_reference',
)
TOLERANCE = Decimal('0.01')
ILLUSTRATIVE_VAT_RATE = Decimal('0.05')


def money(value):
    """Parse a finite monetary decimal without binary floating-point errors."""
    amount = Decimal(str(value))
    if not amount.is_finite():
        raise InvalidOperation('non-finite monetary value')
    return amount


def validate_v02(records):
    """Produce row-indexed findings; do not mutate input records."""
    counts = Counter(
        (str(r.get('supplier_id') or '').strip(), str(r.get('invoice_number') or '').strip())
        for r in records
    )
    findings = []
    for row_number, record in enumerate(records, 1):
        def flag(rule, detail):
            findings.append({'row': row_number, 'rule': rule, 'detail': detail})

        supplier = str(record.get('supplier_id') or '').strip()
        invoice = str(record.get('invoice_number') or '').strip()
        if not supplier or not invoice:
            flag('required_field', 'Supplier ID and invoice number are mandatory')
        if supplier and invoice and counts[(supplier, invoice)] > 1:
            flag('duplicate_invoice', 'Repeated supplier/invoice identifier')
        try:
            invoice_date = date.fromisoformat(str(record.get('invoice_date') or ''))
            due_date = date.fromisoformat(str(record.get('due_date') or ''))
            if due_date < invoice_date:
                flag('date_order', 'Due date precedes invoice date')
        except ValueError:
            flag('invalid_date', 'Invalid ISO invoice or due date')

        try:
            subtotal = money(record.get('subtotal', ''))
            vat = money(record.get('vat', ''))
            total = money(record.get('total', ''))
        except (InvalidOperation, ValueError, TypeError):
            flag('invalid_amount', 'Subtotal, VAT and total must be finite decimals')
            subtotal = vat = total = None

        if total is not None:
            if abs(subtotal + vat - total) > TOLERANCE:
                flag('total_mismatch', 'Subtotal plus VAT does not equal total')
            # Controlled assumption: every synthetic transaction is standard-rated.
            if abs(vat - (subtotal * ILLUSTRATIVE_VAT_RATE)) > TOLERANCE:
                flag('vat_rate_mismatch', 'VAT differs from illustrative 5% scenario')
            try:
                paid = money(record.get('payment_amount', ''))
            except (InvalidOperation, ValueError, TypeError):
                flag('payment_mismatch', 'Payment amount is not a finite decimal')
            else:
                if abs(paid - total) > TOLERANCE:
                    flag('payment_mismatch', 'Payment amount does not reconcile to invoice total')

        if not str(record.get('payment_reference') or '').strip():
            flag('missing_payment_reference', 'Payment reference is missing')
        if not str(record.get('ledger_reference') or '').strip():
            flag('missing_ledger_reference', 'Ledger reference is missing')
    return findings


def evaluate_v02(rows):
    """Compare row-rule predictions with independently supplied fixture labels."""
    records = [{k: v for k, v in row.items() if k != 'expected_rules'} for row in rows]
    predicted = {(f['row'], f['rule']) for f in validate_v02(records)}
    expected = set()
    for row_number, row in enumerate(rows, 1):
        for rule in filter(None, (part.strip() for part in str(row.get('expected_rules') or '').split('|'))):
            if rule not in RULES:
                raise ValueError(f'Unknown expected rule at row {row_number}: {rule}')
            expected.add((row_number, rule))

    def scores(actual, truth, opportunities):
        tp = len(actual & truth)
        fp = len(actual - truth)
        fn = len(truth - actual)
        tn = opportunities - tp - fp - fn
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
        fpr = fp / (fp + tn) if fp + tn else None
        return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
                'precision': precision, 'recall': recall, 'f1': f1,
                'false_positive_rate': fpr}

    per_rule = {}
    for rule in RULES:
        actual = {item for item in predicted if item[1] == rule}
        truth = {item for item in expected if item[1] == rule}
        per_rule[rule] = scores(actual, truth, len(rows))
    summary = scores(predicted, expected, len(rows) * len(RULES))
    return {'version': '0.2', 'records': len(rows),
            'rule_opportunities': len(rows) * len(RULES),
            'summary': summary, 'per_rule': per_rule,
            'findings': validate_v02(records)}


def write_reports(result, output_dir):
    """Write deterministic JSON, CSV findings, and Markdown summaries."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'metrics.json').write_text(
        json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    with (output / 'findings.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['row', 'rule', 'detail'])
        writer.writeheader()
        writer.writerows(result['findings'])
    s = result['summary']
    lines = [
        '# Synthetic AP benchmark v0.2 — generated results',
        '',
        f"Records: {result['records']}; row-rule opportunities: {result['rule_opportunities']}.",
        '',
        '| TP | FP | FN | TN | Precision | Recall | F1 |',
        '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
        f"| {s['tp']} | {s['fp']} | {s['fn']} | {s['tn']} | "
        f"{s['precision']} | {s['recall']} | {s['f1']} |",
        '',
        'Results apply only to a hand-constructed synthetic fixture. '
        'They are not evidence of production accuracy or tax compliance.',
        '',
        '| Rule | TP | FP | FN | Precision | Recall | F1 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for rule, m in result['per_rule'].items():
        lines.append(
            f"| {rule} | {m['tp']} | {m['fp']} | {m['fn']} | "
            f"{m['precision']} | {m['recall']} | {m['f1']} |")
    (output / 'results.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Evaluate synthetic AP benchmark v0.2')
    parser.add_argument('--input', default='data/benchmark_v02.csv')
    parser.add_argument('--output-dir', default='reports/v02')
    args = parser.parse_args()
    with Path(args.input).open(newline='', encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    result = evaluate_v02(rows)
    write_reports(result, args.output_dir)
    print(json.dumps({k: v for k, v in result.items() if k != 'findings'}, indent=2))


if __name__ == '__main__':
    main()
