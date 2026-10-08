# rev0111 audit — external transparency receipt semantics

## Targeted branch

The target was the external receipt reference branch inside `tools/validate_archive.py`, plus the discovery result path that can return `external_transparency_receipt_reference` values.

## Why this was worth doing

External transparency receipt references are deliberately compact. That makes digest-class accuracy important: if the digest fields bind the wrong artifact classes, the record looks externally anchored while the executable semantics are not actually bound to the aggregate statement, external checkpoint, or external receipt.

## Extracted helper

```text
tools/external_receipt_semantics.py
```

The helper now owns:

```text
external receipt non-upgrade boundary checks
validated statement digest class checks
validated checkpoint digest class checks
validated receipt digest class checks
```

## New fail-closed rules

```text
statement_digest -> aggregate_verifier_audit_summary
checkpoint_digest -> append_only_replay_log_checkpoint or private_log_checkpoint
receipt_digest -> external_transparency_receipt
```

## Fixtures

```text
DF-0111-001 -> external-receipt-statement-wrong-bind-invalid.json
DF-0111-002 -> external-receipt-checkpoint-wrong-bind-invalid.json
DF-0111-003 -> external-receipt-receipt-wrong-bind-invalid.json
DF-0111-004 -> discovery-external-receipt-wrong-bind-invalid.json
```

## Non-goals

rev0111 does not introduce:

```text
external transparency service semantics
monitor identity registry
receipt cryptographic verification
SCITT/CT/Rekor conformance profile
raw proof disclosure
provenance graph
```

It only makes existing compact digest-binding claims executable and consistent across aggregate and discovery-returned receipt references.
