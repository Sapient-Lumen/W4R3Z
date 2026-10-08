# Rev0847 next work

## 1. Classify every callback and user-data owner

Search all C/C++ registration sites that retain an application pointer:
SQLite hooks and authorizers, OpenSSL callbacks, C library comparators, thread
entry contexts, signal-adjacent hooks, and test process callbacks. For each,
record lifetime owner, process/thread authority, detach order, reentrancy,
exception policy, and synchronization. Prefer a generated inventory consumed by
one semantic audit over multiple hand-maintained counts.

The immediate candidate is the remaining SQLite callback surface. The rev0847
budget fix should become a reusable callback-context owner pattern only after
comparing differing callback contracts; blindly copying fail-stop affinity may
be wrong for intentionally shared or reentrant hooks.

## 2. Make shared execution explicit

Exact-thread affinity is appropriate for owners that must never transfer. Where
product behavior needs cross-thread work, introduce a serialized executor or
message-passing owner whose queue, shutdown, and callback lifetime are explicit.
Do not weaken thread checks merely because SQLite FULLMUTEX prevents simultaneous
connection entry.

Add model tests for shutdown races: queued operation versus detach, callback in
flight versus owner destruction, process fork versus executor thread loss, and
exception/cancellation during callback registration replacement.

## 3. Turn convergence into executable semantics

Define a compact reference model for create, update, delete, recreation, rename,
concurrent mutation, schema epoch, key epoch, and externally visible effects.
Classify each operation by idempotence, commutativity, monotonicity, causal
requirements, and required coordination. Generate duplicated, reordered,
partitioned, concurrent, retried, and restarted histories; compare the C++ state
and emitted effects with the model.

Until this exists, “convergence engine” remains an architectural direction rather
than a tested distributed property.

## 4. Build one cross-resource crash oracle

Compose SQLite commit/WAL/checkpoint state, local JSONL publication, temporary
files, directory sync barriers, recovery receipts, and downstream effects into
one cutpoint state machine. Enumerate legal durable prefixes and reject states
that independently valid subsystem tests currently fail to relate.

## 5. Isolate hostile interpretation

Move hostile SQLite/document parsing into disposable workers receiving only
sealed descriptors and bounded requests. Enforce CPU, memory, wall-clock,
output, descriptor, filesystem, namespace, and syscall limits. Treat seccomp or
filesystem restrictions as layers, not as a complete sandbox.

## 6. Specify privacy, devices, and keys

Define payload encryption, device membership and generations, key epochs,
rotation, revocation, state-loss recovery, forward secrecy, post-compromise
recovery, metadata leakage, traffic analysis, backup custody, rollback
resistance, and realistic erasure limits. Authentication and local ledger
integrity do not establish anonymity.

## 7. Reduce change amplification

Extract invariant-owned production libraries from `sync_domain.cpp` and replace
large selftest aggregators with focused production-facing targets. Generate
repetitive CMake/audit inventory from checked data. Retire lexical audits once a
typed boundary or semantic oracle supersedes them. Keep historical evidence
available, but stop making every routine handoff carry an ever-growing recursive
proof archive when a signed content-addressed lineage index can bind it.
