# Audit — rev0111 external transparency receipt binding refactor

rev0111 continues FT-0090 with executable validation work only. The six-field TimeState core is unchanged.

## What was risky

External transparency receipt references were compact and intentionally non-operational, but the validator only partially enforced the digest classes behind a validated receipt.

The highest-risk path was not a missing transparency-log verifier. It was simpler: a record could say `receipt_validation_status = validated` while one of the digest-looking fields bound the wrong artifact class. That makes a compact external receipt look usable while actually pointing at a scope guard, retained record, or aggregate batch instead of the statement/checkpoint/receipt object the semantics depend on.

A second concrete bypass existed through discovery. `external_transparency_receipt_reference` could be returned as a byte-envelope discovery result, but that nested value did not receive the same semantic checks as an aggregate embedded reference.

## What changed

New helper:

```text
tools/external_receipt_semantics.py
```

Moved out of `tools/validate_archive.py`:

```text
external_transparency_receipt_reference boundary checks
validated receipt checkpoint/receipt digest checks
```

New executable checks:

```text
validated external receipt requires statement_digest binding aggregate_verifier_audit_summary
validated external receipt checkpoint_digest must bind append_only_replay_log_checkpoint or private_log_checkpoint
validated external receipt requires receipt_digest binding external_transparency_receipt
discovery-returned external_transparency_receipt_reference values are semantically checked
```

## New regression fixtures

```text
examples/negative/external-receipt-statement-wrong-bind-invalid.json
examples/negative/external-receipt-checkpoint-wrong-bind-invalid.json
examples/negative/external-receipt-receipt-wrong-bind-invalid.json
examples/negative/discovery-external-receipt-wrong-bind-invalid.json
```

Each is derivation-checked from a positive fixture through `tests/fixture-derivations.yaml`.

## Boundary intentionally preserved

rev0111 does not add a transparency log, monitor registry, receipt-verification protocol, SCITT/CT/Rekor implementation, proof-disclosure format, or provenance graph. It only makes existing compact digest claims fail closed when they bind the wrong artifact class.

## Remaining risk

FT-0090 remains open. The remaining high-value work is continued validator decomposition and fixture-family derivation where it prevents real copy drift.
