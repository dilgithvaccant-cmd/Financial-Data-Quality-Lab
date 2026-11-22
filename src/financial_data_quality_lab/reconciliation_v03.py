"""Synthetic document-payment-ledger reconciliation with audit evidence."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

RULES = ('missing_ledger', 'ledger_mismatch', 'unbalanced_settlement',
         'duplicate_payment', 'missing_payment', 'overpayment', 'credit_note_mismatch')
SEVERITY = dict(zip(RULES, ('high', 'high', 'high', 'critical', 'medium', 'high', 'high')))


def amount(value):
    number = Decimal(str(value))
    if not number.is_finite():
        raise ValueError('Nonfinite monetary amount')
    return number


def reconcile(documents, payments, ledger):
    """Positive invoices and negative credit notes; partial payments are permitted."""
    ids = Counter(p['payment_id'] for p in payments)
    by_doc, by_ledger = defaultdict(list), defaultdict(list)
    for p in payments:
        by_doc[p['document_id']].append(p)
    for e in ledger:
        by_ledger[e['document_id']].append(e)
    findings = []
    for doc in documents:
        key = doc['document_id']
        face = amount(doc['amount'])
        linked, entries = by_doc[key], by_ledger[key]
        paid = sum((amount(p['amount']) for p in linked), Decimal('0'))
        posted = sum((amount(e['amount']) for e in entries), Decimal('0'))
        evidence = {'document_id': key, 'document_type': doc['document_type'],
                    'document_amount': str(face), 'paid_amount': str(paid),
                    'ledger_amount': str(posted),
                    'payment_ids': sorted(p['payment_id'] for p in linked),
                    'ledger_entry_ids': sorted(e['entry_id'] for e in entries)}
        def flag(rule):
            findings.append({'document_id': key, 'rule': rule,
                             'severity': SEVERITY[rule], 'evidence': evidence})
        if not entries:
            flag('missing_ledger')
        elif posted != face:
            flag('ledger_mismatch')
        if doc['document_type'] == 'credit_note':
            if face >= 0 or paid != 0:
                flag('credit_note_mismatch')
        elif doc['document_type'] == 'invoice':
            if not linked:
                flag('missing_payment')
            if paid > face:
                flag('overpayment')
            if paid < 0:
                flag('unbalanced_settlement')
        else:
            raise ValueError('Unknown document type')
        if any(ids[p['payment_id']] > 1 for p in linked):
            flag('duplicate_payment')
    return findings


def evaluate(findings, labels, document_ids):
    """Compare findings with separate, scenario-authored labels."""
    actual = {(f['document_id'], f['rule']) for f in findings}
    expected, ids = set(), set(document_ids)
    for label in labels:
        key = (label['document_id'], label['rule'])
        if key[0] not in ids or key[1] not in RULES or key in expected:
            raise ValueError(f'Invalid or repeated label: {key}')
        expected.add(key)
    def score(pred, truth, count):
        tp, fp, fn = len(pred & truth), len(pred - truth), len(truth - pred)
        return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': count - tp - fp - fn,
                'precision': tp / (tp + fp) if tp + fp else None,
                'recall': tp / (tp + fn) if tp + fn else None,
                'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}
    return {'documents': len(ids), 'opportunities': len(ids) * len(RULES),
            'summary': score(actual, expected, len(ids) * len(RULES)),
            'per_rule': {rule: score({x for x in actual if x[1] == rule},
                                      {x for x in expected if x[1] == rule}, len(ids))
                         for rule in RULES}}


def load_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as source:
        return list(csv.DictReader(source))


def write_reports(findings, metrics, output_dir, sources):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    evidence = {'version': '0.3', 'input_sha256': {
        Path(p).name: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources},
        'findings': findings, 'evaluation': metrics}
    (output / 'audit_evidence.json').write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    with (output / 'exceptions.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['document_id', 'rule', 'severity', 'evidence_json'])
        writer.writeheader()
        for finding in findings:
            writer.writerow({**{k: finding[k] for k in ('document_id', 'rule', 'severity')},
                             'evidence_json': json.dumps(finding['evidence'], sort_keys=True)})
    s = metrics['summary']
    lines = ['# Synthetic AP reconciliation v0.3', '',
             f"Documents: {metrics['documents']}; opportunities: {metrics['opportunities']}", '',
             '| TP | FP | FN | Precision | Recall | F1 |',
             '| ---: | ---: | ---: | ---: | ---: | ---: |',
             f"| {s['tp']} | {s['fp']} | {s['fn']} | {s['precision']} | {s['recall']} | {s['f1']} |",
             '', 'Scenario-authored labels; not independently adjudicated.', '',
             '| Rule | TP | FP | FN | F1 |', '| --- | ---: | ---: | ---: | ---: |']
    for rule, value in metrics['per_rule'].items():
        lines.append(f"| {rule} | {value['tp']} | {value['fp']} | {value['fn']} | {value['f1']} |")
    (output / 'research_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='data/v03')
    parser.add_argument('--output-dir', default='reports/v03')
    args = parser.parse_args()
    root = Path(args.data_dir)
    paths = [root / f'{name}.csv' for name in ('documents', 'payments', 'ledger', 'labels')]
    docs, payments, ledger, labels = (load_csv(path) for path in paths)
    findings = reconcile(docs, payments, ledger)
    result = evaluate(findings, labels, [d['document_id'] for d in docs])
    write_reports(findings, result, args.output_dir, paths)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
