# Rev0980 audit handoff

## Scope

Rev0980 prevents independently created or explicitly recovered replica SQLite databases from aliasing retention candidate and deletion-free-mark authority merely because their logical rows match. It remains deletion-free.

## Primary correction

Schema v7 mints one CSPRNG-derived database incarnation and one nonzero recovery epoch, binds both into the complete SQLite cutpoint, preserves exact v6 migration authority, and propagates lineage through retention candidate witness v2, writer-fenced page v2, and deletion-free mark v5. Foreign-database and pre-recovery requests fail before payload observation.

## Adjacent audit/refactor

The SQLite-owner source audit still treated schema v6 as the destination and initially rejected the correct v6-to-v7 migration. The oracle was upgraded to follow exact historical schemas, v7 publication, preserved pins, incarnation minting, and recovery-epoch regressions. The structural oracle was also refactored to follow the shared cutpoint-authority helper rather than requiring duplicated digest grammar in the wrapper.

A divergent local-control/service prototype and all source-divergent, interrupted, remount-lost, or stale-cache results were excluded. The accepted implementation was reconstructed from the exact sealed parent and independently patch-reapplied across the complete active projection.

## Nonclaim

Incarnation and recovery epoch live inside SQLite. Exact whole-image rollback restores both. Destructive retention still requires an external monotonic anchor, a mandatory operator recovery-epoch advance, or conservative reset of mark age whenever continuity is uncertain. No trusted-clock proof, quota decision, collection quarantine, reclaim, rename, or unlink is added.
