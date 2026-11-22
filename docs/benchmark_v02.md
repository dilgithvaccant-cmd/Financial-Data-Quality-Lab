# Financial Data Quality Lab — v0.2 benchmark protocol

## Dataset and controls

`data/benchmark_v02.csv` contains **120 invented invoice/payment/ledger rows**. It is generated from 10 repeated blocks of 12 deterministic scenarios; it is not sampled from a real ledger and does not contain real parties or accounts. The 10 controls are: required supplier/invoice identifiers; duplicate supplier/invoice keys; due-date ordering; invalid dates; invoice arithmetic; invalid decimal amounts; illustrative 5% VAT arithmetic; payment-to-invoice amount mismatch; missing payment reference; and missing ledger reference.

**Important:** The 5% VAT assumption is deliberately fixed for this synthetic standard-rated scenario. It does not establish UAE tax compliance, treatment of zero-rated/exempt transactions, or eligibility of input VAT. A matching payment amount is not evidence of actual bank settlement or ledger posting. Missing references are workflow exceptions, not proof of fraud.

## Labeling and evaluation

The final `expected_rules` column encodes manually specified scenario labels separated by `|`. The validator is never passed this column. Duplicate-pair scenarios label **both** matching rows as positive. Every rule is evaluated at the **(row, rule)** level, including true negatives. There are 120 × 10 = 1,200 row-rule opportunities, and 110 positive labels in the fixture.

Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 = 2TP/(2TP+FP+FN); false-positive rate = FP/(FP+TN). Undefined denominators produce `null`, not an invented 100%. Summary metrics are micro-averaged over all row-rule pairs. This fixture intentionally aligns labels to transparent checks; perfect results would be a **self-consistency check, not independent validation**.

## Reproduce

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m financial_data_quality_lab.controls_v02 --input data/benchmark_v02.csv --output-dir reports/v02
```

The CLI writes `metrics.json`, `findings.csv`, and `results.md`. Re-running with identical input produces byte-identical files. Generated reports are not required to be committed; CI verifies the implementation via pytest.

## Limitations and next experiment

- The fixture is deliberately easy and repeats scenarios; it cannot support generalization claims.
- No independent blinded annotation, adversarial cases, partial payments, credit notes, multiple VAT treatments, exchange rates, or bank statement reconciliation are included.
- Rule coverage is not fraud detection, audit assurance, or a substitute for qualified accounting review.
- Future work: independently annotated held-out cases, scenario diversity, configurable tolerance and tax assumptions, and stratified error analysis.
