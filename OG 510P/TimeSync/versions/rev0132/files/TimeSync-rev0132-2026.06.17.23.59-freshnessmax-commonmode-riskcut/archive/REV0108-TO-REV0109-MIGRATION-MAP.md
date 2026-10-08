# rev0108 to rev0109 migration map

rev0108 extracted transport capability advertisement semantics. rev0109 extracts aggregate revision-lineage semantics and closes compact-lineage / publication-cadence contradictions.

## Compatibility

No TimeState fields changed. No schema was expanded. Existing aggregate lineage records remain valid when lineage and publication-cadence metadata describe the same aggregate publication chain.

## New invalid cases

The following now fail semantic validation:

```text
aggregate revision-lineage publication_sequence differs from aggregate_privacy_controls.publication_cadence.publication_sequence
immediate-predecessor correction prior_aggregate_digest differs from publication_cadence.previous_publication_digest
present revision_chain_digest does not bind aggregate_publication_revision_chain
```

## Fixture normalization

Existing aggregate fixtures with immediate-predecessor correction lineage were normalized so:

```text
aggregate_revision_lineage.prior_aggregate_digest == aggregate_privacy_controls.publication_cadence.previous_publication_digest
```

when:

```text
previous_publication_sequence == publication_sequence - 1
```

## Files added

```text
tools/aggregate_lineage_semantics.py
examples/negative/aggregate-lineage-publication-sequence-mismatch-invalid.json
examples/negative/aggregate-lineage-immediate-predecessor-digest-mismatch-invalid.json
examples/negative/aggregate-lineage-revision-chain-wrong-bind-invalid.json
AUDIT-2026.06.13-rev0109.md
archive/REV0109-AUDIT-AGGREGATE-LINEAGE-REFACTOR.md
```

## Test additions

```text
TV-N295
TV-N296
TV-N297
DF-0109-001
DF-0109-002
DF-0109-003
```

The semantic vector suite grows from 313 to 316 vectors.
