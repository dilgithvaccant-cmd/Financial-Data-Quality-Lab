"""Reproducible, row-rule-level evaluation of synthetic invoice findings."""
import argparse
import csv
import json
from pathlib import Path

from financial_data_quality_lab.validator import validate

RULES = (
    'required_field', 'duplicate_invoice', 'date_order',
    'invalid_date', 'total_mismatch', 'invalid_amount',
)


def evaluate(rows):
    """Evaluate each (row number, rule) pair against independently authored labels."""
    records = [{key: value for key, value in row.items() if key != 'expected_rules'} for row in rows]
    actual = {(finding['row'], finding['rule']) for finding in validate(records)}
    expected = set()
    for index, row in enumerate(rows, 1):
        for rule in filter(None, (part.strip() for part in row.get('expected_rules', '').split('|'))):
            if rule not in RULES:
                raise ValueError(f'Unknown expected rule on row {index}: {rule}')
            expected.add((index, rule))
    metrics = {}
    for rule in RULES:
        predicted = {(row, name) for row, name in actual if name == rule}
        truth = {(row, name) for row, name in expected if name == rule}
        tp = len(predicted & truth)
        fp = len(predicted - truth)
        fn = len(truth - predicted)
        tn = len(rows) - tp - fp - fn
        metrics[rule] = {
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'false_positive_rate': fp / (fp + tn) if fp + tn else None,
        }
    tp = len(actual & expected)
    fp = len(actual - expected)
    fn = len(expected - actual)
    return {
        'records': len(rows), 'rule_opportunities': len(rows) * len(RULES),
        'true_positives': tp, 'false_positives': fp, 'false_negatives': fn,
        'precision': tp / (tp + fp) if tp + fp else None,
        'recall': tp / (tp + fn) if tp + fn else None,
        'per_rule': metrics,
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate synthetic AP validation benchmark')
    parser.add_argument('--input', default='data/benchmark_invoices.csv')
    parser.add_argument('--output', help='Optional JSON output path')
    args = parser.parse_args()
    with Path(args.input).open(newline='', encoding='utf-8') as source:
        result = evaluate(list(csv.DictReader(source)))
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(output + '\n', encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
