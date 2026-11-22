# Research methodology

## Question
Can deterministic checks identify common accounts-payable data-quality defects in synthetic invoice records?

## Approach
Apply documented rules to synthetic CSV data. Findings identify the source row, rule ID, and explanation. All rules must be deterministic and testable.

## Initial controls
Required supplier and invoice identifiers; duplicate supplier/invoice combinations; ISO date parsing; due-date ordering; and arithmetic reconciliation of subtotal, VAT and total.

## Evaluation plan
Create a labeled synthetic benchmark and report precision, recall and false-positive rate per rule. No production performance claims are made from this initial demonstration.

## Limitations
Duplicate keys may represent legitimate corrections; invoice dates and VAT rates require jurisdictional and business context. Human review is required before consequential financial actions.
