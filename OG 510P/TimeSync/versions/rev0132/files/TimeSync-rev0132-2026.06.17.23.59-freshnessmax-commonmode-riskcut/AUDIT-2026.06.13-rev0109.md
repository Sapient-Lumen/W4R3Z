# Audit — rev0109 aggregate lineage cadence refactor

rev0109 continues FT-0090 with executable validation work only. The six-field TimeState core is unchanged.

## Risk selected

The next riskiest remaining branch was aggregate revision lineage. Correction lineage and aggregate publication cadence both describe the same aggregate publication chain, but before rev0109 they were validated largely independently.

The dangerous cases were small but concrete:

```text
aggregate_revision_lineage.publication_sequence != aggregate_privacy_controls.publication_cadence.publication_sequence
```

and, for immediate-predecessor corrections:

```text
aggregate_revision_lineage.prior_aggregate_digest != publication_cadence.previous_publication_digest
```

A third gap was that `revision_chain_digest`, when present, was not checked for the correct artifact class binding.

These are not new policy questions. They are internal consistency checks for compact lineage metadata that already existed.

## Executable change

Added:

```text
tools/aggregate_lineage_semantics.py
```

The helper now owns:

```text
lineage boundary flags
original / corrected / withdrawn / superseded / reconciled status checks
prior aggregate digest checks
publication sequence checks
publication-cadence cross-checks
revision_chain_digest binding checks
reconciliation boundary and chain-head checks
```

`tools/validate_archive.py` now delegates this concern family to the helper and keeps only the surrounding aggregate-summary routing plus correction-authority reference call.

## Fixture correction

While adding the cross-check, existing aggregate fixtures exposed a real inconsistency: many immediate-predecessor corrections had `previous_publication_sequence = publication_sequence - 1`, but `prior_aggregate_digest` and `publication_cadence.previous_publication_digest` contained different placeholder digests.

rev0109 normalizes those fixtures so the two compact surfaces point at the same immediate predecessor.

## New negative coverage

Added three derivation-checked negatives:

```text
examples/negative/aggregate-lineage-publication-sequence-mismatch-invalid.json
examples/negative/aggregate-lineage-immediate-predecessor-digest-mismatch-invalid.json
examples/negative/aggregate-lineage-revision-chain-wrong-bind-invalid.json
```

Added semantic vectors:

```text
TV-N295
TV-N296
TV-N297
```

Added fixture derivations:

```text
DF-0109-001
DF-0109-002
DF-0109-003
```

## Boundary preserved

rev0109 does not add:

```text
correction workflow engine
publication repository
verifier registry
provenance graph
suppressed-delta export
individual replay-result reconciliation
```

The new checks keep lineage metadata internally coherent; they do not turn aggregate correction lineage into proof material or current individual replay visibility.

## Remaining work

FT-0090 should remain open. The next pass should continue the same discipline: extract validator concern families only when it makes existing executable behavior smaller, more testable, or harder to misuse.
