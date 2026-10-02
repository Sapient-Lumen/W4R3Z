# ADR 0095: serialize signed-HEAD publishers and account immutable objects

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: local synchronization writer concurrency and object-store admission
- Depends on: ADRs 0093 and 0094
- Superseded lock scope: ADR 0099 replaces the publisher-only lock with one namespace transaction

## Context

An in-memory mutex linearized threads sharing one `SignedHeadStore`, but separate daemon/tool
processes could still load the same predecessor and each publish a competing successor. Namespace
policy also carried whole-store byte and object ceilings that the ordered publisher did not inventory
across existing revisions.

## Decision

1. Every signed-HEAD publication acquires an exclusive advisory `flock` on the namespace's persistent
   `published-heads/<namespace>.publish.lock` before loading its predecessor.
2. The lock file must be a no-follow, owner-owned, mode-0600, single-link regular file. Its root and
   parent are real owner-owned directories made mode 0700. Invalid lock state fails before HEAD load
   or mutation.
3. The lock remains held through predecessor verification, successor construction, and atomic HEAD
   replacement. Closing the descriptor releases it after the transaction.
4. The flat object directory has one strict inventory: only lowercase 256-bit digest names ending in
   `.artifact` or `.manifest` are accepted. Every entry must satisfy the existing private,
   owner-owned, single-link regular-file contract.
5. Inventory uses checked byte accumulation and refuses stores already beyond `maximum_objects` or
   `maximum_store_bytes`. Local publication and accepted-artifact installation admit prospective
   growth against the same inventory before committing a new object.

## Consequences

- Separate local publisher processes now form one exact signed chain instead of racing from a shared
  predecessor.
- Exact HEAD retry behavior remains unchanged under the process lock.
- Sequential local jobs cannot silently exceed configured whole-store object or byte ceilings.
- The lock is cooperative and local-filesystem scoped. It is not a distributed lease, and a same-user
  process can cause denial of service by retaining it.
- No single lock yet spans every future process's inventory, transfer, retention, pin, accepted-HEAD,
  and activation transaction. Concurrent object-producing job classes, retention/GC, and crash-point
  power-loss qualification remain later gates.

## Rejected alternatives

### Rely on atomic rename alone

Rejected because rename prevents torn files but does not prevent two valid successors from being
constructed from the same predecessor and one silently replacing the other.

### Put the lock in memory

Rejected because the missing guarantee is specifically coordination among separate processes.

### Delete objects automatically when a ceiling is reached

Rejected until pin, retained-revision, accepted-HEAD, active-revision, and current-publisher reachability
are one frozen graph. Admission must fail rather than guess which valid content is disposable.
