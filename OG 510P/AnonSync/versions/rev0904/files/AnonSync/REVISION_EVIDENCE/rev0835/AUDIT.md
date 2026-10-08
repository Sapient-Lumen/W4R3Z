# Audit — AnonSync rev0835

## Boundary under review

Rev0834 proved bounded fresh-image output capture, but the remaining raw-fork
surface was still distributed: 15 calls in eight test translation units. Each
caller could independently decide when a PID became authority, whether a wait
was bounded, how a timeout killed descendants, when an output descriptor was
closed, and what `ECHILD` meant. Two supposed inheritance probes did not use
pre-fork application state at all.

The audit also found a subtle common-owner defect. On a normal leader exit, the
owners could reap the leader before terminating the rest of its process group.
That released the zombie/PID identity pin while descendants might remain alive.
A successful status was being accepted as if it were proof that the complete
owned process topology had ended.

## Corrected ownership model

`InheritedTestProcess` is the sole raw-fork implementation and a move-only
capability over leader PID, top-level process group, optional capture descriptor,
monotonic deadline, byte ceiling, kill, exact reap, and numeric-authority
relinquishment. Thirteen inherited-state spawn sites across seven consumers use
it. Nested probes stay in the outer group.

Both inherited and self-exec owners now observe a waitable leader with
`waitid(..., WNOWAIT)`, kill the still-identity-bound group, and then reap the
exact leader. `ECHILD` clears numeric authority before failure propagation.
Linux subreaper tests prove the exact lingering descendant is killed by
`SIGKILL` after a successful leader exit.

## Semantic reclassification

SQLite connection-affinity and owner-generation borrow/close campaigns created
all database state after their old fork. They now begin in pinned self-exec
images. This removes copied allocator, mutex, SQLite, and C++ runtime state
without weakening the facts under test. Tests that actually exercise inherited
capability rejection remain raw-inheritance probes.

The process-lineage pipe now carries only a typed PID/generation observation.
It no longer serializes the object representation of a capability type that is
deliberately non-trivially-copyable.

## Measured result

- production raw forks: **0**;
- test raw forks: **1 in 1 translation unit**;
- shared-owner inherited spawn sites: **13 across 7 consumers**;
- pinned fresh-image campaigns: **7**;
- inherited owner runtime: **20/20 checks**;
- self-exec owner runtime: **35/35 checks**;
- focused direct runtime: **491/491 checks**;
- owner/caller stress: **90/90 executions**; and
- changed/dependent structural audits: **277/277 checks**.

The source patch replays to all **211 active files**. GCC 14.2 builds every target.
The complete 122-test inventory passes in nine bounded final partitions. Nine
focused targets pass under GCC ASan/UBSan after the final lifecycle change.

## Claim boundary

Centralization makes ownership reviewable; it does not make arbitrary post-fork
C++ safe. The inherited callback remains a narrow test-only exception whose
semantics require copied process state. The owners do not prevent a hostile
child from escaping its group and do not provide pidfd, namespace, cgroup,
resource-limit, seccomp, Landlock, credential, or parent-death guarantees.
