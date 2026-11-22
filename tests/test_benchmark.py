import csv
from pathlib import Path

import pytest

from financial_data_quality_lab.benchmark import evaluate


DATA = Path(__file__).resolve().parents[1] / 'data' / 'benchmark_invoices.csv'


def load():
    with DATA.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def test_benchmark_expected_counts():
    result = evaluate(load())
    assert result['records'] == 8
    assert result['rule_opportunities'] == 48
    assert result['true_positives'] == 6
    assert result['false_positives'] == 0
    assert result['false_negatives'] == 0
    assert result['precision'] == 1.0
    assert result['recall'] == 1.0


def test_duplicate_flags_both_records():
    result = evaluate(load())
    assert result['per_rule']['duplicate_invoice']['tp'] == 2


def test_empty_positive_class_is_undefined():
    result = evaluate(load())
    assert result['per_rule']['invalid_amount']['precision'] is None
    assert result['per_rule']['invalid_amount']['recall'] is None


def test_mislabeled_rule_raises():
    rows = load()
    rows[0]['expected_rules'] = 'not_a_rule'
    with pytest.raises(ValueError, match='Unknown expected rule'):
        evaluate(rows)


def test_false_positive_and_false_negative_accounting():
    rows = load()
    rows[0]['expected_rules'] = 'total_mismatch'
    rows[6]['expected_rules'] = ''
    result = evaluate(rows)
    assert result['false_positives'] == 1
    assert result['false_negatives'] == 1
    assert result['true_positives'] == 5
    assert result['precision'] == pytest.approx(5 / 6)
    assert result['recall'] == pytest.approx(5 / 6)
