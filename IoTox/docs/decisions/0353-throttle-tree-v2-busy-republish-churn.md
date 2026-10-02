# ADR 0353: Throttle tree-v2 busy republish churn

- Status: accepted and implemented
- Date: 2026-09-09

## Context

ADR 0341 made Linux source-tree changes wake sync automation immediately, and ADR 0342 added a
250 ms non-sliding debounce while preserving changes observed during an active publish. The next
current-tree near-ceiling Sandwurm comparison found a new scale failure mode:

- cap 4 remained correct and fast enough, with 3,500 files converging in 386.718 seconds of
  capacity catch-up on source revision `f0f0145ddab85e3a28dd92426b0be4b68d43f0f7`;
- cap 8 reduced file commit batches from 875 to 438 per follower but regressed to 1,084.185 seconds
  of capacity catch-up;
- the regression correlated with full CAS inventory scans increasing from 7/11 to 74/81 and
  inspected objects increasing from 9,643/13,503 to 160,198/158,813.

That was not a correctness failure. Both runs converged, repaired, retained all branches, preserved
the three-way conflict lifecycle, and drained retired transfer state. It was a churn failure:
source-watch changes observed while the publisher was already busy could mature immediately after
the busy publish completed. With the near-ceiling harness' intentionally aggressive automation
interval, that created too many intermediate published heads and too many follower pull jobs.

## Decision

Keep the signed automation policy, namespace policy, peer frames, branch records, manifests, and
authority model unchanged. Add only a runtime scheduling rule:

- the Agent passes a 5,000 ms busy-republish delay when a source-watch event belongs to a tree-v2
  namespace;
- `SyncAutomationScheduler::trigger_source_change()` retains that delay alongside the existing
  pending source-publish due time, taking the maximum delay if several events arrive before the
  pending publish is claimed;
- when a publish completes with a delayed tree-v2 source publish still pending, the pending due time
  is clamped to at least `completion_time + delay`;
- for `publish` and `writable` modes, a delayed pending source publish suppresses an earlier normal
  periodic publish wake-up;
- for `bidirectional` mode, remote-source pulls may still run on their independent round-robin peer
  clocks while the local source republish cools down.

The direct scheduler API still defaults to a zero busy-republish delay. Non-tree-v2 engines keep the
existing 250 ms debounce and periodic behavior.

## Consequences

Large tree-v2 write bursts should publish fewer intermediate heads while the source is still being
populated. The cost is bounded latency: a source change that arrives during an active tree-v2 publish
may wait up to the 5-second cooldown before the next local source publish/reconcile attempt. That is
acceptable for bulk tree synchronization, and it is intentionally scoped away from Ratox/control
latency.

The cooldown is not a transfer protocol fix. It does not bundle objects, transfer object ranges,
make projection incremental, trust stale CAS inventories, or make cap 16+ lane widths safe by
itself. The post-fix cap-16 run still regressed to 1,271.565 seconds of capacity catch-up with
90/111 full scans and 20/39 late-offer cancellations. For the current 2-vCPU/2-GiB Sandwurm profile,
cap 8 is the measured lane-width sweet spot and cap 16 is a negative scaling proof.

## Evidence

Accepted local checks:

```text
nix develop -c bash -lc 'cmake --build build -j2 && ctest --test-dir build -R "^(iotox\.unit-and-integration)$" --output-on-failure'
nix develop -c bash -lc 'ctest --test-dir build -R "^(iotox\.sync-three-writer-sandwurm-verifier|iotox\.sync-tree-process|iotox\.sync-publication-process)$" --output-on-failure'
```

Post-commit source revision `5203d7bd43a404682c6770fed282f29640fb0342` was then qualified in the
networkless Sandwurm three-writer near-ceiling profiles:

| Cap | Compact proof | Capacity catch-up | Full scans | Result |
| ---: | --- | ---: | ---: | --- |
| 4 | `.sandwurm/exports/three-writer/run.Ed6ZvJvG` | 512.569 s | 0 / 3 / 9 | accepted, slower than cap 8 |
| 8 | `.sandwurm/exports/three-writer/run.BKxk74nS` | 480.819 s | 0 / 23 / 25 | accepted, current sweet spot |
| 16 | `.sandwurm/exports/three-writer/run.EFQ2DS2A` | 1,271.565 s | 0 / 90 / 111 | accepted negative proof |

All three compact exports independently pass `verify-three-writer` and
`verify-sandwurm-vm-smoke.py`.

The exact receipt table lives in `docs/evidence/2026-09-09-sync-tree-v2-busy-republish.md`.
