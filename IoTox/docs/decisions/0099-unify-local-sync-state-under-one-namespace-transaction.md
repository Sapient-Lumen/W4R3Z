# ADR 0099: unify local synchronization state under one namespace transaction

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: cooperating-process serialization of implemented namespace state
- Depends on: ADRs 0093 through 0098

## Context

Signed publication and retention each had a private advisory lock, while accepted-HEAD installation,
activation, object admission, and reachability scans did not share either lock. Per-file atomic replace
prevented torn records, but it did not provide one stable relationship among roots and objects. A scan
could classify an object between its commit and HEAD update, or read roots across an activation or pin
transition.

Simply making every nested store acquire the same `flock` would deadlock: independent opens create
independent lock descriptions, including within one process. A shared transaction therefore needs an
explicit proof passed into nested operations.

## Decision

1. Each namespace has one persistent
   `transactions/<namespace>.transaction.lock`. The root and transaction directory are real,
   owner-owned mode-0700 directories; the lock is an owner-owned mode-0600, single-link, no-follow
   regular file.
2. `SyncNamespaceTransaction` owns the locked descriptor. It is move-only and records the acquiring
   process and thread. Namespace/root mismatch, moved-from use, fork inheritance, and cross-thread
   token reuse fail closed.
3. Public mutation entrypoints acquire the transaction once. Token-aware nested overloads require the
   exact namespace/root-bound proof and never reopen the lock.
4. The transaction spans every implemented local sync mutation: immutable object inventory/admission
   and commit, signed publication HEAD, accepted HEAD, activation pointer, and retained-revision
   pin/unpin.
5. Invalid conditions decidable without persisted state are rejected before creating the lock
   hierarchy. Once state is consulted, the token remains held through the final atomic commit.
6. Stored-state reachability acquires once, loads published, accepted, activated, and retained roots,
   inventories objects, and completes mark planning before release.
7. The former publisher-only and retention-only lock files are no longer used. There is no deployed
   migration obligation because synchronization remains default-off and outside the daemon.
8. No delete operation is introduced.

## Consequences

- Cooperating IoTox threads and processes cannot interleave implemented namespace mutations with a
  stable stored-state mark pass.
- Nested operations avoid recursive-flock deadlock without weakening thread exclusion.
- Direct pure planning remains available for deterministic tests but does not claim a stable
  filesystem snapshot.
- The lock does not control same-owner out-of-band filesystem mutation or namespace policy replacement
  performed outside these entrypoints.
- Accepted HEAD and activation records were canonical but unauthenticated at this decision; ADRs 0100
  and 0101 subsequently authenticate both.
  Complete signed retention-tip replay after restart also remains possible. These facts continue to
  prohibit garbage collection.

## Rejected alternatives

### Keep one lock per state family

Rejected because lock ordering cannot make an object/root scan atomic across publication, acceptance,
activation, and retention without a common outer boundary.

### Reacquire the namespace flock in every nested store

Rejected because a second independently opened lock description can block behind the first one held by
the same thread.

### Make the token freely shareable between threads

Rejected because sharing one already-held descriptor would bypass in-process mutual exclusion even
though cross-process exclusion remained intact.

### Enable collection after the shared lock lands

Rejected because transaction stability does not authenticate every root or prevent replay of a
complete older signed retention tip.
