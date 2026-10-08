# Synthetic ballot-accounting reconciliation

Archive version: `v900`  
Report: `artifacts/reports/ballot-accounting-reconciliation-rev0900.json`  

This is a synthetic reconciliation of the Example County minimal BD/CVR fixture against a minimal ballot-accounting ledger.

## Result

- Decision: `SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE`.
- Reporting units checked: `2`.
- Contest accounting rows checked: `4`.
- Synthetic CVR records counted: `6`.
- Errors: `0`.

## What this catches

- CVR record count drift against ballot-accounting totals.
- Contest eligible-ballot, selection-slot, selection-count, undervote-slot, and overvote-record mismatches.
- Unknown reporting units or contests in the accounting ledger.

## Boundary

This is not live custody evidence, not a full NIST CDF conformance result, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.
It does not authorize live pilot use and does not replace ballot accounting, custody transfer/seal records, audit, recount, canvass, certification, retention, public-records review, or counsel review.
