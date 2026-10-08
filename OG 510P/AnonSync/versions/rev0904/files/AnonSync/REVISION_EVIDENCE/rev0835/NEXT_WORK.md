# Next work after rev0835

## 1. Prototype pidfd-backed leader ownership

Build a Linux-only feature-detected experiment using `clone3(CLONE_PIDFD)` where
possible, with an explicit fallback. Compare wait, signal, timeout, external
reap, and PID-reuse behavior against the current owner. Keep process-group and
descendant ownership separate from the single-task pidfd claim.

## 2. Minimize the inherited callback frontier

Inventory every operation executed in the raw-fork child and classify it against
async-signal-safety. Precompute immutable contexts in the parent, replace
allocation/string/reporting paths with fixed-layout observations where feasible,
and retain self-exec for everything that does not require copied authority.

## 3. Split the largest selftest translation units

`src/sync_domain_selftests.cpp` remains about 9,000 lines and materially raises
compiler memory in this 4 GiB cloudtainer. Extract coherent corpora behind the
existing test-only library boundary, preserving exact registration and runtime
behavior while reducing peak compile memory and incremental rebuild waste.

## 4. Build the executable convergence algebra

Classify each durable transition as commutative/order-sensitive, idempotent or
single-use, monotone/retracting, causally dependent/independent, and
coordination-free/requiring. Differentially execute duplicate, reorder, loss,
partition, retry, concurrent update/delete, restart, and epoch-change traces
against the C++ implementation.

## 5. Build a crash-cut protocol oracle

Interpose write, sync, truncate, WAL, journal, rename, directory-sync, sidecar,
and publication operations. Judge SQLite state, receipts, snapshots, sidecars,
and externally visible filesystem effects with one domain recovery oracle.

## 6. Separate hostile artifact interpretation and specify privacy

Move hostile SQLite inspection into a disposable resource-bounded worker with
no-new-privileges and narrow seccomp/Landlock layers where supported. Separately
write the threat/leakage and key-lifecycle specification needed to distinguish
authentication, confidentiality, anonymity, metadata hiding, forward secrecy,
post-compromise recovery, revocation, backup, and erasure.
