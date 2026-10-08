# Actual intake import gate and failed-gate public summary

rev0197 targets the next laundering seam after response-to-intake conversion. rev0196 created an eligible-shaped response and intake candidate with `response_state=actual-response-received` and `receipt_state=actual-external`, but the collection context is still a controlled fixture. A live system must not treat those state fields as enough to alter the receipt floor.

## Core rules

**Actual-shaped is not actual.** A response/intake pair may carry actual-looking fields and still be disqualified if provenance shows controlled fixture, dry-run, host-self-attested, stale, dependency-correlated, or non-retained collection context.

**Import changes the live floor only through a provenance gate.** `independent_receipts_present` may increase only when the import gate proves live counterparty collection context, non-host retention, independent timestamp, matching request trace, dependency separation, sealed/public parity, and class-local credit discipline.

**Public failed-gate summary is not receipt satisfaction.** Publishing a failed-gate shell makes non-satisfaction visible; it does not cure the failed class, waive rights, prove consent, prove nonpersonhood, or close WRSR.

**No-response and declination are not waiver.** Declined and expired response states trigger substitute routing, cure clocks, and public non-satisfaction disclosure. They do not satisfy representative contact, independent review, result return, or cross-critical reliance.

**One imported class is not cross-critical reliance.** Even a future valid result-return import would satisfy only one class. Cross-critical reliance remains stayed until the required classes and dependency groups are satisfied.

## Object lane

The import gate is `schemas/actual-receipt-import-gate.schema.json` with current example `examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json`.

The public failed-gate shell is `schemas/failed-gate-public-summary.schema.json` with current example `examples/failed-gate-public-summary-response-conversion-batch.json`.

The gate is deliberately run against the rev0196 eligible-shaped branch. The outcome is no live import: `live_floor_delta=0`, `live_class_credit_granted=false`, `cross_critical_quorum_satisfied=false`, and `reliance_effect=stayed`.

## Failed-gate public shell minimum

A failed-gate summary must disclose the failed class, the public reason, the non-waiver statement, the cure or substitute route, the sealed descriptor, and anti-harassment controls. It may withhold sealed details, but it cannot hide the existence of the failed class.

The rev0197 summary carries four items: fixture-disqualified import, defective continuity response, representative declination, and independent-review no-response expiry. Each item is non-satisfaction evidence only.

## Blocking fixtures

rev0197 adds three fixtures:

- `fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json`
- `fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json`
- `fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json`

Together they block actual-state-field laundering, public-shell omission of failed branches, and no-response-as-waiver laundering.

## Live posture

No actual live external receipt exists in this revision. rev0197 improves the import gate and public failed-gate shell so that when a live response arrives, it can be imported without weakening the rules. Reliance remains stayed until actual non-host receipt collection satisfies the class and dependency gates.

## rev0198 recomputation hardening

rev0198 adds a live counterparty import-attempt record and quorum recomputation report. Actual-shaped state fields remain insufficient, and even a future class-local import must pass recomputation before `independent_receipts_present` changes.
