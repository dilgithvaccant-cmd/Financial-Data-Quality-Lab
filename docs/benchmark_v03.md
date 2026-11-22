# v0.3 audit reconciliation benchmark

## Scope and evaluation design

The new `data/v03/` fixture contains 28 fictional documents, 27 payment rows, 27 ledger entries, and **7 scenario-authored exception labels** in a separate `labels.csv`. Labels are not passed to the reconciliation engine. They were specified from scenario design, **not** independently annotated by a blinded human reviewer. This is a separate evaluation fixture, not evidence of independent external validation.

A signed negative document represents a credit note. Partial payment is legitimate and does not automatically trigger an exception. Payment references are matched by document ID and duplicate payment IDs are flagged. Ledger entries are compared with document face amounts. This is a simplified three-way matching demonstration; it is not a bank reconciliation or full accounting ledger posting engine.

## Seven controls

`missing_ledger`, `ledger_mismatch`, `unbalanced_settlement`, `duplicate_payment`, `missing_payment`, `overpayment`, `credit_note_mismatch`.

Findings include a deterministic severity classification, source document ID, linked payment/ledger entry IDs, and amount evidence. The report includes SHA-256 hashes of all four input files. Hashes demonstrate input identity, **not** that the source transactions are genuine.

## Reproduce

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m financial_data_quality_lab.reconciliation_v03 --data-dir data/v03 --output-dir reports/v03
```

Outputs: `audit_evidence.json`, `exceptions.csv`, and `research_report.md`. Results are evaluated at the document-rule level (28 × 7 = 196 opportunities). Precision, recall and F1 are undefined when denominators are zero, and no score should be interpreted as performance on live financial records.

## Limitations

No independent human adjudication, no real bank feed, no multi-currency, no credit-note allocation across invoices, no partial-payment aging, and no verification of settlement status. Severity is an illustrative prioritization, not a fraud finding. The original v0.2 engine remains unchanged. Do not publish employer, customer, supplier or bank records.
