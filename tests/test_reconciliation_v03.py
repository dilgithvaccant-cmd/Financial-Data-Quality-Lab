from pathlib import Path

import pytest

from financial_data_quality_lab.reconciliation_v03 import (
    RULES, evaluate, load_csv, reconcile, write_reports,
)

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'v03'


def fixture():
    return [load_csv(ROOT / f'{name}.csv') for name in ('documents', 'payments', 'ledger', 'labels')]


def test_dataset_size():
    docs, payments, ledger, labels = fixture()
    assert len(docs) == 28
    assert len(payments) == 27
    assert len(ledger) == 27
    assert len(labels) == 7


def test_evaluation_metrics():
    docs, payments, ledger, labels = fixture()
    result = evaluate(reconcile(docs, payments, ledger), labels, [d['document_id'] for d in docs])
    assert result['opportunities'] == 28 * len(RULES)
    assert result['summary']['tp'] == 7
    assert result['summary']['fp'] == 0
    assert result['summary']['fn'] == 0
    assert result['summary']['f1'] == 1


def test_partial_payment_is_allowed():
    docs, payments, ledger, _ = fixture()
    assert not any(f['document_id'] == 'D003' for f in reconcile(docs, payments, ledger))


def test_credit_note_not_missing_payment():
    docs, payments, ledger, _ = fixture()
    assert ('D004', 'missing_payment') not in {
        (f['document_id'], f['rule']) for f in reconcile(docs, payments, ledger)}


def test_duplicate_payment_critical():
    docs, payments, ledger, _ = fixture()
    flags = [f for f in reconcile(docs, payments, ledger) if f['rule'] == 'duplicate_payment']
    assert len(flags) == 1
    assert flags[0]['severity'] == 'critical'
    assert flags[0]['evidence']['payment_ids']


def test_invalid_label_rejected():
    docs, payments, ledger, labels = fixture()
    with pytest.raises(ValueError):
        evaluate(reconcile(docs, payments, ledger),
                 labels + [{'document_id': 'NONE', 'rule': 'missing_payment'}],
                 [d['document_id'] for d in docs])


def test_reproducible_reports(tmp_path):
    docs, payments, ledger, labels = fixture()
    findings = reconcile(docs, payments, ledger)
    metrics = evaluate(findings, labels, [d['document_id'] for d in docs])
    paths = [ROOT / f'{name}.csv' for name in ('documents', 'payments', 'ledger', 'labels')]
    write_reports(findings, metrics, tmp_path, paths)
    original = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    write_reports(findings, metrics, tmp_path, paths)
    assert original == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert len(original) == 3


def test_credit_note_mismatch():
    docs, payments, ledger, _ = fixture()
    docs = [dict(d) for d in docs]
    next(d for d in docs if d['document_id'] == 'D004')['amount'] = '10.00'
    assert any(f['rule'] == 'credit_note_mismatch' for f in reconcile(docs, payments, ledger))
