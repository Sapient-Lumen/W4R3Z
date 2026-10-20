# ADR 0096: freeze bounded synchronization retention before garbage collection

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: explicit retained-revision state; destructive collection remains prohibited
- Depends on: ADRs 0094 and 0095
- Subsequent authentication: ADR 0097 replaces the unsigned wire image with signed v2
- Superseded lock scope: ADR 0099 replaces the retention-only lock with one namespace transaction

## Context

The object store now has strict accounting, but deletion cannot be safe until operators can name old
revisions that must survive. The preserved toxsync component has a broad append-only pin journal and
content-v2 reachability collector. Importing it directly would also import its independent namespace
identity, clock-expiry semantics, and unaffiliated trust state before IoTox's own revision roots and
transaction locking are complete.

## Decision

1. IoTox introduces one local, transport-neutral retained-revision snapshot per namespace.
2. Each retained entry freezes generation, accepted record identity, artifact and manifest identities,
   and both exact sizes. Entries are sorted by strictly increasing generation and record identities
   are unique.
3. Pins can only be created from an `AcceptedHead` that validates against current namespace policy.
   Same-generation forks and conflicting duplicate identities fail closed.
4. `maximum_retained_revisions` is enforced before mutation. Exact retries are idempotent, and unpin
   names the complete accepted-record identity rather than an ambiguous generation.
5. The canonical fixed-layout snapshot is atomically replaced under a private persistent advisory
   mutation lock. State and lock files are owner-owned, mode 0600, single-link, no-follow files beneath
   real owner-only directories.
6. No destructive GC is enabled by this decision.

## Consequences

- Explicit retention survives restart and has a small bounded memory/disk representation.
- Pin mutation is serialized across local processes without introducing remote or clock-based expiry.
- A missing snapshot means no explicit pins; it does not imply that any object is unreachable or safe
  to delete.
- The current snapshot is structurally canonical and owner-private but not yet signed or hash-chained.
  It therefore cannot be the sole authority for deleting bytes.
- Before destructive GC, IoTox must authenticate retention state and hold one ordered transaction lock
  across object producers, signed/accepted HEADs, activation, retention mutation, reachability marking,
  and deletion. Until then, admission fails at store ceilings instead of collecting automatically.

## Rejected alternatives

### Delete every object not named by the current HEAD

Rejected because it would destroy accepted, activated, explicitly retained, interrupted-transfer, or
rollback-basis content.

### Import toxsync's pin journal unchanged

Rejected because namespace identity, authorization, expiry clocks, and content-v2 graph reachability
must first be reconciled with IoTox's stable principals and fixed signed HEAD.

### Treat a private canonical snapshot as authenticated

Rejected. File permissions and canonical decoding detect many failures, but they do not provide a
cryptographic deletion authorization boundary.
