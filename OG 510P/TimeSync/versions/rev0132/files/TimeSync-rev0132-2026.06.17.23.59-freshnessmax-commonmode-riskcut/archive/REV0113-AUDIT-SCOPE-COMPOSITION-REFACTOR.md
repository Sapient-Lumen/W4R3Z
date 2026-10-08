# REV0113 audit — scope-composition source binding refactor

## Problem

Scope-composition guards existed to prevent mixed-layer metadata from upgrading profile assessment, TimeState provenance, actionability, or lifecycle suppression. However, the validator still allowed a current guard to combine:

- `surface_decisions[*].source_digest` for one digest-bound artifact, and
- `temporal_coherence.input_observations[*].source_time_digest` for another artifact class or digest value.

That created a subtle freshness/identity split. The surface could be declared current, but the freshness timestamp might have observed a different object.

## Refactor

`tools/scope_composition_semantics.py` now owns:

- mixed-layer decision-matrix row completeness;
- guard non-upgrade boundary checks;
- required mixed-layer surface checks;
- current-surface source digest artifact-class checks;
- temporal source-digest alignment with current surface source digests;
- delegation to the shared temporal-coherence helper.

`tools/validate_archive.py` now imports the helper rather than keeping the scope-composition branch inline.

## New executable checks

For current scope-composition surfaces:

```text
surface_decisions[*].source_digest.binds must match the expected artifact class
input_observations[*].source_time_digest must equal the corresponding surface source_digest
```

Digest equality here means the same `algorithm`, `value`, and `binds` target.

## Fixture normalization

The existing rev0090 scope-composition fixtures had one inconsistent edge:

```text
surface = aggregate_lifecycle_rollup
surface source_digest.binds = aggregate_correction_authority_lifecycle_summary
temporal source_time_digest.binds = aggregate_lifecycle_decision_table
```

rev0113 aligns the temporal digest with the composed surface digest. The decision table remains checked where it belongs in aggregate lifecycle rollup validation; it is not used as the freshness identity for the current composed surface.

## Boundary preserved

No new registry, proof format, or provenance model was added. The change only binds existing current-use guard metadata to the same compact digest identity.
