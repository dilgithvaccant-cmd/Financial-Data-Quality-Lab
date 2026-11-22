# Financial Data Quality Lab

Reproducible, open-source experiments with deterministic data-quality checks for **synthetic accounts-payable invoices**.

## Research question

How reliably do transparent validation rules identify intentionally labeled invoice defects in a controlled synthetic dataset?

## Current implementation

- Python validator: required identifiers, duplicate supplier/invoice keys, ISO dates, due-date ordering, invalid numeric amounts and subtotal/VAT/total reconciliation
- Eight-row labeled synthetic benchmark with row-rule ground truth
- Precision, recall, false-positive rate and confusion counts per rule
- Automated pytest suite and GitHub Actions workflow

**Status:** early research prototype. The benchmark is hand-constructed and cannot establish accuracy on real-world accounting data.

## Reproduce

Requires Python 3.10+.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m financial_data_quality_lab.benchmark --input data/benchmark_invoices.csv --output benchmark-results.json
```

Read [benchmark methodology](docs/benchmark.md) and [research methodology](docs/methodology.md).

## Research integrity

Only fictional records are included. No confidential financial information, employer records, or supplier/customer data may be committed. Flags require human review before financial decisions. The validator checks arithmetic consistency of VAT amounts, **not** VAT-rate compliance.

## Roadmap

Expand edge-case coverage, validate labels independently, evaluate a larger held-out synthetic dataset and add clear CSV/JSON exception reports.
