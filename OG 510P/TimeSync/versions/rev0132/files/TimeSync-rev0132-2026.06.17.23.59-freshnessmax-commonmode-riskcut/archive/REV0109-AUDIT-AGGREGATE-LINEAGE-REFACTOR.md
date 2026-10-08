# rev0109 audit — aggregate revision-lineage semantics

## Finding

Aggregate revision-lineage validation still lived largely inline in the monolithic validator, and it did not cross-check publication-cadence metadata even though both surfaces describe the same aggregate publication chain.

The concrete defect was visible in positive fixtures: immediate-predecessor corrections had:

```text
previous_publication_sequence = publication_sequence - 1
```

but the lineage `prior_aggregate_digest` and publication-cadence `previous_publication_digest` used different digest values. A consumer could therefore see two compact references to two different prior aggregates for the same correction step.

## Refactor

Added `tools/aggregate_lineage_semantics.py` and routed aggregate revision-lineage validation through it. The helper owns lineage boundary/status/sequence/digest/reconciliation semantics and has a standalone self-test.

`tools/validate_archive.py` now keeps only the aggregate summary routing and correction-authority reference call around this branch.

## Negative coverage

Added three rendered fixtures, all patch-derived from the positive aggregate revision-lineage discovery example:

```text
DF-0109-001 -> aggregate-lineage-publication-sequence-mismatch-invalid.json
DF-0109-002 -> aggregate-lineage-immediate-predecessor-digest-mismatch-invalid.json
DF-0109-003 -> aggregate-lineage-revision-chain-wrong-bind-invalid.json
```

This preserves human-reviewable JSON while making copy drift visible to validation.

## Non-goals

rev0109 does not:

```text
create a correction-authority registry
turn aggregate lineage into a publication repository
export verifier identities or individual result identifiers
define correction workflow state beyond the existing compact lineage vocabulary
```

The improvement is an internal consistency guard: lineage and cadence metadata cannot quietly describe different aggregate publication chains.
