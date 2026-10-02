# ADR 0361: Duration-bound sync soak and retained recovery drill

- Date: 2026-09-10
- Status: accepted

## Context

The three-writer sync construction already covered graph convergence, read/write sharing, capacity,
conflict resolution, maintenance lifecycle, and node-loss/all-live-node recovery. The remaining
graduation gates need two reusable mechanisms:

1. a wall-clock writable soak that can become a real 24-hour evidence cell instead of only a fixed
   successor-cycle count; and
2. a compact recovery receipt that operators can retain with an independently selected backup
   generation without storing paths or contents.

ADR 0360 made backup provenance labels recordable by `sync-recovery-verify`, but the Sandwurm
follow-up still emitted only absent provenance and there was no wrapper for a normal operator drill.

## Decision

`tools/run-sync-three-writer.py` now accepts:

```sh
--soak-seconds SECONDS
--soak-minimum-cycles COUNT
--soak-cycle-delay SECONDS
--soak-restart-every N
--soak-repair-every N
--soak-repair-restart-policy defer|coincident
--sync-repair-control-timeout-ms MS
```

The soak rotates writes across all three writers, toggles a deleted/restored marker, optionally
restarts daemons, optionally runs repair passes, and requires all ordinary worktrees to converge with
three branches and no conflicts after every cycle. Its content-free receipt records elapsed time,
cycle count, delete cycles, restart/repair counts, timing bounds, high-water RSS, and a final digest
commitment.

The Sandwurm flake now exposes two reproducible profiles:

```sh
tools/iotox-sandwurm-lab.sh up-three-writer soak-smoke
tools/iotox-sandwurm-lab.sh up-three-writer soak-24h
```

`soak-smoke` is a short construction check. `soak-24h` is the real graduation command and must not be
documented as passed until an accepted 24-hour proof is retained.

`tools/run-sync-retained-recovery-drill.py` wraps `iotox sync-recovery-verify`, requires the strict
no-live-state/no-overclaim report fields, validates all-or-none operator provenance labels, and
writes `iotox.sync-retained-recovery-drill.v1` with report SHA-256, label SHA-256 values, manifest
digests, counts, byte totals, and root-device observation. The node-loss recovery rehearsal also
passes concrete same-VM drill labels in the Sandwurm follow-up and requires those labels to be bound
into all four restore-verifier reports.

## Consequences

This closes the mechanism gap for the next sync trust work. It does not close the 24-hour gate by
itself, does not prove that same-VM backup labels name an independent failure domain, and does not
make IoTox a backup. A real graduation receipt still needs an independently retained,
immutable/versioned backup generation and an accepted 24-hour run.
