# rev0221 quorum participation and rollback recompute refactor

rev0221 closes the next live-path overclaim after floor activation: an activation record may admit an actual import gate to the final recompute route, but activation is still not enough for class-local counting, cross-critical quorum, or reliance upgrade.

The new boundary is a **live receipt quorum participation record**. It is deliberately narrow. It consumes an actual import gate plus its linked floor-activation record and replays the quorum-specific posture that is easiest to skip when pressure rises: duplicate counterparty, duplicate dependency group, duplicate issuer key, duplicate receipt class, supersession, challenge/rollback, failed-gate summary readiness, no manual quorum override, single-class-quorum blocking, full-vector recompute requirement, and public/private release safety.

The live route is now:

`evidence drop -> pilot -> LEAP candidate -> candidate challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> intake record -> import readiness gate -> actual import gate -> floor activation record -> quorum participation record -> computed floor`

## Why this was risky

rev0220 made readiness replay and floor activation mandatory before an import gate could enter computed-floor evaluation. That was a substantive improvement, but it left one seam: once activation succeeded, the final recompute path still relied on the floor engine to apply quorum, duplicate, supersession, and rollback controls internally. The controls existed, but there was no object whose sole purpose was to say: this specific import may enter the independence-discount set, but this record has no direct floor, quorum, or reliance effect.

That seam matters because the first real artifact path will likely be run under urgency. A single class-local success could be rhetorically overread as cross-critical quorum. A stale activation could be counted after a challenge opens. Multiple receipts from the same org, issuer, dependency group, or class could look like independent progress. rev0221 makes those failure modes visible and script-blocked.

## What changed

New surfaces:

- `tools/prepare_live_receipt_quorum_participation_record.py`
- `tools/audit_live_receipt_quorum_participation_record.py`
- `schemas/live-receipt-quorum-participation-record.schema.json`
- `examples/live-receipt-quorum-participation-record-rev0221-blocked-no-activation.json`
- `fixtures/negative-tests/quorum-participation-skipped-activation.json`
- `fixtures/negative-tests/quorum-participation-single-class-upgrade.json`
- `fixtures/negative-tests/quorum-participation-rollback-not-replayed.json`

Refactored surfaces:

- `tools/live_floor_lib.py`
- `tools/compute_live_receipt_floor.py`
- `tools/build_live_artifact_admission_graph.py`
- `tools/build_artifact_import_invariant_report.py`
- `schemas/live-receipt-floor-computed-snapshot.schema.json`
- `schemas/live-artifact-admission-graph.schema.json`
- `schemas/artifact-import-invariant-report.schema.json`
- `tools/audit_live_receipt_floor_activation_record.py`
- `tools/lint_archive.py`
- `tools/audit_schema_fixture_coverage.py`

## Operational rule

A candidate import now requires all of the following before it can be counted:

1. strict `actual-live-import` provenance;
2. replayed import-readiness gate object;
3. verified cryptographic adapter;
4. eligible floor-activation record;
5. eligible quorum participation record;
6. independence discount across dependency group, counterparty org, issuer key, and receipt class;
7. required-class recomputation;
8. challenge/rollback exclusion if contested.

The quorum participation record can only allow `may_enter_independence_discount: true`. It must keep `may_satisfy_cross_critical_quorum_by_itself: false`, `manual_live_floor_update_allowed: false`, `live_floor_delta_allowed_by_participation_record: false`, and `can_upgrade_reliance_by_itself: false`.

## Audit/refactor result

`tools/audit_live_receipt_quorum_participation_record.py` proves that:

- an activated gate without a quorum participation record is excluded;
- a gate with eligible activation plus eligible quorum participation can count only as one class-local control candidate;
- duplicate recheck omission blocks participation;
- challenge/rollback omission blocks participation;
- single-class quorum bypass blocks participation.

The archive still contains no genuine external artifact, verified response, live intake, actual live import, floor activation, quorum participation, quorum, or live-floor movement. The computed live floor remains zero and reliance remains stayed.
