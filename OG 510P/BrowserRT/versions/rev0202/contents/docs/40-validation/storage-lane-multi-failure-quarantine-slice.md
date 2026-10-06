# Storage-lane multi-failure quarantine slice — rev0073

## Purpose

`rev0073` hardens the late-provider failure quarantine introduced in `rev0070`. A single timed-out provider failure was already quarantined; this slice proves that multiple late failures remain separate review items and that recovery is not reopened by an accidental broad clear.

## Executable proof

```bash
node tools/storage_lane_multi_failure_quarantine_probe.mjs --json artifacts/validation/REV0073-STORAGE-LANE-MULTI-FAILURE-QUARANTINE-PROBE.json
```

The proof schedules two storage-lane provider operations, dispatches both before the storage lane is marked unhealthy, lets both time out as `BRT_STORAGE_OPERATION_TIMEOUT`, then releases both providers so they reject later as `BRT_OPFS_OPERATION_FAILED`.

## Earned behavior

The slice checks that both late failures remain present as separate `failedTimedOutOperations`; `clearFailedTimedOutOperations()` rejects unreviewed clears with `late-failure-clear-review-required`; reviewed clears without either `opId` or `allowLaneWide: true` reject with `late-failure-clear-scope-required`; clearing only one failure keeps recovery blocked with `timed-out-operation-late-failure`; and recovery succeeds only after both failed timed-out operations are explicitly reviewed and cleared.

## Runtime hooks

```text
storage-lane:late-provider-failure-clear-rejected
lateProviderFailureClearRejected
reviewedLateProviderFailures
reviewToken
allowLaneWide
late-failure-clear-review-required
late-failure-clear-scope-required
```

## Non-claims

This is not cancellation, rollback, no-mutation, exactly-once, provider interruption, automatic recovery, production authorization, or cross-browser evidence. It does not prove quota survival, eviction survival, crash recovery, OPFS durability, persistent-storage retention, throughput, latency, SLOs, or production readiness. Review tokens in this slice are maintenance-review evidence only.
Scoped review is required; every clear must be reviewed and scoped by opId unless allowLaneWide is explicitly true.
