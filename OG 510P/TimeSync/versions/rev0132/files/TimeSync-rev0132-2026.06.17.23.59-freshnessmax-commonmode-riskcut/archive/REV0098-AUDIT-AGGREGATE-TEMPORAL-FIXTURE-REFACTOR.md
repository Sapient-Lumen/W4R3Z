# rev0098 audit — aggregate temporal and fixture-derivation refactor

rev0098 continues FT-0090 with executable validation work only.

## What was risky

Aggregate verifier audit summaries carry both a publication time and a later record-created/check time. Prior checks used the latter to bound nested lifecycle and notification evidence, but did not prove the publication time itself was not after that artifact/check time.

That is a small ordering hole, but it matters because aggregate summaries are already compact and privacy-preserving. The archive should reject impossible artifact timing without adding more external registry machinery.

## What changed

`tools/aggregate_temporal.py` now owns aggregate publication-time checks:

```text
aggregate verifier audit issued_at <= aggregate_record_created_at
aggregate period start < aggregate period end
```

`tools/validate_archive.py` delegates to this helper from replay-transparency audit validation.

## Fixture strategy

`examples/negative/aggregate-issued-after-created-invalid.json` is generated from a positive discovery/replay-transparency fixture by one explicit patch operation. The rendered JSON remains present for review, while `tests/fixture-derivations.yaml` proves it has not drifted from its declared mutation.

`tools/fixture_derivations.py` also now rejects duplicate derivation IDs and duplicate output targets.

## What did not change

rev0098 does not change the TimeState core, profile conformance rules, transport adapter semantics, evidence classes, digest canonicalization policy, or any schema ID. Aggregate artifact-time metadata still cannot update TimeState freshness, profile assessment, or current actionability.
