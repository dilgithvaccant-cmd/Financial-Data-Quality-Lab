import csv
from pathlib import Path

import pytest

from financial_data_quality_lab.controls_v02 import (
    RULES, evaluate_v02, validate_v02, write_reports,
)

DATA = Path(__file__).resolve().parents[1] / 'data' / 'benchmark_v02.csv'


def load():
    with DATA.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def test_fixture_is_labeled_and_has_at_least_100_records():
    rows = load()
    assert len(rows) == 120
    assert sum(bool(r['expected_rules']) for r in rows) == 110


def test_expected_micro_metrics():
    result = evaluate_v02(load())
    assert result['records'] == 120
    assert result['rule_opportunities'] == 120 * len(RULES)
    assert result['summary']['tp'] == 110
    assert result['summary']['fp'] == 0
    assert result['summary']['fn'] == 0
    assert result['summary']['precision'] == 1
    assert result['summary']['recall'] == 1
    assert result['summary']['f1'] == 1


def test_each_reconciliation_control_detected():
    metrics = evaluate_v02(load())['per_rule']
    assert metrics['payment_mismatch']['tp'] == 10
    assert metrics['missing_payment_reference']['tp'] == 10
    assert metrics['missing_ledger_reference']['tp'] == 10
    assert metrics['vat_rate_mismatch']['tp'] == 10


def test_duplicate_flags_both_records():
    assert evaluate_v02(load())['per_rule']['duplicate_invoice']['tp'] == 20


def test_mislabel_changes_precision_recall_and_f1():
    rows = load()
    rows[0]['expected_rules'] = 'payment_mismatch'
    rows[9]['expected_rules'] = ''
    result = evaluate_v02(rows)['summary']
    assert result['tp'] == 109
    assert result['fp'] == 1
    assert result['fn'] == 1
    assert result['precision'] == pytest.approx(109 / 110)
    assert result['recall'] == pytest.approx(109 / 110)
    assert result['f1'] == pytest.approx(109 / 110)


def test_unknown_label_is_rejected():
    rows = load()
    rows[0]['expected_rules'] = 'unknown'
    with pytest.raises(ValueError, match='Unknown expected rule'):
        evaluate_v02(rows)


def test_nonfinite_values_are_invalid():
    row = dict(load()[0])
    row['subtotal'] = 'NaN'
    assert 'invalid_amount' in {f['rule'] for f in validate_v02([row])}


def test_missing_payment_reference_is_not_missing_payment():
    row = dict(load()[0])
    row['payment_reference'] = ''
    rules = {f['rule'] for f in validate_v02([row])}
    assert 'missing_payment_reference' in rules
    assert 'payment_mismatch' not in rules


def test_reports_are_reproducible(tmp_path):
    result = evaluate_v02(load())
    write_reports(result, tmp_path)
    files = {name: (tmp_path / name).read_bytes()
             for name in ('metrics.json', 'findings.csv', 'results.md')}
    assert all(files.values())
    write_reports(result, tmp_path)
    assert files == {name: (tmp_path / name).read_bytes() for name in files}
    assert b'110' in files['results.md']
