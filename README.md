# Financial Data Quality Lab

Reproducible applied research into **synthetic accounts-payable data quality, invoice/payment reconciliation, and auditable controls**.

## Research question

How consistently do transparent accounting validation rules detect labeled exceptions in a controlled synthetic invoice/payment/ledger dataset?

## v0.2 — active benchmark

- **120 fictional records**, 10 documented controls, 1,200 row-rule opportunities
- Invoice duplicate, missing field, date, monetary arithmetic and illustrative VAT checks
- Payment amount reconciliation and missing payment/ledger reference controls
- Per-rule and micro-averaged precision, recall, F1 and false-positive rate
- Deterministic JSON, CSV and Markdown research reports
- Automated tests and GitHub Actions

The fixture is intentionally constructed to match the controls. Even if all test cases pass, **this does not establish real-world detection accuracy, tax compliance, fraud detection or audit assurance**.

## Reproduce

Requires Python 3.10+.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m financial_data_quality_lab.controls_v02 --input data/benchmark_v02.csv --output-dir reports/v02
```

Reports are written to `reports/v02/metrics.json`, `findings.csv`, and `results.md`.

Read the [v0.2 benchmark protocol](docs/benchmark_v02.md), [v0.1 benchmark](docs/benchmark.md), and [research methodology](docs/methodology.md).

## Research integrity

All data is fictional. Do not upload confidential employer, supplier, customer or financial records. The illustrative 5% VAT assumption is **not a compliance engine**. Findings require human review before accounting or financial decisions.

## Roadmap

Independently labeled held-out datasets, credit notes, partial payments, bank-ledger matching, configurable tax assumptions, and robustness evaluation.
