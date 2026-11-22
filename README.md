# Financial Data Quality Lab

Reproducible applied research using **fictional accounts-payable invoices, payments and ledger records**.

## v0.3 — audit reconciliation research prototype

- A separate 28-document synthetic evaluation fixture with seven scenario-authored exception labels
- Three-way document/payment/ledger amount and reference matching
- Credit notes, partial payments, overpayments and duplicate payment IDs
- Severity-tagged exceptions and traceable document/payment/ledger evidence
- Precision, recall and F1 at document-rule level
- Deterministic CSV, JSON and Markdown reports with input SHA-256 hashes

**Important:** Labels are maintained in a separate file, but were created from known synthetic scenarios; they are **not independently adjudicated by external reviewers**. This project does not establish real-world accuracy, audit assurance or fraud detection.

## Reproduce

Python 3.10+:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m financial_data_quality_lab.reconciliation_v03 --data-dir data/v03 --output-dir reports/v03
```

Reports: `reports/v03/audit_evidence.json`, `exceptions.csv`, `research_report.md`.

Read the [v0.3 research protocol](docs/benchmark_v03.md). The [v0.2 benchmark](docs/benchmark_v02.md) and original [methodology](docs/methodology.md) remain available.

## Research integrity

Only synthetic records. No confidential employer, supplier, customer, bank or personal records. Human review is required before accounting decisions. The example does not verify actual payment settlement, bank statements or tax compliance.

## Roadmap

Independent blinded annotation, broader adverse scenarios, settlement aging, credit-note allocation, balanced double-entry checks and cross-currency reconciliation.
