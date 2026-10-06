# Cube audit rev0026

Revision: rev0028

This revision adds a runtime slice and an audit/factor pass, but keeps the broad release gate browser-light.

## What was audited

- `PersistedSpillMailbox` retained-ref accounting.
- `compact-delete` journal/recovery coherence.
- Manifest task metadata for the new proof and audit.
- Impact-map coverage for source, probe, audit, and docs.
- Surface-inventory coverage.
- Non-claim legibility in the charter and future-session office manual.
- Release-tier browser-light policy.

## Found and fixed

- Current office surfaces still talked as if rev0025's scheduler model walk were the current slice. They now describe rev0026's persisted-spill compaction stair while retaining scheduler-model non-claims.
- `src/types.d.ts` did not expose the new `compact()` method. It now does.
- The persisted-spill recovery frontier lacked a current retention/compaction document. Rev0026 adds one instead of overloading the recovery doc.

## Remaining caution

The cube is still artifact-rich. Future sessions should keep cheap fake/model slices in release and leave browser/OPFS/CDP work explicit by tier/id unless a turn specifically budgets for it.
