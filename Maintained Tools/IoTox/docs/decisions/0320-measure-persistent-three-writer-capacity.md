# ADR 0320: Measure persistent three-writer synchronization capacity

- Status: accepted and implemented
- Date: 2026-09-03

## Context

The founding three-writer gates proved causal convergence and lifecycle semantics with small trees.
ADR 0319 and the first capacity controls measured a near-ceiling source and a 4,096-file structural
path on tmpfs, but did not measure durable-media amplification, three-node catch-up, repair, or
memory in the real full-mesh service.

The existing Sandwurm harness also used `sync-repair` as a 10 Hz liveness predicate. Because the
predicate short-circuited at the first incomplete node, the observer could monopolize that node's
local control/event loop and prevent the Tox progress it was trying to observe.

## Decision

Extend `run-sync-three-writer.py` with an optional bounded capacity phase. It creates deterministic
private regular files beneath one writer, waits for exact content/mode agreement at all three
worktrees, then runs one explicit authenticated repair per node. The content-free receipt records
file count and size, logical bytes, a canonical tree digest, catch-up time, repair time per node,
Agent `VmHWM`, and allocated-byte delta per node. The phase is disabled unless both capacity
arguments are present and refuses more than 3,500 files, 1 MiB per file, or 56 MiB total.

Liveness polling counts only canonical 64-hex `.branch` frontier filenames in the managed store.
That count is an observer hint, not an integrity assertion. Explicit `sync-repair` remains at the
capacity checkpoint, and the later semantic assertions still require exact worktree bytes,
conflict alternatives, checkpoint propagation, quarantine/restore, and writer cutoff.

The retained default VM cell uses fresh state, a persistent ext4 disk, 2 vCPUs, 2 GiB RAM, and 512
files of 16,384 bytes each. It preserves the existing three-way offline conflict, 24 alternating
writer edits, and maintenance lifecycle.

## Consequences

The accepted cell transferred 8,388,608 logical bytes, converged all three worktrees, passed repair,
and recorded about 20--22 MiB of allocated-state growth per node and 16--18 MiB Agent high-water
RSS. The clean-source fresh-state catch-up was 70.997 seconds and the complete campaign passed in
269.284 seconds without restart. A prior byte-identical-binary cell took 130.219 seconds and
418.235 seconds respectively, crossed one watchdog under ext4 journal pressure, and exercised ADR
0322's restart recovery.

This closes the first persistent three-node capacity measurement, not the full representative-
capacity or precious-data gate. It does not cover a near-ceiling 53 MiB population, cold-cache
repetition, 4,096 files across three stores, conflict amplification at that size, 24-hour operation,
power loss, ENOSPC/read-only transitions, hardware durability, or independent machines. The harness
still uses same-host guests and a private loopback Tox topology.
