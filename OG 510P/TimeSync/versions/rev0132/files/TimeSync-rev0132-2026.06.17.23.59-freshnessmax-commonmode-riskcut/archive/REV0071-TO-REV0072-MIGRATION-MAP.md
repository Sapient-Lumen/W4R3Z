# rev0071 to rev0072 migration map

## New files

```text
schema/replay-transparency-audit.schema.json
spec/35-replay-transparency-and-aggregate-verifier-audit.md
examples/evaluator/replay-transparency-receipt-p3-redacted.json
examples/evaluator/aggregate-verifier-audit-summary-p3.json
examples/discovery-request-with-replay-transparency.json
archive/FT-0071-CLOSURE.md
archive/REV0071-TO-REV0072-MIGRATION-MAP.md
```

## Normative changes

- Added the non-satisfying evidence class `replay_transparency_receipt`.
- Added detached replay-transparency receipt and aggregate verifier audit summary schema validation.
- Added discovery-returned nested validation for `replay_transparency_receipt` and `aggregate_verifier_audit_summary`.
- Regenerated profile normative digests because the non-satisfying evidence-class set is part of evidence policy.

## Compatibility note

rev0071 challenge results remain structurally valid, but rev0072 consumers may request or retain detached replay-transparency receipts when replay visibility is required by local policy. These receipts do not upgrade or reopen the underlying profile assessment.
