# 0397 — Retain final-restart long-soak rejection

Date: 2026-09-22

Status: accepted

Current note: ADR 0403 refreshes the current accepted `sync.long-soak` proof
to `.sandwurm/exports/three-writer/run.2nPKtCoX`. This ADR remains the record
for the retained `run.WAb1ARs9` rejection and the historical
`run.9nqvO8B2` acceptance it did not demote at the time.

## Context

The post-ADR 0377 same-host KVM/ext4 long-soak proof
`.sandwurm/exports/three-writer/run.9nqvO8B2` remains the accepted sync
long-soak evidence for the current stable gate: it completed 289 writable
cycles over more than 24 hours with restart-settle, repair, recovery, and
maintenance subproofs.

A later 24-hour candidate,
`.sandwurm/lab/three-writer-soak-24h/run.WAb1ARs9`, used the same
representative profile and ran deep enough to exercise a harder tail. It
crossed the 24-hour wall-clock floor, converged 287 writable cycles, rotated
12 scheduled daemon restarts, completed 11 restart-settle passes, completed 28
repair passes, deferred 11 repairs across scheduled restarts, and recovered 5
stalled cycles. It then rejected at the final scheduled restart before cycle
288 could be counted complete.

The rejected receipt reports:

- `status=rejected`;
- `soak_cycles=287`;
- `soak_minimum_cycles=288`;
- `soak_elapsed_ms=113271153`;
- `soak_daemon_restarts=12`;
- `soak_restart_settle_passes=11`;
- `soak_repair_passes=28`;
- `soak_repair_deferrals=11`;
- `soak_stalled_cycle_recoveries=5`; and
- failure class `c sync-repair field-notes failed: IoTox control response deadline elapsed`.

The failure is content-free and hash-bound as
`ba59bd2daff3a30c91a7111552018622856c4e88285c7ac98f15faad4c8dc29f`.
The partial projections still matched across all three nodes, with 3 branches
per node, 512 capacity files per node, zero conflict alternatives, and
identical final soak projection hashes.

## Decision

Retain `.sandwurm/exports/three-writer/run.WAb1ARs9` as a verified rejected
proof, not as stable long-soak acceptance.

The compact export is intentionally content-free and small:

- proof root: `.sandwurm/exports/three-writer/run.WAb1ARs9`;
- status: `rejected`;
- compact manifest SHA-256:
  `185b581843445f0fd0511eb4b685aada0adf5c22103f21d9a6f6db3f5599e655`;
- total exported bytes: `79675`; and
- exported file count: `4`.

The dedicated three-writer verifier accepts both the raw and compact rejected
proof. The generic VM-smoke verifier is not applicable to this compact export,
because the three-writer compact export deliberately keeps only the minimal
three-writer evidence and does not carry `vm-smoke.json`.

This rejection does not demote the accepted `run.9nqvO8B2` gate. It does,
however, define the next sync frontier: final scheduled-restart repair near the
minimum-cycle boundary must become boring. A future accepted repeat should
either complete this same final-restart pattern or deliberately alter the
representative profile with a new ADR.

## Consequences

The long-soak gate remains accepted by `run.9nqvO8B2`, but the newer
`run.WAb1ARs9` result proves that the tail still has a sharp edge. Stable
release evidence must continue to cite an accepted long-soak proof, not this
rejected candidate.

Operators should read "24 hours elapsed" as necessary but insufficient: the
representative sync soak also has a minimum-cycle floor. ADR 0396's follow-up
status-tool change now reports wall-clock remaining and acceptance remaining
separately so this distinction is visible during live runs.

The outer Sandwurm wrapper stayed alive after the IoTox-specific rejected
receipt was written. A clean `ch-remote shutdown-vmm` caused it to write
`direct-cloud-hypervisor-live-chain.json`, after which the dedicated verifier
and compact exporter worked normally. That wrapper behavior is an operator
ergonomics issue, not an IoTox sync acceptance.

## Validation

```sh
./tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.WAb1ARs9

./tools/iotox-sandwurm-lab.sh export-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.WAb1ARs9

./tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/exports/three-writer/run.WAb1ARs9
```

The verifier output classifies the compact proof as:

```text
schema=iotox.sync-three-writer-sandwurm-verification.v1
status=rejected
partial_soak_cycles=287
partial_soak_restart_settle_passes=11
partial_soak_stalled_cycle_recoveries=5
contains_secrets=false
```
