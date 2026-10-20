# ADR 0328: Fence open-descriptor sync source mutation

- Status: accepted and implemented
- Date: 2026-09-03

## Context

Tree-v2 publication scans an ordinary worktree, records each file's digest and byte length, then
installs missing immutable CAS objects from the recorded source paths under the namespace transaction.
An ordinary application does not take that transaction. It may already hold a writable file
descriptor and mutate bytes after the scan but before object installation.

That is a real synchronization boundary. If IoTox trusted only the scan result, it could author a
signed branch over stale or mismatched bytes. If the failure path was incomplete, it could also leave
a partial install temporary behind for later confusion.

## Decision

Add an owned tree-v2 worktree gate for the post-scan open-descriptor mutation case. The test writes a
source file, opens it for writing, scans the tree, rewrites the same path through the already-open
descriptor with same-length different bytes, and then attempts to store the stale scan.

The required result is fail-closed:

- the stale store fails with `protocol_error`;
- the digest-named immutable object is not installed;
- the fanout `.install.tmp` is removed; and
- a fresh scan of the new bytes can install exactly one new object successfully.

This keeps the existing production behavior: `copy_file_exact` still copies from the path but
validates the installed object against the scan's exact digest and byte length before exposing it.

## Consequences

This closes the direct scan/store open-descriptor source-mutation regression boundary. It gives the
precious-data roadmap a concrete piece of descriptor coverage without changing peer framing,
authority semantics, worktree projection, or the storage-fault harness.

It does not prove whole-VM power cuts, descriptor writes across a projection exchange, open
descriptors surviving remount or namespace restart, every durable-record corruption family, lying
storage, continuous filesystem watching, or backup suitability. Those remain larger storage
qualification gates.
