# Representative/RERB receipt chain and quorum ledger

rev0193 narrows the live-drill gap from receipt intake to receipt-chain accounting. rev0192 could distinguish defective intake from satisfaction, but it still lacked a chain object that could answer the operational question: which receipt classes exist, which are only high-fidelity dry runs, which dependency groups are independent, and what exactly remains outside live quorum.

## Core rules

**Receipt chain is not live quorum.** A chain can show that representative and research-ethics review lanes were exercised, but the chain satisfies no live reliance floor unless every counted record is actual-external, independently timestamped or signed, non-host retained, dependency-cleared, and class-appropriate.

**Dry-run quorum is rehearsal only.** A high-fidelity non-host dry run can prove that forms, routing, public failed-gate language, and role choreography are ready. It cannot prove live witness satisfaction.

**Representative/RERB participation is not WRSR closure.** Representative notice and RERB review may convert a WRSR exercise from missing-review no-go to witnessed-readiness dry run, but closure still stays blocked when result return, non-retaliation, or actual external receipt capture is incomplete.

## New object family

The new schema is `schemas/external-receipt-quorum-ledger.schema.json`.

The current example is `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`. It evaluates three receipt intake records:

- `examples/external-receipt-intake-record-first-touch-defective-template.json` — defective first-touch receipt, excluded from live and dry-run quorum;
- `examples/external-receipt-intake-record-representative-notice-dryrun.json` — representative-contact dry-run receipt, eligible only for dry-run choreography;
- `examples/external-receipt-intake-record-rerb-review-dryrun.json` — independent-review dry-run receipt, eligible only for dry-run choreography.

The ledger intentionally keeps `live_quorum_satisfied=false`. It may mark dry-run readiness for the representative/RERB lane, but it cannot upgrade the cross-critical packet to live-witnessed status.

## WRSR exercise progression

The companion WRSR outcome is `examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json`. It shows progress beyond the rev0192 no-go: representative notice and independent review are now exercised through receipt-intake records. The outcome still keeps closure stayed because those records are high-fidelity dry runs rather than actual external receipts, and result-return remains stayed pending subject/representative readable completion.

## Blocking fixtures

rev0193 adds two fixtures:

- `fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json`
- `fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json`

The first blocks dry-run receipt chains from satisfying live receipt quorum. The second blocks representative/RERB dry-run participation from being mislabeled as WRSR closure.

## Refactor effect

This surface becomes the operational receipt-chain spine. The previous receipt-intake surface remains the object definition and defect-triage head; this surface owns quorum accounting across receipt records, live-drill packet references, and WRSR exercise progression. Future work should add actual external receipt records here rather than adding new doctrine surfaces.


## rev0194 result-return quorum layer

rev0194 adds a result-return dry-run receipt and a second quorum ledger: `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`.

The new rule is: **Receipt request is not receipt satisfaction**. The representative, RERB, and result-return lanes can now be rehearsed together, but the live ledger remains unsatisfied until actual external receipts replace high-fidelity dry-run intake records.

## rev0195 response reconciliation

rev0195 keeps the representative/RERB chain in force while adding response reconciliation. Response records may prove that a counterparty replied, declined, or failed verification; they do not convert dry-run quorum into live quorum.
