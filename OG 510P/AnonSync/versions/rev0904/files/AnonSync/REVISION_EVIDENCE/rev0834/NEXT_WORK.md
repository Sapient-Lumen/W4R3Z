# Next work after rev0834

## 1. Bound inherited-process probes without erasing their semantics

The remaining 15 raw forks are exact inheritance or lineage probes, but several
parents still combine blocking pipes and waits. Extract a separate move-only
`InheritedTestProcess` supervisor that preserves raw inheritance while owning a
monotonic deadline, process-group kill/reap, and optional bounded capture. Do not
replace a test whose fact is inherited authority with self-exec.

## 2. Strengthen process identity ownership

Evaluate pidfds for race-resistant observation and a deliberate parent-death
contract for helpers. These should be capability improvements, not ambient
Linux assumptions. Keep fallback behavior explicit and tested.

## 3. Build the executable convergence algebra

Classify each durable transition as commutative/order-sensitive, idempotent or
single-use, monotone/retracting, causally dependent/independent, and
coordination-free/requiring. Differentially execute duplicate, reorder, loss,
partition, retry, concurrent update/delete, restart, and epoch-change traces
against the C++ implementation.

## 4. Build a crash-cut protocol oracle

Move beyond application-selected cuts. Interpose write, sync, truncate, WAL,
journal, rename, directory-sync, sidecar, and publication operations, then judge
SQLite state, receipts, snapshots, sidecars, and externally visible filesystem
effects with one domain recovery oracle.

## 5. Separate hostile artifact interpretation

Move hostile SQLite inspection into a disposable one-request worker with parent
wall-clock enforcement, CPU/address-space/file/descriptor limits, no-new-privileges,
and narrow seccomp/Landlock layers where available. Return a typed result rather
than a live database capability.

## 6. Specify privacy and key lifecycle

Write a threat/leakage matrix separating authentication, confidentiality,
anonymity, metadata hiding, forward secrecy, post-compromise recovery, device
enrollment, revocation, epoch rotation, backup, and secret erasure. The current
code does not prove that complete protocol.
