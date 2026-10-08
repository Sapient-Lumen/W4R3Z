# Rev0951 research notes

Consulted 2026-07-30.

## Syncthing Block Exchange Protocol v1

- https://docs.syncthing.net/specs/bep-v1.html

The protocol retains an index ID and monotonically increasing sequence so index
updates can continue from a peer's known cutpoint across connections. The useful
architectural precedent is a small durable continuation paired with an
authoritative indexed dataset. AnonSync's remote cursor is deliberately weaker:
it controls scheduling order only and cannot authorize operations, predecessor
bytes, payloads, or filesystem effects.

The same precedent suggests the next scale refactor should not overload the
cursor. A durable exact metadata/subtree, remote-work, and payload index should
own incremental sequence and bounded queues, while descriptor-rooted scans
remain rebuild and rotating-scrub authority.

## SQLite transactions

- https://sqlite.org/lang_transaction.html

SQLite documents `BEGIN IMMEDIATE` as beginning a write transaction immediately
and potentially failing when another writer already owns the database. Rev0951
uses that shape for exact schema migration and optimistic cursor publication:
reload expected scheduling state, update one singleton, re-read staged state,
and commit through the retained transaction owner.

## Linux inotify

- https://man7.org/linux/man-pages/man7/inotify.7.html

The interface documents event-queue overflow and the need for applications to
rebuild state; rename pairing is also inherently racy. This supports AnonSync's
existing split: watcher notifications accelerate work, while rooted descriptor
traversal remains repair, absence, and rebuild authority.

## Inference from the crash-order audit

Scheduling authorization should not depend on ephemeral lifetime of a repair
journal. The catalog's exact predecessor identity is durable content history,
but even it should nominate rather than authorize a replacement. Fresh metadata
can cheaply reject obvious divergence; the existing exact apply owner must keep
the load-bearing complete rehash and rooted publication proof.

Likewise, a verified payload inventory is a frozen readiness observation. It may
be shared to eliminate repeated namespace work, but payload bytes must still be
opened and re-proved, and a digest arriving after the snapshot must remain
ordinary next-pass work rather than mutable-snapshot magic.
