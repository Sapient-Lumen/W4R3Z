# Whole-VMM tree-v2 post-exchange power-cut evidence — 2026-09-04

## Result

One source-linked, networkless Sandwurm campaign passed the second workspace linearization. The
guest double-read an unchanged signed pending workspace around a visible projection marker naming
the pending manifest. Raw phase byte 2 and a still-present exchanged stage directory were both bound
into the arm before the host sent `SIGKILL` to the exact task-owned Cloud Hypervisor process.

A distinct second kernel booted a reflink of the exact crash disk. Before any Agent started, all
three writers exposed the completed tree; the interrupted follower retained pending phase byte 2,
its pending projection marker, and the old projection in the stage path. Startup recovery removed
that old side, stabilized the journal, preserved all identities, retained three branches per node,
and passed exact convergence and repair.

Together with the pre-exchange result in
[`2026-09-04-sync-whole-vmm-power-cut.md`](2026-09-04-sync-whole-vmm-power-cut.md), this qualifies both
durable sides of the tree-v2 workspace directory exchange on the construction VM stack. It does not
qualify other transaction boundaries, physical or dishonest storage, or sole-copy use.

## Reproduction

```sh
./tools/iotox-sandwurm-lab.sh up-sync-power-cut post-exchange
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/lab/sync-power-cut-post-exchange/run.nhjaizl2
./tools/iotox-sandwurm-lab.sh export-sync-power-cut \
  .sandwurm/lab/sync-power-cut-post-exchange/run.nhjaizl2
./tools/iotox-sandwurm-lab.sh verify-sync-power-cut \
  .sandwurm/exports/sync-power-cut/run.nhjaizl2
```

## Bound identities

```text
source Git commit:  bb0dc88b20ed1170aea9e236a3fb15d14e3b9e19
product:            IoTox 0.47.0 rev0047
binary SHA-256:     8e62c38c7a042e6f5f1be4126dd20d9b9c5b5d697fcf25efd6b404022157a81e
substrate:          Cloud Hypervisor / KVM, 2 vCPU, 2 GiB, network class none
root image:         24-GiB sparse task-owned disk
first VMM PID:      1286632
first VMM start:    2012430 Linux clock ticks
first VMM exit:     137; ch-remote exit control false
second VMM PID:     1287780
second VMM exit:    0; ch-remote exit control true
copy method:        cp-reflink-always-sparse-auto
campaign elapsed:   477636 ms
```

The two SHA-256-only boot identities differ. The first VMM PID, `/proc` start time, NUL-delimited argv
hash, and exact writable-disk argument match Sandwurm's terminal launch receipt.

## Boundary and recovery

```text
prior:                  17 files, 1 directory, 65563 bytes
prior SHA:              f678f55be7b21ee7d42771ec16d07e22203978f463a70f54d294a476b0343a88
completed:              18 files, 1 directory, 33619995 bytes
final SHA:              e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d
requested/observed:     post-exchange-pending
arm journal:            pending, raw phase 2
arm visible marker:     pending manifest
arm stage:              present
offline views:          completed, completed, completed
recovered journal:      pending, raw phase 2
recovered marker/stage: pending / present
recovery:               1631 ms; branches 3/3/3; repairs 3
```

This is the unambiguous post-`RENAME_EXCHANGE` side: before rename, the stage contains the pending
tree and the visible marker names active; after rename, the visible marker names pending and the
stage contains the old active tree. Both stage and journal survived the VMM cut, so startup exercised
the recovery branch that validates and removes the old projection before committing stable state.

## Compact proof

```text
proof:             .sandwurm/exports/sync-power-cut/run.nhjaizl2
manifested bytes:  139366
allocated bytes:   221184
campaign SHA-256:  fac3a4225b91d803660425b2125040c1f8710d4a044f20a37ee34ea50b65fc24
manifest SHA-256:  f163743ff7c4a8e82232e78b9ba6efaa29dcd0b0bffa483115331d2a5d8e3ea4
contains secrets:  false
```

The v3 verifier checks the exact ten-file closure and digests, requested/observed boundary,
projection orientation, raw phase encoding, stage booleans, offline completed-only result, recovered
journal/marker agreement, source and binary identity, VMM process binding, noncooperative first exit,
normal second exit, networkless launches, distinct boots, crash-image lineage, branches, and repairs.

## Remaining boundary

The two workspace sides do not cover object temporary creation/rename, branch-record commit,
freshness-witness transitions, record corruption, open descriptors into the old directory, cold or
near-ceiling populations, randomized repetition, physical power removal, or storage that lies about
flushes. Those remain explicit roadmap gates. Independent backup and restore practice remains
mandatory for precious data.
