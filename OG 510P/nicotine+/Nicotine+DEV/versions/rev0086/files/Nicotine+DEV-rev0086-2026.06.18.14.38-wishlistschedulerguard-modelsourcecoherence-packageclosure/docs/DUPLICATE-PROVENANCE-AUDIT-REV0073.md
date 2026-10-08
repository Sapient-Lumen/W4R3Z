# Duplicate provenance audit — rev0073

## Question

Rev0072 proposed manifest-driven duplicate deletion after resolving a packet. Rev0073 tested that proposal against the U-123 family while also replacing the active copied-fixture tests with a readable shared harness.

## Result

The active rev0073 U-123 files are now unique; they were deliberately refactored rather than kept byte-identical to the old packet. Historical exact duplicates still remain:

```text
collision-rejection historical group: 3 copies × 9,420 bytes
identity-guard historical group: 2 copies × 9,433 bytes
exact duplicate groups: 2
rows belonging to duplicate groups: 5
safe deletions identified: 0
```

The copies occur under the byte-preserved rev0072 archive and revision-scoped rev0048/rev0062 handoff paths. Their paths encode separate provenance contracts.

## Why hash-only deletion is unsafe

```text
docs/archive/rev0072-active-u123/
  preserves the exact rev0072 active packet that rev0073 superseded

handoff/rev0048/...
handoff/rev0062/...
  preserve self-contained exports from those revisions

maintainer_artifacts/u123/
  contains the new readable and role-classified rev0073 artifacts
```

Deleting one historical copy would save bytes but weaken an old bundle's self-contained meaning and could invalidate references or manifests. Byte identity is therefore necessary but not sufficient evidence of semantic redundancy.

## Revised compaction rule

Delete an exact duplicate only when it is also:

```text
- provenance-equivalent;
- unreferenced by current and historical navigation/manifests;
- deterministically reproducible from a declared canonical source;
- removable without weakening a revision-scoped handoff;
- covered by a before/after manifest and link audit.
```

The historical U-123 groups do not meet that rule. The high-value optimization this turn was to refactor the active surface while preserving old evidence.

## Machine-readable audit

```text
data/rev0073_u123_duplicate_semantics.csv
data/rev0073_u123_duplicate_semantics.json
data/rev0073_research_boundary_summary.json
```

The corrected boundary audit found 321 historical files containing legacy readiness language across 329 inventory rows. Those occurrences are inventoried, not silently rewritten. Current entrypoints are policy-gated as research-only. The initial construction audit counted its own outputs; `docs/SELF-REFERENTIAL-AUDIT-REFACTOR-REV0073.md` records the idempotence correction.

## Future compaction target

A future deletion pass should begin with derived indexes or repeated generated inventories that have no revision contract, no unique references, and a deterministic regeneration command. That is a safer target than immutable handoff evidence.
