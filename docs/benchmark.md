# Synthetic accounts-payable benchmark v0.1

## Objective and labels

Evaluate deterministic invoice validation at the **(CSV row, rule ID)** level. `data/benchmark_invoices.csv` contains eight entirely fictional records. The `expected_rules` column is a manually specified synthetic ground truth, not an output of the validator. Multiple labels can be separated with `|`.

The validator never receives the `expected_rules` field. The duplicate-invoice rule flags **both** occurrences of a repeated supplier/invoice pair, so both are labeled positive.

## Reproduce

From the repository root:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m financial_data_quality_lab.benchmark --input data/benchmark_invoices.csv --output benchmark-results.json
```

The JSON output is generated, not a committed research result.

## Definitions

For each rule and record, TP is a predicted finding with a matching label, FP is a predicted finding without a label, FN is a label without a finding, and TN is neither. Precision = TP/(TP+FP); recall = TP/(TP+FN); false-positive rate = FP/(FP+TN). Undefined denominators are represented as JSON `null` rather than artificially scoring a rule at 100%.

Micro-averaged precision and recall aggregate all row-rule pairs. No train/test split is needed for fixed deterministic rules, but this hand-constructed example is **not** an independent estimate of performance on real financial data.

## Known limitations

- Eight records are insufficient to support claims about generalization, robustness, production suitability or model performance.
- Labels intentionally match transparent rules, so high benchmark scores would only establish implementation consistency on these examples.
- The benchmark contains no invalid-amount positive cases; its precision and recall for that rule are undefined.
- The validator currently checks subtotal + VAT = total, **not** the correctness of a jurisdiction-specific VAT rate.
- Duplicate identifiers may be legitimate corrections; flags are for human review, not automatic rejection.
- No private, employer, supplier or customer records are used.
