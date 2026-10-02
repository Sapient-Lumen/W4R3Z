# ADR 0098: plan synchronization reachability before removal

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: canonical object inventory and non-destructive live-root evidence
- Depends on: ADRs 0093 through 0097
- Subsequent transaction: ADR 0099 supplies the shared local mutation/scan lock

## Context

Object admission is bounded and explicit retention is authenticated, but safe collection requires an
exact answer to two separate questions: which immutable objects physically exist, and which persisted
states currently name them. Counts alone cannot explain missing live bytes, size conflicts, or an
object that appears unreferenced.

Deleting immediately after an ordinary sequence of root reads and a directory scan would be unsafe.
Publication, acceptance, activation, and pin mutation do not yet share one transaction lock. Accepted
HEAD and activation pointers are canonical but not cryptographically authenticated deletion
witnesses. A complete older signed retention tip can also be replayed after restart.

## Decision

1. The strict object-store scanner exposes one bounded canonical record per entry: object kind,
   32-byte digest identity, and exact nonzero byte count. Path text is reconstructed from identity and
   is not retained as authority-bearing state.
2. Inventory opens each candidate without following the final component, measures the acquired inode,
   and rejects malformed names, unexpected entries, non-private or linked files, invalid sizes,
   duplicate kind/identity pairs, arithmetic overflow, and namespace object/byte quota excess.
3. A pure planner validates and merges four current root classes:
   stable-device-signed published HEAD, accepted HEAD, activated revision, and authenticated explicit
   retained revisions.
4. A root identity appearing from multiple classes preserves a bit mask of every source. Conflicting
   expected sizes fail closed.
5. The plan reports exact existing rooted objects, missing roots, same-identity size mismatches, and
   inventory objects not named by any supplied root. Counts and byte totals remain bounded by policy.
6. The planner performs no filesystem mutation and exposes no delete operation. An `unreferenced`
   result means only “not named in this supplied snapshot,” never “safe to unlink.”

## Consequences

- Operators and later orchestration can explain object-store amplification and corrupt or incomplete
  live state without changing it.
- Publication, acceptance, activation, and pin overlap is explicit instead of being double-counted.
- A missing retention record is represented as unauthenticated absence; the plan records that fact.
- Before removal, accepted and activation state must become trustworthy deletion inputs, and one
  namespace transaction lock must span every root read or transition, inventory scan, mark, and
  unlink/fsync sequence.
- Restart-safe anti-rollback remains independently unresolved. This ADR does not weaken ADR 0097's
  whole-tip replay nonclaim.

## Rejected alternatives

### Delete everything except the current published HEAD

Rejected because accepted, activated, retained, and future in-flight revisions can name different
live objects.

### Treat digest-shaped filenames as sufficient inventory

Rejected because kind, exact opened-file size, ownership, mode, link count, quotas, and duplicate
identity all affect whether a record is a valid immutable object.

### Call unreferenced candidates garbage

Rejected because the current scan has neither a unified transaction snapshot nor complete
anti-rollback. Naming them garbage would turn diagnostic evidence into an unsafe authority claim.
