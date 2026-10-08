# rev0083 audit/refactor — aggregate correction authority validator seam

The rev0082 aggregate lineage validator had one growing function for correction, withdrawal, supersession, and reconciliation semantics.

rev0083 splits the newly introduced authority/notification/portability checks into:

```text
check_aggregate_correction_authority_reference(...)
```

and keeps lineage relationship checks in:

```text
check_aggregate_revision_lineage(...)
```

## Why

Correction lineage and correction authority fail differently:

- lineage failures concern prior digests, monotonic sequences, suppressed deltas, and reconciliation windows;
- authority failures concern authorization status, authority role, notification freshness, compatible-operator authority equivalence, and correction-chain portability.

Keeping these seams separate reduces validator drift as aggregate publication semantics continue to grow.

## Additional hardening

rev0083 also adds direct discovery validation for `aggregate_correction_authority_reference`, so discovery cannot become a bypass path for malformed authority or notification posture.
